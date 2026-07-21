import re
from utils.logger import logger

class PatientExtractor:
    """
    Extracts key patient details from raw report text using regular expressions.
    Extracted fields: Patient Name, Age, Gender, Patient ID, Doctor, Hospital, and Report Date.
    """

    # Compiled regex patterns for patient information
    PATTERNS = {
        "name": [
            re.compile(r"(?:patient\s+name|name\s+of\s+patient)\s*[:\-\s]?\s*(?:mr\.|ms\.|mrs\.|dr\.|master|baby|mast\.)?\s*([a-zA-Z\s\.\u00C0-\u017F]+)", re.IGNORECASE),
            re.compile(r"\b(?:patient|name)\s*[:\-]\s*(?:mr\.|ms\.|mrs\.|dr\.|master|baby|mast\.)?\s*([a-zA-Z\s\.\u00C0-\u017F]+)", re.IGNORECASE),
        ],
        "age": [
            re.compile(r"(?:age|yrs|years)\s*[:\-\s]\s*(\d{1,3})\s*(?:yrs|years|y/o|y|m|months)?", re.IGNORECASE),
            re.compile(r"\b(\d{1,3})\s*(?:years|yrs|y/o|yo)\s*(?:old)?\b", re.IGNORECASE),
            re.compile(r"\b(?:age)\s*[:\-\s]\s*(\d{1,3})\b", re.IGNORECASE),
        ],
        "gender": [
            re.compile(r"\b(?:gender|sex)\s*[:\-\s]\s*(male|female|m|f|other|transgender|boy|girl)\b", re.IGNORECASE),
            re.compile(r"\b(male|female|other)\s*/\s*(male|female|other)\b", re.IGNORECASE),  # Matches M/F structures
            re.compile(r"\b([mf])\b\s*[:\-\s]?\s*(?:age)?", re.IGNORECASE),
        ],
        "patient_id": [
            re.compile(r"(?:patient\s*id|pid|uhid|mrn|reg\s*(?:no|num|number)|registration\s*(?:no|number)|ref\s*(?:no|num))\s*[:\-\s]\s*([a-zA-Z0-9\-/\s]+)", re.IGNORECASE),
            re.compile(r"\b(?:id|uhid|mrn)\s*[:\-\s]\s*([a-zA-Z0-9\-/\s]+)", re.IGNORECASE),
        ],
        "doctor": [
            re.compile(r"(?:referred\s+by|ref\s+by|doctor|dr\.|physician|consultant|ref\s+dr)\s*[:\-\s]\s*(?:dr\.?|dr)?\s*([a-zA-Z\s\.\-\u00C0-\u017F]+)", re.IGNORECASE),
            re.compile(r"referred\s+by\s*[:\-\s]\s*([a-zA-Z\s\.\-]+)", re.IGNORECASE),
            re.compile(r"dr\.\s*([a-zA-Z\s\.\-]+)", re.IGNORECASE),
        ],
        "hospital": [
            re.compile(r"(?:hospital|lab|laboratory|clinic|center|centre|diagnostic\s*center|diagnostics)\s*[:\-\s]\s*([a-zA-Z0-9\s\.\-&,\u00C0-\u017F]+)", re.IGNORECASE),
            re.compile(r"(?:diagnostic\s*labs|health\s*care|med\s*centre)\s*[:\-\s]\s*([a-zA-Z0-9\s\.\-&,]+)", re.IGNORECASE),
        ],
        "date": [
            re.compile(r"(?:date|report\s*date|collection\s*date|printed\s*on|date\s*of\s*report)\s*[:\-\s]\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2})", re.IGNORECASE),
            re.compile(r"\b(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2})\b"),
            re.compile(r"\b(\d{1,2}\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{2,4})\b", re.IGNORECASE),
        ]
    }

    @classmethod
    def extract_patient_info(cls, text: str) -> dict:
        """
        Parses text to extract demographics and report metadata.
        
        Args:
            text (str): Raw extracted document text.
            
        Returns:
            dict: Structured dictionary of patient details.
        """
        logger.info("Starting patient information extraction...")
        
        extracted_data = {
            "name": None,
            "age": None,
            "gender": None,
            "patient_id": None,
            "doctor": None,
            "hospital": None,
            "date": None
        }

        # Preprocess text slightly to help matching
        # (replace multiple spaces with single space, preserve lines)
        cleaned_lines = [re.sub(r'\s+', ' ', line).strip() for line in text.splitlines() if line.strip()]
        flat_text = "\n".join(cleaned_lines)

        for field, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                # Check line by line first, which is cleaner
                match = None
                for line in cleaned_lines:
                    match = pattern.search(line)
                    if match:
                        val = match.group(1).strip()
                        if cls._validate_field_raw(field, val):
                            extracted_data[field] = cls._clean_field_val(field, val)
                            break
                
                # If no match line-by-line, search the full text (multiline)
                if not extracted_data[field]:
                    match = pattern.search(flat_text)
                    if match:
                        val = match.group(1).strip()
                        if cls._validate_field_raw(field, val):
                            extracted_data[field] = cls._clean_field_val(field, val)
                            break
                            
            if extracted_data[field]:
                logger.info(f"Extracted {field.upper()}: {extracted_data[field]}")
            else:
                logger.warning(f"Failed to extract {field.upper()} field.")

        # Fallback for hospital: Check first 3 lines of report if no labeled hospital was found.
        # Often the header carries the hospital name without a label.
        if not extracted_data["hospital"] and len(cleaned_lines) > 0:
            for i in range(min(3, len(cleaned_lines))):
                line = cleaned_lines[i]
                # If the line is short-to-medium and contains typical hospital words
                if any(word in line.lower() for word in ["hospital", "lab", "clinic", "diagnostic", "centre", "center", "health"]):
                    extracted_data["hospital"] = line
                    logger.info(f"Hospital fallback extraction (from header line {i+1}): {line}")
                    break

        return extracted_data

    @staticmethod
    def _validate_field_raw(field: str, val: str) -> bool:
        """
        Performs quick validation of the raw extracted value before recording it.
        """
        if not val or len(val) < 2:
            return False
        
        # Stop matches that capture titles as names
        if field == "name":
            if val.lower() in ["name", "patient name", "patient"]:
                return False
        
        # Don't capture numeric fields as names
        if field in ["name", "doctor"] and re.match(r'^\d+$', val):
            return False

        # Don't capture excessively long garbage text
        if len(val) > 100:
            return False

        return True

    @staticmethod
    def _clean_field_val(field: str, val: str) -> str:
        """
        Cleans up extracted fields: normalizes punctuation, cleans casing, removes noise.
        """
        # Trim leading/trailing punctuation commonly captured (like colons, semicolons, dashes)
        val = re.sub(r'^[:\-\s\.]+', '', val)
        val = re.sub(r'[:\-\s\.]+$', '', val)
        val = re.sub(r'\s+', ' ', val).strip()

        if field == "gender":
            val_lower = val.lower()
            if val_lower.startswith("m"):
                return "Male"
            elif val_lower.startswith("f"):
                return "Female"
            elif val_lower.startswith("o"):
                return "Other"
            
        elif field == "age":
            # Extract just digits if any text is still attached
            digits = re.findall(r'\d+', val)
            if digits:
                return digits[0]
            
        elif field == "name":
            # Strip remaining titles if any match was captured
            val = re.sub(r'^(mr|ms|mrs|dr|master|baby|mast|shri|smt)\.?\s+', '', val, flags=re.IGNORECASE)
            
        elif field == "doctor":
            val = re.sub(r'^(dr|doctor|physician)\.?\s+', '', val, flags=re.IGNORECASE)

        return val
