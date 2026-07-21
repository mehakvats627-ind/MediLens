import json
import time
from pathlib import Path
import sys

# Ensure the project root is in sys.path to enable smooth imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from utils.logger import logger
import config

from parser.report_detector import ReportDetector
from parser.pdf_parser import PDFParser
from parser.ocr_parser import OCRParser
from extractor.patient_extractor import PatientExtractor
from extractor.parameter_extractor import ParameterExtractor
from validator.validator import Validator
from converter.json_converter import JSONConverter
from integration.gemini_connector import GeminiConnector

def process_report(file_path: str) -> dict:
    """
    Main entry point for backend integration.
    Processes a medical report file (PDF or image) end-to-end:
    1. Detects report type (digital PDF, scanned PDF, or image).
    2. Parses text (via PyMuPDF for digital, falling back to EasyOCR for scans/images).
    3. Extracts patient demographics and laboratory parameters.
    4. Validates parameters for biological bounds and OCR decimal typos.
    5. Converts to standard JSON structure.
    6. Connects with Gemini AI for high-level clinical interpretation.
    7. Saves the output JSON and returns the dictionary payload.
    
    Args:
        file_path (str): Path to the report file (PDF, JPG, JPEG, PNG).
        
    Returns:
        dict: Standardized validated JSON payload including patient details,
              laboratory parameters, and Gemini clinical interpretation.
    """
    start_time = time.time()
    logger.info(f"========== Start Processing Report: {file_path} ==========")
    
    input_path = Path(file_path)
    if not input_path.exists():
        logger.error(f"Input file does not exist: {file_path}")
        raise FileNotFoundError(f"Report file not found at: {file_path}")

    try:
        # Step 1: Detect report type
        report_type = ReportDetector.detect_report_type(str(input_path))
        logger.info(f"Step 1: Detected report type: {report_type}")

        # Step 2: Extract text (with automatic OCR fallback)
        raw_text = ""
        
        if report_type == "digital_pdf":
            try:
                raw_text = PDFParser.extract_text(str(input_path))
                if not raw_text.strip():
                    raise ValueError("Digital PDF extraction returned no text.")
            except Exception as e:
                logger.warning(f"Digital PDF extraction failed: {e}. Switching to OCR fallback...")
                report_type = "scanned_pdf"

        # If it is scanned or digital parsing yielded no text
        if report_type == "scanned_pdf":
            # Render PDF pages to images and run EasyOCR
            # We save preprocessed page images in outputs/ for debugging
            debug_preprocess_dir = config.OUTPUT_DIR / f"debug_{input_path.stem}"
            raw_text = OCRParser.extract_text_from_pdf(str(input_path), str(debug_preprocess_dir))
            
        elif report_type == "image":
            debug_image_path = config.OUTPUT_DIR / f"debug_{input_path.name}"
            raw_text = OCRParser.extract_text_from_image(str(input_path), str(debug_image_path))

        # Check that we recovered some raw text
        if not raw_text.strip():
            logger.error("Failed to extract any text content from the report.")
            raise ValueError("Extraction yielded empty text content. Report is unreadable.")

        # Step 3: Extract patient profile and laboratory parameters
        logger.info("Step 3: Extracting data from text...")
        raw_patient = PatientExtractor.extract_patient_info(raw_text)
        raw_parameters = ParameterExtractor.extract_parameters(raw_text)

        # Step 4: Validate extracted info (demographics, decimals omissions, ranges)
        logger.info("Step 4: Validating extracted data...")
        validated_patient = Validator.validate_patient_info(raw_patient)
        validated_parameters = Validator.validate_parameters(raw_parameters)

        # Step 5: Convert validated data into standardized schema format
        logger.info("Step 5: Converting to standard JSON schema...")
        report_payload = JSONConverter.to_dict(validated_patient, validated_parameters)

        # Step 6: Connect with Gemini AI for clinical interpretation and recommendations
        logger.info("Step 6: Generating Gemini clinical summary and recommendations...")
        gemini_analysis = GeminiConnector.analyze_report(report_payload)
        report_payload["analysis"] = gemini_analysis

        # Add execution performance metadata
        elapsed_time = time.time() - start_time
        report_payload["metadata"] = {
            "source_file": input_path.name,
            "report_type": report_type,
            "processed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time_sec": round(elapsed_time, 2)
        }

        # Step 7: Save structured JSON file to outputs/
        output_file_name = f"{input_path.stem}_output.json"
        output_file_path = config.OUTPUT_DIR / output_file_name
        
        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(report_payload, f, indent=4, default=str)
            
        logger.info(f"Saved structured report analysis to: {output_file_path}")
        logger.info(f"========== Successfully Processed Report (Took {elapsed_time:.2f}s) ==========")
        
        return report_payload

    except Exception as e:
        logger.error(f"========== Pipeline Failure on {file_path}: {e} ==========", exc_info=True)
        # Re-raise to let the calling backend route handle the exception details
        raise e
