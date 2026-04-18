"""
Centralized configuration for MT2IWN pipeline.
"""

import xml.etree.ElementTree as ET

# ---------------------------------------------------------------------------
# Scoring thresholds
# These values must be identical to whatever filter.py (Stage 3) uses so
# that audit.py reproduces the same 747 / 410 split when run on the same
# breakdown.csv.
# ---------------------------------------------------------------------------
 
GLOSS_HIGH_THRESHOLD  = 0.43   # Gate A: accepted on gloss similarity alone
GLOSS_LOW_THRESHOLD   = 0.13   # Gate B: floor on gloss when relations help
REL_SUPPORT_THRESHOLD = 0.09   # Gate B: minimum relation similarity
 
# ---------------------------------------------------------------------------
# Audit output directory (used by scripts/audit.py as default --out-dir)
# ---------------------------------------------------------------------------
 
AUDIT_OUT_DIR = "results/audit"

class Paths:
    # Input
    MARIT = 'data/MariT.xml'
    IWN = 'data/IWN.xml'

    # Intermediate
    CANDIDATES_CSV = 'results/candidates.csv'
    BREAKDOWN_CSV = 'results/breakdown.csv'
    FILT_MART = 'results/MariT_filtered.xml'
    FILT_IWN = 'results/IWN_filtered.xml'
    UPDATES = 'results/IWN_updates.xml'
    IWN_PRE_MOD = 'results/IWN_pre_merge.xml'
    IWN_POST_MM = 'results/IWN_post_merge.xml'
    IWN_MM_W_GLOSSES = 'results/IWN_post_merge_glosses.xml'

    # Final
    FINALIZED_IWN = 'results/IWN_final.xml'
    FINALIZED_MARIT = 'results/MariT_final.xml'


class Config:
    ALLOWED_RELATION_TYPES = {
        "has_hyperonym", "has_hyponym", "near_synonym",
        "has_xpos_hyperonym", "has_xpos_hyponym", "xpos_near_synonym"
    }


def parse_xml(file_path):
    return ET.parse(file_path).getroot()

