"""
Shared biomarker mapping and utility functions for bloodwork analysis.

This module contains the common biomarker mappings used by the Bortz Blood Age
Calculator URL generators, along with utility functions for data cleaning and validation.
"""

from typing import Optional
import re

# Constants
BASE_URL = 'https://www.longevity-tools.com/humanitys-bortz-blood-age#?'
DATA_NOT_AVAILABLE = "data not available"

# Mapping of CSV Biomarker names to Bortz Calculator IDs
# This ensures only the required biomarkers are included in the URL.
BIOMARKER_MAP = {
    "Age": "age",
    "Albumin": "S-albumin",
    "S-albumin": "S-albumin",
    "ALP": "S-ALP",
    "S-ALP": "S-ALP",
    "Urea": "S-urea",
    "S-urea": "S-urea",
    "BUN": "S-urea",
    "Cholesterol": "S-cholesterol",
    "Total Cholesterol": "S-cholesterol",
    "S-cholesterol": "S-cholesterol",
    "Creatinine": "S-creatinine",
    "S-creatinine": "S-creatinine",
    "Cystatin C": "S-cystatin-C",
    "S-cystatin-C": "S-cystatin-C",
    "HbA1c": "B-HbA1c",
    "B-HbA1c": "B-HbA1c",
    "hsCRP": "S-hsCRP",
    "hs-CRP": "S-hsCRP",
    "S-hsCRP": "S-hsCRP",
    "GGT": "S-GGT",
    "S-GGT": "S-GGT",
    "Red Blood Cell Count": "RBC",
    "RBC": "RBC",
    "MCV": "MCV",
    "RDW": "RDW",
    "RDW (RDW-CV)": "RDW",
    "RDW-SD": "RDW",
    "RDW-CV": "RDW",
    "Absolute Monocytes": "MONOabs",
    "MONOabs": "MONOabs",
    "Monocytes (Absolute)": "MONOabs",
    "Absolute Neutrophils": "NEUabs",
    "NEUabs": "NEUabs",
    "Neutrophils (Absolute)": "NEUabs",
    "LYM": "LYM",
    "Lymphocytes (%)": "LYM",
    "ALT": "S-ALT",
    "S-ALT": "S-ALT",
    "SHBG": "S-SHBG",
    "S-SHBG": "S-SHBG",
    "Vitamin D (25-OH)": "S-25-OH-D",
    "Vitamin D - 25(OH)D": "S-25-OH-D",
    "Vitamin D3 (25-OH D3)": "S-25-OH-D",
    "Vitamin D, 25-Hydroxy": "S-25-OH-D",
    "S-25-OH-D": "S-25-OH-D",
    "Glucose": "S-glucose",
    "S-glucose": "S-glucose",
    "Glucose (Fasting)": "S-glucose",
    "MCH": "MCH",
    "ApoA1": "S-ApoA1",
    "S-ApoA1": "S-ApoA1",
    "Apolipoprotein A1": "S-ApoA1"
}


def clean_value(val: str) -> str:
    """
    Removes non-numeric prefixes like '<', '>', or '=' from biomarker values.

    Args:
        val: The raw value string from the CSV

    Returns:
        Cleaned value string with comparison operators removed
    """
    if not val:
        return ""
    # Remove common prefixes used in lab reports
    cleaned = val.replace('<', '').replace('>', '').replace('=', '').strip()
    return cleaned


def is_valid_numeric(val: str) -> bool:
    """
    Validates if a string represents a valid numeric value.

    Args:
        val: The cleaned value string to validate

    Returns:
        True if the value is a valid number, False otherwise
    """
    if not val:
        return False

    # Check for common non-numeric indicators
    if val.lower() in [DATA_NOT_AVAILABLE, 'n/a', 'na', 'pending', 'none', 'null']:
        return False

    # Try to convert to float
    try:
        float(val)
        return True
    except ValueError:
        return False


def normalize_unit(unit: str) -> str:
    """
    Normalizes units for URL encoding.

    Args:
        unit: The unit string from the CSV

    Returns:
        URL-encoded unit string
    """
    if unit == '%':
        return '%25'  # URL encode percent sign
    return unit
