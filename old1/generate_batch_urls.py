import csv
import urllib.parse
from datetime import datetime
import json

# Setup
CSV_FILE = 'bloodwork.csv'
BASE_URL = 'https://www.longevity-tools.com/humanitys-bortz-blood-age#?'

# Re-use the mapping
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
    if not val: return ""
    return val.replace('<', '').replace('>', '').replace('=', '').strip()

def get_all_urls():
    # 1. Load all data
    all_rows = []
    unique_dates = set()
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_rows.append(row)
                unique_dates.add(row['Measurement Date'].strip())
    except FileNotFoundError:
        print("Error: bloodwork.csv not found.")
        return

    sorted_dates = sorted(list(unique_dates))
    results = []

    for cutoff_str in sorted_dates:
        cutoff_date = datetime.strptime(cutoff_str, '%Y-%m-%d')
        data = {}
        for row in all_rows:
            raw_marker = row['Biomarker'].strip()
            if raw_marker not in BIOMARKER_MAP: continue
            
            marker_id = BIOMARKER_MAP[raw_marker]
            value = clean_value(row['Value'].strip())
            if not value or value.lower() == "data not available": continue
            
            unit = row['Unit'].strip()
            date_str = row['Measurement Date'].strip()
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError: continue
            
            if date_obj <= cutoff_date:
                if marker_id not in data or date_obj > data[marker_id]['date']:
                    data[marker_id] = {'value': value, 'unit': unit, 'date': date_obj}
        
        if not data: continue
        
        params = []
        for marker_id in sorted(data.keys()):
            info = data[marker_id]
            unit = info['unit'].replace('%', '%25')
            val_unit = f"{info['value']}_{unit}"
            params.append(f"{marker_id}={urllib.parse.quote(val_unit, safe='')}")
        
        results.append({
            "date": cutoff_str,
            "url": BASE_URL + '&'.join(params)
        })

    with open('batch_urls.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Generated {len(results)} URLs in batch_urls.json")

if __name__ == "__main__":
    get_all_urls()
