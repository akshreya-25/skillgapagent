import os
import pdfplumber
import PyPDF2

def extract_text_from_pdf(file_path):
    """
    Extracts plain text from a PDF file using pdfplumber and PyPDF2 as fallback.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found at {file_path}")
        
    text = ""
    
    # 1. Try extracting with pdfplumber (best for layout and tables)
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        # If text is extracted successfully, return it
        if text.strip():
            return clean_text(text)
    except Exception as e:
        print(f"pdfplumber extraction failed: {e}. Trying PyPDF2 fallback...")

    # 2. Try PyPDF2 as fallback
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            return clean_text(text)
    except Exception as e:
        print(f"PyPDF2 extraction failed: {e}.")
        
    # If both fail, return empty or raise error
    return ""

def clean_text(text):
    """
    Basic text cleaning (removes excessive whitespaces, normalizes line breaks).
    """
    if not text:
        return ""
    # Replace multiple spaces with a single space
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        cleaned_line = " ".join(line.split())
        if cleaned_line:
            cleaned_lines.append(cleaned_line)
    return "\n".join(cleaned_lines)

if __name__ == "__main__":
    # Test stub
    import sys
    if len(sys.argv) > 1:
        test_pdf = sys.argv[1]
        print(f"Extracting text from: {test_pdf}")
        extracted = extract_text_from_pdf(test_pdf)
        print("--- EXTRACTED TEXT (FIRST 500 CHARS) ---")
        print(extracted[:500])
    else:
        print("Please provide a PDF file path to test.")
