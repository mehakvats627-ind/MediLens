import io
import numpy as np
import fitz  # PyMuPDF
from PIL import Image
from utils.logger import logger
from utils.image_preprocessing import preprocess_image

# Custom exception class for OCR errors
class OCRParserError(Exception):
    """Exception raised for errors in the OCR parsing process."""
    pass

class OCRParser:
    """
    OCR Parser that extracts text from images and scanned PDFs using EasyOCR.
    It applies image preprocessing (grayscale, denoise, sharpening, contrast, scaling) 
    before performing OCR to optimize reading accuracy.
    """
    
    _reader_instance = None

    @classmethod
    def _get_reader(cls):
        """
        Lazy-loads the EasyOCR Reader as a singleton to avoid loading models on every run.
        """
        if cls._reader_instance is None:
            logger.info("Initializing EasyOCR Reader...")
            try:
                import easyocr
                import torch
                # Detect GPU acceleration availability
                gpu_available = torch.cuda.is_available()
                logger.info(f"EasyOCR initialization: CUDA/GPU is_available = {gpu_available}")
                # Initialize reader for English with verbose=False to prevent terminal encoding errors
                cls._reader_instance = easyocr.Reader(["en"], gpu=gpu_available, verbose=False)
                logger.info("EasyOCR Reader successfully initialized.")
            except ImportError as e:
                logger.error("EasyOCR package is not installed. Please run pip install easyocr.")
                raise OCRParserError("EasyOCR library is missing. Install requirements.") from e
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR reader: {e}")
                raise OCRParserError(f"OCR Engine initialization failed: {e}") from e
        return cls._reader_instance

    @classmethod
    def extract_text_from_image(cls, image_path_or_array, save_processed_path: str = None) -> str:
        """
        Runs image preprocessing and extracts text using EasyOCR.
        
        Args:
            image_path_or_array: Path to the image or numpy array / PIL Image.
            save_processed_path (str, optional): Path to save the preprocessed image.
            
        Returns:
            str: Extracted layout-preserved text.
        """
        reader = cls._get_reader()
        logger.info("Starting OCR extraction on image...")
        
        try:
            # 1. Apply OpenCV preprocessing
            preprocessed_img = preprocess_image(image_path_or_array, save_processed_path)
            
            # 2. Perform OCR with word coordinates
            # detail=1 returns bounding box, text string, and confidence score
            ocr_results = reader.readtext(preprocessed_img, detail=1)
            
            if not ocr_results:
                logger.warning("EasyOCR returned empty results for the image.")
                return ""
            
            # 3. Layout preservation: group bounding boxes into lines by Y coordinates
            # Bounding box is format: [[top_left], [top_right], [bottom_right], [bottom_left]]
            # Let's group text items that are on the same horizontal line.
            lines = cls._reconstruct_layout(ocr_results)
            
            extracted_text = "\n".join(lines)
            logger.info(f"Successfully OCR'd image. Character count: {len(extracted_text)}")
            return extracted_text
            
        except Exception as e:
            logger.error(f"OCR parsing failed on image: {e}")
            raise OCRParserError(f"OCR failed on image: {e}")

    @classmethod
    def extract_text_from_pdf(cls, pdf_path: str, save_processed_dir: str = None) -> str:
        """
        Converts scanned PDF pages to images and runs OCR on each page.
        
        Args:
            pdf_path (str): Path to the scanned PDF.
            save_processed_dir (str, optional): Directory to save preprocessed page images.
            
        Returns:
            str: Accumulated text content from all pages.
        """
        logger.info(f"Starting scanned PDF OCR parsing for: {pdf_path}")
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            logger.error(f"Failed to open PDF file {pdf_path} for OCR: {e}")
            raise OCRParserError(f"Failed to open PDF for OCR: {e}")

        try:
            extracted_pages = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                logger.info(f"Rendering Page {page_num + 1} of {len(doc)} to image (DPI=200)...")
                
                # Render page to high-quality image (200 DPI resolution)
                pix = page.get_pixmap(dpi=200)
                png_bytes = pix.tobytes("png")
                
                # Convert png bytes to Pillow Image, then to NumPy array
                pil_img = Image.open(io.BytesIO(png_bytes))
                
                # Setup path to save preprocessed image if directory is specified
                save_path = None
                if save_processed_dir:
                    save_path = f"{save_processed_dir}/page_{page_num + 1}.png"
                
                # Extract text for this page using our image OCR function
                page_text = cls.extract_text_from_image(pil_img, save_path)
                
                if page_text.strip():
                    extracted_pages.append(page_text)
                    logger.info(f"Page {page_num + 1} OCR text extracted. Length: {len(page_text)} chars.")
                else:
                    logger.warning(f"Page {page_num + 1} OCR yielded no text.")
            
            full_text = "\n\n--- Page Break ---\n\n".join(extracted_pages)
            if not full_text.strip():
                raise OCRParserError("Scanned PDF OCR returned empty content on all pages.")
                
            return full_text
            
        except Exception as e:
            if not isinstance(e, OCRParserError):
                logger.error(f"Error during PDF OCR processing: {e}")
                raise OCRParserError(f"Scanned PDF OCR failed: {e}")
            raise e
        finally:
            doc.close()

    @staticmethod
    def _reconstruct_layout(ocr_results, y_tolerance: int = 15) -> list:
        """
        Groups EasyOCR bounding boxes into horizontal text lines to preserve document layout.
        
        Args:
            ocr_results: List of tuples from reader.readtext: (bbox, text, confidence)
            y_tolerance: Vertical distance tolerance in pixels to consider text on the same line.
        """
        # Element structure: { 'x': min_x, 'y': center_y, 'text': text, 'conf': conf }
        elements = []
        for bbox, text, conf in ocr_results:
            # bbox is [[x0,y0], [x1,y1], [x2,y2], [x3,y3]]
            # Calculate bounding box bounds and center y
            xs = [pt[0] for pt in bbox]
            ys = [pt[1] for pt in bbox]
            min_x = min(xs)
            center_y = sum(ys) / 4.0
            
            elements.append({
                "x": min_x,
                "y": center_y,
                "text": text.strip(),
                "conf": conf
            })

        # Sort elements primarily by Y (top-to-bottom)
        elements.sort(key=lambda e: e["y"])
        
        lines = []
        if not elements:
            return lines

        # Group elements into lines based on Y coordinate tolerance
        current_line_elements = [elements[0]]
        
        for el in elements[1:]:
            # If the vertical distance is within tolerance, group in the same line
            if abs(el["y"] - current_line_elements[-1]["y"]) <= y_tolerance:
                current_line_elements.append(el)
            else:
                # Sort the completed line by X coordinate (left-to-right) and join
                current_line_elements.sort(key=lambda e: e["x"])
                line_text = "   ".join([e["text"] for e in current_line_elements])
                lines.append(line_text)
                # Start new line
                current_line_elements = [el]
                
        # Handle the last line
        if current_line_elements:
            current_line_elements.sort(key=lambda e: e["x"])
            line_text = "   ".join([e["text"] for e in current_line_elements])
            lines.append(line_text)
            
        return lines
