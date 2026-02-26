"""
CSV reader with multi-threshold candidate selection for IWN update.
"""


def read_lemmas_from_csv(file_path):
    import csv

    lemmas = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            gloss_similarity = float(row['Gloss S. (WM)'])
            total_weighted_similarity = float(row['T. Relation S.'])
            total_similarity = float(row['Total S.'])
            malus = float(row['Malus'])
            literal_lemma = row['Literal Lemma']
            mari_t_sense = row.get('MariT sense', 'N/A')
            iwn_sense = row.get('IWN sense', 'N/A')

            if gloss_similarity >= 0.43 or total_weighted_similarity > 0.00:
                lemmas.append({'literal_lemma': literal_lemma, 'mari_t_sense': mari_t_sense, 'iwn_sense': iwn_sense})
            elif gloss_similarity == 0 or malus == 0:
                print(f"Skipped - G.Sim (WM) or Malus = 0: {literal_lemma} | MariTerm Sense: {mari_t_sense} | ItalWN Sense: {iwn_sense}")
            else:
                if mari_t_sense == iwn_sense:
                    if (
                        (0.29 <= gloss_similarity < 0.42 and (-0.03 <= total_similarity or total_similarity <= -0.35)) or
                        (0.16 < gloss_similarity < 0.29 and (malus == -0.33 or total_similarity >= -0.42)) or
                        (0.13 <= gloss_similarity <= 0.16 and (-0.83 <= total_similarity <= -0.20)) or
                        (0.10 <= gloss_similarity <= 0.12 and total_similarity >= -0.55) or
                        (0.06 <= gloss_similarity <= 0.09 and (-0.60 <= total_similarity <= -0.26)) or
                        (0 < gloss_similarity <= 0.05 and (-0.61 <= total_similarity <= -0.28))
                    ):
                        lemmas.append({'literal_lemma': literal_lemma, 'mari_t_sense': mari_t_sense, 'iwn_sense': iwn_sense})
                else:
                    if (
                        (0.29 < gloss_similarity < 0.42 and total_similarity >= -0.02) or
                        (0.25 <= gloss_similarity < 0.28 and total_similarity >= -1.07) or
                        (0.19 <= gloss_similarity <= 0.24 and (-4.40 < total_similarity < -0.11 or total_similarity >= -0.76)) or
                        (0.16 <= gloss_similarity <= 0.18 and total_similarity >= -1.14) or
                        (0.13 <= gloss_similarity <= 0.15 and -1.52 <= total_similarity < -0.18) or
                        (0.10 <= gloss_similarity < 0.12 and (total_similarity >= -0.55 or total_similarity == -0.89)) or
                        (0.07 < gloss_similarity <= 0.09 and (-2.55 <= total_similarity <= -0.25 or total_similarity == -2.55)) or
                        (0 < gloss_similarity <= 0.06 and total_similarity < -0.63)
                    ):
                        lemmas.append({'literal_lemma': literal_lemma, 'mari_t_sense': mari_t_sense, 'iwn_sense': iwn_sense})
                    else:
                        print(f"Skipped - other : {literal_lemma} | MariTerm Sense: {mari_t_sense} | ItalWN Sense: {iwn_sense}")

    print(f"Final Selected Lemmas: {lemmas}")
    print(f"Total selected:{len(lemmas)}")
    return lemmas