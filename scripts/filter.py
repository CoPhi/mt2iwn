#!/usr/bin/env python3
"""
CLI: Filter scored candidates and produce filtered MariTerm / IWN XML files.

Reads the breakdown CSV, matches lemmas by sense, and writes filtered XML
pairs for downstream IWN updating.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.config import Paths
from scripts.filtering import transcribe_candidates


def main():
    parser = argparse.ArgumentParser(description="Filter MariTerm / ItalWordNet candidate pairs")
    parser.add_argument('--marit', default=Paths.MARIT, help='Path to MariTerm XML file')
    parser.add_argument('--iwn', default=Paths.IWN, help='Path to ItalWordNet XML file')
    parser.add_argument('--breakdown', default=Paths.BREAKDOWN_CSV, help='Breakdown CSV (input)')
    parser.add_argument('--output-marit', default=Paths.FILT_MART, help='Filtered MariTerm XML (output)')
    parser.add_argument('--output-iwn', default=Paths.FILT_IWN, help='Filtered IWN XML (output)')
    args = parser.parse_args()

    print("=" * 70)
    print("FILTERING CANDIDATES")
    print("=" * 70)
    print(f"MariTerm file:   {args.marit}")
    print(f"ItalWordNet file:{args.iwn}")
    print(f"Breakdown CSV:   {args.breakdown}")
    print(f"Output MariTerm: {args.output_marit}")
    print(f"Output IWN:      {args.output_iwn}")
    print()

    transcribe_candidates(args.marit, args.iwn, args.breakdown, args.output_marit, args.output_iwn)

    print(f"\n{'=' * 70}")
    print(f"✓ Filtered MariTerm written to {args.output_marit}")
    print(f"✓ Filtered IWN written to      {args.output_iwn}")
    print("=" * 70)


if __name__ == '__main__':
    main()