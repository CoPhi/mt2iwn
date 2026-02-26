"""
Plugin link updater — populates PLUG-IN_LINKS in MariTerm synsets
pointing back to their corresponding ItalWordNet entries.
"""

import xml.etree.ElementTree as ET


def insert_plugin_node(word_meaning, plugin_links_node):
    """
    Helper function to insert the PLUG-IN_LINKS node in the correct position.
    """
    inserted = False
    internal_links_node = word_meaning.find("INTERNAL_LINKS")
    eq_links_node = word_meaning.find("EQ_LINKS")

    # Insert after INTERNAL_LINKS if it exists
    if internal_links_node is not None:
        for i, child in enumerate(list(word_meaning)):
            if child is internal_links_node:
                word_meaning.insert(i + 1, plugin_links_node)
                inserted = True
                break

    # Otherwise, insert before EQ_LINKS if INTERNAL_LINKS is not found
    if not inserted and eq_links_node is not None:
        for i, child in enumerate(list(word_meaning)):
            if child is eq_links_node:
                word_meaning.insert(i, plugin_links_node)
                inserted = True
                break

    # If neither are found, just append the PLUG-IN_LINKS node at the end
    if not inserted:
        word_meaning.append(plugin_links_node)


def update_plugin_links(iwn_root, mariterm_root, synset_relations_storage, iwn_synsets_with_plugins, structured_relations):
    valid_wm_ids = {synset['WORD_MEANING_ID'] for synset in synset_relations_storage}

    for word_meaning in mariterm_root.findall(".//WORD_MEANING"):
        wm_id = word_meaning.get('ID')

        # Remove existing PLUG-IN_LINKS if present
        existing_plugin_links = word_meaning.findall("PLUG-IN_LINKS")
        for plugin in existing_plugin_links:
            word_meaning.remove(plugin)
            print(f"Removed existing PLUG-IN_LINKS node for WM ID {wm_id}")

        # Find corresponding synset from synset_relations_storage
        corresponding_synset = next((synset for synset in synset_relations_storage if synset['WORD_MEANING_ID'] == wm_id), None)

        if corresponding_synset:
            plugin_links_node = ET.Element("PLUG-IN_LINKS")
            added_relations = set()  # Track added relations to avoid duplicates
            first_literal_lemma = word_meaning.find('.//LITERAL').get('LEMMA')
            current_pos = word_meaning.get('PART_OF_SPEECH')

            # Iterate through all relations in the corresponding synset
            for relation in corresponding_synset['RELATIONS']:
                # Check if the current first literal matches the relation's target literal
                for iwn_id, literal in iwn_synsets_with_plugins.items():
                    if first_literal_lemma.lower() in literal.lower():
                        target_wm_id = f"{iwn_id}#{first_literal_lemma}"

                        # Fetch all literals associated with the ID
                        iwn_entry = iwn_root.find(f".//WORD_MEANING[@ID='{iwn_id}']")
                        if iwn_entry is not None:
                            additional_literals = [lit.get('LEMMA') for lit in iwn_entry.findall('.//LITERAL')]
                            all_literals = list(set([first_literal_lemma]))  # Avoid duplicates in literals

                            for lit in additional_literals:
                                if lit not in all_literals:
                                    all_literals.append(lit)

                            target_wm_id = f"{iwn_id}#" + ','.join(all_literals)

                        target_wm_pos = iwn_entry.get('PART_OF_SPEECH') if iwn_entry is not None else None

                        # Add the relation if it's valid and not already added
                        relation_type = relation.get('RELATION_TYPE', '')
                        if relation_type and target_wm_id not in added_relations and target_wm_id != "" and (target_wm_pos == current_pos):
                            # Ensure relation type is prefixed with 'plug-'
                            if not relation_type.startswith('plug-'):
                                relation_type = f"plug-{relation_type}"

                            # Add the relation to the PLUG-IN_LINKS node
                            relation_node = ET.SubElement(plugin_links_node, "RELATION", {
                                "TYPE": relation_type,
                                "ID": relation['ID'],
                                "INV_ID": relation['ID']
                            })
                            ET.SubElement(relation_node, "TARGET_WM", {"ID": target_wm_id})
                            added_relations.add(target_wm_id)
                            print(f"Added relation {relation['RELATION_TYPE']} for {first_literal_lemma} with ID {target_wm_id}")

            # Insert the PLUG-IN_LINKS node if relations were added
            if added_relations:
                insert_plugin_node(word_meaning, plugin_links_node)
            else:
                # If no relations were added, insert an empty PLUG-IN_LINKS node
                print(f"No relations found for WM ID {wm_id}. Creating an empty PLUG-IN_LINKS node.")
                empty_plugin_links_node = ET.Element("PLUG-IN_LINKS")
                insert_plugin_node(word_meaning, empty_plugin_links_node)

        else:
            # No corresponding synset found, create an empty PLUG-IN_LINKS node
            print(f"No corresponding synset found for WM ID {wm_id}. Creating an empty PLUG-IN_LINKS node.")
            empty_plugin_links_node = ET.Element("PLUG-IN_LINKS")
            insert_plugin_node(word_meaning, empty_plugin_links_node)