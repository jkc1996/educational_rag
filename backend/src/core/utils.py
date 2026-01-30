# src/utils.py

import re

def final_clean_text(text):
    """
    Removes PDF linebreak artifacts, hyphens, and extra whitespace for cleaner chunked text.
    """
    # Remove hyphen + newline artifacts
    text = re.sub(r'-\n', '', text)
    # Replace any remaining newlines with space
    text = re.sub(r'\n+', ' ', text)
    # Remove excess spaces
    text = re.sub(r' +', ' ', text)
    return text.strip()
