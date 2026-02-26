"""
XML formatting utilities — indentation, pretty-printing.
"""

import re
import xml.dom.minidom
from xml.dom import minidom
import xml.etree.ElementTree as ET


def format_xml_with_indentation(file_path):
    """Format the XML file with proper indentation and remove unnecessary blank lines."""
    # Read the file and parse it into an XML document
    with open(file_path, 'r', encoding='utf-8') as file:
        xml_str = file.read()

    # Parse the XML string
    dom = xml.dom.minidom.parseString(xml_str)

    # Pretty print with indentation
    pretty_xml_as_string = dom.toprettyxml(indent="  ")

    # Remove extra blank lines
    pretty_xml_as_string = re.sub(r'\n\s*\n', '\n', pretty_xml_as_string)

    # Write the cleaned and pretty-printed XML back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(pretty_xml_as_string)


def save_pretty_xml(tree, xml_file_path):
    # Pretty-print the XML with proper formatting
    rough_string = ET.tostring(tree.getroot(), 'utf-8')
    reparsed = minidom.parseString(rough_string)

    # Custom cleanup to remove excessive whitespace
    pretty_xml = "\n".join([line for line in reparsed.toprettyxml(indent="    ").splitlines() if line.strip()])

    with open(xml_file_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    print(f"Pretty XML file saved to {xml_file_path}")