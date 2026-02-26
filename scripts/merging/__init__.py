"""
Merging module for MT2IWN project.

Merges the updated IWN entries back into the original IWN file
and formats the output XML with proper indentation.
"""

from .merger import merge_and_format_iwn_files
from .formatter import format_xml_with_indentation, save_pretty_xml

__all__ = [
    'merge_and_format_iwn_files',
    'format_xml_with_indentation',
    'save_pretty_xml',
]