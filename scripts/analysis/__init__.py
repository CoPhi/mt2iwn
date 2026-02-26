"""
Analysis module for MT2IWN project.

Post-hoc analysis utilities: ID conflict detection, last WM ID retrieval,
and identification of new/updated synsets between IWN versions.
"""

from .comparator import extract_ids_and_lemmas, compare_files
from .id_manager import get_last_word_meaning_id
from .identifier import extract_internal_links, identify_updates_in_iwn

__all__ = [
    'extract_ids_and_lemmas',
    'compare_files',
    'get_last_word_meaning_id',
    'extract_internal_links',
    'identify_updates_in_iwn',
]