"""
Centralized configuration for MT2IWN pipeline.
"""

import xml.etree.ElementTree as ET


class Paths:
    # Input
    MARIT = 'data/MariT_03_24.xml'
    IWN = 'data/IWN_03_24.xml'

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
