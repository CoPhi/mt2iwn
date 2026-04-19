"""
scripts/matching/report.py
==========================
Writes full score-breakdown .txt files for accepted and rejected candidate
pairs.  Called by score.py (Stage 2) immediately after it writes both
breakdown CSVs so the text reports are produced in the same run as the data.

Also imported by audit.py for threshold re-analysis, guaranteeing identical
formatting in both cases.

Row format
----------
Rows are raw current_match dicts as built by matcher.py, with these keys:
    Literal Lemma, MariT sense, IWN sense,
    Gloss S. (WM), Total S., T. Relation S.,
    Mariterm ID, ItalWN ID,
    Mariterm Gloss, ItalWN Gloss,
    MariTerm Relations, ItalWN Relations,
    bonus, malus, missing_relations, no_gloss_relations, bonus_relations

This is distinct from the subset written to breakdown.csv by store_to_csv /
format_results.  breakdown_rejected.csv uses the same full-dict format so
that both .txt breakdown files can be generated from it without data loss.

Gate logic (mirrors matcher.py exactly)
----------------------------------------
Gate A  Gloss S. (WM) >= 0.43  OR  T. Relation S. > 0
Gate B  Gloss S. (WM) >= 0.13  AND  (Gloss S. < 0.43  OR  T. Rel. > 0)
Gate C  T. Relation S. > 0.09
        OR  0.14 <= Gloss S. < 0.19
        OR  0.24 <= Gloss S. < 0.29
        OR  Gloss S. >= 0.44

A row is REJECTED only when it fails all three gates.  The rejection reason
string names every gate and the value that caused it to fail.

Public API
----------
format_block(row, decision, reason)              →  str
write_breakdown_txts(accepted, rejected,
                     out_dir, timestamp)         →  (matched_path, rejected_path)
"""

from __future__ import annotations

import ast
import os
from datetime import datetime


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_list_field(raw) -> list[str]:
    """
    Recover a list from a value that may be:
      • already a Python list  (when coming straight from matcher.py)
      • a Python repr string   "['rel1', 'rel2']"  (after CSV round-trip)
      • a pipe-joined string   "rel1|rel2"          (hand-edited CSVs)
      • an empty string / None
    """
    if isinstance(raw, list):
        return [str(item) for item in raw]
    raw = (raw or "").strip()
    if not raw:
        return []
    try:
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except (ValueError, SyntaxError):
        pass
    return [item.strip() for item in raw.split("|") if item.strip()]


# ---------------------------------------------------------------------------
# Gate logic (exact mirror of matcher.py threshold block)
# ---------------------------------------------------------------------------

def _passes_gate(row: dict) -> bool:
    """Return True if the row would be accepted by matcher.py's thresholds."""
    g  = _safe_float(row.get("Gloss S. (WM)"))
    rs = _safe_float(row.get("T. Relation S."))
    if g >= 0.43 or rs > 0:
        return True
    if g >= 0.13 and (g < 0.43 or rs > 0):
        return True
    if rs > 0.09 or (0.14 <= g < 0.19) or (0.24 <= g < 0.29) or g >= 0.44:
        return True
    return False


def _accepted_reason(row: dict) -> str:
    """Name the first gate that accepted this row."""
    g  = _safe_float(row.get("Gloss S. (WM)"))
    rs = _safe_float(row.get("T. Relation S."))
    if g >= 0.43:
        return f"Gate A — Gloss S. ({g:.2f}) >= 0.43"
    if rs > 0:
        return f"Gate A — T. Relation S. ({rs:.2f}) > 0"
    if g >= 0.13:
        return f"Gate B — Gloss S. ({g:.2f}) >= 0.13"
    if rs > 0.09:
        return f"Gate C — T. Relation S. ({rs:.2f}) > 0.09"
    if 0.14 <= g < 0.19:
        return f"Gate C — Gloss S. ({g:.2f}) in [0.14, 0.19)"
    if 0.24 <= g < 0.29:
        return f"Gate C — Gloss S. ({g:.2f}) in [0.24, 0.29)"
    return f"Gate C — Gloss S. ({g:.2f}) >= 0.44"


