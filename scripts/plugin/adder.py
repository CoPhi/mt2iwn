"""
Plugin link addition: populates PLUG-IN_LINKS in ItalWordNet synsets
pointing to their corresponding MariTerm entries.
"""

import csv
import xml.etree.ElementTree as ET

from scripts.config import Config


def load_csv_data(csv_file_path):
    reference = {}
    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            iwn_lemma = row['Literal Lemma']
            iwn_sense = row.get('IWN sense', 'N/A')
            mari_lemma = row['Literal Lemma']
            mari_sense = row.get('MariT sense', 'N/A')
            reference[(iwn_lemma, iwn_sense)] = (mari_lemma, mari_sense)
    return reference


def find_mariterm_synset(root, lemma, sense):
    """Utility function to find a MariTerm synset by lemma and sense."""
    for wm in root.findall('.//WORD_MEANING'):
        literal = wm.find('.//LITERAL')
        if literal is not None and literal.get('LEMMA') == lemma and literal.get('SENSE') == sense:
            return wm
    return None


def insert_after(parent, new_element, after_element):
    """Inserts new_element in parent right after after_element."""
    found = False
    for i, elem in enumerate(parent):
        if elem == after_element:
            found = True
            parent.insert(i + 1, new_element)
            break
    if not found:
        parent.append(new_element)


def ensure_plugin_links(wm):
    """Ensure the <PLUG-IN_LINKS/> tag is present for synsets that don't have it."""
    plugin_links = wm.find('.//PLUG-IN_LINKS')
    if plugin_links is None:
        internal_links = wm.find('.//INTERNAL_LINKS')
        empty_plugin_links = ET.Element('PLUG-IN_LINKS')
        if internal_links is not None:
            insert_after(wm, empty_plugin_links, internal_links)
        else:
            wm.append(empty_plugin_links)
        print(f"Added empty PLUG-IN_LINKS for Lemma={wm.find('.//LITERAL').get('LEMMA')}, Sense={wm.find('.//LITERAL').get('SENSE')}")


