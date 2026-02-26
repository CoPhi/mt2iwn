# analysis

Post-hoc analysis utilities: ID conflict detection, next available
WORD_MEANING ID retrieval, and identification of new/updated synsets.

## Modules

| File | Contents |
|------|----------|
| `comparator.py` | `extract_ids_and_lemmas`, `compare_files` |
| `id_manager.py` | `get_last_word_meaning_id` |
| `identifier.py` | `extract_internal_links`, `identify_updates_in_iwn` |

## API

```python
from scripts.analysis import (
    extract_ids_and_lemmas,
    compare_files,
    get_last_word_meaning_id,
    extract_internal_links,
    identify_updates_in_iwn,
)
```

### extract_ids_and_lemmas(xml_file)
Returns a `{numeric_id: [lemma, ...]}` dict from a WORD_MEANING XML file.

### compare_files(file1_data, file2_data)
Prints any IDs that map to different lemmas across two files (conflict detection).

### get_last_word_meaning_id(file)
Returns `max_numeric_id + 1` — the next safe ID to assign in the given file.
```python
next_id = get_last_word_meaning_id('results/IWN_post_merge.xml')
print(f"Next ID: {next_id}")
```

### extract_internal_links(wm)
Returns a `{(type, lemma, sense, id): relation_element}` dict
for all INTERNAL_LINKS relations in a WORD_MEANING element.

### identify_updates_in_iwn(ItalWN, plug_att)
Compares the original IWN against the post-merge file and returns:
- `updated_synsets` — list of synsets with new relations
- `new_synsets` — list of synsets not present in the original
- `new_word_meanings_info` — `[(lemma, sense), ...]` for new entries
- `newly_added_relations_info` — flat list of 7-tuples:
  `(rel_type, target_lemma, target_sense, src_lemma, src_sense, target_id, synset_id)`

```python
updated, new, new_wm, new_rels = identify_updates_in_iwn(
    'data/IWN_03_24.xml',
    'results/IWN_post_merge.xml',
)
```

## Dependencies

- `scripts.config` — `Config.ALLOWED_RELATION_TYPES`
- Python stdlib (`xml.etree.ElementTree`)