"""
Updating module for MT2IWN project.

Reads filtered candidates, creates or merges ItalWordNet word meanings,
handles relations, and produces the updated IWN XML file.

Module-level state (replaced_glosses, new_word_meanings, updated_entries)
is intentionally mutable so that creator and updater functions share
the same lists/set without altering the original notebook logic.
"""

# Shared mutable state — mirrors the global variables in the original notebook
replaced_glosses = []
new_word_meanings = []
updated_entries = set()

from .reader import read_lemmas_from_csv
from .retriever import (
    retrieve_wm,
    find_word_meaning_in_root,
    get_new_id,
    get_gloss_from_italwn,
    extract_target_ids,
    retrieve_relation_ids,
)
from .creator import (
    create_or_merge_word_meaning,
    determine_inverse_relation,
    extract_eq_links_and_top_onto,
    merge_sections,
)
from .cleaner import (
    clean_target_wm_id,
    remove_duplicate_relations,
    clean_existing_target_wm_ids,
    clean_and_move_eq_links_at_end,
    sort_word_meanings_by_lemma_and_sense,
)
from .updater import (
    update_iwn_entries,
    replace_gloss_with_original,
    remove_redundant_word_meanings,
)

__all__ = [
    # State
    'replaced_glosses',
    'new_word_meanings',
    'updated_entries',
    # Reader
    'read_lemmas_from_csv',
    # Retriever
    'retrieve_wm',
    'find_word_meaning_in_root',
    'get_new_id',
    'get_gloss_from_italwn',
    'extract_target_ids',
    'retrieve_relation_ids',
    # Creator
    'create_or_merge_word_meaning',
    'determine_inverse_relation',
    'extract_eq_links_and_top_onto',
    'merge_sections',
    # Cleaner
    'clean_target_wm_id',
    'remove_duplicate_relations',
    'clean_existing_target_wm_ids',
    'clean_and_move_eq_links_at_end',
    'sort_word_meanings_by_lemma_and_sense',
    # Updater
    'update_iwn_entries',
    'replace_gloss_with_original',
    'remove_redundant_word_meanings',
]