def add_plugins(iwn_root, mariterm_filtered_root, mariterm_original_root, reference, newly_added_relations_info):
    relation_type_mapping = {
        "plug-synonym": "1",
        "plug-near_synonym": "2",
        "plug-xpos_near_synonym": "2",
        "plug-has_hyperonym": "3",
        "plug-has_xpos_hyperonym": "3",
        "plug-has_hyponym": "4",
        "plug-has_xpos_hyponym": "4",
    }

    iwn_synsets_with_plugins = {}
    target_mariterm_id = None
    synset_relations_storage = []

    for wm in iwn_root.findall('.//WORD_MEANING'):
        lemma_element = wm.find('.//LITERAL')
        lemma = lemma_element.get('LEMMA') if lemma_element is not None else None
        sense = lemma_element.get('SENSE') if lemma_element is not None else None

        if not lemma or not sense:
            continue

        mari_synset = reference.get((lemma, sense))
        if not mari_synset:
            ensure_plugin_links(wm)
            continue

        mari_lemma, mari_sense = mari_synset
        mariterm_synset = find_mariterm_synset(mariterm_filtered_root, mari_lemma, mari_sense)
        if mariterm_synset is None:
            mariterm_synset = find_mariterm_synset(mariterm_original_root, mari_lemma, mari_sense)
        if mariterm_synset is not None:
            mariterm_id = mariterm_synset.get('ID')
            literals = [lit.get('LEMMA') for lit in mariterm_synset.findall('.//LITERAL')]
            literals_str = ','.join(literals)

            plugin_links = wm.find('.//PLUG-IN_LINKS')
            if plugin_links is None:
                plugin_links = ET.Element('PLUG-IN_LINKS')
                internal_links = wm.find('.//INTERNAL_LINKS')
                if internal_links is not None:
                    insert_after(wm, plugin_links, internal_links)
                else:
                    wm.append(plugin_links)
            # Track the synsets with plugin links
            iwn_id = wm.get('ID')  # Get ID from WORD_MEANING
            first_literal_lemma = lemma  # Assuming lemma is defined earlier
            iwn_synsets_with_plugins[iwn_id] = first_literal_lemma


            if not any(rel['RELATION_TYPE'] == 'plug-synonym' and rel['TARGET_WM_ID'] == f"{mariterm_id}#{literals_str}"
                    for entry in synset_relations_storage if entry['WORD_MEANING_ID'] == mariterm_id
                    for rel in entry['RELATIONS']):
                # Proceed with adding plug-synonym only if it doesn't already exist
                plug_synonym = ET.SubElement(plugin_links, 'RELATION', TYPE="plug-synonym", ID="1", INV_ID="1")
                ET.SubElement(plug_synonym, 'TARGET_WM', ID=f"{mariterm_id}#{literals_str}")
                print(f"Added PLUG-IN LINK with target {mariterm_id}#{literals_str} for Lemma={lemma}, Sense={sense}.")

                # Create the plug-synonym entry to add to synset_relations_storage
                plug_synonym_entry = {
                    'RELATION_TYPE': 'plug-synonym',
                    'ID': '1',
                    'PART_OF_SPEECH': mariterm_synset.get('PART_OF_SPEECH'),
                    'TARGET_WM_ID': f"{mariterm_id}#{literals_str}",
                    'TARGET_WM_LEMMA': lemma,
                    'LITERALS': [lemma]  # Store the literal as a list
                }

                # Check if there's already an entry for the WORD_MEANING_ID in synset_relations_storage
                existing_entry = next((entry for entry in synset_relations_storage if entry['WORD_MEANING_ID'] == mariterm_id), None)

                if existing_entry:
                    # Check if the relation already exists
                    if not any(rel['RELATION_TYPE'] == 'plug-synonym' and rel['TARGET_WM_ID'] == plug_synonym_entry['TARGET_WM_ID'] for rel in existing_entry['RELATIONS']):
                        existing_entry['RELATIONS'].append(plug_synonym_entry)
                else:
                    synset_relations_storage.append({
                        'WORD_MEANING_ID': mariterm_id,
                        'FIRST LITERAL': lemma,
                        'RELATIONS': [plug_synonym_entry]  # New entry for new relations
                    })

            # Process only the relevant relations for this synset
            for relation_info in newly_added_relations_info:
                rel_type, target_lemma, target_sense, src_lemma, src_sense, target_id, synset_id = relation_info

                if src_lemma == lemma and src_sense == sense:
                    print(f"Processing new relation: Type={rel_type}, Target Lemma={target_lemma}, Target Sense={target_sense}")

                    if rel_type in Config.ALLOWED_RELATION_TYPES:
                        print(f"Relation type {rel_type} is eligible for plug-in.")

                        mari_rel_synset = find_mariterm_synset(mariterm_filtered_root, target_lemma, target_sense)
                        if mari_rel_synset is None:
                            print(f"Target Lemma={target_lemma}, Sense={target_sense} not found in filtered MariTerm. Checking original MariTerm.")
                            mari_rel_synset = find_mariterm_synset(mariterm_original_root, target_lemma, target_sense)

                        if mari_rel_synset is not None:
                            part_of_speech = mari_rel_synset.get('PART_OF_SPEECH')
                            id_part = mari_rel_synset.get('ID')

                            if id_part.startswith(f"{part_of_speech}#"):
                                target_mariterm_id = id_part
                            else:
                                target_mariterm_id = f"{part_of_speech}#{id_part}"

                            word_meaning_synset = find_mariterm_synset(mariterm_original_root, target_mariterm_id.split('#')[1], target_sense)

                            if word_meaning_synset is not None:
                                literals = [lit.get('LEMMA') for lit in word_meaning_synset.findall('.//LITERAL')]
                                literals_str = ','.join(literals)
                                print(f"Retrieved literals: {literals_str}")
                            else:
                                literals_str = target_lemma
                                print(f"Fallback to using target lemma: {literals_str}")

                            plug_relation_type = f"plug-{rel_type}"
                            plug_relation_id = relation_type_mapping[plug_relation_type]
                            plug_relation = ET.SubElement(plugin_links, 'RELATION', TYPE=plug_relation_type, ID=plug_relation_id, INV_ID=plug_relation_id)

                            # Create a new entry for each relation type
                            relation_entry = {
                                'RELATION_TYPE': plug_relation_type,  # Updated to use the correct plug relation type
                                'ID': plug_relation_id,
                                'PART_OF_SPEECH': mariterm_synset.get('PART_OF_SPEECH'),
                                'TARGET_WM_ID': f"{mariterm_id}#{literals_str}",
                                'TARGET_WM_LEMMA': literals[0],
                                'LITERALS': literals
                            }

                            # Check if there's already an entry for the WORD_MEANING_ID in synset_relations_storage
                            existing_entry = next((entry for entry in synset_relations_storage if entry['WORD_MEANING_ID'] == mariterm_id), None)
                            if existing_entry:
                                existing_entry['RELATIONS'].append(relation_entry)
                            else:
                                synset_relations_storage.append({
                                    'WORD_MEANING_ID': mariterm_id,
                                    'FIRST LITERAL': first_literal_lemma,
                                    'RELATIONS': [relation_entry]  # New entry for new relations
                                })

                            if ' ' in literals_str:
                                literals_str = literals_str.replace(' ', '_')

                            ET.SubElement(plug_relation, 'TARGET_WM', ID=f"{target_mariterm_id}#{literals_str}")

                        else:
                            print(f"Target Lemma={target_lemma}, Sense={target_sense} not found in MariTerm.")
                    else:
                        print(f"Relation type {rel_type} is not eligible for plug-in.")

    return synset_relations_storage, iwn_synsets_with_plugins