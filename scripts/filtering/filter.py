"""
Word meaning filtering from XML by lemma and sense.
"""


def filter_wm(xml_root):
    word_meanings = []
    for word_meaning in xml_root.findall(".//WORD_MEANING"):
        lemma_variants = word_meaning.find("VARIANTS")
        lemmas = [literal.get("LEMMA") for literal in lemma_variants.findall("LITERAL") if literal.get("LEMMA")]
        senses = [literal.get("SENSE") for literal in lemma_variants.findall("LITERAL") if literal.get("SENSE")]
        first_literal = lemma_variants.find("LITERAL")
        first_literal_lemma = first_literal.get("LEMMA") if first_literal is not None else "No Literal Lemma"
        first_literal_sense = first_literal.get("SENSE") if first_literal is not None else "No Sense"

        word_meanings.append({
            "id": word_meaning.get("ID"),
            "lemmas": lemmas,
            "senses": senses,
            "first_literal_lemma": first_literal_lemma,
            "first_literal_sense": first_literal_sense,
            "original_element": word_meaning
        })

    return word_meanings