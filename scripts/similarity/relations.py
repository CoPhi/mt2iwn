"""
Weighted semantic relation similarity calculation.
"""

from .gloss import calculate_gloss_similarity


def calculate_relation_similarity(wn_g_sim, relations1, relations2):
    weights = {
        "has_hyperonym": 0.82,
        "has_hyponym": 0.76,
        "near_synonym": 0.6,
        "has_xpos_hyperonym": 0.5,
        "has_xpos_hyponym": 0.5,
        "xpos_near_synonym": 0.5
    }

    relation_weights = {}
    total_weighted_similarity = 0
    bonus = 0
    malus = 0
    bonus_relations = []
    malus_count = 0
    missing_relations_details = []
    no_gloss_relations = []
    no_gloss_words = []

    relations1_dict = {(r["relation_type"], r["target_lemma"]): r["target_gloss"] for r in relations1}
    relations2_dict = {(r["relation_type"], r["target_lemma"]): r["target_gloss"] for r in relations2}

    for key, mari_gloss in relations1_dict.items():
        if key in relations2_dict:
            ital_gloss = relations2_dict[key]

            if (mari_gloss != "No Gloss" and ital_gloss == "No Gloss") or (mari_gloss == "No Gloss" and ital_gloss != "No Gloss"):
                gloss_similarity = 0.5
            else:
                gloss_similarity = calculate_gloss_similarity(mari_gloss, ital_gloss)

            weight = weights.get(key[0], 0)
            weighted_similarity = gloss_similarity * weight

            relation_weights[key] = (weighted_similarity, gloss_similarity, weight)
            total_weighted_similarity += weighted_similarity

            if (mari_gloss != "No Gloss" and ital_gloss != "No Gloss") or (mari_gloss == "No Gloss" and ital_gloss == "No Gloss"):
                bonus += 0.33
                bonus_relations.append(key[1])
            elif mari_gloss != "No Gloss" and ital_gloss == "No Gloss":
                malus -= 0.33
                no_gloss_relations.append(key[1])
                no_gloss_words.append(mari_gloss)
        else:
            malus -= 0.33
            missing_relations_details.append(key[1])

    total_similarity = wn_g_sim + total_weighted_similarity + bonus + malus
    malus_count = len(no_gloss_relations)

    return total_weighted_similarity, relation_weights, bonus, malus, malus_count, missing_relations_details, no_gloss_relations, no_gloss_words, total_similarity, bonus_relations