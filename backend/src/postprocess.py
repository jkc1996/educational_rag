# src/postprocess.py

import re
import spacy
from src.logger import get_logger

logger = get_logger()
nlp = spacy.load("en_core_web_sm")

def spacy_polish(text):
    doc = nlp(text)
    clean = " ".join(sent.text.strip() for sent in doc.sents)
    # Remove all newlines and tabs ONLY (not slashes)
    clean = re.sub(r'[\n\t]+', ' ', clean)
    # Collapse multiple spaces
    clean = re.sub(r' +', ' ', clean)
    logger.debug("Polished answer with spaCy.")
    return clean.strip()