def _rejection_reason(row: dict) -> str:
    """
    Name what each gate saw and why the row failed all three.
    Always describes all three gates so the reader can judge borderline cases.
    """
    g  = _safe_float(row.get("Gloss S. (WM)"))
    rs = _safe_float(row.get("T. Relation S."))
    parts = [
        f"Gate A: Gloss S. ({g:.2f}) < 0.43  AND  T. Relation S. ({rs:.2f}) = 0",
        f"Gate B: Gloss S. ({g:.2f}) < 0.13"
        if g < 0.13
        else f"Gate B: Gloss S. ({g:.2f}) >= 0.13 but T. Relation S. = 0 and Gloss >= 0.43 not met",
        f"Gate C: T. Relation S. ({rs:.2f}) <= 0.09  AND  "
        f"Gloss S. ({g:.2f}) not in [0.14,0.19) | [0.24,0.29) | >=0.44",
    ]
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Block formatter
# ---------------------------------------------------------------------------

def format_block(row: dict, decision: str, reason: str) -> str:
    """
    One self-contained text block for a candidate pair.

    Layout mirrors display.py's print_and_return_best_match terminal output,
    extended with the audit verdict so the two .txt files are directly
    comparable entry for entry.

    Parameters
    ----------
    row      : dict  — raw current_match dict from matcher.py
                       (or a row read back from breakdown_rejected.csv)
    decision : str   — 'ACCEPTED' or 'REJECTED'
    reason   : str   — from _accepted_reason() or _rejection_reason()

    Returns
    -------
    str  — ends with separator + blank line, safe to concatenate directly
    """
    lines: list[str] = []

    lines.append(f"Decision         : {decision}")
    lines.append(f"Reason           : {reason}")
    lines.append("")

    lines.append(f"Literal Lemma    : {row.get('Literal Lemma', 'N/A')}")
    lines.append(f"MariTerm ID      : {row.get('Mariterm ID', 'N/A')}")
    lines.append(f"ItalWN ID        : {row.get('ItalWN ID', 'N/A')}")
    lines.append(f"MariTerm Sense   : {row.get('MariT sense', 'N/A')}")
    lines.append(f"ItalWN Sense     : {row.get('IWN sense', 'N/A')}")
    lines.append("")

    mari_gloss = str(row.get("Mariterm Gloss", "") or "").strip() or "[NO GLOSS]"
    ital_gloss = str(row.get("ItalWN Gloss",  "") or "").strip() or "[NO GLOSS]"
    lines.append(f"MariTerm Gloss   : {mari_gloss}")
    lines.append(f"ItalWN Gloss     : {ital_gloss}")
    lines.append("")

    g   = _safe_float(row.get("Gloss S. (WM)"))
    rs  = _safe_float(row.get("T. Relation S."))
    bon = _safe_float(row.get("bonus"))
    mal = _safe_float(row.get("malus"))
    tot = _safe_float(row.get("Total S."))

    bonus_rels    = _parse_list_field(row.get("bonus_relations",    ""))
    missing_rels  = _parse_list_field(row.get("missing_relations",  ""))
    no_gloss_rels = _parse_list_field(row.get("no_gloss_relations", ""))
    mari_rels     = _parse_list_field(row.get("MariTerm Relations", ""))
    iwn_rels      = _parse_list_field(row.get("ItalWN Relations",   ""))

    lines.append(f"Gloss S. (WM)    : {g:.2f}")
    lines.append(f"T. Relation S.   : {rs:.2f}")
    lines.append(
        f"  Bonus          : {bon:.2f}  "
        f"({len(bonus_rels)}/{len(mari_rels)} shared — "
        f"{', '.join(bonus_rels) if bonus_rels else 'none'})"
    )
    lines.append(
        f"  Malus          : {mal:.2f}  "
        f"({len(missing_rels) + len(no_gloss_rels)}/{len(mari_rels)} penalised — "
        f"no ItalWN gloss: {len(no_gloss_rels)} "
        f"[{', '.join(no_gloss_rels) if no_gloss_rels else '—'}]  "
        f"missing entirely: [{', '.join(missing_rels) if missing_rels else '—'}])"
    )
    lines.append(f"Total S.         : {tot:.2f}")
    lines.append("")

    lines.append("MariTerm Relations:")
    for rel in (mari_rels or ["[none]"]):
        lines.append(f"   {rel}")
    lines.append("ItalWN Relations:")
    for rel in (iwn_rels or ["[none]"]):
        lines.append(f"   {rel}")

    lines.append("")
    lines.append("-" * 80)
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# File writers
# ---------------------------------------------------------------------------

