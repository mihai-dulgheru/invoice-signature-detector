import logging
import os
import platform
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from colorama import Fore, Style, init
from pdf2image import convert_from_path

# Initialize colorama
init()

# Set the path to the Poppler and Tesseract executables if on Windows
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    POPPLER_PATH = Path(r"C:\Software\poppler-24.02.0\Library\bin")
else:
    POPPLER_PATH = None


def enhance_image(image):
    """Convert to grayscale to get a binary image."""
    return cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)


def extract_region(image, crop_area):
    """Crop the image to the specified region."""
    height, width = image.shape
    x1, y1 = int(width * crop_area[0]), int(height * crop_area[1])
    x2, y2 = int(width * crop_area[2]), int(height * crop_area[3])
    return image[y1:y2, x1:x2]


def check_for_signature(prefix, image):
    """Check if a signature is present in the given image region."""
    h, w = image.shape
    mask = np.zeros(image.shape, dtype=np.uint8)
    x1, y1 = int(w * 0.1), int(h * 0.5)
    x2, y2 = int(w * 0.9), int(h * 0.9)
    mask[y1:y2, x1:x2] = 255
    masked_image = cv2.bitwise_and(image, image, mask=mask)
    cv2.imwrite(f"{prefix}_signature_masked.jpg", masked_image)
    signature_text = pytesseract.image_to_string(masked_image, config='--psm 6')
    return bool(signature_text.strip())


def process_invoice(pdf_path, crop_area):
    """Process each page of the PDF to detect signatures."""
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    os.makedirs("output", exist_ok=True)
    invoice_name = os.path.splitext(os.path.basename(pdf_path))[0]

    for index, image in enumerate(images):
        prefix = f"output/{invoice_name}_{index}"
        enhanced_image = enhance_image(image)
        signature_region = extract_region(enhanced_image, crop_area)
        cv2.imwrite(f"{prefix}_signature_region.jpg", signature_region)
        if check_for_signature(prefix, signature_region):
            log_with_color("Signature found", Fore.GREEN)
        else:
            log_with_color("Signature not found", Fore.RED)


def extract_awb(pdf_path):
    """Extract the AWB number from the PDF."""
    awb_crop_area = (0.40, 0.16, 0.60, 0.26)
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    os.makedirs("output", exist_ok=True)
    invoice_name = os.path.splitext(os.path.basename(pdf_path))[0]

    for index, image in enumerate(images):
        prefix = f"output/{invoice_name}_{index}"
        enhanced_image = enhance_image(image)
        awb_region = extract_region(enhanced_image, awb_crop_area)
        cv2.imwrite(f"{prefix}_awb_region.jpg", awb_region)
        h, w = awb_region.shape
        mask = np.zeros(awb_region.shape, dtype=np.uint8)
        x1, y1 = int(w * 0.0), int(h * 0.66)
        x2, y2 = int(w * 1.0), int(h * 1.0)
        mask[y1:y2, x1:x2] = 255
        masked_image = cv2.bitwise_and(awb_region, awb_region, mask=mask)
        cv2.imwrite(f"{prefix}_awb_masked.jpg", masked_image)
        awb_text = pytesseract.image_to_string(masked_image, config='--psm 6')
        awb_number = awb_text.replace("\n", "").replace(" ", "").strip()
        log_with_color(f"AWB number: {awb_number}", Fore.YELLOW)


def log_with_color(message, color):
    """Log a message with a specified color."""
    logging.info(color + message + Style.RESET_ALL)


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Define crop areas for signature detection
    crop_areas = [(0.58, 0.80, 0.78, 0.85)] * 5

    # Process each invoice with the corresponding crop area
    for i in range(1, 6):
        log_with_color(f"Processing invoice_{i}.pdf", Fore.BLUE)
        process_invoice(f"input/invoice_{i}.pdf", crop_area=crop_areas[i - 1])
        extract_awb(f"input/invoice_{i}.pdf")
        log_with_color(f"Finished processing invoice_{i}.pdf", Fore.GREEN)
