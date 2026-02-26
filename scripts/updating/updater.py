"""
Main IWN update orchestration: entry creation, gloss replacement, redundancy removal.
"""

import xml.etree.ElementTree as ET

from scripts.config import Config
from .retriever import (
    retrieve_wm,
    extract_target_ids,
    get_gloss_from_italwn,
    retrieve_relation_ids,
)
from .creator import (
    create_or_merge_word_meaning,
    extract_eq_links_and_top_onto,
    determine_inverse_relation,
)
from .cleaner import (
    clean_and_move_eq_links_at_end,
    sort_word_meanings_by_lemma_and_sense,
    clean_existing_target_wm_ids,
)
import scripts.updating as state  # shared mutable state


def remove_redundant_word_meanings(iwn_root):
    for replacement in state.replaced_glosses:
        for word_meaning in iwn_root.findall('.//WORD_MEANING'):
            literal = word_meaning.find('.//LITERAL')
            gloss_element = word_meaning.find('.//GLOSS')
            if literal is not None and gloss_element is not None:
                if literal.get('LEMMA') == replacement['lemma'] and gloss_element.text.strip() == replacement['original_gloss']:
                    iwn_root.remove(word_meaning)
                    print(f"Removed redundant word meaning for {replacement['lemma']} with replaced gloss: '{replacement['original_gloss']}'")


def replace_gloss_with_original(iwn_root, original_iwn_root, updated_entries):
    replaced_glosses_set = set()

    for iwn_wm in iwn_root.findall('.//WORD_MEANING'):
        lemma = iwn_wm.find('.//LITERAL').get('LEMMA')
        sense = iwn_wm.find('.//LITERAL').get('SENSE')
        pos = iwn_wm.get('PART_OF_SPEECH')

        if (lemma, sense) in updated_entries:
            continue  # Skip this entry if it has already been updated

        original_gloss = get_gloss_from_italwn(lemma, sense, original_iwn_root, pos)

        if original_gloss:
            iwn_gloss_element = iwn_wm.find('.//GLOSS')
            current_gloss = iwn_gloss_element.text.strip() if iwn_gloss_element is not None and iwn_gloss_element.text else None
            if current_gloss != original_gloss:
                if iwn_gloss_element is not None:
                    iwn_gloss_element.text = original_gloss
                else:
                    iwn_gloss_element = ET.SubElement(iwn_wm, 'GLOSS')
                    iwn_gloss_element.text = original_gloss

                # Print the replacement message only if it hasn't been printed for this lemma-sense-pos combination
                if (lemma, sense, pos) not in replaced_glosses_set:
                    print(f"Replaced WORD_MEANING gloss for '{lemma}' sense '{sense}' with original IWN gloss.")
                    replaced_glosses_set.add((lemma, sense, pos))

            # Replace glosses in TARGET_WM elements
            for target_wm in iwn_root.findall(f'.//TARGET_WM[@LEMMA="{lemma}"][@SENSE="{sense}"][@PART_OF_SPEECH="{pos}"]'):
                target_gloss = target_wm.get('GLOSS')
                if target_gloss != original_gloss:
                    target_wm.set('GLOSS', original_gloss)

                    # Print the replacement message only if it hasn't been printed for this lemma-sense-pos combination
                    if (lemma, sense, pos) not in replaced_glosses_set:
                        print(f"Replaced TARGET_WM gloss for '{lemma}' sense '{sense}' with original IWN gloss.")
                        replaced_glosses_set.add((lemma, sense, pos))


