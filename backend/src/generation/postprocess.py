import re
import spacy
import logging

nlp = spacy.load("en_core_web_sm")

def spacy_polish(text):
    doc = nlp(text)
    clean = " ".join(sent.text.strip() for sent in doc.sents)
    # Remove all newlines and tabs ONLY (not slashes)
    clean = re.sub(r'[\n\t]+', ' ', clean)
    # Collapse multiple spaces
    clean = re.sub(r' +', ' ', clean)
    logging.debug({
        "event": "spacy_polish",
        "original_length": len(text),
        "polished_length": len(clean.strip())
    })
    return clean.strip()
