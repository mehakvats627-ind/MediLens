import unittest
import sys
from pathlib import Path

# Add project root directory to sys.path so we can import modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from parser.report_detector import ReportDetector, UnsupportedFileError
from extractor.patient_extractor import PatientExtractor
from extractor.parameter_extractor import ParameterExtractor
from validator.validator import Validator
from converter.json_converter import JSONConverter
from integration.gemini_connector import GeminiConnector
from integration.process_report import process_report
from utils.generate_test_reports import generate_sample_digital_pdf

class TestMedicalReportAnalyzer(unittest.TestCase):
    """
    Unit tests for the Medical Report Analyzer pipeline components:
    detection, extraction, validation, JSON formatting, and Gemini integration fallbacks.
    """

    def test_report_detector_unsupported_file(self):
        """
        Verify that detector correctly rejects unsupported extensions.
        """
        # Create a temporary dummy file with an unsupported extension
        dummy_file = Path(__file__).resolve().parent / "dummy_test.txt"
        dummy_file.write_text("unsupported content format testing")
        try:
            with self.assertRaises(UnsupportedFileError):
                ReportDetector.detect_report_type(str(dummy_file))
        finally:
            if dummy_file.exists():
                dummy_file.unlink()

    def test_patient_extractor(self):
        """
        Verify that PatientExtractor successfully extracts and normalizes demographics.
        """
        mock_text = (
            "PATIENT REPORT\n"
            "PATIENT NAME : Jane Doe\n"
            "AGE : 42 Yrs    GENDER: Female\n"
            "PATIENT ID: PID-987654\n"
            "REFERRED BY: Dr. Gregory House\n"
            "LABORATORY: Metro Diagnostics Centre\n"
            "DATE : 15/04/2026\n"
        )
        
        extracted = PatientExtractor.extract_patient_info(mock_text)
        
        self.assertEqual(extracted["name"], "Jane Doe")
        self.assertEqual(extracted["age"], "42")
        self.assertEqual(extracted["gender"], "Female")
        self.assertEqual(extracted["patient_id"], "PID-987654")
        self.assertEqual(extracted["doctor"], "Gregory House")
        self.assertEqual(extracted["hospital"], "Metro Diagnostics Centre")
        self.assertEqual(extracted["date"], "15/04/2026")

    def test_parameter_extractor(self):
        """
        Verify that ParameterExtractor extracts parameters, values, units, ranges, and status.
        """
        mock_text = (
            "Test Name           Result      Unit      Ref Range       Status\n"
            "Hb                  14.2        g/dL      12.0 - 16.0     Normal\n"
            "WBC Count           7500        /uL       4000-11000      \n"
            "RBS                 185         mg/dL     70 - 140        High\n"
            "Serum Uric Acid     8.2         mg/dL     3.5 - 7.2       H\n"
        )
        
        parameters = ParameterExtractor.extract_parameters(mock_text)
        
        # Verify normalizations and lengths
        self.assertEqual(len(parameters), 4)
        
        # Check Hb -> Haemoglobin mapping
        hb_param = next(p for p in parameters if p["parameter"] == "Haemoglobin")
        self.assertEqual(hb_param["value"], "14.2")
        self.assertEqual(hb_param["unit"], "g/dL")
        self.assertEqual(hb_param["reference_range"], "12.0 - 16.0")
        self.assertEqual(hb_param["status"], "Normal")

        # Check WBC Count -> White Blood Cell Count mapping
        wbc_param = next(p for p in parameters if p["parameter"] == "White Blood Cell Count")
        self.assertEqual(wbc_param["value"], "7500")
        self.assertEqual(wbc_param["unit"], "/uL")
        self.assertEqual(wbc_param["reference_range"], "4000-11000")
        
        # Check RBS -> Random Blood Sugar mapping
        rbs_param = next(p for p in parameters if p["parameter"] == "Random Blood Sugar")
        self.assertEqual(rbs_param["value"], "185")
        self.assertEqual(rbs_param["status"], "High")

        # Check Uric Acid mapping and status normalisation ('H' -> 'High')
        uric_param = next(p for p in parameters if p["parameter"] == "Serum Uric Acid")
        self.assertEqual(uric_param["value"], "8.2")
        self.assertEqual(uric_param["status"], "High")

    def test_validator_demographics(self):
        """
        Verify that Validator catches impossible age values and trims names.
        """
        bad_demographics = {
            "name": "  Mr. Alice Cooper  ",
            "age": "400",  # Impossible age
            "gender": "m",
            "patient_id": " 123 ",
            "doctor": "Dr. Frankenstein",
            "hospital": "Transylvania Clinic",
            "date": "10-10-2025"
        }
        
        validated = Validator.validate_patient_info(bad_demographics)
        
        self.assertEqual(validated["name"], "Alice Cooper")
        self.assertIsNone(validated["age"])  # Rejected
        self.assertIn("age_warning", validated)
        self.assertEqual(validated["gender"], "Male")
        self.assertEqual(validated["patient_id"], "123")

    def test_validator_decimal_typo_detection(self):
        """
        Verify that Validator flags missing decimals (e.g. 95 instead of 9.5 for Haemoglobin).
        """
        suspicious_parameters = [
            {
                "parameter": "Haemoglobin",
                "value": "95",
                "unit": "g/dL",
                "reference_range": "12.0 - 16.0",
                "status": None
            },
            {
                "parameter": "Serum Creatinine",
                "value": "11.0",
                "unit": "mg/dL",
                "reference_range": "0.6 - 1.2",
                "status": None
            }
        ]
        
        validated = Validator.validate_parameters(suspicious_parameters)
        
        # Assert Hb decimal error flagged
        hb_val = next(v for v in validated if v["parameter"] == "Haemoglobin")
        self.assertFalse(hb_val["is_valid"])
        self.assertTrue(hb_val["low_confidence"])
        self.assertEqual(hb_val["corrected_value"], 9.5)
        
        # Assert Creatinine decimal error flagged
        creat_val = next(v for v in validated if v["parameter"] == "Serum Creatinine")
        self.assertFalse(creat_val["is_valid"])
        self.assertEqual(creat_val["corrected_value"], 1.1)

    def test_validator_status_inference(self):
        """
        Verify that Validator infers correct Status based on Reference Range if missing.
        """
        params = [
            {
                "parameter": "Haemoglobin",
                "value": "9.5",
                "unit": "g/dL",
                "reference_range": "12-16",
                "status": None  # Missing status
            },
            {
                "parameter": "Random Blood Sugar",
                "value": "150.0",
                "unit": "mg/dL",
                "reference_range": "70 - 140",
                "status": None  # Missing status
            }
        ]
        
        validated = Validator.validate_parameters(params)
        
        hb_val = next(v for v in validated if v["parameter"] == "Haemoglobin")
        self.assertEqual(hb_val["status"], "Low")
        
        rbs_val = next(v for v in validated if v["parameter"] == "Random Blood Sugar")
        self.assertEqual(rbs_val["status"], "High")

    def test_json_converter(self):
        """
        Verify that JSONConverter compiles structures to matching backend schema.
        """
        patient_data = {
            "name": "Bruce Wayne",
            "age": 35,
            "gender": "Male",
            "patient_id": "BAT-1",
            "doctor": "Alfred Pennyworth",
            "hospital": "Wayne Manor Clinic",
            "date": "19-07-2026"
        }
        
        params = [
            {
                "parameter": "Haemoglobin",
                "value": "15.5",
                "numeric_value": 15.5,
                "unit": "g/dL",
                "reference_range": "12-16",
                "status": "Normal",
                "is_valid": True
            }
        ]
        
        schema_dict = JSONConverter.to_dict(patient_data, params)
        
        self.assertIn("patient", schema_dict)
        self.assertIn("parameters", schema_dict)
        self.assertEqual(schema_dict["patient"]["name"], "Bruce Wayne")
        self.assertEqual(schema_dict["patient"]["referred_by"], "Alfred Pennyworth")
        self.assertEqual(schema_dict["parameters"][0]["parameter"], "Haemoglobin")
        self.assertEqual(schema_dict["parameters"][0]["value"], 15.5)

    def test_gemini_fallback(self):
        """
        Verify that GeminiConnector handles configuration errors gracefully.
        """
        # Call analyze_report when config key is empty (or mock environment)
        import config
        old_key = config.GEMINI_API_KEY
        config.GEMINI_API_KEY = None
        
        try:
            analysis = GeminiConnector.analyze_report({})
            self.assertIn("clinical_summary", analysis)
            self.assertIn("risk_assessment", analysis)
            self.assertIn("follow_up_suggestions", analysis)
            self.assertEqual(analysis["abnormal_parameters"], [
                "Review parameter status flags (High/Low) in the structured parameters list above."
            ])
            self.assertIn("medical_disclaimer", analysis)
        finally:
            config.GEMINI_API_KEY = old_key

    def test_end_to_end_pipeline(self):
        """
        Verify that process_report executes end-to-end on a digital PDF.
        """
        import config
        sample_dir = config.SAMPLE_REPORTS_DIR
        sample_pdf = sample_dir / "digital_report.pdf"
        
        # Ensure sample report is generated if missing
        if not sample_pdf.exists():
            generate_sample_digital_pdf(sample_pdf)
            
        # Run pipeline
        result = process_report(str(sample_pdf))
        
        # Assert structure
        self.assertIn("patient", result)
        self.assertIn("parameters", result)
        self.assertIn("metadata", result)
        self.assertIn("analysis", result)
        
        # Assert patient details
        self.assertEqual(result["patient"]["name"], "Bruce Wayne")
        self.assertEqual(result["patient"]["age"], 35)
        
        # Assert parameters are populated and cleaned of demographics
        params_list = result["parameters"]
        hb_param = next((p for p in params_list if p["parameter"] == "Haemoglobin"), None)
        self.assertIsNotNone(hb_param)
        self.assertEqual(hb_param["value"], 14.2)
        
        # Age should have been stripped from the parameter results array
        age_param = next((p for p in params_list if p["parameter"] == "Age"), None)
        self.assertIsNone(age_param)

if __name__ == "__main__":
    unittest.main()
