# matching

Extracts word meanings from XML, matches MariTerm and ItalWordNet candidates
by similarity score, and exports results to CSV.

## Modules

| File | Contents |
|------|----------|
| `extractor.py` | `extract_word_meanings` |
| `matcher.py` | `match_lemmas_with_alternate_senses` |
| `formatter.py` | `print_and_return_best_match`, `format_results`, `print_formatted_results` |
| `writer.py` | `save_entries`, `store_to_csv` |

## API

```python
from scripts.matching import (
    extract_word_meanings,
    match_lemmas_with_alternate_senses,
    print_and_return_best_match,
    format_results,
    print_formatted_results,
    save_entries,
    store_to_csv,
)
```

### extract_word_meanings(xml_root)
Parses an XML root and returns a list of word meaning dicts, each containing:
`id`, `lemmas`, `normalized_lemmas`, `senses`, `normalized_senses`, `gloss`,
`normalized_gloss`, `relations`, `first_literal_lemma`, `first_literal_sense`,
`part_of_speech`.

### match_lemmas_with_alternate_senses(mari_term_wms, ital_wn_wms)
Matches MariTerm and ItalWordNet word meanings by normalized lemma and POS.
Applies gloss and relation similarity thresholds to select the best match per
ItalWordNet entry. Returns a list of `(best_match_dict, [])` tuples.

**Thresholds:**
- `gloss_similarity >= 0.43` OR `relation_similarity > 0` → accepted
- `gloss_similarity >= 0.13` with partial relation support → accepted
- Finer-grained thresholds for low-similarity pairs

### save_entries(MariT, ItalWN, breakdown_csv)
Runs the full matching pipeline and returns unique 1-to-1 matched entries.
Removes fallback glosses (`[FALLBACK]`) before returning.

### format_results(MariT, ItalWN, breakdown_csv)
Wraps `save_entries` and returns a list of flat result dicts sorted by `Total S.`.

### store_to_csv(formatted_results, breakdown_csv)
Writes formatted results to a semicolon-delimited CSV file.

## CSV Output Format

```
Literal Lemma;IWN ID;MariTerm ID;IWN sense;MariT sense;Gloss S. (WM);Total S.;T. Relation S.;Malus;Bonus;MariTerm Gloss
ancora;N#12345;N#67890;1;1;0.72;1.05;0.33;0.00;0.33;Dispositivo di ancoraggio
```

## Dependencies

- `scripts.similarity` — normalization and scoring functions
- `scripts.config` — `Config.ALLOWED_RELATION_TYPES`, `parse_xml`
- `pandas`, `scikit-learn`