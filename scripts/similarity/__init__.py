"""
Similarity module for MT2IWN project.

Provides text normalization and semantic similarity functions for comparing
MariTerm and ItalWordNet entries via gloss and relation scoring.
"""

from .gloss import calculate_gloss_similarity
from .relations import calculate_relation_similarity
from .normalizer import normalize_lemma, normalize_text
from .scoring import format_relations, get_fallback_gloss

__all__ = [
    'normalize_lemma',
    'normalize_text',
    'calculate_gloss_similarity',
    'calculate_relation_similarity',
    'format_relations',
    'get_fallback_gloss',
]
