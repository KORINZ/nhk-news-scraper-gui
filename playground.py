"""A playground for testing out OCR on images of Japanese text."""

# Standard library imports
import logging
import os
import sys
from typing import Tuple, Optional

# Third-party imports
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

# Set the logging level
logging.basicConfig(level=logging.INFO)


def set_tesseract_path() -> None:
    """Set the path to the Tesseract executable."""
    if os.name == "nt":
        path = r"C:/Program Files/Tesseract-OCR/tesseract.exe"
    elif os.name == "posix":
        path = r"/opt/homebrew/bin/tesseract"
    else:
        raise RuntimeError(f"Unsupported operating system: {os.name}")

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Tesseract executable not found. Please check the path: {path}")

    pytesseract.pytesseract.tesseract_cmd = path


def preprocess_image(
    image: Image.Image,
    size: Optional[Tuple[int, int]] = None,
    contrast: float = 2.0,
    sharpness: float = 2.0,
    denoise_kernel_size: int = 3,
    threshold: int = 135,
) -> Image.Image:
    """Preprocess an image to improve OCR accuracy."""
    if size is not None:
        image = image.resize(size, Image.BICUBIC)

    # Convert image to grayscale
    image = image.convert("L")

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)

    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(sharpness)

    # Apply a median filter (denoising)
    image = image.filter(ImageFilter.MedianFilter(denoise_kernel_size))

    # Apply adaptive thresholding
    image = image.point(lambda x: 0 if x < threshold else 255, "1")

    return image


def ocr_image(
    image_path: str,
    lang: str = "jpn",
    preprocess: bool = True,
    preprocess_params: Optional[dict] = None,
) -> str:
    """Perform OCR on an Japanese text image and return the result."""
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File '{image_path}' does not exist.")

    image = Image.open(image_path)

    if preprocess:
        if preprocess_params is not None:
            logging.info("Preprocessing image...\n")
            image = preprocess_image(image, **preprocess_params)
        else:
            image = preprocess_image(image)

        # Display the preprocessed image
        image.show()

    # psm 6: Assume a single uniform block of text. oem 3: Use LSTM neural network.
    config = "--psm 6 --oem 3 -c preserve_interword_spaces=1"
    text = pytesseract.image_to_string(image, lang=lang, config=config)
    return text.strip().replace(" ", "")


if __name__ == "__main__":
    """
    The main script that performs OCR on a specified image and prints the result.
    """
    try:
        set_tesseract_path()
    except (RuntimeError, FileNotFoundError) as e:
        print(e)
        sys.exit(1)

    image_path = r"./ocr_images/2.png"
    try:
        with Image.open(image_path) as image:
            result = ocr_image(
                image_path,
                preprocess_params={
                    "size": (image.width * 4, image.height * 4)},
            )
            print(result)
    except FileNotFoundError:
        print(f"File '{image_path}' does not exist.")
