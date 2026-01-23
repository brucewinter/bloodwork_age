"""
Levine PhenoAge Calculator biomarker mapping and utilities.

The Levine PhenoAge Calculator uses 9 biomarkers + age to calculate
phenotypic age based on clinical chemistry and blood count markers.
"""

from typing import Dict

# Base URL for Levine PhenoAge Calculator
LEVINE_BASE_URL = 'https://www.longevity-tools.com/levine-pheno-age#'

# Mapping of CSV Biomarker names to Levine Calculator IDs
# Levine uses: albumin, creatinine, glucose, hsCRP, lymphocyte %,
# MCV, RDW, alkaline phosphatase, WBC, and age
LEVINE_BIOMARKER_MAP: Dict[str, str] = {
    # Age (auto-calculated from birthdate)
    "Age": "age",

    # Albumin
    "Albumin": "S-albumin",
    "S-albumin": "S-albumin",

    # Creatinine
    "Creatinine": "S-creatinine",
    "S-creatinine": "S-creatinine",

    # Glucose
    "Glucose": "S-glucose",
    "S-glucose": "S-glucose",
    "Glucose (Fasting)": "S-glucose",

    # High-sensitivity C-reactive protein
    "hsCRP": "S-hsCRP",
    "hs-CRP": "S-hsCRP",
    "S-hsCRP": "S-hsCRP",
    "CRP": "S-hsCRP",

    # Lymphocyte percentage
    "LYM": "LYM",
    "Lymphocytes (%)": "LYM",
    "Lymphocytes": "LYM",

    # Mean Corpuscular Volume
    "MCV": "MCV",

    # Red Cell Distribution Width
    "RDW": "RDW",
    "RDW (RDW-CV)": "RDW",
    "RDW-SD": "RDW",
    "RDW-CV": "RDW",

    # Alkaline Phosphatase
    "ALP": "S-ALP",
    "S-ALP": "S-ALP",
    "Alkaline Phosphatase": "S-ALP",

    # White Blood Cell count
    "WBC": "WBC",
    "White Blood Cell Count": "WBC",
    "White Blood Cells": "WBC",
    "Leukocytes": "WBC",
}

# Required biomarkers for Levine calculation (all 9 must be present)
LEVINE_REQUIRED_BIOMARKERS = {
    "S-albumin",
    "S-creatinine",
    "S-glucose",
    "S-hsCRP",
    "LYM",
    "MCV",
    "RDW",
    "S-ALP",
    "WBC",
    "age"
}


def get_levine_biomarker_names() -> list:
    """
    Get the canonical names of Levine biomarkers.

    Returns:
        List of biomarker IDs used by Levine calculator
    """
    return sorted(LEVINE_REQUIRED_BIOMARKERS)


def validate_levine_data(data: Dict[str, any]) -> tuple[bool, list]:
    """
    Validate that all required Levine biomarkers are present.

    Args:
        data: Dictionary of biomarker data

    Returns:
        Tuple of (is_valid, list of missing biomarkers)
    """
    present = set(data.keys())
    required = LEVINE_REQUIRED_BIOMARKERS
    missing = required - present

    return len(missing) == 0, sorted(missing)
