"""
Matching module for MT2IWN project.

Extracts word meanings from XML, matches MariTerm and ItalWordNet entries
using similarity scoring, and exports results to CSV.
"""

from .extractor import extract_word_meanings
from .matcher import match_lemmas_with_alternate_senses
from .formatter import print_and_return_best_match, format_results, print_formatted_results
from .writer import save_entries, store_to_csv

__all__ = [
    'extract_word_meanings',
    'match_lemmas_with_alternate_senses',
    'print_and_return_best_match',
    'format_results',
    'print_formatted_results',
    'save_entries',
    'store_to_csv',
]