def update_iwn_entries(selected_lemmas, mari_root, iwn_root, original_mari_root, original_iwn_root):
    mari_meanings = retrieve_wm(mari_root)
    original_target_ids = extract_target_ids(original_iwn_root)
    mari_eq_links, mari_top_onto = extract_eq_links_and_top_onto(original_mari_root)
    existing_ids = {word.get('ID') for word in iwn_root.findall('.//WORD_MEANING')}
    relation_ids = retrieve_relation_ids(iwn_root)

    relations_added = 0
    word_meanings_created = 0
    lemmas_processed = 0

    def retrieve_or_generate_gloss(target_lemma, target_sense, main_gloss=None):
        italwn_gloss = get_gloss_from_italwn(target_lemma, target_sense, iwn_root)
        mariterm_gloss = get_gloss_from_relation_in_mariterm(target_lemma, target_sense, mari_meanings)
        italwn_gloss_original = None

        if not italwn_gloss and not mariterm_gloss:
            italwn_gloss_original = get_gloss_from_italwn(target_lemma, target_sense, original_iwn_root)
            if italwn_gloss_original:
                print(f"Special case: Found gloss for '{target_lemma}' sense '{target_sense}' in original IWN.")
                return italwn_gloss_original

        if mariterm_gloss and italwn_gloss and mariterm_gloss != italwn_gloss:
            state.replaced_glosses.append({"lemma": target_lemma, "sense": target_sense, "original_gloss": mariterm_gloss})
            print(f"Replacing gloss for '{target_lemma}' (sense {target_sense}). Original: '{mariterm_gloss}', New: '{italwn_gloss}'")

        return italwn_gloss if italwn_gloss else mariterm_gloss

    def get_gloss_from_relation_in_mariterm(target_lemma, target_sense, mari_meanings):
        for mari_word in mari_meanings.values():
            for rel in mari_word.findall('.//INTERNAL_LINKS//RELATION'):
                target_wm = rel.find('.//TARGET_WM')
                if target_wm is not None and target_wm.get('LEMMA') == target_lemma and target_wm.get('SENSE') == target_sense:
                    return target_wm.get('GLOSS', '').strip()
        return ""

    for entry in selected_lemmas:
        lemma, mari_sense, iwn_sense = entry['literal_lemma'], entry['mari_t_sense'], entry['iwn_sense']
        lemmas_processed += 1

        mari_word = mari_meanings.get((lemma, mari_sense))
        if mari_word is None:
            print(f"Skipped: MariTerm sense {mari_sense} for {lemma} not found in MariTerm filtered.")
            continue  # Skip to the next iteration if mari_word is None

        mari_gloss_element = mari_word.find('.//GLOSS')
        mari_gloss = mari_gloss_element.text.strip() if mari_gloss_element is not None and mari_gloss_element.text else ''

        if any(r['lemma'] == lemma and r['sense'] == mari_sense and r['original_gloss'] == mari_gloss for r in state.replaced_glosses):
            print(f"Skipping redundant creation for lemma '{lemma}' with sense '{mari_sense}' and gloss '{mari_gloss}'")
            continue

        word_meaning, _ = create_or_merge_word_meaning(
            lemma, iwn_sense, existing_ids, mari_eq_links, mari_top_onto, iwn_root, [], relation_ids,
            gloss=retrieve_or_generate_gloss(lemma, iwn_sense, mari_gloss),
            original_iwn_root=original_iwn_root
        )
        word_meanings_created += 1 if word_meaning is not None else 0

        for rel in mari_word.findall('.//INTERNAL_LINKS//RELATION'):
            rel_type = rel.get('TYPE')
            if rel_type not in Config.ALLOWED_RELATION_TYPES:
                continue

            target_lemma = rel.find('.//TARGET_WM').get('LEMMA', '')
            target_sense = rel.find('.//TARGET_WM').get('SENSE')
            target_gloss = retrieve_or_generate_gloss(target_lemma, target_sense, mari_gloss)

            target_id = original_target_ids.get((target_lemma, target_sense))
            if not target_id:
                back_references = [{
                    "id": word_meaning.get('ID'),
                    "inv_id": relation_ids[rel_type]['INV_ID'],
                    "part_of_speech": word_meaning.get('PART_OF_SPEECH'),
                    "lemma": lemma,
                    "sense": iwn_sense,
                    "gloss": mari_gloss,
                    "inverse_relation": determine_inverse_relation(rel_type)
                }]
                new_wm, target_id = create_or_merge_word_meaning(
                    target_lemma, target_sense, existing_ids, mari_eq_links, mari_top_onto, iwn_root, back_references, relation_ids,
                    original_iwn_root=original_iwn_root
                )
                word_meanings_created += 1 if new_wm is not None else 0

            if rel_type in relation_ids:
                new_rel = ET.SubElement(word_meaning.find('.//INTERNAL_LINKS'), 'RELATION', TYPE=rel_type, ID=relation_ids[rel_type]['ID'], INV_ID=relation_ids[rel_type]['INV_ID'])
                new_target_wm = ET.SubElement(new_rel, 'TARGET_WM', ID=target_id.replace(f"{word_meaning.get('PART_OF_SPEECH')}#", ""), PART_OF_SPEECH=rel.find('.//TARGET_WM').get('PART_OF_SPEECH'), LEMMA=target_lemma, SENSE=target_sense)
                if target_gloss:
                    new_target_wm.set('GLOSS', target_gloss)
                relations_added += 1

    clean_and_move_eq_links_at_end(iwn_root)
    remove_redundant_word_meanings(iwn_root)
    sort_word_meanings_by_lemma_and_sense(iwn_root)
    replace_gloss_with_original(iwn_root, original_iwn_root, state.updated_entries)

    total_word_meanings = len(iwn_root.findall('.//WORD_MEANING'))
    print(f"Total relations added: {relations_added}")
    print(f"New Word Meanings Created: {state.new_word_meanings}")
    print(f"Total brand new WM: {len(state.new_word_meanings)}")
    print(f"Total word meanings in the file: {total_word_meanings}")