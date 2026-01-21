# Bloodwork Biological Age Calculator

A Python toolkit for processing bloodwork data and calculating biological age using the [Bortz Blood Age Calculator](https://www.longevity-tools.com/humanitys-bortz-blood-age) from Longevity Tools.

## Features

- Generate Bortz Calculator URLs from CSV bloodwork data
- Support for 40+ biomarker aliases and variations
- Batch processing for historical trend analysis
- Interactive HTML dashboard with Chart.js visualization
- Comprehensive data validation and error reporting
- Configurable file paths and logging

## Quick Start

### 1. Prepare Your Data

Create a CSV file named `bloodwork.csv` with the following columns:

```csv
Biomarker,Value,Unit,Measurement Date
Albumin,4.5,g/dL,2024-01-15
Glucose,95,mg/dL,2024-01-15
Cholesterol,180,mg/dL,2024-01-15
...
```

### 2. Generate Calculator URL

```bash
python generate_calculator_url.py
```

This creates `output_url.txt` containing the Bortz Calculator URL with your latest biomarker values.

### 3. Get Historical URLs

```bash
python generate_batch_urls.py
```

This generates `batch_urls.json` with URLs for each measurement date in your data.

### 4. Visualize Trends

After manually entering biological ages into `age_history.csv`:

```bash
python visualize_age.py
```

This creates `age_trend.html` - an interactive dashboard showing your biological age over time.

## Scripts Overview

### `generate_calculator_url.py`

Generate a single Bortz Calculator URL with the latest biomarker values.

**Usage:**
```bash
# Basic usage
python generate_calculator_url.py

# With custom date cutoff
python generate_calculator_url.py --date 2024-06-30

# Custom file paths
python generate_calculator_url.py --input data.csv --output url.txt

# Verbose logging
python generate_calculator_url.py --verbose
```

**Options:**
- `--date YYYY-MM-DD`: Use only data on or before this date
- `--input PATH`: Input CSV file (default: bloodwork.csv)
- `--output PATH`: Output URL file (default: output_url.txt)
- `--verbose`: Enable detailed logging

### `generate_batch_urls.py`

Generate URLs for all unique measurement dates for historical analysis.

**Usage:**
```bash
# Basic usage
python generate_batch_urls.py

# Custom file paths
python generate_batch_urls.py --input data.csv --output urls.json

# Verbose logging
python generate_batch_urls.py --verbose
```

**Options:**
- `--input PATH`: Input CSV file (default: bloodwork.csv)
- `--output PATH`: Output JSON file (default: batch_urls.json)
- `--verbose`: Enable detailed logging

### `visualize_age.py`

Create interactive HTML visualization of biological age trends.

**Usage:**
```bash
# Basic usage
python visualize_age.py

# Custom file paths
python visualize_age.py --input data.csv --output dashboard.html

# Custom template
python visualize_age.py --template custom_template.html

# Verbose logging
python visualize_age.py --verbose
```

**Options:**
- `--input PATH`: Input age history CSV (default: age_history.csv)
- `--output PATH`: Output HTML file (default: age_trend.html)
- `--template PATH`: HTML template file (default: age_trend_template.html)
- `--verbose`: Enable detailed logging

### `debug_biomarkers.py`

Analyze and validate biomarker data for debugging.

**Usage:**
```bash
# Basic usage
python debug_biomarkers.py

# Custom sample size
python debug_biomarkers.py --samples 10

# Custom file paths
python debug_biomarkers.py --input data.csv --output report.txt

# Verbose logging
python debug_biomarkers.py --verbose
```

**Options:**
- `--input PATH`: Input CSV file (default: bloodwork.csv)
- `--output PATH`: Output report file (default: debug_markers.txt)
- `--samples N`: Number of sample values per biomarker (default: 5)
- `--verbose`: Enable detailed logging

## Supported Biomarkers

The toolkit recognizes 40+ biomarker names and aliases, including:

**Blood Markers:**
- Albumin, ALP, ALT, GGT
- Creatinine, Urea/BUN, Cystatin C

**Metabolic:**
- Glucose (Fasting)
- HbA1c
- Cholesterol (Total)
- ApoA1 (Apolipoprotein A1)

**Blood Cells:**
- RBC (Red Blood Cell Count)
- MCV (Mean Corpuscular Volume)
- RDW (Red Cell Distribution Width)
- Monocytes (Absolute)
- Neutrophils (Absolute)
- Lymphocytes (%)

**Inflammation & Hormones:**
- hsCRP / CRP
- SHBG

**Vitamins:**
- Vitamin D (25-OH)

See `biomarkers.py` for the complete mapping.

## File Structure

```
bloodwork_age/
├── biomarkers.py                 # Shared biomarker mappings and utilities
├── logger_config.py              # Logging configuration
├── generate_calculator_url.py   # Single URL generator
├── generate_batch_urls.py       # Batch URL generator
├── visualize_age.py             # HTML visualization generator
├── debug_biomarkers.py          # Data validation utility
├── age_trend_template.html      # HTML template for visualization
├── test_biomarkers.py           # Unit tests
├── bloodwork.csv                # Your input data (gitignored)
├── age_history.csv              # Biological age results
├── output_url.txt               # Generated URL (gitignored)
├── batch_urls.json              # Generated batch URLs (gitignored)
├── age_trend.html               # Generated visualization (gitignored)
└── README.md                    # This file
```

## Data Format

### Input CSV (`bloodwork.csv`)

Required columns:
- `Biomarker`: Name of the biomarker (e.g., "Albumin", "Glucose")
- `Value`: Numeric value (supports prefixes like `<`, `>`, `=`)
- `Unit`: Unit of measurement (e.g., "g/dL", "mg/dL", "%")
- `Measurement Date`: Date in YYYY-MM-DD format

Example:
```csv
Biomarker,Value,Unit,Measurement Date
Albumin,4.5,g/dL,2024-01-15
Glucose,<100,mg/dL,2024-01-15
Cholesterol,180,mg/dL,2024-01-15
hsCRP,0.8,mg/L,2024-01-15
```

### Age History CSV (`age_history.csv`)

Required columns:
- `Measurement Date`: Date in YYYY-MM-DD format
- `Bortz Biological Age`: Calculated biological age (numeric)
- `Notes`: Optional notes (not used by scripts)

Example:
```csv
Measurement Date,Bortz Biological Age,Notes
2024-01-15,56.2,Baseline
2024-06-20,54.8,After lifestyle changes
```

## Development

### Running Tests

```bash
# Using pytest
python -m pytest test_biomarkers.py -v

# Using unittest directly
python test_biomarkers.py
```

### Code Quality

The codebase includes:
- Type hints on all functions
- Comprehensive docstrings
- Input validation and error handling
- Structured logging
- Unit tests for critical functions

## Privacy & Security

- Personal medical data (`bloodwork.csv`) is automatically excluded from git
- All generated output files are gitignored by default
- No data is sent to external services (URLs are generated locally)
- You manually visit the Bortz Calculator URLs in your browser

## Workflow

1. Export bloodwork results to `bloodwork.csv`
2. Run `generate_batch_urls.py` to create URLs for all dates
3. Open each URL in the Bortz Calculator and record the biological age
4. Add results to `age_history.csv`
5. Run `visualize_age.py` to see trends
6. Analyze and adjust lifestyle based on trends

## Troubleshooting

**"No valid biomarkers found"**
- Check that your CSV column names match exactly: `Biomarker`, `Value`, `Unit`, `Measurement Date`
- Verify biomarker names are recognized (run `debug_biomarkers.py` to see all biomarkers)
- Use `--verbose` flag to see detailed error messages

**"Invalid date format"**
- Ensure dates are in YYYY-MM-DD format
- Check for extra whitespace or special characters

**"Skipped invalid value"**
- The script automatically skips non-numeric values like "N/A" or "pending"
- Use `--verbose` to see which values are being skipped

**Missing biomarkers in URL**
- Check the biomarker name against `biomarkers.BIOMARKER_MAP`
- Add aliases to `biomarkers.py` if needed

## License

This is a personal utility tool. The Bortz Blood Age Calculator is provided by Longevity Tools.

## Contributing

This is a personal project, but suggestions and improvements are welcome via issues or pull requests.

## Credits

- Bortz Blood Age Calculator by [Longevity Tools](https://www.longevity-tools.com/)
- Visualization powered by [Chart.js](https://www.chartjs.org/)
