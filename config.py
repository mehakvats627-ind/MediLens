import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent

# Upload and Output directories
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
SAMPLE_REPORTS_DIR = BASE_DIR / "sample_reports"

# Ensure crucial directories exist
for directory in [UPLOAD_DIR, OUTPUT_DIR, SAMPLE_REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# OCR and Image Preprocessing configurations
OCR_CONFIDENCE_THRESHOLD = 0.35  # Threshold below which we raise warnings or flag results
DEFAULT_LANGUAGES = ["en"]        # Languages supported by EasyOCR

# Gemini AI configurations
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Parameter normalizations dictionary
# Maps raw parameter forms to normalized standard parameter names
PARAMETER_NORMALIZATION_MAP = {
    # Haemoglobin
    "hb": "Haemoglobin",
    "hgb": "Haemoglobin",
    "haemoglobin": "Haemoglobin",
    "hemoglobin": "Haemoglobin",
    
    # White Blood Cells
    "wbc": "White Blood Cell Count",
    "wbc count": "White Blood Cell Count",
    "white blood cell": "White Blood Cell Count",
    "white blood cells": "White Blood Cell Count",
    "total wbc": "White Blood Cell Count",
    "tlc": "White Blood Cell Count",
    
    # Red Blood Cells
    "rbc": "Red Blood Cell Count",
    "rbc count": "Red Blood Cell Count",
    "red blood cell": "Red Blood Cell Count",
    "red blood cells": "Red Blood Cell Count",
    "total rbc": "Red Blood Cell Count",
    
    # Platelets
    "platelet": "Platelet Count",
    "platelets": "Platelet Count",
    "platelet count": "Platelet Count",
    
    # Blood Sugar / Glucose
    "rbs": "Random Blood Sugar",
    "random blood sugar": "Random Blood Sugar",
    "fbs": "Fasting Blood Sugar",
    "fasting blood sugar": "Fasting Blood Sugar",
    "blood sugar fasting": "Fasting Blood Sugar",
    "ppbs": "Post Prandial Blood Sugar",
    "post prandial blood sugar": "Post Prandial Blood Sugar",
    "blood sugar post prandial": "Post Prandial Blood Sugar",
    "hba1c": "Glycated Haemoglobin (HbA1c)",
    "hb a1c": "Glycated Haemoglobin (HbA1c)",
    "glycated haemoglobin": "Glycated Haemoglobin (HbA1c)",
    
    # Kidney Function Test (KFT)
    "urea": "Blood Urea",
    "blood urea": "Blood Urea",
    "creatinine": "Serum Creatinine",
    "serum creatinine": "Serum Creatinine",
    "uric acid": "Serum Uric Acid",
    "serum uric acid": "Serum Uric Acid",
    
    # Liver Function Test (LFT)
    "sgot": "Aspartate Aminotransferase (SGOT)",
    "ast": "Aspartate Aminotransferase (SGOT)",
    "sgpt": "Alanine Aminotransferase (SGPT)",
    "alt": "Alanine Aminotransferase (SGPT)",
    "bilirubin": "Total Bilirubin",
    "total bilirubin": "Total Bilirubin",
}
