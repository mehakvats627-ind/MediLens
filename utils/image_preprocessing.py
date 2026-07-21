import cv2
import numpy as np
from pathlib import Path
from PIL import Image
from utils.logger import logger


def _deskew_image(gray: np.ndarray) -> np.ndarray:
    """Estimate rotation angle from the dominant text orientation and deskew the image."""
    # Use a binary threshold so contours become clearer for text lines.
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
    )
    coords = np.column_stack(np.where(binary > 0))
    if len(coords) == 0:
        return gray

    # Use the minimum area rectangle around the text region to estimate skew.
    rect = cv2.minAreaRect(coords[:, ::-1])
    angle = rect[-1]

    if angle < -45:
        angle = 90 + angle
    elif angle > 45:
        angle = angle - 90

    # Skip deskewing if angle is very small or unstable.
    if abs(angle) < 0.5:
        return gray

    (h, w) = gray.shape[:2]
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    deskewed = cv2.warpAffine(gray, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    logger.info(f"Deskewed image by {angle:.2f} degrees for OCR compatibility.")
    return deskewed


def preprocess_image(image_path_or_array, save_processed_path: str = None) -> np.ndarray:
    """
    Applies image preprocessing pipeline to optimize document images for EasyOCR:
    1. Grayscale
    2. Resize (upscale low-res images to a target height for legible text size)
    3. Denoise
    4. Contrast enhancement (CLAHE)
    5. Adaptive thresholding
    6. Deskew rotated documents
    7. Shadow removal / brightness enhancement
    8. Sharpening
    
    Args:
        image_path_or_array: Path to the image file, PIL Image, or existing numpy array.
        save_processed_path: If specified, saves the preprocessed image to this file path.
        
    Returns:
        np.ndarray: Preprocessed grayscale image ready for OCR.
    """
    try:
        # 1. Load image into numpy array (OpenCV format)
        if isinstance(image_path_or_array, (str, Path)):
            img = cv2.imread(str(image_path_or_array))
            if img is None:
                raise ValueError(f"Failed to load image from path: {image_path_or_array}")
            logger.info(f"Loaded image from path: {image_path_or_array} for preprocessing.")
        elif isinstance(image_path_or_array, Image.Image):
            img = np.array(image_path_or_array)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif isinstance(image_path_or_array, np.ndarray):
            img = image_path_or_array.copy()
        else:
            raise TypeError("Unsupported image type. Must be file path, PIL Image, or numpy array.")

        if img.size == 0:
            raise ValueError("Empty image array provided.")

        # 2. Grayscale Conversion
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # 3. Resize / Upscaling
        h, w = gray.shape[:2]
        target_width = 1600
        if w < target_width:
            scale_factor = target_width / w
            new_dim = (target_width, int(h * scale_factor))
            gray = cv2.resize(gray, new_dim, interpolation=cv2.INTER_CUBIC)
            logger.info(f"Upscaled image from {w}x{h} to {new_dim[0]}x{new_dim[1]} (factor {scale_factor:.2f})")

        # 4. Denoise and normalize brightness
        denoised = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
        normalized = cv2.normalize(denoised, None, 0, 255, cv2.NORM_MINMAX)

        # 5. Contrast enhancement with CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast_enhanced = clahe.apply(normalized)

        # 6. Adaptive thresholding for low-contrast or blurred documents
        thresholded = cv2.adaptiveThreshold(
            contrast_enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
        )

        # 7. Deskew rotation estimation
        deskewed = _deskew_image(thresholded)

        # 8. Shadow removal and brightness correction
        blur = cv2.GaussianBlur(deskewed, (31, 31), 0)
        corrected = cv2.addWeighted(deskewed, 1.2, blur, -0.2, 0)

        # 9. Sharpening
        sharpening_kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])
        sharpened = cv2.filter2D(corrected, -1, sharpening_kernel)

        if save_processed_path:
            save_path = Path(save_processed_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(save_path), sharpened)
            logger.info(f"Saved preprocessed image to: {save_path}")

        return sharpened

    except Exception as e:
        logger.error(f"Error during image preprocessing: {str(e)}")
        raise e
