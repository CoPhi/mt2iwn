"""
Plugin link cleanup — duplicate removal and relation sorting.
"""


def remove_duplicate_plugins(iwn_root):
    for wm in iwn_root.findall('.//WORD_MEANING'):
        plugin_links = wm.find('.//PLUG-IN_LINKS')
        if plugin_links is not None:
            # Use a set to track unique relations
            unique_relations = set()
            relations_to_remove = []

            for relation in plugin_links.findall('.//RELATION'):
                rel_type = relation.get('TYPE')
                rel_id = relation.get('ID')
                target_wm = relation.find('.//TARGET_WM').get('ID')

                # Normalize the TARGET_WM ID by replacing spaces with underscores
                normalized_target_wm = target_wm.replace(' ', '_')

                # Create a tuple that uniquely identifies a relation (normalize target_wm)
                relation_key = (rel_type, rel_id, normalized_target_wm)

                if relation_key in unique_relations:
                    # Mark the relation for removal if it's a duplicate
                    relations_to_remove.append(relation)
                else:
                    # Add the normalized relation key to the set
                    unique_relations.add(relation_key)

            # Remove all duplicate relations
            for relation in relations_to_remove:
                plugin_links.remove(relation)

            if relations_to_remove:
                print(f"Removed {len(relations_to_remove)} duplicate relations for Lemma={wm.find('.//LITERAL').get('LEMMA')}, Sense={wm.find('.//LITERAL').get('SENSE')}")


def sort_plugin_links(plugin_links):
    # Extract relations
    relations = plugin_links.findall('.//RELATION')

    # Sort relations by ID (numerically) and then by the TARGET_WM attribute (alphabetically)
    relations.sort(key=lambda r: (int(r.get('ID')), r.find('.//TARGET_WM').get('ID')))

    # Clear existing RELATION elements and re-add them in the sorted order
    for rel in plugin_links.findall('.//RELATION'):
        plugin_links.remove(rel)

    for rel in relations:
        plugin_links.append(rel)