# similarity

Text normalization and semantic similarity scoring for MariTerm / ItalWordNet entry comparison.

## Modules

| File | Contents |
|------|----------|
| `normalizer.py` | `normalize_lemma`, `normalize_text` |
| `gloss.py` | `calculate_gloss_similarity` (TF-IDF cosine) |
| `relations.py` | `calculate_relation_similarity` (weighted scoring) |
| `scoring.py` | `format_relations`, `get_fallback_gloss` |

## API

```python
from scripts.similarity import (
    normalize_lemma,
    normalize_text,
    calculate_gloss_similarity,
    calculate_relation_similarity,
    format_relations,
    get_fallback_gloss,
)
```

### normalize_lemma(lemma)
Lowercases, replaces underscores/apostrophes with spaces, strips punctuation.
```python
normalize_lemma("nave_da_guerra")  # → "nave da guerra"
```

### normalize_text(text)
Same as `normalize_lemma` but operates on arbitrary text (glosses, senses).

### calculate_gloss_similarity(text1, text2)
Returns TF-IDF cosine similarity in [0.0, 1.0]. Returns 0.0 for empty inputs.
```python
calculate_gloss_similarity("grande nave marittima", "imbarcazione di grandi dimensioni")
# → float between 0.0 and 1.0
```

### calculate_relation_similarity(wn_g_sim, relations1, relations2)
Computes weighted relation similarity, bonus, and malus.

**Relation weights:**
- `has_hyperonym`: 0.82
- `has_hyponym`: 0.76
- `near_synonym`: 0.60
- `has_xpos_*` / `xpos_*`: 0.50

Returns a 10-tuple:
```
(total_weighted_similarity, relation_weights, bonus, malus,
 malus_count, missing_relations, no_gloss_relations,
 no_gloss_words, total_similarity, bonus_relations)
```

### format_relations(relations, relation_weights, show_scores=True)
Formats a relation list for display or CSV output.

### get_fallback_gloss(term, fallback_type='near_synonym')
Returns a fallback gloss from a word meaning dict when the primary gloss is empty.
Tries `near_synonym` → `near_xpos_synonym` → `has_hyponym` → `has_hyperonym`.

## Dependencies

- `scikit-learn` — TF-IDF vectorizer and cosine similarity
- Python stdlib (`string`)