"""
Filtering module for MT2IWN project.

Validates XML inputs, filters word meanings by lemma and sense,
and transcribes matched pairs to filtered XML files.
"""

from .validator import validate_xml
from .filter import filter_wm
from .matcher import match_lemmas
from .transcriber import transcribe_matched_pairs, transcribe_candidates

__all__ = [
    'validate_xml',
    'filter_wm',
    'match_lemmas',
    'transcribe_matched_pairs',
    'transcribe_candidates',
]