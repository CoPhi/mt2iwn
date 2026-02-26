# filtering

Validates XML inputs, matches word meaning pairs by lemma and sense,
and transcribes them to filtered XML files for downstream updating.

## Modules

| File | Contents |
|------|----------|
| `validator.py` | `validate_xml` |
| `filter.py` | `filter_wm` |
| `matcher.py` | `match_lemmas` |
| `transcriber.py` | `transcribe_matched_pairs`, `transcribe_candidates` |

## API

```python
from scripts.filtering import (
    validate_xml,
    filter_wm,
    match_lemmas,
    transcribe_matched_pairs,
    transcribe_candidates,
)
```

### validate_xml(file_path)
Returns `True` if the file parses without error, `False` otherwise.

### filter_wm(xml_root)
Extracts a lightweight list of word meaning dicts from an XML root.
Each dict contains: `id`, `lemmas`, `senses`, `first_literal_lemma`,
`first_literal_sense`, `original_element` (the raw `ET.Element`).

### match_lemmas(mari_term_wms, ital_wn_wms, csv_entries)
Matches word meanings using both lemma and sense number from a list of
CSV entry dicts (`literal_lemma`, `mari_t_sense`, `iwn_sense`).
Returns a list of `(mari_element, ital_element)` tuples.
Prints a warning for unmatched entries.

### transcribe_matched_pairs(matched_pairs, filt_mart, filt_iwn)
Writes the matched MariTerm and ItalWordNet elements to two separate XML files.

### transcribe_candidates(MariT, ItalWN, candidates_file, filt_mart, filt_iwn)
High-level entry point: validates inputs, reads the breakdown CSV,
matches pairs, and writes filtered XML files.

```python
transcribe_candidates(
    'data/MariT.xml',
    'data/IWN.xml',
    'results/breakdown.csv',
    'results/MariT_filtered.xml',
    'results/IWN_filtered.xml',
)
# Total matched pairs transcribed: N
```

## Input CSV Format

The CSV must contain at minimum the columns:
`Literal Lemma`, `MariT sense`, `IWN sense`

## Dependencies

- Python stdlib (`csv`, `xml.etree.ElementTree`)