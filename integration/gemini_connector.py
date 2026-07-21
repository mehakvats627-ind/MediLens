import os
import json
import time
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from utils.logger import logger
import config

# Load .env automatically from the absolute project root directory
env_path = config.BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# Define Pydantic schema for strict structured output from Gemini matching all 6 requested fields
class GeminiAnalysis(BaseModel):
    clinical_summary: str = Field(
        description="A clear, patient-friendly summary of the overall lab report, explaining what the report indicates."
    )
    abnormal_parameters: List[str] = Field(
        description="List of out-of-range parameters, explaining what values were found, why they are flagged, and their implications."
    )
    risk_assessment: str = Field(
        description="A clinical risk evaluation highlighting potential concerns based on the combination of lab parameters."
    )
    lifestyle_recommendations: List[str] = Field(
        description="Practical, personalized dietary, hydration, exercise, or sleep recommendations based on the test results."
    )
    follow_up_suggestions: List[str] = Field(
        description="Actionable follow-up guidance, specifying any additional tests, repeats, or clinical consultations recommended."
    )
    medical_disclaimer: str = Field(
        description="A strong clinical disclaimer stating that this report is AI-generated, should not replace professional medical judgment, and the patient must consult their physician."
    )

class GeminiConnector:
    """
    Handles connectivity and interactions with Gemini AI via the google-genai SDK.
    Validates keys, processes structured requests, catches network/rate-limiting errors, 
    and guarantees a standard structured JSON return.
    """

    @staticmethod
    def validate_api_key(api_key: str) -> tuple[bool, str]:
        """
        Validates the format and presence of the Gemini API Key.
        
        Returns:
            tuple (is_valid: bool, reason: str)
        """
        if not api_key:
            return False, "API key is missing or empty in .env configuration."
            
        api_key_clean = api_key.strip()
        
        # Check placeholder values
        placeholder_keywords = ["placeholder", "your_actual", "your_api_key", "here"]
        if any(kw in api_key_clean.lower() for kw in placeholder_keywords):
            return False, "GEMINI_API_KEY contains placeholder text. Please replace it with your actual key."
            
        # Check standard length and prefix for Google Generative Language keys
        if not api_key_clean.startswith("AIza"):
            return False, "GEMINI_API_KEY format is invalid (typically starts with 'AIza')."
            
        if len(api_key_clean) < 30:
            return False, f"GEMINI_API_KEY looks too short ({len(api_key_clean)} chars). A real key is ~39 chars."
            
        return True, "API Key format verified."

    @classmethod
    def analyze_report(cls, report_json: dict) -> dict:
        """
        Sends structured report JSON to Gemini and retrieves a structured analysis.
        Guarantees returned dict matching the 6-field schema even under failure.
        """
        logger.info("Initializing Gemini report analysis...")
        
        # 1. Fetch key from environment
        raw_key = os.getenv("GEMINI_API_KEY")
        
        # 2. Validate API key
        is_valid, validation_reason = cls.validate_api_key(raw_key)
        
        if not is_valid:
            logger.warning(f"Gemini API key validation failed: {validation_reason}")
            return cls._get_fallback_payload(f"Gemini AI summary unavailable: {validation_reason}")

        api_key = raw_key.strip()

        # 3. Request completion using latest Google GenAI SDK
        try:
            from google import genai
            from google.genai import types
            from google.genai.errors import APIError
            
            logger.info("Initializing official google-genai Client...")
            client = genai.Client(api_key=api_key)
            
            prompt = (
                f"You are an expert medical intelligence assistant. Analyze the following structured patient laboratory report "
                f"data and compile a clinical summary, identify abnormal parameters, provide a risk assessment, suggest "
                f"lifestyle adjustments, offer follow-up tests suggestions, and append a clinical disclaimer.\n\n"
                f"REPORT DATA:\n{json.dumps(report_json, indent=2)}\n\n"
                f"Generate a professional response conforming strictly to the requested JSON schema structure."
            )

            logger.info(f"Sending request to Gemini model '{config.GEMINI_MODEL}' (Temp=0.2, Structured Output Schema)...")
            
            start_time = time.time()
            
            # API Request
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=GeminiAnalysis,
                    temperature=0.2
                )
            )
            
            elapsed = time.time() - start_time
            logger.info(f"Gemini response received successfully in {elapsed:.2f} seconds.")

            # Validate response payload content
            response_text = response.text
            if not response_text or not response_text.strip():
                logger.error("Gemini API returned an empty or whitespace response.")
                raise ValueError("Empty response received from API.")

            # Load response into structured dict
            analysis_dict = json.loads(response_text)
            logger.info("Successfully parsed Gemini structured response JSON.")
            return analysis_dict

        except ImportError as e:
            logger.error("Failed to import official google-genai SDK. Install via pip install google-genai.")
            return cls._get_fallback_payload("Google GenAI SDK is not installed in the target environment.")
            
        except APIError as e:
            # Catch specific rate limits, quotas, auth, or endpoint failure
            logger.error(f"Gemini API Error occurred (HTTP {e.code}): {e.message}")
            return cls._get_fallback_payload(f"Gemini API returned code {e.code}: {e.message}")
            
        except Exception as e:
            # Catch timeouts, parsing issues, or network failures
            logger.error(f"Unexpected error during Gemini API request processing: {str(e)}", exc_info=True)
            return cls._get_fallback_payload(f"Failed to generate clinical analysis due to system error: {str(e)}")

    @staticmethod
    def _get_fallback_payload(warning_message: str) -> dict:
        """
        Generates a standardized dictionary payload containing all 6 requested
        fields with diagnostic warning messages. Ensures backend parsing never breaks.
        """
        return {
            "clinical_summary": warning_message,
            "abnormal_parameters": [
                "Review parameter status flags (High/Low) in the structured parameters list above."
            ],
            "risk_assessment": "Unavailable: AI processing pipeline was bypassed or failed.",
            "lifestyle_recommendations": [
                "Please review your results with a licensed healthcare physician."
            ],
            "follow_up_suggestions": [
                "Schedule a follow-up consultation with your doctor."
            ],
            "medical_disclaimer": (
                "AI clinical report analysis is bypassed or unavailable. Standard clinical disclaimers apply: "
                "laboratory measurements should always be evaluated under professional medical supervision."
            )
        }
