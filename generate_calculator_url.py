import csv
import urllib.parse
from datetime import datetime

# Path to the CSV file
CSV_FILE = 'bloodwork.csv'
BASE_URL = 'https://www.longevity-tools.com/humanitys-bortz-blood-age#?'

# Mapping of CSV Biomarker names to Bortz Calculator IDs
# This ensures only the required 22 markers are included in the URL.
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

def clean_value(val):
    """Removes non-numeric prefixes like '<' or '>'."""
    if not val:
        return ""
    # Remove common prefixes
    cleaned = val.replace('<', '').replace('>', '').replace('=', '').strip()
    return cleaned

import argparse

def generate_url(cutoff_date_str=None):
    data = {}
    
    cutoff_date = None
    if cutoff_date_str:
        try:
            cutoff_date = datetime.strptime(cutoff_date_str, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format '{cutoff_date_str}'. Please use YYYY-MM-DD.")
            return

    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [fn.strip() for fn in reader.fieldnames]
            
            for row in reader:
                raw_marker = row['Biomarker'].strip()
                if raw_marker not in BIOMARKER_MAP:
                    continue
                
                marker_id = BIOMARKER_MAP[raw_marker]
                raw_value = row['Value'].strip()
                value = clean_value(raw_value)
                
                if not value or value.lower() == "data not available":
                    continue
                    
                unit = row['Unit'].strip()
                date_str = row['Measurement Date'].strip()
                
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    continue
                
                # Filter by cutoff date if provided
                if cutoff_date and date_obj > cutoff_date:
                    continue

                # Update if marker is new or newer date found (within the cutoff)
                if marker_id not in data or date_obj > data[marker_id]['date']:
                    data[marker_id] = {
                        'value': value,
                        'unit': unit,
                        'date': date_obj
                    }
    except FileNotFoundError:
        print(f"Error: {CSV_FILE} not found.")
        return

    if not data:
        print(f"No valid biomarkers found in CSV {'before ' + cutoff_date_str if cutoff_date_str else ''}.")
        return

    # Construct the query parameters
    params = []
    
    # Sort markers by ID for consistent URL generation
    for marker_id in sorted(data.keys()):
        info = data[marker_id]
        # Special unit handling for Bortz URL
        unit = info['unit']
        if unit == '%':
            unit = '%25' # Double encode for URL
            
        formatted_value = f"{info['value']}_{unit}"
        # We use quote with safe='' to ensure / becomes %2F
        params.append(f"{marker_id}={urllib.parse.quote(formatted_value, safe='')}")

    final_url = BASE_URL + '&'.join(params)
    
    with open('output_url.txt', 'w') as f:
        f.write(final_url)
    
    date_context = f" (data on or before {cutoff_date_str})" if cutoff_date_str else ""
    print(f"\n--- Generated Bortz Blood Age Calculator URL{date_context} ---")
    print(final_url)
    print("--------------------------------------------------\n")
    print("URL has also been saved to output_url.txt")
    return final_url

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Bortz Blood Age Calculator URL from CSV.')
    parser.add_argument('--date', type=str, help='Cutoff date (YYYY-MM-DD). Only uses data on or before this date.', default=None)
    args = parser.parse_args()
    
    generate_url(args.date)
