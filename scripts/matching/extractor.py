"""
Word meaning extraction from MariTerm and ItalWordNet XML files.
"""

from scripts.similarity import normalize_lemma, normalize_text
from scripts.config import Config


def extract_word_meanings(xml_root):
    word_meanings = []
    for word_meaning in xml_root.findall(".//WORD_MEANING"):
        lemma_variants = word_meaning.find("VARIANTS")
        lemmas = [literal.get("LEMMA") for literal in lemma_variants.findall("LITERAL") if literal.get("LEMMA")]
        normalized_lemmas = [normalize_lemma(lemma) for lemma in lemmas]

        senses = [literal.get("SENSE") for literal in lemma_variants.findall("LITERAL") if literal.get("SENSE")]
        normalized_senses = [normalize_text(sense) for sense in senses]

        gloss = word_meaning.find("GLOSS").text or ""
        normalized_gloss = normalize_text(gloss)

        relations = []
        for relation in word_meaning.findall(".//INTERNAL_LINKS/RELATION"):
            target_wm = relation.find("TARGET_WM")
            if target_wm is not None:
                target_id = target_wm.get("ID")
                target_lemma = target_wm.get("LEMMA")
                normalized_target_lemma = normalize_lemma(target_lemma)

                target_gloss = target_wm.get("GLOSS", "No Gloss")
                normalized_target_gloss = normalize_text(target_gloss)

                relation_type = relation.get("TYPE")
                if relation_type in Config.ALLOWED_RELATION_TYPES:
                    relations.append({
                        "relation_type": relation_type,
                        "target_id": target_id,
                        "target_lemma": target_lemma,
                        "normalized_target_lemma": normalized_target_lemma,
                        "target_gloss": target_gloss,
                        "normalized_target_gloss": normalized_target_gloss
                    })

        first_literal = lemma_variants.find("LITERAL")
        first_literal_lemma = first_literal.get("LEMMA") if first_literal is not None else "No Literal Lemma"
        normalized_first_literal_lemma = normalize_lemma(first_literal_lemma)

        first_literal_sense = first_literal.get("SENSE") if first_literal is not None else "No Sense"
        normalized_first_literal_sense = normalize_text(first_literal_sense)

        word_meanings.append({
            "id": word_meaning.get("ID"),
            "lemmas": lemmas,
            "normalized_lemmas": normalized_lemmas,
            "senses": senses,
            "normalized_senses": normalized_senses,
            "gloss": gloss,
            "normalized_gloss": normalized_gloss,
            "relations": relations,
            "first_literal_lemma": first_literal_lemma,
            "normalized_first_literal_lemma": normalized_first_literal_lemma,
            "first_literal_sense": first_literal_sense,
            "normalized_first_literal_sense": normalized_first_literal_sense,
            "part_of_speech": word_meaning.get("PART_OF_SPEECH")
        })
    return word_meanings