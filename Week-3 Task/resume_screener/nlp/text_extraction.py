"""
text_extraction.py
------------------------------------------------------------------
Responsible for extracting raw text out of resume files uploaded
by the user.

Supported formats:
    - .txt  (plain text)
    - .pdf  (extracted using PyPDF2, if installed)
    - .docx (extracted using python-docx, if installed)

To keep this project dependency-light (per the assignment's
technology restrictions: Python, Tkinter, SQLite, Scikit-learn,
Pandas, Matplotlib), PDF/DOCX support is implemented as an OPTIONAL
best-effort feature. If PyPDF2 or python-docx are not installed,
the app still works perfectly using .txt resumes and the manual
"paste resume text" option in the Candidate form.
------------------------------------------------------------------
"""

import os


class TextExtractionError(Exception):
    """Raised when a resume file cannot be read or parsed."""
    pass


def extract_text_from_file(file_path):
    """
    Extracts and returns raw text content from a resume file.

    Args:
        file_path (str): full path to the uploaded resume file.

    Returns:
        str: extracted raw text.

    Raises:
        TextExtractionError: if the file type is unsupported or
                              the file cannot be read.
    """
    if not os.path.exists(file_path):
        raise TextExtractionError(f"File not found: {file_path}")

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".txt":
        return _extract_from_txt(file_path)
    elif file_extension == ".pdf":
        return _extract_from_pdf(file_path)
    elif file_extension == ".docx":
        return _extract_from_docx(file_path)
    else:
        raise TextExtractionError(
            f"Unsupported file type '{file_extension}'. "
            "Please upload a .txt, .pdf, or .docx file."
        )


def _extract_from_txt(file_path):
    """Reads a plain text resume file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file_handle:
            return file_handle.read()
    except Exception as error:
        raise TextExtractionError(f"Could not read text file: {error}")


def _extract_from_pdf(file_path):
    """
    Extracts text from a PDF resume using PyPDF2.
    If PyPDF2 is not installed, raises a clear, friendly error so
    the user can instead paste the resume text manually.
    """
    try:
        import PyPDF2
    except ImportError:
        raise TextExtractionError(
            "PDF support requires the 'PyPDF2' library, which is not installed.\n"
            "Please upload a .txt file instead, or paste the resume text manually."
        )

    try:
        extracted_text = ""
        with open(file_path, "rb") as file_handle:
            pdf_reader = PyPDF2.PdfReader(file_handle)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
        if not extracted_text.strip():
            raise TextExtractionError(
                "No readable text could be found in this PDF (it may be a scanned image)."
            )
        return extracted_text
    except TextExtractionError:
        raise
    except Exception as error:
        raise TextExtractionError(f"Could not read PDF file: {error}")


def _extract_from_docx(file_path):
    """
    Extracts text from a DOCX resume using python-docx.
    If python-docx is not installed, raises a clear, friendly error.
    """
    try:
        import docx
    except ImportError:
        raise TextExtractionError(
            "DOCX support requires the 'python-docx' library, which is not installed.\n"
            "Please upload a .txt file instead, or paste the resume text manually."
        )

    try:
        document = docx.Document(file_path)
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        extracted_text = "\n".join(paragraphs)
        if not extracted_text.strip():
            raise TextExtractionError("No readable text could be found in this DOCX file.")
        return extracted_text
    except TextExtractionError:
        raise
    except Exception as error:
        raise TextExtractionError(f"Could not read DOCX file: {error}")
