#!/usr/bin/env python3
"""
CLI: Extract shared lemma candidates between MariTerm and ItalWordNet.

Identifies lemmas present in both resources and writes them to a
semicolon-delimited CSV with their respective WORD_MEANING IDs.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.config import Paths
from scripts.extraction import find_shared, write_csv


def main():
    parser = argparse.ArgumentParser(description="Extract shared lemma candidates")
    parser.add_argument('--marit', default=Paths.MARIT, help='Path to MariTerm XML file')
    parser.add_argument('--iwn', default=Paths.IWN, help='Path to ItalWordNet XML file')
    parser.add_argument('--output', default=Paths.CANDIDATES_CSV, help='Output CSV file path')
    args = parser.parse_args()

    print("=" * 70)
    print("EXTRACTING SHARED LEMMA CANDIDATES")
    print("=" * 70)
    print(f"MariTerm file:   {args.marit}")
    print(f"ItalWordNet file:{args.iwn}")
    print(f"Output file:     {args.output}")
    print()
    print("Finding shared lemmas...")

    shared, marit, iwn = find_shared(args.marit, args.iwn)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    write_csv(shared, marit, iwn, args.output)

    print(f"Writing {len(shared)} shared lemmas to CSV...")
    print(f"\n{'=' * 70}")
    print(f"✓ Shared lemmas written to {args.output}")
    print("=" * 70)


if __name__ == '__main__':
    main()