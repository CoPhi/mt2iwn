"""
XML cleanup utilities — IDs, duplicate relations, sorting, and EQ_LINKS.
"""


def clean_target_wm_id(target_wm):
    """Remove any prefix (e.g., 'V#') from the ID of a TARGET_WM element."""
    clean_id = target_wm.get('ID').split('#')[-1]
    target_wm.set('ID', clean_id)


def remove_duplicate_relations(iwn_root):
    """
    Remove duplicate relations within each WORD_MEANING in the XML.
    """
    for word_meaning in iwn_root.findall('.//WORD_MEANING'):
        internal_links = word_meaning.find('.//INTERNAL_LINKS')
        if internal_links is not None:
            # Use a set to track unique relation signatures
            seen_relations = set()
            relations_to_remove = []

            for relation in internal_links.findall('.//RELATION'):
                # Create a unique identifier for each relation based on its type, target WM ID, and sense
                relation_signature = (
                    relation.get('TYPE'),
                    relation.find('.//TARGET_WM').get('ID'),
                    relation.find('.//TARGET_WM').get('SENSE')
                )

                # If this signature has already been seen, mark the relation for removal
                if relation_signature in seen_relations:
                    relations_to_remove.append(relation)
                else:
                    seen_relations.add(relation_signature)

            # Remove the duplicates
            for relation in relations_to_remove:
                internal_links.remove(relation)


def clean_existing_target_wm_ids(root):
    """Clean the IDs of all TARGET_WM elements in the provided root."""
    for target_wm in root.findall('.//TARGET_WM'):
        clean_target_wm_id(target_wm)


def clean_and_move_eq_links_at_end(iwn_root):
    """
    This function ensures that any 'eq_*' relations that ended up in INTERNAL_LINKS
    are moved to the EQ_LINKS section, if applicable.
    It also sorts the relations first by ID and then alphabetically by lemma.
    """
    for word_meaning in iwn_root.findall('.//WORD_MEANING'):
        internal_links = word_meaning.find('.//INTERNAL_LINKS')
        eq_links_section = word_meaning.find('.//EQ_LINKS')

        # Updated line to avoid DeprecationWarning
        if internal_links is not None and eq_links_section is not None:
            # Collect any eq_* relations
            eq_relations_to_move = [rel for rel in internal_links.findall('.//RELATION') if rel.get('TYPE', '').startswith('eq_')]

            # Move them to EQ_LINKS
            for rel in eq_relations_to_move:
                internal_links.remove(rel)
                eq_links_section.append(rel)

        # Updated line to avoid DeprecationWarning
        if internal_links is not None:
            relations = sorted(
                internal_links.findall('.//RELATION'),
                key=lambda r: (
                    int(r.get('ID')) if r.get('ID', '').isdigit() else float('inf'),
                    r.find('.//TARGET_WM').get('LEMMA', '').lower()
                )
            )

            # Clear existing relations and re-append sorted relations
            for rel in internal_links.findall('.//RELATION'):
                internal_links.remove(rel)
            for rel in relations:
                internal_links.append(rel)

        # Updated line to avoid DeprecationWarning
        if eq_links_section is not None:
            eq_relations = sorted(
                eq_links_section.findall('.//RELATION'),
                key=lambda r: (
                    int(r.get('ID')) if r.get('ID', '').isdigit() else float('inf'),
                    r.find('.//TARGET_WM').get('LEMMA', '').lower()
                )
            )

            # Clear existing relations and re-append sorted relations
            for rel in eq_links_section.findall('.//RELATION'):
                eq_links_section.remove(rel)
            for rel in eq_relations:
                eq_links_section.append(rel)


def sort_word_meanings_by_lemma_and_sense(root):
    word_meanings = sorted(root.findall('.//WORD_MEANING'), key=lambda wm: (wm.find('.//LITERAL').get('LEMMA').lower(), wm.find('.//LITERAL').get('SENSE')))
    for word in word_meanings:
        root.remove(word)
    for word in word_meanings:
        root.append(word)