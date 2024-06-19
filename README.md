# Invoice Signature Detector

This project processes PDF invoices to detect signatures and extract AWB numbers using image processing and OCR
techniques.

## Requirements

- Python 3.6 or higher
- The following Python packages:
  - `opencv-python`
  - `numpy`
  - `pytesseract`
  - `colorama`
  - `pdf2image`
  - `matplotlib`
  - `scikit-image`

## Installation

### Windows

1. **Install Python**: Download and install Python from the [official website](https://www.python.org/downloads/).

2. **Install Poppler**:

   - Download Poppler for Windows from [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/).
   - Extract the zip file and place the `bin` directory in a known location (
     e.g., `C:\Software\poppler-24.02.0\Library\bin`).

3. **Install Tesseract**:

   - Download Tesseract OCR from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).
   - Install Tesseract and note the installation path (e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`).

4. **Install Python packages**:

   - Open a command prompt and navigate to the project directory.
   - Run the following command to install the required packages:

     ```sh
     pip install -r requirements.txt
     ```

### Linux

1. **Install Python**: Use your distribution's package manager to install Python (e.g., `sudo apt-get install python3`).

2. **Install Poppler**:

   - Use your package manager to install Poppler (e.g., `sudo apt-get install poppler-utils`).

3. **Install Tesseract**:

   - Use your package manager to install Tesseract (e.g., `sudo apt-get install tesseract-ocr`).

4. **Install Python packages**:

   - Open a terminal and navigate to the project directory.
   - Run the following command to install the required packages:

     ```sh
     pip install -r requirements.txt
     ```

### Mac

1. **Install Python**: Use Homebrew to install Python (e.g., `brew install python3`).

2. **Install Poppler**:

   - Use Homebrew to install Poppler (e.g., `brew install poppler`).

3. **Install Tesseract**:

   - Use Homebrew to install Tesseract (e.g., `brew install tesseract`).

4. **Install Python packages**:

   - Open a terminal and navigate to the project directory.
   - Run the following command to install the required packages:

     ```sh
     pip install -r requirements.txt
     ```

## Usage

1. **Prepare Input Files**:

   - Place your PDF invoices in the `input` directory. Name them as `invoice_1.pdf`, `invoice_2.pdf`, etc.

2. **Run the Script**:

   - Open a terminal or command prompt.
   - Navigate to the project directory.
   - Run the script using the following command:

     ```sh
     python main.py
     ```

3. **View Output**:
   - The script will process the invoices and output the results in the `output` directory.
   - Log messages will be displayed in the terminal, indicating the processing status and results.

### Example Output

```text
2024-06-19 14:25:59 - Processing invoice_1.pdf
2024-06-19 14:26:01 - Signature not found
2024-06-19 14:26:02 - AWB number: 1234-5AB6789101112-123.45
2024-06-19 14:26:02 - Finished processing invoice_1.pdf
2024-06-19 14:26:02 - Processing invoice_2.pdf
2024-06-19 14:26:04 - Signature found
2024-06-19 14:26:06 - AWB number: 1234-5AB6789101112-123.45
2024-06-19 14:26:06 - Finished processing invoice_2.pdf
...
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### Note

- The `requirements.txt` file should be placed in the same directory as your `main.py` script.
- The `input` directory should contain your PDF files named as `invoice_1.pdf`, `invoice_2.pdf`, etc.
- Ensure that `Poppler` and `Tesseract` are correctly installed and their paths are set properly for Windows. For Linux
  and Mac, the default paths should work if installed via package managers.
