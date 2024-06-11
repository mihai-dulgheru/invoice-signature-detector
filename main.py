import logging
import os
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path

# Set path to Tesseract executable (for Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Set path to Poppler bin folder (for Windows)
POPPLER_PATH = Path(r"C:\Software\poppler-24.02.0\Library\bin")


def enhance_image(image):
    # Convert to grayscale and apply thresholding to get a binary image
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    # _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    # return thresh
    return gray


def extract_signature_region(image, crop_area=(0.60, 0.80, 0.84, 0.86)):
    # Crop the image to the region where the signature is expected
    height, width = image.shape
    (x1, y1) = (int(width * crop_area[0]), int(height * crop_area[1]))
    (x2, y2) = (int(width * crop_area[2]), int(height * crop_area[3]))
    roi = image[y1:y2, x1:x2]
    return roi


def check_for_signature(prefix, image):
    # Mask the text area to avoid detecting it as a signature
    mask = np.zeros(image.shape, dtype=np.uint8)
    h, w = image.shape
    (x1, y1) = (int(w * 0.1), int(h * 0.5))
    (x2, y2) = (int(w * 0.9), int(h * 0.9))
    mask[y1:y2, x1:x2] = 255
    masked_image = cv2.bitwise_and(image, image, mask=mask)
    cv2.imwrite(f"{prefix}_masked.jpg", masked_image)
    # Use Tesseract to detect any other text (signature) in the remaining area
    signature_text = pytesseract.image_to_string(masked_image, config='--psm 6')
    # If there's text remaining, it means there's a signature
    return bool(signature_text.strip())


def process_invoice(pdf_path, crop_area):
    # Convert PDF to images
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    # Create output directory if not exists
    if not os.path.exists("output"):
        os.makedirs("output")
    # Extract invoice name from the PDF file name
    invoice_name = os.path.splitext(os.path.basename(pdf_path))[0]
    logging.info(f"Processing invoice: {invoice_name}")
    # Process each page of the invoice
    for index, image in enumerate(images):
        prefix = f"output/{invoice_name}_{index}"
        enhanced_image = enhance_image(image)
        signature_region = extract_signature_region(enhanced_image, crop_area=crop_area)
        cv2.imwrite(f"{prefix}_signature_region.jpg", signature_region)
        if check_for_signature(prefix, signature_region):
            logging.info("Signature found")
        else:
            logging.info("Signature not found")


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

    # Define crop areas for each page of the invoice
    crop_areas = [(0.57, 0.81, 0.79, 0.87), (0.60, 0.80, 0.84, 0.86), (0.58, 0.80, 0.80, 0.86)]
    # Process each invoice with the corresponding crop area
    for i, area in enumerate(crop_areas):
        process_invoice(f"input/invoice_{i + 1}.pdf", crop_area=area)
