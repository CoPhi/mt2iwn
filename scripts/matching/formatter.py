"""
Result formatting and display for matched MariTerm / ItalWordNet entries.
"""

from scripts.similarity import get_fallback_gloss


def print_and_return_best_match(results):
    # Sort results by 'Total S.' in descending order
    sorted_results = sorted(results, key=lambda x: x[0].get('Total S.', 0), reverse=True)

    for best_match, matched_senses in sorted_results:
            mari_gloss = best_match.get('Mariterm Gloss', '').strip()
            ital_wn_gloss = best_match.get('ItalWN Gloss', '').strip()

            # Check if both glosses are empty
            if not mari_gloss and not ital_wn_gloss:
                print(f"\nLiteral Lemma: {best_match.get('Literal Lemma', 'N/A')}")
                print(f"MariTerm Gloss: [FALLBACK]")
                print(f"ItalWN Gloss: [FALLBACK]")
                print(f"MariTerm ID: {best_match['Mariterm ID']}")
                print(f"ItalWN ID: {best_match['ItalWN ID']}")
                print(f"MariTerm Sense: {best_match.get('MariT sense', 'N/A')}")
                print(f"ItalWN Sense: {best_match.get('IWN sense', 'N/A')}")
                print("No alternate senses available for comparison.")
                print(f"Gloss S. (WM): 0.00")
                print(f"Total Weighted Relation Similarity: 0.00")
                print(f"  Bonus: 0.00 (0/0 - )")
                print(f"  Malus: 0.00 (0/0 - No Gloss in ItalWN: 0,  - Missing: )")
                print(f"Total S.: 0.00")
                print(f"MariTerm Relations: ")
                print(f"ItalWN Relations: ")
            else:
                # Continue with fallback logic if either gloss is present
                if mari_gloss == '':
                    mari_gloss, mari_fallback_type = get_fallback_gloss(best_match, 'near_synonym')
                    fallback_used = True
                else:
                    mari_fallback_type = None
                    fallback_used = False

                if ital_wn_gloss == '':
                    ital_wn_gloss, ital_fallback_type = get_fallback_gloss(best_match, 'near_synonym')
                else:
                    ital_fallback_type = None

                print(f"\nLiteral Lemma: {best_match.get('Literal Lemma', 'N/A')}")
                print(f"MariTerm Gloss: {mari_gloss}")
                print(f"ItalWN Gloss: {ital_wn_gloss}")
                print(f"MariTerm ID: {best_match['Mariterm ID']}")
                print(f"ItalWN ID: {best_match['ItalWN ID']}")
                print(f"MariTerm Sense: {best_match.get('MariT sense', 'N/A')}")
                print(f"ItalWN Sense: {best_match.get('IWN sense', 'N/A')}")
                print(f"Gloss S. (WM): {best_match['Gloss S. (WM)']:.2f}")
                print(f"Total Weighted Relation Similarity: {best_match['T. Relation S.']:.2f}")
                print(f"  Bonus: {best_match['bonus']:.2f} ({len(best_match['bonus_relations'])}/{len(best_match['MariTerm Relations'])} - {', '.join(best_match['bonus_relations'])})")
                print(f"  Malus: {best_match['malus']:.2f} ({len(best_match['missing_relations']) + len(best_match['no_gloss_relations'])}/{len(best_match['MariTerm Relations'])} - No Gloss in ItalWN: {len(best_match['no_gloss_relations'])}, {', '.join(best_match['no_gloss_relations'])} - Missing: {', '.join(best_match['missing_relations'])})")
                print(f"Total S.: {best_match.get('Total S.', 0.0):.2f}")  # Default to 0.0 if 'Total S.' is not present
                print(f"MariTerm Relations:")
                for rel in best_match.get('MariTerm Relations', []):
                    print(f"   {rel}")
                print(f"ItalWN Relations:")
                for rel in best_match.get('ItalWN Relations', []):
                    print(f"   {rel}")


def format_results(MariT, ItalWN, breakdown_csv):
    from .writer import save_entries

    unique_entries = save_entries(MariT, ItalWN, breakdown_csv)

    if not unique_entries:
        print("No entries found. Exiting.")
        return []

    total_similarities = [entry['Total S.'] for entry in unique_entries]
    min_similarity = min(total_similarities)
    max_similarity = max(total_similarities)

    unique_entries.sort(key=lambda x: x['Total S.'], reverse=True)

    formatted_results = []

    for entry in unique_entries:
        literal_lemma = entry.get('Literal Lemma', 'N/A')
        ital_wn_id = entry.get('IWN ID', 'N/A')
        mari_term_id = entry.get('Mariterm ID', 'N/A')
        iwn_sense = entry.get('IWN sense', 'N/A')
        mari_t_sense = entry.get('MariT sense', 'N/A')
        wn_g_sim = entry.get("Gloss S. (WM)", 0.0)
        total_similarity = entry.get('Total S.', 0.00)
        total_weighted_similarity = entry.get('T. Relation S.', 0.00)
        malus = entry.get('Malus', 0.00)
        bonus = entry.get('Bonus', 0.00)
        gloss = entry.get('Mariterm Gloss', 'No Gloss Available')

        formatted_results.append({
            'Literal Lemma': literal_lemma,
            'IWN ID': ital_wn_id,
            'MariTerm ID': mari_term_id,
            'IWN sense': iwn_sense,
            'MariT sense': mari_t_sense,
            'Gloss S. (WM)': wn_g_sim,
            'Total S.': total_similarity,
            'T. Relation S.': total_weighted_similarity,
            'Malus': malus,
            'Bonus': bonus,
            'MariTerm Gloss': gloss,
        })

    return formatted_results


def print_formatted_results(formatted_results):
    if not formatted_results:
        print("No valid entries to display.")
        return

    print(f"{'Literal Lemma':<25} {'IWN ID':<15} {'MariTerm ID':<15} {'IWN sense':<12} {'MariT sense':<12} {'Gloss S. (WM)':<15} {'Total S.':<15} {'T. Relation S.':<20} {'Malus':<10} {'Bonus':<10} {'MariTerm Gloss':<50}")
    print('-' * 250)

    for result in formatted_results:
        print(f"{result['Literal Lemma']:<25} {result['IWN ID']:<15} {result['MariTerm ID']:<15} {result['IWN sense']:<12} {result['MariT sense']:<12}"
              f"{result['Gloss S. (WM)']:<15.2f} {result['Total S.']:<15.2f} {result['T. Relation S.']:<20.2f}"
              f"{result['Malus']:<10.2f} {result['Bonus']:<10.2f} {result['MariTerm Gloss']:<50}")