"""
Text normalization utilities for lemmas and glosses.
"""

import string


def normalize_lemma(lemma):
    """Replace underscores with spaces in lemma, replace apostrophes with spaces, and lowercase the text."""
    return lemma.replace('_', ' ').lower().replace("'", " ").translate(str.maketrans('', '', string.punctuation.replace("'", ""))) if lemma else ""


def normalize_text(text):
    """Lowercase, replace underscores with spaces, replace apostrophes with spaces, and remove other punctuation from text."""
    text = text.lower().replace('_', ' ').replace("'", " ")  # Replace underscores and apostrophes with spaces
    return text.translate(str.maketrans('', '', string.punctuation.replace("'", "")))  # Remove all other punctuation