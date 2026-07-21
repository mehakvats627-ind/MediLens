import os
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
from utils.logger import logger

# Custom Exceptions for robust error handling
class ReportDetectorError(Exception):
    """Base exception for report detection failures."""
    pass

class UnsupportedFileError(ReportDetectorError):
    """Raised when the file format is not supported."""
    pass

class EmptyFileError(ReportDetectorError):
    """Raised when the input file is empty (0 bytes)."""
    pass

class PasswordProtectedPDFError(ReportDetectorError):
    """Raised when the PDF is encrypted and requires a password."""
    pass

class EmptyPDFError(ReportDetectorError):
    """Raised when the PDF file has no pages."""
    pass

class UnreadableImageError(ReportDetectorError):
    """Raised when an image file cannot be opened or is corrupted."""
    pass


class ReportDetector:
    """
    Detects the report file type and inspects its contents to determine 
    if it is a Digital PDF, Scanned PDF, or an Image (JPG/JPEG/PNG).
    """

    SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
    SUPPORTED_PDF_EXTENSIONS = {".pdf"}

    @staticmethod
    def detect_report_type(file_path: str) -> str:
        """
        Determines the type of the report file.
        
        Args:
            file_path (str): Path to the input file.
            
        Returns:
            str: One of 'digital_pdf', 'scanned_pdf', or 'image'.
            
        Raises:
            UnsupportedFileError: If the file extension is not supported.
            EmptyFileError: If the file is empty.
            PasswordProtectedPDFError: If the PDF is password-protected.
            EmptyPDFError: If the PDF has no pages.
            UnreadableImageError: If the image cannot be read.
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found at: {file_path}")

        # Check for empty file
        if path.stat().st_size == 0:
            logger.error(f"File {file_path} is empty (0 bytes).")
            raise EmptyFileError(f"File {path.name} is empty.")

        ext = path.suffix.lower()

        if ext in ReportDetector.SUPPORTED_PDF_EXTENSIONS:
            return ReportDetector._inspect_pdf(path)
        elif ext in ReportDetector.SUPPORTED_IMAGE_EXTENSIONS:
            return ReportDetector._inspect_image(path)
        else:
            logger.error(f"Unsupported file format: {ext} for path {file_path}")
            raise UnsupportedFileError(
                f"Unsupported file format '{ext}'. Only PDF, JPG, JPEG, and PNG are supported."
            )

    @staticmethod
    def _inspect_pdf(path: Path) -> str:
        """
        Inspects a PDF file using PyMuPDF to classify it as 'digital_pdf' or 'scanned_pdf'.
        """
        logger.info(f"Inspecting PDF file: {path.name}")
        try:
            doc = fitz.open(str(path))
        except Exception as e:
            logger.error(f"Failed to open PDF {path.name}: {e}")
            raise ReportDetectorError(f"Corrupted or invalid PDF file: {e}")

        try:
            if doc.is_encrypted:
                logger.error(f"PDF {path.name} is password protected.")
                raise PasswordProtectedPDFError(f"PDF {path.name} is password protected/encrypted.")

            num_pages = len(doc)
            if num_pages == 0:
                logger.error(f"PDF {path.name} contains no pages.")
                raise EmptyPDFError(f"PDF {path.name} contains no pages.")

            # Iterate through pages and accumulate text characters to determine if digital
            total_text_length = 0
            for page in doc:
                text = page.get_text().strip()
                total_text_length += len(text)

            logger.info(f"PDF has {num_pages} page(s) and {total_text_length} characters of extractable text.")

            # If the PDF contains negligible extractable characters, it requires OCR.
            # Using 50 characters as a threshold for a document.
            if total_text_length > 50:
                logger.info(f"Classified {path.name} as DIGITAL PDF.")
                return "digital_pdf"
            else:
                logger.info(f"Classified {path.name} as SCANNED PDF.")
                return "scanned_pdf"

        finally:
            doc.close()

    @staticmethod
    def _inspect_image(path: Path) -> str:
        """
        Inspects an image to verify it is valid and readable.
        """
        logger.info(f"Inspecting image file: {path.name}")
        try:
            with Image.open(path) as img:
                img.verify()  # Verifies image integrity without loading actual pixel data
            
            # Re-open and verify shape/dimensions are non-zero
            with Image.open(path) as img:
                w, h = img.size
                if w == 0 or h == 0:
                    raise ValueError("Image dimensions are zero.")
                    
            logger.info(f"Classified {path.name} as IMAGE. Size: {w}x{h}")
            return "image"
        except Exception as e:
            logger.error(f"Image {path.name} is unreadable or corrupted: {e}")
            raise UnreadableImageError(f"Unreadable or corrupted image {path.name}: {e}")
