import re
from utils.logger import logger

class Validator:
    """
    Validates patient information and medical parameters to catch extraction/OCR errors.
    Detects missing decimal points, biological boundary anomalies, and normalizes fields.
    """

    @classmethod
    def validate_patient_info(cls, patient_info: dict) -> dict:
        """
        Validates patient metadata, enforcing biological bounds on age and cleansing fields.
        """
        logger.info("Validating patient demographics...")
        validated = patient_info.copy()

        # 1. Clean Name
        if validated.get("name"):
            name = str(validated["name"]).strip()
            # Strip titles like Mr., Ms., Mrs.
            name = re.sub(r'^(mr|ms|mrs|dr|master|baby|mast|shri|smt)\.?\s+', '', name, flags=re.IGNORECASE)
            # If name is excessively long or has digits, flag it
            if len(name) > 60 or any(char.isdigit() for char in name):
                logger.warning(f"Patient name looks suspicious: {name}")
                validated["name_warning"] = "Name may contain OCR artifacts or run-on text"
            validated["name"] = name
        else:
            validated["name"] = None

        # 2. Validate Age (Reject age < 0 or age > 120, check for OCR digits swap)
        if validated.get("age"):
            try:
                age_val = int(str(validated["age"]).strip())
                if age_val < 0 or age_val > 120:
                    logger.warning(f"Invalid age value detected: {age_val}. Rejecting.")
                    validated["age"] = None
                    validated["age_warning"] = f"Age {age_val} rejected as biologically impossible."
                else:
                    validated["age"] = age_val
            except ValueError:
                logger.warning(f"Non-integer age value: {validated['age']}. Setting to None.")
                validated["age"] = None
        else:
            validated["age"] = None

        # 3. Clean Gender
        gender = validated.get("gender")
        if gender:
            gender_str = str(gender).strip().lower()
            if gender_str.startswith("m"):
                validated["gender"] = "Male"
            elif gender_str.startswith("f"):
                validated["gender"] = "Female"
            elif gender_str.startswith("o"):
                validated["gender"] = "Other"
            else:
                validated["gender"] = None
        else:
            validated["gender"] = None

        # 4. Clean other text fields
        for field in ["patient_id", "doctor", "hospital"]:
            if validated.get(field):
                validated[field] = str(validated[field]).strip()
            else:
                validated[field] = None

        # 5. Clean Date
        if validated.get("date"):
            validated["date"] = str(validated["date"]).strip()

        return validated

    @classmethod
    def validate_parameters(cls, parameters: list) -> list:
        """
        Validates laboratory parameters to detect OCR errors like decimal omission
        (e.g., 95 instead of 9.5) or out-of-bounds metrics.
        """
        logger.info("Validating medical laboratory parameters...")
        validated_list = []

        for param in parameters:
            val_dict = param.copy()
            
            # Clean values
            raw_val_str = str(val_dict.get("value", "")).strip()
            val_dict["value"] = raw_val_str
            
            if val_dict.get("unit"):
                val_dict["unit"] = str(val_dict["unit"]).strip()
            if val_dict.get("reference_range"):
                val_dict["reference_range"] = str(val_dict["reference_range"]).strip()

            # Parse numeric value
            num_val = cls._parse_numeric_value(raw_val_str)
            
            if num_val is None:
                # Value is non-numeric (e.g. "Negative", "Nil", "Reactive")
                val_dict["numeric_value"] = None
                val_dict["is_valid"] = True
                validated_list.append(val_dict)
                continue

            val_dict["numeric_value"] = num_val

            # Enforce that laboratory values cannot be negative where impossible
            # (We treat all numeric medical parameter ranges as non-negative by default)
            if num_val < 0:
                logger.warning(f"Negative parameter value detected: {num_val} for {val_dict['parameter']}")
                val_dict["is_valid"] = False
                val_dict["validation_error"] = "Negative value is invalid for this parameter."
                validated_list.append(val_dict)
                continue

            # Check for Decimal Point Omission (e.g. 95 instead of 9.5, or 12 instead of 1.2)
            ref_range = val_dict.get("reference_range")
            low_bound, high_bound = cls._parse_reference_bounds(ref_range)

            is_valid = True
            error_msg = None
            low_confidence = False

            if high_bound is not None and high_bound > 0:
                ratio = num_val / high_bound
                if ratio >= 5.0 and ratio <= 15.0:
                    corrected_test_value = num_val / 10.0
                    low_bound_check = low_bound if low_bound is not None else 0
                    if corrected_test_value >= low_bound_check * 0.5 and corrected_test_value <= high_bound * 1.5:
                        is_valid = False
                        low_confidence = True
                        error_msg = f"Possible decimal point omission error: value '{raw_val_str}' is extremely high relative to reference range '{ref_range}'. Suggesting '{corrected_test_value}'."
                        val_dict["corrected_value"] = corrected_test_value
                        logger.warning(f"Decimal omission anomaly detected for {val_dict['parameter']}: {raw_val_str} vs range {ref_range}")

            # Check biological extremes (e.g., Haemoglobin > 30, Fasting Sugar > 1000)
            # These are extremely high values that indicate OCR error or severe anomaly.
            param_name_lower = val_dict["parameter"].lower()
            if "haemoglobin" in param_name_lower and num_val > 30.0:
                is_valid = False
                # Preserve the original numeric value but clearly mark the anomaly.
                if not error_msg:
                    error_msg = f"Value '{raw_val_str}' exceeds maximum credible biological limit for Haemoglobin."
            elif "fasting blood sugar" in param_name_lower and num_val > 1000.0:
                is_valid = False
                if not error_msg:
                    error_msg = f"Value '{raw_val_str}' exceeds maximum credible limit for fasting blood sugar."

            # Update status flag if missing or incorrect
            if is_valid and not val_dict.get("status") and low_bound is not None and high_bound is not None:
                if num_val < low_bound:
                    val_dict["status"] = "Low"
                elif num_val > high_bound:
                    val_dict["status"] = "High"
                else:
                    val_dict["status"] = "Normal"

            val_dict["is_valid"] = is_valid
            if error_msg:
                val_dict["validation_error"] = error_msg
            if low_confidence:
                val_dict["low_confidence"] = True

            validated_list.append(val_dict)

        return validated_list

    @staticmethod
    def _parse_numeric_value(val_str: str) -> float:
        """
        Extracts the float representation of the value, stripping comparison symbols like < or >.
        """
        # Remove symbols
        clean_str = re.sub(r'[^\d\.]', '', val_str)
        try:
            return float(clean_str)
        except ValueError:
            return None

    @staticmethod
    def _parse_reference_bounds(ref_range: str) -> tuple:
        """
        Parses a reference range string to return (low_bound, high_bound) floats.
        Supports formats: "12-16", "12.0 - 16.0", "< 1.2", "up to 40", "0.6 to 1.2"
        """
        if not ref_range:
            return None, None

        ref_clean = ref_range.lower().strip()

        # Handle operators like < or <=
        if "<" in ref_clean:
            num = Validator._parse_numeric_value(ref_clean)
            return 0.0, num
        
        # Handle operators like > or >=
        if ">" in ref_clean:
            num = Validator._parse_numeric_value(ref_clean)
            return num, 99999.0  # Open-ended high bound

        # Handle "up to X"
        if "up to" in ref_clean:
            num = Validator._parse_numeric_value(ref_clean)
            return 0.0, num

        # Handle range separated by - or "to"
        # Matches: "12-16", "12.0 - 16.0", "12 to 16"
        parts = re.split(r'[\-]|to', ref_clean)
        if len(parts) == 2:
            low = Validator._parse_numeric_value(parts[0])
            high = Validator._parse_numeric_value(parts[1])
            if low is not None and high is not None:
                return low, high

        return None, None
