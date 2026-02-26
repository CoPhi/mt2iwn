#!/usr/bin/env python3
"""
CLI: Merge the updated IWN entries back into the original IWN file.

Replaces existing entries with their updated versions, appends new entries,
sorts alphabetically, and formats the output XML with proper indentation.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.config import Paths
from scripts.merging import merge_and_format_iwn_files


def main():
    parser = argparse.ArgumentParser(description="Merge updated IWN entries into original IWN")
    parser.add_argument('--iwn-original', default=Paths.IWN, help='Original IWN XML')
    parser.add_argument('--iwn-updates', default=Paths.UPDATES, help='Updated IWN XML')
    parser.add_argument('--output', default=Paths.IWN_PRE_MOD, help='Merged IWN XML (output)')
    args = parser.parse_args()

    print("=" * 70)
    print("MERGING IWN FILES")
    print("=" * 70)
    print(f"IWN original: {args.iwn_original}")
    print(f"IWN updates:  {args.iwn_updates}")
    print(f"Output:       {args.output}")
    print()

    merge_and_format_iwn_files(args.iwn_original, args.iwn_updates, args.output)

    print(f"\n{'=' * 70}")
    print(f"✓ Merged IWN written to {args.output}")
    print("=" * 70)


if __name__ == '__main__':
    main()