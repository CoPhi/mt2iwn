"""
Formatting and fallback gloss utilities for similarity scoring.
"""


def format_relations(relations, relation_weights, show_scores=True):
    formatted_relations = []
    seen_relations = set()

    for rel in relations:
        if isinstance(rel, dict):
            rel_type = rel["relation_type"]
            target_lemma = rel["target_lemma"]
            target_gloss = rel.get("target_gloss", "No Gloss")
            key = (rel_type, target_lemma)

            if key not in seen_relations:
                seen_relations.add(key)
                if key in relation_weights and show_scores:
                    weight_score, gloss_similarity, weight = relation_weights[key]
                    formatted_relations.append(f"{rel_type}, {target_lemma}, {target_gloss} "
                        f"(Score: [{gloss_similarity:.2f}] * [{weight:.2f}] = {weight_score:.2f})")
                else:
                    formatted_relations.append(f"{rel_type}, {target_lemma}, {target_gloss} (Score: 0.00)")

    return formatted_relations


def get_fallback_gloss(term, fallback_type='near_synonym'):
    # If a Word Meaning does not have a gloss, a fallback one is used. Check the primary fallback type first
    for relation_type in [fallback_type, 'near_xpos_synonym', 'has_hyponym', 'has_hyperonym']:
        for rel in term.get('relations', []):
            if rel.get('relation_type') == relation_type:
                target_gloss = rel.get('target_gloss', '')
                if target_gloss == "No Gloss":
                    target_gloss = ''  # Replace "No Gloss" with an empty string for comparison
                if target_gloss:
                    return target_gloss, relation_type
    return '', None  # If no valid fallback is found