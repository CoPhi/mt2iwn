"""
Gloss retrieval and XML update for newly created synsets missing glosses.
"""

import xml.etree.ElementTree as ET


def find_glosses_for_new_synsets(xml_file, new_synsets):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Store results
    results = []

    # Iterate over synsets in the new_synsets list
    for synset in new_synsets:
        original_id = synset["ID"]
        numeric_id = original_id.split("#")[1]  # Strip anything before #

        # Find the <WORD_MEANING> node with the matching ID
        word_meaning = root.find(f".//WORD_MEANING[@ID='{original_id}']")
        if word_meaning is None:
            continue

        # Check if the <GLOSS> tag is empty
        gloss = word_meaning.find("GLOSS")
        if gloss is not None and (gloss.text is None or gloss.text.strip() == ""):
            lemma = synset["LEMMA"]

            # Look for this ID in <TARGET_WM> entries
            retrieved_gloss = None
            for target in root.findall(f".//TARGET_WM[@ID='{numeric_id}']"):
                retrieved_gloss = target.get("GLOSS")
                if retrieved_gloss:  # If a GLOSS attribute is found, stop searching
                    break

            # Add the result
            results.append({
                "id": numeric_id,
                "lemma": lemma,
                "retrieved_gloss": retrieved_gloss if retrieved_gloss else "No gloss found"
            })

    return results


def display_results(results):
    # Print results in a readable format
    print(f"{'ID':<10} {'Lemma':<30} {'Retrieved Gloss':<80}")
    print("-" * 120)
    for result in results:
        print(f"{result['id']:<10} {result['lemma']:<30} {result['retrieved_gloss']:<80}")


def update_glosses_in_xml(xml_file, results, output_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Debugging list to track updates
    debugging_updates = []

    # Iterate through results to update the gloss
    for result in results:
        numeric_id = result["id"]
        lemma = result["lemma"]
        retrieved_gloss = result["retrieved_gloss"]

        # Find the <WORD_MEANING> node with the matching ID
        word_meaning = root.find(f".//WORD_MEANING[@ID='N#{numeric_id}']")
        if word_meaning is None:
            continue  # Skip if no matching node is found

        # Find the <GLOSS> node
        gloss_node = word_meaning.find("GLOSS")
        if gloss_node is not None and retrieved_gloss != "No gloss found":
            # Update the <GLOSS> node text with the retrieved gloss
            gloss_node.text = retrieved_gloss

            # Add to the debugging list
            debugging_updates.append({
                "id": numeric_id,
                "lemma": lemma,
                "added_gloss": retrieved_gloss
            })

    # Save the updated XML
    tree.write(output_file, encoding="utf-8", xml_declaration=True)

    # Print debugging updates
    print("\nUpdated Glosses:")
    for update in debugging_updates:
        print(f"ID: {update['id']}, Lemma: {update['lemma']}, Added Gloss: {update['added_gloss']}")