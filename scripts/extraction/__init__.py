"""
Extraction module for MT2IWN project.

This module provides functionality for extracting lemmas from MariTerm and ItalWordNet
XML files and finding shared entries between the two resources.
"""

from .xml_parser import extract_lemmas
from .matcher import find_shared
from .writer import write_csv

__all__ = [
    'extract_lemmas',
    'find_shared',
    'write_csv'
]
