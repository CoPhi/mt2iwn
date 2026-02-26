"""
XML validation for MariTerm and ItalWordNet input files.
"""

import xml.etree.ElementTree as ET


def validate_xml(file_path):
    try:
        ET.parse(file_path)
        return True
    except ET.ParseError as e:
        print(f"Error parsing {file_path}: {e}")
        return False