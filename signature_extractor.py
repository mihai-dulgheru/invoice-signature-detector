import os
import platform
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from colorama import Fore, Style, init
from pdf2image import convert_from_path
from skimage import measure, morphology
from skimage.measure import regionprops

# Initialize colorama
init()

if platform.system() == "Windows":
    # Set the path to the Poppler executable
    POPPLER_PATH = Path(r"C:\Software\poppler-24.02.0\Library\bin")
else:
    POPPLER_PATH = None

# Constants
AVERAGE_DIVISOR = 84
AREA_MULTIPLIER = 250
BASE_CONSTANT = 100
OUTLIER_MULTIPLIER = 18


def enhance_image(image):
    """Convert to grayscale and apply thresholding to get a binary image."""
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return thresh


def process_image(page_number, img):
    """Process image to remove small and large connected components."""
    # Ensure binary
    img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]

    # Connected component analysis
    blobs_labels = measure.label(img > img.mean(), background=1)

    the_biggest_component = 0
    total_area = 0
    counter = 0
    for region in regionprops(blobs_labels):
        if region.area > 10:
            total_area += region.area
            counter += 1
        if region.area >= 250 and region.area > the_biggest_component:
            the_biggest_component = region.area

    average = total_area / counter if counter else 0
    print(f"The biggest component: {the_biggest_component}")
    print(f"Average: {average}")

    # Experimental-based ratio calculations
    small_outlier_constant = ((average / AVERAGE_DIVISOR) * AREA_MULTIPLIER) + BASE_CONSTANT
    big_outlier_constant = small_outlier_constant * OUTLIER_MULTIPLIER
    print(f"Small size outlier constant: {small_outlier_constant}")
    print(f"Big size outlier constant: {big_outlier_constant}")

    # Remove small and large connected pixels
    pre_version = morphology.remove_small_objects(blobs_labels, small_outlier_constant)
    component_sizes = np.bincount(pre_version.ravel())
    too_large_mask = component_sizes > big_outlier_constant
    pre_version[too_large_mask[pre_version]] = 0

    # Save pre-version
    plt.imsave(f"output/{page_number}_pre_version.jpg", pre_version)

    # Read and ensure binary
    img = cv2.imread(f"output/{page_number}_pre_version.jpg", cv2.IMREAD_GRAYSCALE)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    # Save the result
    cv2.imwrite(f"output/{page_number}_result.jpg", img)


def process_pdf(pdf_path, pdf_index):
    """Process each page of the PDF."""
    print_colored(f"Processing PDF: {pdf_path}", Fore.BLUE)
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    # Create output directory if not exists
    if not os.path.exists("output"):
        os.makedirs("output")
    for j, image in enumerate(images):
        enhanced_image = enhance_image(image)
        cv2.imwrite(f"output/{pdf_index}_{j}_enhanced.jpg", enhanced_image)
        process_image(f"{pdf_index}_{j}", enhanced_image)


def print_colored(message, color):
    """Print a message with a specified color."""
    print(color + message + Style.RESET_ALL)


# Example usage
if __name__ == "__main__":
    for i in range(1, 6):
        process_pdf(f"input/invoice_{i}.pdf", i)
        print_colored(f"Finished processing invoice_{i}.pdf", Fore.GREEN)
