import fitz  # PyMuPDF
from PIL import Image, ImageDraw
from pathlib import Path
from utils.logger import logger
import config

def generate_sample_digital_pdf(output_path: Path):
    """
    Generates a structured digital PDF containing standard patient details 
    and laboratory test rows to test digital PDF parsing.
    """
    logger.info(f"Generating digital sample PDF at: {output_path}")
    try:
        # Create a new blank PDF document
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)  # A4 size in points
        
        # Define layout text
        text_lines = [
            ("METRO DIAGNOSTIC HEALTH CENTRE", 50, 50, 16),
            ("123 Clinic Road, Health City, HC-5678", 50, 70, 10),
            ("--------------------------------------------------", 50, 85, 10),
            ("PATIENT DEMOGRAPHICS", 50, 105, 12),
            ("Patient Name: Bruce Wayne", 50, 125, 10),
            ("Age: 35 Years      Gender: Male", 50, 140, 10),
            ("Patient ID: PID-100801", 50, 155, 10),
            ("Referred By: Dr. Alfred Pennyworth", 300, 125, 10),
            ("Hospital: Gotham General Hospital", 300, 140, 10),
            ("Report Date: 19/07/2026", 300, 155, 10),
            ("--------------------------------------------------", 50, 175, 10),
            ("CLINICAL LABORATORY TEST REPORT", 50, 195, 12),
            ("Parameter Name       Result      Unit      Ref Range       Status", 50, 220, 10),
            ("Hb                   14.2        g/dL      12.0-16.0       Normal", 50, 240, 10),
            ("WBC Count            7500        /uL       4000-11000      Normal", 50, 255, 10),
            ("RBS                  95          mg/dL     70-140          Normal", 50, 270, 10),
            ("Serum Creatinine     11.0        mg/dL     0.6-1.2         Normal", 50, 285, 10),  # Suspicious decimal error (11.0 vs 1.1)
            ("AST SGOT             35          U/L       < 40            Normal", 50, 300, 10),
            ("--------------------------------------------------", 50, 320, 10),
            ("END OF REPORT - Verified by Dr. Leslie Thompkins", 50, 340, 9)
        ]
        
        # Draw lines onto the page
        for text, x, y, size in text_lines:
            page.insert_text((x, y), text, fontsize=size)
            
        doc.save(str(output_path))
        logger.info("Successfully generated sample digital PDF.")
    except Exception as e:
        logger.error(f"Failed to generate sample PDF: {e}")
        raise e

def generate_sample_scanned_jpg(output_path: Path):
    """
    Generates a mock scanned report image (JPG) with custom text drawing
    to test the image preprocessing and EasyOCR parser route.
    """
    logger.info(f"Generating scanned sample JPG at: {output_path}")
    try:
        # Create a white canvas (800x1100, resembling paper aspect ratio)
        img = Image.new("RGB", (800, 1100), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Add basic scanner artifacts / noise simulation (light grey background tinting)
        for i in range(0, 800, 10):
            draw.line([(i, 0), (i, 1100)], fill=(250, 250, 250), width=1)
            
        # Draw text rows simulating scanned printout
        # (Standard fonts will fallback to default system fonts)
        text_lines = [
            ("APEX DIAGNOSTIC LABORATORIES", 60, 60),
            ("Patient Name: Jane Doe", 60, 140),
            ("Age: 29 Years      Gender: Female", 60, 170),
            ("Patient ID: PID-50201", 60, 200),
            ("Referred By: Dr. Gregory House", 60, 230),
            ("Report Date: 18-07-2026", 60, 260),
            ("--------------------------------------------------------", 60, 300),
            ("TEST PARAMETER       RESULT      UNIT      REFERENCE RANGE", 60, 330),
            ("Hb                   95          g/dL      12.0-16.0", 60, 370),       # Missed decimal point (9.5 represented as 95)
            ("WBC Count            8900        /uL       4000-11000", 60, 400),
            ("Fasting Blood Sugar  105         mg/dL     70-100", 60, 430),
            ("RBS                  115         mg/dL     70-140", 60, 460),
            ("--------------------------------------------------------", 60, 500),
            ("Report Status: Complete", 60, 540)
        ]
        
        for text, x, y in text_lines:
            draw.text((x, y), text, fill=(30, 30, 30))  # Slightly muted grey to simulate ink print
            
        img.save(output_path, "JPEG")
        logger.info("Successfully generated sample scanned JPG.")
    except Exception as e:
        logger.error(f"Failed to generate sample JPG: {e}")
        raise e

if __name__ == "__main__":
    # Ensure folders exist and populate them
    digital_pdf = config.SAMPLE_REPORTS_DIR / "digital_report.pdf"
    scanned_jpg = config.SAMPLE_REPORTS_DIR / "scanned_report.jpg"
    
    generate_sample_digital_pdf(digital_pdf)
    generate_sample_scanned_jpg(scanned_jpg)