_SEP = "=" * 80

_MATCHED_HEADER = """\
{sep}
mt2iwn — MATCHED SYNSET PAIRS
Generated  : {timestamp}
Gate A : Gloss S. >= 0.43  OR  T. Relation S. > 0
Gate B : Gloss S. >= 0.13  AND  (Gloss S. < 0.43  OR  T. Relation S. > 0)
Gate C : T. Relation S. > 0.09  OR  Gloss in [0.14,0.19) | [0.24,0.29) | >=0.44
{sep}

"""

_REJECTED_HEADER = """\
{sep}
mt2iwn — REJECTED CANDIDATE PAIRS
Generated  : {timestamp}
Gate A : Gloss S. >= 0.43  OR  T. Relation S. > 0
Gate B : Gloss S. >= 0.13  AND  (Gloss S. < 0.43  OR  T. Relation S. > 0)
Gate C : T. Relation S. > 0.09  OR  Gloss in [0.14,0.19) | [0.24,0.29) | >=0.44

Each block shows a pair that failed all three gates, sorted by Total S.
descending so near-misses appear first.

The 'Reason' line shows what each gate saw for this pair.

Pairs most worth re-examining:
  — T. Relation S. = 0 but bonus_relations > 0: relation existed but gloss
    of the target was missing, so the bonus was earned but no Gate A credit
    was given (T. Relation S. is the *weighted* sum, not raw bonus)
  — Both glosses [NO GLOSS]: scorer had nothing to compare; low Gloss S.
    reflects a data gap, not a semantic mismatch
  — Gloss S. just below 0.13: terse or divergent wording for the same concept
{sep}

"""

_FOOTER = """\
{sep}
SUMMARY
  Accepted (matched) : {n_accepted}
  Rejected           : {n_rejected}
  Total              : {total}
"""


def write_breakdown_txts(
    accepted_rows: list[dict],
    rejected_rows: list[dict],
    out_dir: str,
    timestamp: str | None = None,
) -> tuple[str, str]:
    """
    Write matched_breakdown.txt and rejected_breakdown.txt to out_dir.

    Called by score.py (Stage 2) after both CSVs are written.
    Also called by audit.py for threshold re-analysis.

    Parameters
    ----------
    accepted_rows : list[dict]
        Raw current_match dicts from matcher.py that passed the threshold.
        Sorted by Total S. descending before writing.
    rejected_rows : list[dict]
        Raw current_match dicts that failed all three gates.
        Sorted by Total S. descending (near-misses first).
    out_dir : str
        Output directory (created if absent).
    timestamp : str | None
        ISO datetime string; uses current time if None.

    Returns
    -------
    (matched_path, rejected_path) : absolute paths of the two files written.
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    os.makedirs(out_dir, exist_ok=True)

    matched_path  = os.path.join(out_dir, "matched_breakdown.txt")
    rejected_path = os.path.join(out_dir, "rejected_breakdown.txt")

    hdr = dict(sep=_SEP, timestamp=timestamp)
    footer = _FOOTER.format(
        sep=_SEP,
        n_accepted=len(accepted_rows),
        n_rejected=len(rejected_rows),
        total=len(accepted_rows) + len(rejected_rows),
    )

    # Sort both by Total S. descending
    accepted_sorted = sorted(
        accepted_rows, key=lambda r: _safe_float(r.get("Total S.")), reverse=True
    )
    rejected_sorted = sorted(
        rejected_rows, key=lambda r: _safe_float(r.get("Total S.")), reverse=True
    )

    _write_file(
        matched_path,
        header=_MATCHED_HEADER.format(**hdr),
        rows=accepted_sorted,
        decision="ACCEPTED",
        reason_fn=_accepted_reason,
        footer=footer,
    )

    _write_file(
        rejected_path,
        header=_REJECTED_HEADER.format(**hdr),
        rows=rejected_sorted,
        decision="REJECTED",
        reason_fn=_rejection_reason,
        footer=footer,
    )

    return os.path.abspath(matched_path), os.path.abspath(rejected_path)


def _write_file(path, header, rows, decision, reason_fn, footer):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(header)
        for row in rows:
            fh.write(format_block(row, decision, reason_fn(row)))
        fh.write(footer)