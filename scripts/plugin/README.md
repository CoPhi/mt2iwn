# plugins

Adds bidirectional `PLUG-IN_LINKS` between ItalWordNet and MariTerm synsets,
retrieves missing glosses for new synsets, removes duplicate plugin relations,
and produces the finalized XML files.

## Modules

| File | Contents |
|------|----------|
| `adder.py` | `load_csv_data`, `find_mariterm_synset`, `insert_after`, `ensure_plugin_links`, `add_plugins` |
| `updater.py` | `insert_plugin_node`, `update_plugin_links` |
| `cleaner.py` | `remove_duplicate_plugins`, `sort_plugin_links` |
| `glosses.py` | `find_glosses_for_new_synsets`, `display_results`, `update_glosses_in_xml` |

## API

```python
from scripts.plugins import (
    load_csv_data, add_plugins, ensure_plugin_links,
    update_plugin_links, remove_duplicate_plugins, sort_plugin_links,
    find_glosses_for_new_synsets, display_results, update_glosses_in_xml,
)
```

### load_csv_data(csv_file_path)
Reads the breakdown CSV and returns a `{(iwn_lemma, iwn_sense): (mari_lemma, mari_sense)}` reference dict.

### add_plugins(iwn_root, mariterm_filtered_root, mariterm_original_root, reference, newly_added_relations_info)
Populates `PLUG-IN_LINKS` in each IWN WORD_MEANING pointing to the
corresponding MariTerm entry. Also adds `plug-{relation_type}` links for
newly added semantic relations. Returns `(synset_relations_storage, iwn_synsets_with_plugins)`.

**Relation type mapping:**
- `plug-synonym` → ID `1`
- `plug-near_synonym`, `plug-xpos_near_synonym` → ID `2`
- `plug-has_hyperonym`, `plug-has_xpos_hyperonym` → ID `3`
- `plug-has_hyponym`, `plug-has_xpos_hyponym` → ID `4`

### update_plugin_links(iwn_root, mariterm_root, synset_relations_storage, iwn_synsets_with_plugins, structured_relations)
Populates `PLUG-IN_LINKS` in each MariTerm WORD_MEANING pointing back to
the corresponding IWN entries (reverse direction).

### find_glosses_for_new_synsets(xml_file, new_synsets)
For new synsets with an empty `<GLOSS>`, searches `TARGET_WM[@GLOSS]`
attributes in the same file and returns matches as a list of result dicts.

### update_glosses_in_xml(xml_file, results, output_file)
Applies the retrieved glosses to the `<GLOSS>` nodes and writes the output.

### remove_duplicate_plugins(iwn_root) / sort_plugin_links(plugin_links)
Remove duplicate `PLUG-IN_LINKS` relations and sort by ID then target ID.

## Dependencies

- `scripts.config` — `Config.ALLOWED_RELATION_TYPES`
- Python stdlib (`csv`, `xml.etree.ElementTree`)