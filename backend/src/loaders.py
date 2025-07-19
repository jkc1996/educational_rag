# src/loaders.py

import pdfplumber
import logging

def load_pdf_pages(pdf_path):
    """
    Loads each page of a PDF using pdfplumber.
    Returns a list of dicts: [{'page_num': n, 'text': ...}, ...]
    """
    logging.info({
        "event": "pdf_load_start",
        "file": pdf_path
    })
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text or len(text.strip()) < 10:
                logging.debug({
                    "event": "pdf_page_skipped",
                    "file": pdf_path,
                    "page_num": i + 1,
                    "reason": "empty_or_short"
                })
                continue
            pages.append({'page_num': i + 1, 'text': text})
            logging.debug({
                "event": "pdf_page_loaded",
                "file": pdf_path,
                "page_num": i + 1,
                "char_count": len(text)
            })
    logging.info({
        "event": "pdf_load_done",
        "file": pdf_path,
        "pages_loaded": len(pages)
    })
    return pages
