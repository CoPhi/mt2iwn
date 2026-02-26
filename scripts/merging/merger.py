"""
IWN file merger — combines original IWN with updated entries.
"""

import xml.etree.ElementTree as ET
from .formatter import format_xml_with_indentation


def merge_and_format_iwn_files(ItalWN, updates, IWN_pre_mod):
    # Parse the original unfiltered IWN and the final output files
    tree_original = ET.parse(ItalWN)
    root_original = tree_original.getroot()

    tree_output = ET.parse(updates)
    root_output = tree_output.getroot()

    # Create a dictionary to store word meanings from the final output file by (lemma, sense)
    output_wm_dict = {}
    for word_meaning in root_output.findall('.//WORD_MEANING'):
        lemma = word_meaning.find('.//LITERAL').get('LEMMA')
        sense = word_meaning.find('.//LITERAL').get('SENSE')
        output_wm_dict[(lemma, sense)] = word_meaning

    # Merge the original IWN with the final output, replacing old entries with new ones
    merged_wm_list = []
    for word_meaning in root_original.findall('.//WORD_MEANING'):
        lemma = word_meaning.find('.//LITERAL').get('LEMMA')
        sense = word_meaning.find('.//LITERAL').get('SENSE')

        # If there's an updated version in the output file, use that one
        if (lemma, sense) in output_wm_dict:
            merged_wm_list.append(output_wm_dict.pop((lemma, sense)))
        else:
            merged_wm_list.append(word_meaning)

    # Add any remaining new word meanings from the final output file
    merged_wm_list.extend(output_wm_dict.values())

    # Sort the word meanings alphabetically by the first LITERAL LEMMA
    merged_wm_list.sort(key=lambda wm: (wm.find('.//LITERAL').get('LEMMA').lower(), wm.find('.//LITERAL').get('SENSE')))

    # Create a new XML tree for the merged content
    new_root = ET.Element(root_original.tag)

    for word_meaning in merged_wm_list:
        new_root.append(word_meaning)

    # Write the merged and formatted XML to a new file
    tree_merged = ET.ElementTree(new_root)
    tree_merged.write(IWN_pre_mod, encoding='utf-8', xml_declaration=True)

    # Format the XML with indentation
    format_xml_with_indentation(IWN_pre_mod)

    print(f"Merged IWN file created and saved as '{IWN_pre_mod}'")