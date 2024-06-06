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
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    # Increase contrast using histogram equalization
    # enhanced = cv2.equalizeHist(gray)
    # return enhanced
    return gray


def extract_signature_region(image):
    height, width = image.shape
    # Define the region of interest (ROI) containing the signature box
    (x1, y1) = (int(width * 0.60), int(height * 0.80))
    (x2, y2) = (int(width * 0.84), int(height * 0.86))
    roi = image[y1:y2, x1:x2]
    return roi


def check_for_signature(image):
    # Use Tesseract to detect text
    text = pytesseract.image_to_string(image, config='--psm 6')
    # Check if the detected text matches the required text above the signature box
    if "Numele si semnatura persoanei" in text and "care a receptionat marfa" in text:
        # Mask the text area to avoid detecting it as a signature
        mask = np.zeros(image.shape, dtype=np.uint8)
        h, w = image.shape
        (x1, y1) = (0, int(h * 0.5))
        (x2, y2) = (w, h)
        mask[y1:y2, x1:x2] = 255
        masked_image = cv2.bitwise_and(image, image, mask=mask)
        # Save the masked image to a file for further analysis
        cv2.imwrite("masked_image.jpg", masked_image)
        # Use Tesseract to detect any other text (signature) in the remaining area
        signature_text = pytesseract.image_to_string(masked_image, config='--psm 6')
        # If there's text remaining, it means there's a signature
        return bool(signature_text.strip())
    return False


def process_invoice(pdf_path):
    # Convert PDF to images
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    for image in images:
        enhanced_image = enhance_image(image)
        signature_region = extract_signature_region(enhanced_image)
        # Save the signature region to a file for further analysis
        cv2.imwrite("signature_region.jpg", signature_region)
        if check_for_signature(signature_region):
            print("Signature found.")
        else:
            print("Signature not found.")


# Example usage
process_invoice("invoices/invoice-2.pdf")
