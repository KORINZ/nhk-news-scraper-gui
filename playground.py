"""A playground for testing out OCR on images of Japanese text."""

# Standard library imports
import logging
import os
import sys
from typing import Tuple, Optional

# Third-party imports
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import pyautogui

# Set the logging level
logging.basicConfig(level=logging.INFO)

# TODO: filter non-text characters (e.g. emojis, symbols, etc.) and background pictures

# TODO: fix green box blinking when first time selecting the region

# TODO: press esc to exit the program, press c or enter to confirm the selection


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
            f"Tesseract executable not found. Please check the path: {path}"
        )

    pytesseract.pytesseract.tesseract_cmd = path


def draw_rectangle(event, x, y, flags, param) -> None:
    coords = param  # Get the coordinates dictionary from the 'param' argument

    if event == cv2.EVENT_LBUTTONDOWN:
        if not coords["drawing"]:
            coords["drawing"] = True
            coords["ix"], coords["iy"] = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if coords["drawing"]:
            coords["x_end"], coords["y_end"] = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        coords["drawing"] = False
        coords["x_end"], coords["y_end"] = x, y


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
    image: Image.Image,
    lang: str = "jpn",
    preprocess: bool = True,
    preprocess_params: Optional[dict] = None,
) -> str:
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
    try:
        set_tesseract_path()
    except (RuntimeError, FileNotFoundError) as e:
        print(e)
        sys.exit(1)

    # Take a screenshot and select the region
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    cv2.imwrite("temp_screenshot.png", screenshot)
    img = cv2.imread("temp_screenshot.png")

    coords = {"ix": -1, "iy": -1, "x_end": -1, "y_end": -1, "drawing": False}

    # Create a window to select the region in fullscreen mode
    cv2.namedWindow("Select ROI", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        "Select ROI", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback("Select ROI", draw_rectangle, param=coords)

    while True:
        img_copy = img.copy()
        if coords["drawing"]:
            cv2.rectangle(
                img_copy,
                (coords["ix"], coords["iy"]),
                (coords["x_end"], coords["y_end"]),
                (0, 255, 0),
                2,
            )
        elif coords["ix"] != -1 and coords["iy"] != -1:
            cv2.rectangle(
                img_copy,
                (coords["ix"], coords["iy"]),
                (coords["x_end"], coords["y_end"]),
                (0, 255, 0),
                2,
            )
        cv2.imshow("Select ROI", img_copy)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):  # Press 'c' to confirm the selection
            if (
                coords["ix"] != -1
                and coords["iy"] != -1
                and coords["x_end"] != -1
                and coords["y_end"] != -1
            ):
                break

    cv2.destroyAllWindows()

    # Ensure that the coordinates are ordered correctly
    x_start, x_end = min(coords["ix"], coords["x_end"]), max(
        coords["ix"], coords["x_end"]
    )
    y_start, y_end = min(coords["iy"], coords["y_end"]), max(
        coords["iy"], coords["y_end"]
    )

    region = (x_start, y_start, x_end - x_start, y_end - y_start)

    # Use pyautogui.screenshot to capture the region based on the given coordinates
    screenshot_region = pyautogui.screenshot(region=region)

    # Perform OCR on the selected region
    result = ocr_image(
        screenshot_region,
        preprocess_params={
            "size": (screenshot_region.width * 4, screenshot_region.height * 4)
        },
    )
    print(result)
