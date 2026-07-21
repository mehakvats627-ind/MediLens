import re
from utils.logger import logger
from config import PARAMETER_NORMALIZATION_MAP

class ParameterExtractor:
    """
    Extracts laboratory parameters (name, value, unit, reference range, abnormal status) 
    from raw report text. Standardizes and normalizes parameter names, and filters out duplicates.
    """

    # Matches a value candidate (e.g., 14.2, 95, 0.85, <0.01)
    # The value is usually a float or integer, occasionally preceded by comparison signs.
    VALUE_REGEX = re.compile(r'\b(?:<|>|<=|>=)?\s*\d+(?:\.\d+)?\b')
    UNIT_NORMALIZATION_MAP = {
        "g dl": "g/dL",
        "g/dl": "g/dL",
        "mg dl": "mg/dL",
        "mg/dl": "mg/dL",
        "u/l": "U/L",
        "ul": "/uL",
        "/ul": "/uL",
        "u l": "U/L",
        "mmo l": "mmol/L",
        "mmol/l": "mmol/L",
    }

    # Matches range patterns (e.g., 12.0-16.0, 12 - 16, 70 to 110, < 1.2, up to 40)
    RANGE_REGEX = re.compile(
        r'(\b\d+(?:\.\d+)?\s*(?:\-|\bto\b)\s*\d+(?:\.\d+)?\b)|((?:<|>|<=|>=)\s*\d+(?:\.\d+)?\b)|(\bup\s*to\s*\d+(?:\.\d+)?\b)', 
        re.IGNORECASE
    )

    # Keywords that suggest a line is a header, metadata, or reference text rather than a result row
    EXCLUDE_KEYWORDS = {
        "page", "date", "reference", "range", "ref range", "unit", "result", 
        "patient", "doctor", "referred", "hospital", "uhid", "name", "gender", 
        "clinical", "history", "laboratory", "report", "test name", "method", "test",
        "patlentid", "pid", "mrn", "registration", "reg no", "uhid no"
    }

    # Matches standard abnormal status indicators
    STATUS_KEYWORDS = ["high", "low", "abnormal", "normal", "critical", "h", "l", "n"]

    @classmethod
    def extract_parameters(cls, text: str) -> list:
        """
        Parses raw text line-by-line to extract lab parameters.
        
        Args:
            text (str): Raw text of the report.
            
        Returns:
            list: List of dicts, each representing an extracted laboratory parameter.
        """
        logger.info("Starting medical parameter extraction...")
        parameters = []
        seen_parameters = set()

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        for line in lines:
            # Skip lines that are just headers or metadata
            line_lower = line.lower()
            if any(keyword == line_lower for keyword in cls.EXCLUDE_KEYWORDS) or \
               (len(line_lower) < 5 and not any(char.isdigit() for char in line_lower)):
                continue
            
            # Extract parameters from the line
            extracted = cls._parse_line(line)
            if extracted:
                norm_name = extracted["parameter"]
                # Deduplication logic
                if norm_name.lower() not in seen_parameters:
                    parameters.append(extracted)
                    seen_parameters.add(norm_name.lower())
                    logger.info(f"Extracted Parameter: {extracted}")
                else:
                    logger.warning(f"Skipped duplicate parameter: {norm_name}")

        logger.info(f"Completed extraction. Found {len(parameters)} unique parameters.")
        return parameters

    @classmethod
    def _parse_line(cls, line: str) -> dict:
        """
        Analyzes a single line using vertical column splits to capture 
        parameter, value, unit, range, and status.
        """
        # Find all numeric value candidates in the line
        matches = list(cls.VALUE_REGEX.finditer(line))
        if not matches:
            return None

        # In a typical lab report line: [Parameter Name] [Result Value] [Unit] [Reference Range] [Status]
        # The actual result value is usually the first numeric match that is NOT part of a range
        # Let's check which numeric match serves as the value.
        value_match = None
        for m in matches:
            start, end = m.span()
            # If this match is inside a range expression (like 12-16), skip it.
            # We can check this by seeing if the RANGE_REGEX matches a substring surrounding it.
            context_start = max(0, start - 15)
            context_end = min(len(line), end + 15)
            context = line[context_start:context_end]
            if cls.RANGE_REGEX.search(context) and m.group() in cls.RANGE_REGEX.search(context).group():
                continue
            
            # Found the main test value candidate
            value_match = m
            break
            
        if not value_match:
            # Fallback: if all numbers are inside range bounds, this might not be a parameter line
            return None

        val_str = value_match.group().strip()
        val_start, val_end = value_match.span()

        # Split line around the test value:
        # Left side is Parameter Name
        parameter_name = line[:val_start].strip()
        
        # Right side contains Unit, Reference Range, and Status
        right_side = line[val_end:].strip()

        # Check if the parameter name is empty or contains excluded keywords (e.g. headers or demographics)
        exclude_words = {
            "unit", "reference", "test name", "signature", "patient", "doctor", 
            "referred", "age", "gender", "sex", "date", "uhid", "mrn", "hospital", 
            "lab", "diagnostic", "collection", "page", "result", "history"
        }
        if not parameter_name or any(kw in parameter_name.lower() for kw in exclude_words):
            return None
            
        # Clean parameter name (remove extra symbols commonly seen in tables)
        parameter_name = re.sub(r'^[.\-\s*]+', '', parameter_name)
        parameter_name = re.sub(r'[.\-\s*:]+$', '', parameter_name)
        parameter_name = re.sub(r'\s+', ' ', parameter_name).strip()

        if len(parameter_name) < 2:
            return None

        # Initialize remaining fields
        unit = ""
        ref_range = ""
        status = ""

        # Extract Reference Range from the right side
        range_match = cls.RANGE_REGEX.search(right_side)
        if range_match:
            ref_range = range_match.group().strip()
            # Remove range from right side to clean other fields
            r_start, r_end = range_match.span()
            right_side = right_side[:r_start] + " " + right_side[r_end:]
            
        # Clean range formatting
        ref_range = re.sub(r'\s+', ' ', ref_range).strip()

        # Extract Status from the remaining right side
        # Split right side into tokens to identify status keyword
        tokens = right_side.split()
        remaining_tokens = []
        for token in tokens:
            cleaned_token = re.sub(r'[^a-zA-Z]', '', token).lower()
            if cleaned_token in cls.STATUS_KEYWORDS:
                # Keep original status casing or map to Title Case
                if cleaned_token in ["high", "h"]:
                    status = "High"
                elif cleaned_token in ["low", "l"]:
                    status = "Low"
                elif cleaned_token in ["abnormal", "critical"]:
                    status = "Abnormal"
                else:
                    status = "Normal"
            else:
                remaining_tokens.append(token)

        # The remaining tokens on the right represent the Unit
        unit = " ".join(remaining_tokens).strip()
        
        # Trim surrounding punctuation from unit
        unit = re.sub(r'^[:\-\s\.,\(\)]+', '', unit)
        unit = re.sub(r'[:\-\s\.,\(\)]+$', '', unit)
        unit = re.sub(r'\s+', ' ', unit).strip()

        # Normalize unit formatting for consistent JSON output
        unit = cls._normalize_unit(unit)

        # Normalize the parameter name using the predefined map
        normalized_name = cls._normalize_parameter_name(parameter_name)

        return {
            "parameter": normalized_name,
            "raw_parameter": parameter_name,
            "value": val_str,
            "unit": unit if unit else None,
            "reference_range": ref_range if ref_range else None,
            "status": status if status else None
        }

    @staticmethod
    def _normalize_parameter_name(name: str) -> str:
        """
        Maps shorthand parameter names to their normalized standard forms.
        """
        name_clean = name.lower().strip()
        # Remove common punctuation markers inside names
        name_clean = re.sub(r'[\(\)\-\:\.]', ' ', name_clean)
        name_clean = re.sub(r'\s+', ' ', name_clean).strip()
        
        # Check standard normalizations map
        if name_clean in PARAMETER_NORMALIZATION_MAP:
            return PARAMETER_NORMALIZATION_MAP[name_clean]
            
        # Check substring matches (e.g., AST (SGOT) contains sgot/ast)
        for shorthand, standard in PARAMETER_NORMALIZATION_MAP.items():
            if f" {shorthand} " in f" {name_clean} ":
                return standard

        # Default back to original parameter name if no normalization matches
        # but format with Title Case for clean presentation
        return name.title()

    @staticmethod
    def _normalize_unit(unit: str) -> str:
        """Convert common OCR-produced unit variations into normalized standard units."""
        if not unit:
            return None

        unit_clean = unit.strip().lower()
        unit_clean = re.sub(r'[^a-zA-Z0-9/\.\-\s]', '', unit_clean)
        unit_clean = re.sub(r'\s+', ' ', unit_clean).strip()

        if unit_clean in ParameterExtractor.UNIT_NORMALIZATION_MAP:
            return ParameterExtractor.UNIT_NORMALIZATION_MAP[unit_clean]

        # Common fallback for units like 'g dL' or 'mg dL'
        if unit_clean.startswith('g') and 'dl' in unit_clean:
            return 'g/dL'
        if unit_clean.startswith('mg') and 'dl' in unit_clean:
            return 'mg/dL'
        if unit_clean.startswith('u') and 'l' in unit_clean:
            return 'U/L'
        if unit_clean.startswith('mmol') and 'l' in unit_clean:
            return 'mmol/L'

        return unit
