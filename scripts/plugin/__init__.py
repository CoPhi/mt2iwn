"""
Plugins module for MT2IWN project.

Adds bidirectional PLUG-IN_LINKS between ItalWordNet and MariTerm synsets,
updates MariTerm plugin links, removes duplicates, retrieves missing glosses,
and produces the finalized XML files.
"""

from .adder import add_plugins, ensure_plugin_links, find_mariterm_synset, insert_after, load_csv_data
from .updater import update_plugin_links, insert_plugin_node
from .cleaner import remove_duplicate_plugins, sort_plugin_links
from .glosses import find_glosses_for_new_synsets, display_results, update_glosses_in_xml

__all__ = [
    'add_plugins',
    'ensure_plugin_links',
    'find_mariterm_synset',
    'insert_after',
    'load_csv_data',
    'update_plugin_links',
    'insert_plugin_node',
    'remove_duplicate_plugins',
    'sort_plugin_links',
    'find_glosses_for_new_synsets',
    'display_results',
    'update_glosses_in_xml',
]