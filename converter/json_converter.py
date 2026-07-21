import json
from utils.logger import logger

class JSONConverter:
    """
    Standardizes the validated patient data and medical parameter structures 
    into a consistent JSON schema for backend delivery.
    """

    @staticmethod
    def to_dict(validated_patient: dict, validated_parameters: list) -> dict:
        """
        Combines patient and parameter data into a unified dictionary structure.
        
        Args:
            validated_patient (dict): Validated patient info from Validator.
            validated_parameters (list): Validated parameter list from Validator.
            
        Returns:
            dict: Structured data dictionary matching the final JSON schema.
        """
        logger.info("Converting validated data structures to standardized schema.")
        
        # Structure the patient profile
        patient_schema = {
            "name": validated_patient.get("name"),
            "age": validated_patient.get("age"),
            "gender": validated_patient.get("gender"),
            "patient_id": validated_patient.get("patient_id"),
            "referred_by": validated_patient.get("doctor"),
            "lab_name": validated_patient.get("hospital"),
            "report_date": validated_patient.get("date")
        }

        # Structure the parameters
        parameters_schema = []
        for param in validated_parameters:
            # We map values: use the numeric value if valid, or fall back to the original string.
            # E.g., if value is "9.5", numeric_value is 9.5 (float).
            # If value is "Positive", numeric_value is None, we keep "Positive".
            # If there's a corrected value (like 9.5 corrected from 95), the backend gets the original "95"
            # as value, but we include "corrected_value" and "is_valid: False" so the backend has visibility.
            val = param.get("numeric_value")
            if val is None:
                val = param.get("value")
                
            param_item = {
                "parameter": param.get("parameter"),
                "value": val,
                "unit": param.get("unit"),
                "reference_range": param.get("reference_range"),
                "status": param.get("status"),
                "raw_value": param.get("value"),  # Keep original value unchanged for audits
                "is_valid": param.get("is_valid", True)
            }
            
            # Optional debug fields only added if validation flags exist
            if param.get("low_confidence"):
                param_item["low_confidence"] = True
                param_item["corrected_value"] = param.get("corrected_value")
                
            if param.get("validation_error"):
                param_item["validation_error"] = param.get("validation_error")

            parameters_schema.append(param_item)

        # Assemble the final payload
        payload = {
            "patient": patient_schema,
            "parameters": parameters_schema
        }
        
        return payload

    @staticmethod
    def to_json_string(validated_patient: dict, validated_parameters: list, indent: int = 4) -> str:
        """
        Serializes the structured data dictionary into a formatted JSON string.
        """
        data = JSONConverter.to_dict(validated_patient, validated_parameters)
        return json.dumps(data, indent=indent, default=str)
