import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
from pdf2image import convert_from_path
from skimage import measure, morphology
from skimage.measure import regionprops

# Set path to Poppler bin folder (for Windows)
POPPLER_PATH = r"C:\Software\poppler-24.02.0\Library\bin"

# Constants
CONSTANT_1 = 84
CONSTANT_2 = 250
CONSTANT_3 = 100
CONSTANT_4 = 18


def enhance_image(image):
    # Convert to grayscale and apply thresholding to get a binary image
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return thresh


def process_image(page_number, img):
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
    a4_small_size_outlier_constant = ((average / CONSTANT_1) * CONSTANT_2) + CONSTANT_3
    a4_big_size_outlier_constant = a4_small_size_outlier_constant * CONSTANT_4
    print(f"A4 small size outlier constant: {a4_small_size_outlier_constant}")
    print(f"A4 big size outlier constant: {a4_big_size_outlier_constant}")

    # Remove small and large connected pixels
    pre_version = morphology.remove_small_objects(blobs_labels, a4_small_size_outlier_constant)
    component_sizes = np.bincount(pre_version.ravel())
    too_large_mask = component_sizes > a4_big_size_outlier_constant
    pre_version[too_large_mask[pre_version]] = 0

    # Save pre-version
    plt.imsave(f"output/{page_number}_pre_version.jpg", pre_version)

    # Read and ensure binary
    img = cv2.imread(f"output/{page_number}_pre_version.jpg", cv2.IMREAD_GRAYSCALE)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    # Save the result
    cv2.imwrite(f"output/{page_number}_result.jpg", img)


def process_pdf(pdf_path):
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    # Create output directory if not exists
    if not os.path.exists("output"):
        os.makedirs("output")
    for i, image in enumerate(images):
        enhanced_image = enhance_image(image)
        cv2.imwrite(f"output/{i}_enhanced.jpg", enhanced_image)
        process_image(i, enhanced_image)


# Example usage
if __name__ == "__main__":
    process_pdf("input/invoice_2.pdf")
