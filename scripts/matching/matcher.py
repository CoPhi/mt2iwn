"""
Candidate matching logic with alternate sense handling and similarity thresholds.
"""

from scripts.similarity import (
    calculate_gloss_similarity,
    calculate_relation_similarity,
    format_relations,
    get_fallback_gloss,
)


def match_lemmas_with_alternate_senses(mari_term_wms, ital_wn_wms):
    results = []
    best_matches_per_ital_wn = {}
    seen_pairs = set()

    if not mari_term_wms or not ital_wn_wms:
        return results

    for wm1 in mari_term_wms:
        best_match = None
        best_gloss_similarity = -1
        best_total_weighted_relation_similarity = -1
        best_total_similarity = -1

        for wm2 in ital_wn_wms:
            if wm1.get("normalized_first_literal_lemma") == wm2.get("normalized_first_literal_lemma") and wm1.get("part_of_speech") == wm2.get("part_of_speech"):
                mari_gloss = wm1.get("normalized_gloss", "")
                ital_gloss = wm2.get("normalized_gloss", "")

                # Handle Mariterm fallback gloss
                if not mari_gloss.strip():
                    mari_gloss, mari_fallback_type = get_fallback_gloss(wm1, 'near_synonym')
                    fallback_used = True
                else:
                    mari_fallback_type = None
                    fallback_used = False

                # Handle ItalWN fallback gloss
                if not ital_gloss.strip():
                    ital_gloss, ital_fallback_type = get_fallback_gloss(wm2, 'near_synonym')
                    ital_fallback_used = True
                    if ital_gloss == 'No Gloss':
                        ital_gloss = ''  # Compare against an empty string instead of "No Gloss"
                else:
                    ital_fallback_type = None
                    ital_fallback_used = False

                wn_g_sim = calculate_gloss_similarity(mari_gloss, ital_gloss)

                if mari_fallback_type:
                    if mari_fallback_type == 'has_hyponym':
                        wn_g_sim -= 0.05
                    elif mari_fallback_type == 'has_hyperonym':
                        wn_g_sim -= 0.10

                if ital_fallback_used:
                    if ital_fallback_type == 'has_hyponym':
                        wn_g_sim -= 0.10
                    elif ital_fallback_type == 'has_hyperonym':
                        wn_g_sim -= 0.10

                total_weighted_similarity, relation_weights, bonus, malus, malus_count, missing_relations, no_gloss_relations, no_gloss_words, total_similarity, bonus_relations = calculate_relation_similarity(
                    wn_g_sim, wm1.get("relations", []), wm2.get("relations", [])
                )

                current_match = {
                    "Literal Lemma": wm1.get("first_literal_lemma", ""),
                    "MariT sense": wm1.get("first_literal_sense", ""),
                    "IWN sense": wm2.get("first_literal_sense", ""),
                    "Gloss S. (WM)": wn_g_sim,
                    "Total S.": total_similarity,
                    "T. Relation S.": total_weighted_similarity,
                    "Mariterm ID": wm1.get("id", ""),
                    "ItalWN ID": wm2.get("id", ""),
                    "Mariterm Gloss": mari_gloss if not fallback_used else f"[FALLBACK] {get_fallback_gloss(wm1, 'near_synonym')[0]}",
                    "ItalWN Gloss": ital_gloss if not ital_fallback_used else f"[FALLBACK] {get_fallback_gloss(wm2, 'near_synonym')[0]}",
                    "MariTerm Relations": format_relations(wm1.get("relations", []), relation_weights),
                    "ItalWN Relations": format_relations(wm2.get("relations", []), relation_weights),
                    "bonus": bonus,
                    "malus": malus,
                    "missing_relations": missing_relations,
                    "no_gloss_relations": no_gloss_relations,
                    "bonus_relations": bonus_relations,
                }

                # Track the best match across all possible pairs for this ItalWN entry
                if wn_g_sim > best_gloss_similarity or \
                   (wn_g_sim == best_gloss_similarity and total_weighted_similarity > best_total_weighted_relation_similarity) or \
                   (wn_g_sim == best_gloss_similarity and total_weighted_similarity == best_total_weighted_relation_similarity and total_similarity > best_total_similarity) or \
                   (wn_g_sim == best_gloss_similarity and total_weighted_similarity == best_total_weighted_relation_similarity and total_similarity == best_total_similarity):

                    best_gloss_similarity = wn_g_sim
                    best_total_weighted_relation_similarity = total_weighted_similarity
                    best_total_similarity = total_similarity
                    best_match = current_match

        # Apply the matching criteria based on thresholds
        if best_match:
            ital_wn_id = best_match.get('ItalWN ID')
            if best_match['Gloss S. (WM)'] >= 0.43 or best_match['T. Relation S.'] > 0:
                best_matches_per_ital_wn[ital_wn_id] = best_match
            elif best_match['Gloss S. (WM)'] >= 0.13 and (best_match['Gloss S. (WM)'] < 0.43 or best_match['T. Relation S.'] > 0):
                best_matches_per_ital_wn[ital_wn_id] = best_match
            elif best_match['T. Relation S.'] > 0.09 or (0.14 <= best_match['Gloss S. (WM)'] < 0.19) or (0.24 <= best_match['Gloss S. (WM)'] < 0.29) or best_match['Gloss S. (WM)'] >= 0.44:
                best_matches_per_ital_wn[ital_wn_id] = best_match

    results = [(match, []) for match in best_matches_per_ital_wn.values()]

    return results