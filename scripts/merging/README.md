# merging

Merges updated IWN entries back into the original IWN file and formats
the output XML with proper indentation.

## Modules

| File | Contents |
|------|----------|
| `merger.py` | `merge_and_format_iwn_files` |
| `formatter.py` | `format_xml_with_indentation`, `save_pretty_xml` |

## API

```python
from scripts.merging import merge_and_format_iwn_files, format_xml_with_indentation, save_pretty_xml
```

### merge_and_format_iwn_files(ItalWN, updates, IWN_pre_mod)
1. Parses the original IWN and the updates file
2. Replaces existing entries with updated versions (matched by lemma + sense)
3. Appends new entries not present in the original
4. Sorts all entries alphabetically by lemma then sense
5. Writes the merged file and applies `format_xml_with_indentation`

```python
merge_and_format_iwn_files(
    'data/IWN_03_24.xml',
    'results/IWN_updates.xml',
    'results/IWN_pre_merge.xml',
)
# Merged IWN file created and saved as 'results/IWN_pre_merge.xml'
```

### format_xml_with_indentation(file_path)
Reads an XML file, pretty-prints it with 2-space indentation using
`xml.dom.minidom`, strips extra blank lines, and writes it back in place.

### save_pretty_xml(tree, xml_file_path)
Pretty-prints an `ET.ElementTree` with 4-space indentation and strips
blank lines. Used for the final IWN and MariTerm output files.

## Dependencies

- Python stdlib (`re`, `xml.etree.ElementTree`, `xml.dom.minidom`)