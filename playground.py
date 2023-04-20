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
import pyperclip

# Set the logging level
logging.basicConfig(level=logging.INFO)

"""A playground for testing out OCR on images of Japanese text."""
"""Does not work on Mac OS"""

# TODO: filter non-text characters (e.g. emojis, symbols, etc.) and background pictures

# TODO: create a GUI to select the region of interest (ROI) and perform OCR on the selected region

# TODO: change macos implementation to read image instead of screenshot


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
    """Draw a rectangle on the image when the mouse is clicked and dragged"""
    coords = param  # Get the coordinates dictionary from the 'param' argument

    if event == cv2.EVENT_LBUTTONDOWN:
        if not coords["drawing"]:
            coords["drawing"] = True
            coords["ix"], coords["iy"] = x, y
            # Set initial coords when first clicked
            coords["x_end"], coords["y_end"] = x, y

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
    threshold: int = 145,
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
    """Perform OCR on an image."""
    if preprocess:
        if preprocess_params is not None:
            logging.info("Preprocessing image...\n")
            image = preprocess_image(image, **preprocess_params)
        else:
            image = preprocess_image(image)
        
        # Save the preprocessed image
        image.save("./ocr_images/preprocessed.png")
        
        # Display the preprocessed image
        image.show()

    # psm 6: Assume a single uniform block of text. oem 3: Use LSTM neural network.
    config = "--psm 6 --oem 3 -c preserve_interword_spaces=1"
    text = pytesseract.image_to_string(image, lang=lang, config=config)
    text = text.strip().replace(" ", "").replace("\n", "")
    if lang == "jpn":
        text = text.replace("?", "？").replace("!", "！").replace(".", "。")
    return text


def get_roi_coordinates(coords: dict) -> Tuple[int, int, int, int]:
    """Get the coordinates of the region of interest (ROI)"""
    # Ensure that the coordinates are ordered correctly
    x_start, x_end = min(coords["ix"], coords["x_end"]), max(
        coords["ix"], coords["x_end"]
    )
    y_start, y_end = min(coords["iy"], coords["y_end"]), max(
        coords["iy"], coords["y_end"]
    )

    return x_start, y_start, x_end - x_start, y_end - y_start


def select_region_and_capture(coords: dict) -> Image.Image:
    """Display a window to select the region, and capture the selected region."""
    screenshot = pyautogui.screenshot()
    img = np.array(screenshot)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

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

        if key == 27:  # Press 'Esc' to exit the program
            cv2.destroyAllWindows()
            sys.exit(0)
        elif (
            key == ord("c") or key == 13
        ):  # Press 'c' or 'Enter' to confirm the selection
            if (
                coords["ix"] != -1
                and coords["iy"] != -1
                and coords["x_end"] != -1
                and coords["y_end"] != -1
            ):
                break

    cv2.destroyAllWindows()
    region = get_roi_coordinates(coords)

    # Use pyautogui.screenshot to capture the region based on the given coordinates
    screenshot_region = pyautogui.screenshot(region=region)

    # Convert the region screenshot to a PIL Image object
    screenshot_region = Image.frombytes(
        "RGB",
        (screenshot_region.width, screenshot_region.height),
        screenshot_region.tobytes(),
    )

    return screenshot_region


def compare_result_answer(result, answer) -> None:
    """Compare the OCR result with the correct answer."""
    import difflib

    match = difflib.SequenceMatcher(None, result, answer)
    similarity = match.ratio()
    print(f"Similarity ratio: {similarity:.2%}")

    for tag, i1, i2, j1, j2 in match.get_opcodes():
        if tag == "replace":
            print(
                f"Mismatched parts: OCR result - '{result[i1:i2]}', Correct answer - '{answer[j1:j2]}'"
            )
        elif tag == "delete":
            print(f"Extra parts: OCR result - '{result[i1:i2]}'")
        elif tag == "insert":
            print(f"Missing parts: Correct answer - '{answer[j1:j2]}'")


if __name__ == "__main__":
    try:
        set_tesseract_path()
    except (RuntimeError, FileNotFoundError) as e:
        print(e)
        sys.exit(1)

    coords = {"ix": -1, "iy": -1, "x_end": -1, "y_end": -1, "drawing": False}
    screenshot_region = select_region_and_capture(coords)

    # Perform OCR on the selected region
    result = ocr_image(
        screenshot_region,
        preprocess_params={
            "size": (screenshot_region.width * 4, screenshot_region.height * 4)
        },
    )

    print(result)

    answer = """"""

    if answer:
        compare_result_answer(result, answer)

    # Copy the OCR result to the clipboard
    pyperclip.copy(result)
