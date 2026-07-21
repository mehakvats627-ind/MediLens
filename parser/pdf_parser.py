import fitz  # PyMuPDF
from utils.logger import logger

class PDFParserError(Exception):
    """Exception raised for errors in the PDF parsing process."""
    pass

class PDFParser:
    """
    Parses digital PDF files to extract textual content using PyMuPDF.
    """

    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Opens a PDF file and extracts all readable text page-by-page.
        
        Args:
            file_path (str): Absolute or relative path to the PDF file.
            
        Returns:
            str: Accumulated text content from all pages.
            
        Raises:
            PDFParserError: If the PDF cannot be opened or parsed.
        """
        logger.info(f"Starting digital text extraction for: {file_path}")
        
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            logger.error(f"Failed to open PDF file {file_path} for text extraction: {e}")
            raise PDFParserError(f"Failed to open PDF file: {e}")

        try:
            # Check encryption status just in case
            if doc.is_encrypted:
                logger.error(f"Cannot parse {file_path} - PDF is password protected.")
                raise PDFParserError("Cannot parse password-protected PDF.")

            extracted_pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Extract text using PyMuPDF's layout preserving text extraction
                page_text = page.get_text("text")
                
                # Basic cleaning of page text lines
                cleaned_lines = []
                for line in page_text.splitlines():
                    trimmed = line.strip()
                    if trimmed:
                        cleaned_lines.append(trimmed)
                
                page_content = "\n".join(cleaned_lines)
                
                if page_content:
                    extracted_pages.append(page_content)
                    logger.info(f"Successfully extracted {len(page_content)} characters from Page {page_num + 1}.")
                else:
                    logger.warning(f"Page {page_num + 1} of {file_path} yielded no text content.")

            # Join pages with double newlines
            full_text = "\n\n--- Page Break ---\n\n".join(extracted_pages)
            
            if not full_text.strip():
                logger.warning(f"No text extracted from digital PDF {file_path}.")
                raise PDFParserError("Digital PDF text extraction returned empty content.")
                
            logger.info(f"Total extracted text length: {len(full_text)} characters.")
            return full_text
            
        except Exception as e:
            if not isinstance(e, PDFParserError):
                logger.error(f"Error parsing PDF content in {file_path}: {e}")
                raise PDFParserError(f"Error during PDF parsing: {e}")
            raise e
        finally:
            doc.close()
