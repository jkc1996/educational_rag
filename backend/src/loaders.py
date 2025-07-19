# src/loaders.py

import pdfplumber
from src.logger import get_logger

logger = get_logger()

def load_pdf_pages(pdf_path):
    """
    Loads each page of a PDF using pdfplumber.
    Returns a list of dicts: [{'page_num': n, 'text': ...}, ...]
    """
    logger.info(f"Loading PDF: {pdf_path}")
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text or len(text.strip()) < 10:
                logger.debug(f"Skipping empty/short page {i+1}")
                continue
            pages.append({'page_num': i + 1, 'text': text})
            logger.debug(f"Loaded page {i + 1}: {len(text)} chars")
    logger.info(f"Loaded {len(pages)} pages from {pdf_path}")
    return pages
