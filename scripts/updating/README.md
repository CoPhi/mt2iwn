# updating

Reads scored candidates, applies multi-threshold selection, creates or merges
ItalWordNet word meanings, adds relations, handles gloss replacement, and
produces the updated IWN XML file.

## Modules

| File | Contents |
|------|----------|
| `reader.py` | `read_lemmas_from_csv` — threshold-based candidate selection |
| `retriever.py` | `retrieve_wm`, `find_word_meaning_in_root`, `get_new_id`, `get_gloss_from_italwn`, `extract_target_ids`, `retrieve_relation_ids` |
| `creator.py` | `create_or_merge_word_meaning`, `determine_inverse_relation`, `extract_eq_links_and_top_onto`, `merge_sections` |
| `cleaner.py` | `clean_target_wm_id`, `remove_duplicate_relations`, `clean_existing_target_wm_ids`, `clean_and_move_eq_links_at_end`, `sort_word_meanings_by_lemma_and_sense` |
| `updater.py` | `update_iwn_entries`, `replace_gloss_with_original`, `remove_redundant_word_meanings` |

## Shared Mutable State

The module exposes three module-level objects that are shared across
`creator.py` and `updater.py`, mirroring the original notebook globals:

```python
import scripts.updating as updating

updating.replaced_glosses  # list — glosses replaced during update
updating.new_word_meanings  # list — newly created word meaning lemmas
updating.updated_entries    # set  — (lemma, sense) pairs already updated
```

**Always reset these before a new run:**
```python
updating.replaced_glosses.clear()
updating.new_word_meanings.clear()
updating.updated_entries.clear()
```

## API

### read_lemmas_from_csv(file_path)
Reads the breakdown CSV and selects candidates using multi-threshold logic
based on `Gloss S. (WM)`, `T. Relation S.`, `Total S.`, and `Malus`.
Returns a list of `{'literal_lemma', 'mari_t_sense', 'iwn_sense'}` dicts.

### update_iwn_entries(selected_lemmas, mari_root, iwn_root, original_mari_root, original_iwn_root)
Main update function. For each selected lemma:
1. Finds or creates the corresponding IWN word meaning
2. Adds semantic relations from MariTerm
3. Creates back-reference word meanings for unknown relation targets
4. Cleans, sorts, and deduplicates the result

### replace_gloss_with_original(iwn_root, original_iwn_root, updated_entries)
Restores original IWN glosses for entries that were not part of the update.

## Dependencies

- `scripts.config` — `Config.ALLOWED_RELATION_TYPES`
- Python stdlib (`csv`, `xml.etree.ElementTree`)