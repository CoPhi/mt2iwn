"""
Candidate matching logic with alternate sense handling and similarity thresholds.
"""

from scripts.similarity import (
    calculate_gloss_similarity,
    calculate_relation_similarity,
    format_relations,
    get_fallback_gloss,
)


def match_lemmas_with_alternate_senses(mari_term_wms, ital_wn_wms,
                                       return_rejected=False):
    """
    Score and threshold-filter MariTerm / ItalWordNet candidate pairs.

    Parameters
    ----------
    mari_term_wms   : list[dict]  — word meanings from MariTerm XML
    ital_wn_wms     : list[dict]  — word meanings from ItalWordNet XML
    return_rejected : bool
        False (default) → returns only accepted results; all existing callers
        are completely unaffected.
        True → returns (results, rejected).

    Returns
    -------
    return_rejected=False  →  results                list of (dict, [])
    return_rejected=True   →  (results, rejected)    both lists of (dict, [])

    Rejected set
    ------------
    Keyed by ItalWN ID, mirroring best_matches_per_ital_wn exactly.
    Multiple MariTerm senses can compete for the same IWN sense; only the
    highest-scoring failed attempt per IWN ID is kept.  An IWN ID that was
    accepted by any MariTerm sense is excluded from rejected entirely.
    Result: each IWN sense appears in at most one of the two outputs.

    Threshold gates (unchanged)
    ---------------------------
    Gate A  Gloss S. >= 0.43  OR  T. Relation S. > 0
    Gate B  Gloss S. >= 0.13  AND  (Gloss S. < 0.43  OR  T. Relation S. > 0)
    Gate C  T. Relation S. > 0.09
            OR  0.14 <= Gloss S. < 0.19
            OR  0.24 <= Gloss S. < 0.29
            OR  Gloss S. >= 0.44
    """
    results = []
    best_matches_per_ital_wn = {}         # ItalWN ID → accepted match (unchanged)
    best_rejected_per_iwn_id: dict = {}   # ItalWN ID → best failed attempt

    seen_pairs = set()

    if not mari_term_wms or not ital_wn_wms:
        if return_rejected:
            return results, []
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
                        ital_gloss = ''
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

        # Apply the matching criteria based on thresholds (unchanged)
        if best_match:
            ital_wn_id = best_match.get('ItalWN ID')

            if best_match['Gloss S. (WM)'] >= 0.43 or best_match['T. Relation S.'] > 0:
                best_matches_per_ital_wn[ital_wn_id] = best_match
            elif best_match['Gloss S. (WM)'] >= 0.13 and (best_match['Gloss S. (WM)'] < 0.43 or best_match['T. Relation S.'] > 0):
                best_matches_per_ital_wn[ital_wn_id] = best_match
            elif best_match['T. Relation S.'] > 0.09 or (0.14 <= best_match['Gloss S. (WM)'] < 0.19) or (0.24 <= best_match['Gloss S. (WM)'] < 0.29) or best_match['Gloss S. (WM)'] >= 0.44:
                best_matches_per_ital_wn[ital_wn_id] = best_match
            else:
                # Failed all gates.
                # Keep the highest-scoring failed attempt for this IWN ID so
                # each IWN sense appears at most once in the rejected output,
                # matched to whichever MariTerm sense scored best against it.
                existing = best_rejected_per_iwn_id.get(ital_wn_id)
                if existing is None or best_match['Total S.'] > existing['Total S.']:
                    best_rejected_per_iwn_id[ital_wn_id] = best_match

    results = [(match, []) for match in best_matches_per_ital_wn.values()]

    if return_rejected:
        # Step 1: exclude IWN IDs that were accepted by any MariTerm sense.
        rejected_by_iwn = {
            iwn_id: match
            for iwn_id, match in best_rejected_per_iwn_id.items()
            if iwn_id not in best_matches_per_ital_wn
        }

        # Step 2: deduplicate by Literal Lemma.
        # A lemma with two failing MariTerm senses each pointing to a
        # different IWN ID produces two entries after Step 1 — one per
        # IWN ID — but should appear only once in the rejected output.
        # Keep the row with the highest Total S. (closest miss).
        best_per_lemma: dict[str, dict] = {}
        for match in rejected_by_iwn.values():
            lemma = match.get("Literal Lemma", "")
            existing = best_per_lemma.get(lemma)
            if existing is None or match["Total S."] > existing["Total S."]:
                best_per_lemma[lemma] = match

        rejected = [(match, []) for match in best_per_lemma.values()]
        return results, rejected

    return results