# Bloodwork Biological Age Calculator

A Python toolkit for processing bloodwork data and calculating biological age using two validated calculators:
- [Bortz Blood Age Calculator](https://www.longevity-tools.com/humanitys-bortz-blood-age) (22 biomarkers)
- [Levine PhenoAge Calculator](https://www.longevity-tools.com/levine-pheno-age) (9 biomarkers)

## Features

- Generate Calculator URLs from CSV bloodwork data (Bortz and/or Levine)
- Support for 40+ biomarker aliases and variations
- Batch processing for historical trend analysis
- Interactive HTML dashboards with Chart.js visualization
- Combined dashboard comparing both calculators
- Automatic chronological age calculation from birthdate
- Age delta tracking (biological/phenotypic age vs chronological age)
- Selenium automation for extracting results
- Comprehensive data validation and error reporting
- Configurable file paths and logging

## Quick Start

### Incremental Updates (Adding New Data)

When you have new bloodwork measurements and want to add them without reprocessing everything:

```bash
# 1. Update bloodwork.csv with new measurements

# 2. Generate URLs for new dates only and append to existing JSON files
python update_incremental.py

# 3. Process new URLs with Selenium (appends to existing CSV files)
python process_batch_urls.py --incremental
python process_levine_batch_urls.py --incremental

# 4. Regenerate visualizations
.\Quick-Visualize.ps1
```

**How it works:**
- `update_incremental.py` identifies dates not yet in batch_urls.json
- Generates URLs only for new dates
- Appends new URLs to existing JSON files
- Process scripts with `--incremental` flag skip already-processed dates
- Results are appended (not overwritten) to age_history.csv files

This saves significant time by avoiding reprocessing of historical data.

### Automated Workflow (Recommended)

**PowerShell (Windows):**
```powershell
# Run complete pipeline - both calculators (default)
.\Run-BloodworkAnalysis.ps1

# Run only Bortz Blood Age Calculator
.\Run-BloodworkAnalysis.ps1 -Calculator Bortz

# Run only Levine PhenoAge Calculator
.\Run-BloodworkAnalysis.ps1 -Calculator Levine

# With custom CSV file
.\Run-BloodworkAnalysis.ps1 -InputCsv "my_bloodwork.csv"

# Skip Selenium automation (if CSV files exist)
.\Run-BloodworkAnalysis.ps1 -SkipSelenium

# Run in headless mode (no browser GUI)
.\Run-BloodworkAnalysis.ps1 -Headless

# Enable verbose logging
.\Run-BloodworkAnalysis.ps1 -VerboseLogging

# Combine options
.\Run-BloodworkAnalysis.ps1 -Calculator Both -InputCsv "data.csv" -Headless -VerboseLogging

# Get help documentation
.\Run-BloodworkAnalysis.ps1 -Help
Get-Help .\Run-BloodworkAnalysis.ps1 -Full

# Quick visualization update only (combined dashboard)
.\Quick-Visualize.ps1

# Quick visualization for single calculator
.\Quick-Visualize.ps1 -Calculator Bortz
```

**Batch File (Windows - Simple):**
```batch
REM Run with default bloodwork.csv
run.bat

REM Run with custom CSV
run.bat my_bloodwork.csv
```

The automated scripts will:
1. Generate Calculator URLs from your CSV (Bortz and/or Levine)
2. Automatically extract biological/phenotypic ages using Selenium
3. Generate interactive visualization dashboard (combined or single calculator)
4. Open the dashboard in your browser

### Configuration

**Important:** Before running, update your birthdate in `config.py`:

```python
BIRTHDATE = "1958-07-08"  # Update with your actual birthdate
```

This enables automatic chronological age calculation for all tests.

### Manual Step-by-Step

If you prefer manual control:

#### 1. Prepare Your Data

Create a CSV file named `bloodwork.csv` with the following columns:

```csv
Biomarker,Value,Unit,Measurement Date
Albumin,4.5,g/dL,2024-01-15
Glucose,95,mg/dL,2024-01-15
Cholesterol,180,mg/dL,2024-01-15
...
```

**Note:** Age is now calculated automatically from your birthdate in `config.py`. Don't include Age in your CSV.

#### 2. Generate Calculator URL

```bash
python generate_calculator_url.py
```

This creates `output_url.txt` containing the Bortz Calculator URL with your latest biomarker values.

#### 3. Get Historical URLs

```bash
python generate_batch_urls.py
```

This generates `batch_urls.json` with URLs for each measurement date in your data.

#### 4. Extract Biological Ages (Automated)

```bash
python process_batch_urls.py
```

This uses Selenium to automatically open each URL and extract the biological age, saving results to `age_history.csv`.

#### 5. Visualize Trends

```bash
python visualize_age.py
```

This creates `age_trend.html` - an interactive dashboard with:
- Biological age vs chronological age over time
- Age delta chart (biological - chronological)
- Statistics and trend analysis

## Automation Scripts

### `Run-BloodworkAnalysis.ps1` (Recommended)

Complete pipeline automation with error handling, progress reporting, and colored output.

**Features:**
- Validates configuration and dependencies
- Runs all steps in sequence
- Detailed progress reporting
- Error handling with helpful messages
- Optional verbose logging and headless mode

**Usage:**
```powershell
# Basic usage - complete pipeline
.\Run-BloodworkAnalysis.ps1

# With custom CSV file
.\Run-BloodworkAnalysis.ps1 -InputCsv "my_data.csv"

# Skip URL generation (use existing batch_urls.json)
.\Run-BloodworkAnalysis.ps1 -SkipUrlGeneration

# Skip Selenium (use existing age_history.csv)
.\Run-BloodworkAnalysis.ps1 -SkipSelenium

# Headless browser automation (no GUI)
.\Run-BloodworkAnalysis.ps1 -Headless

# Enable verbose logging
.\Run-BloodworkAnalysis.ps1 -VerboseLogging

# Combine options
.\Run-BloodworkAnalysis.ps1 -InputCsv "data.csv" -Headless -VerboseLogging
```

### `Quick-Visualize.ps1`

Fast visualization regeneration when you only need to update the dashboard.

**Usage:**
```powershell
.\Quick-Visualize.ps1
```

**Use cases:**
- After updating config.py (e.g., birthdate correction)
- After modifying the HTML template
- After manually editing age_history.csv
- Quick refresh without rerunning Selenium

### `run.bat`

Simple batch file for quick runs without parameters.

**Usage:**
```batch
REM With default bloodwork.csv
run.bat

REM With custom CSV file
run.bat my_bloodwork.csv
```

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

### Levine PhenoAge Calculator Scripts

#### `generate_levine_url.py`

Generate a single Levine PhenoAge Calculator URL with the latest biomarker values.

**Usage:**
```bash
# Basic usage
python generate_levine_url.py

# With custom date cutoff
python generate_levine_url.py --date 2024-06-30

# Custom file paths
python generate_levine_url.py --input data.csv --output levine_url.txt

# Verbose logging
python generate_levine_url.py --verbose
```

**Options:**
- `--date YYYY-MM-DD`: Use only data on or before this date
- `--input PATH`: Input CSV file (default: bloodwork.csv)
- `--output PATH`: Output URL file (default: levine_url.txt)
- `--verbose`: Enable detailed logging

#### `generate_levine_batch_urls.py`

Generate Levine Calculator URLs for all unique measurement dates.

**Usage:**
```bash
# Basic usage
python generate_levine_batch_urls.py

# Custom file paths
python generate_levine_batch_urls.py --input data.csv --output levine_urls.json

# Verbose logging
python generate_levine_batch_urls.py --verbose
```

**Options:**
- `--input PATH`: Input CSV file (default: bloodwork.csv)
- `--output PATH`: Output JSON file (default: levine_batch_urls.json)
- `--verbose`: Enable detailed logging

#### `process_levine_batch_urls.py`

Automatically extract phenotypic ages from Levine Calculator URLs using Selenium.

**Usage:**
```bash
# Basic usage
python process_levine_batch_urls.py

# Incremental mode - append new results only
python process_levine_batch_urls.py --incremental

# Headless mode (no browser window)
python process_levine_batch_urls.py --headless

# Custom wait time
python process_levine_batch_urls.py --wait 15

# Custom file paths
python process_levine_batch_urls.py --input levine_urls.json --output levine_ages.csv

# Verbose logging
python process_levine_batch_urls.py --verbose
```

**Options:**
- `--input PATH`: Input batch URLs JSON (default: levine_batch_urls.json)
- `--output PATH`: Output CSV file (default: levine_age_history.csv)
- `--wait N`: Seconds to wait for page load (default: 10)
- `--headless`: Run browser in headless mode
- `--incremental`: Only process new dates, append to existing CSV
- `--verbose`: Enable detailed logging

#### `visualize_combined_age.py`

Create combined HTML visualization comparing Bortz and Levine calculators.

**Usage:**
```bash
# Basic usage
python visualize_combined_age.py

# Custom file paths
python visualize_combined_age.py --bortz age_history.csv --levine levine_age_history.csv

# Custom output and template
python visualize_combined_age.py --output combined_dashboard.html --template custom_template.html

# Verbose logging
python visualize_combined_age.py --verbose
```

**Options:**
- `--bortz PATH`: Input Bortz age history CSV (default: age_history.csv)
- `--levine PATH`: Input Levine age history CSV (default: levine_age_history.csv)
- `--output PATH`: Output HTML file (default: combined_age_trend.html)
- `--template PATH`: HTML template file (default: combined_age_trend_template.html)
- `--verbose`: Enable detailed logging

### `convert_siphox_to_pdf.py`

Convert Siphox CSV data to individual LabCorp-style PDF reports.

This script reads the wide-format Siphox CSV export and generates separate professional PDF reports for each test date, formatted similar to LabCorp lab reports. Each PDF includes organized biomarker results, reference ranges, and flags for out-of-range values.

**Usage:**
```bash
# Basic usage
python convert_siphox_to_pdf.py

# Custom input and output directory
python convert_siphox_to_pdf.py --input siphox_data.csv --output-dir reports/

# Verbose logging
python convert_siphox_to_pdf.py --verbose
```

**Options:**
- `--input PATH`: Path to Siphox CSV file (default: siphox_2025_08b.csv)
- `--output-dir PATH`: Directory to save PDF reports (default: siphox_reports/)
- `--verbose`: Enable detailed logging

**Features:**
- Generates one PDF per test date (e.g., LabReport_2024-08-08.pdf)
- Groups biomarkers by category (Heart Health, Metabolic Health, etc.)
- Includes reference ranges (Optimal, Good, Fair)
- Flags out-of-range values (H = High, L = Low)
- Professional LabCorp-style formatting
- Ready for import into medical databases

**Output format:**
- PDF files named: `LabReport_YYYY-MM-DD.pdf`
- Each report includes: Collection Date, Test Results Table, Reference Ranges, Flags
- Color-coded flags: Red for High, Blue for Low

### `update_incremental.py`

Identify and process only new measurement dates without reprocessing historical data.

This script analyzes your CSV file and existing batch_urls.json files to determine
which dates are new. It then generates URLs only for those dates and appends them
to the existing JSON files.

**Usage:**
```bash
# Basic usage - updates both calculators
python update_incremental.py

# Update specific calculator
python update_incremental.py --calculator Bortz
python update_incremental.py --calculator Levine

# Custom input file
python update_incremental.py --input new_bloodwork.csv

# Verbose logging
python update_incremental.py --verbose
```

**Options:**
- `--input PATH`: Path to bloodwork CSV (default: bloodwork.csv)
- `--calculator CALC`: Which calculator to update: Bortz, Levine, or Both (default: Both)
- `--verbose`: Enable detailed logging

**Workflow:**
1. Compares CSV dates against existing batch_urls.json
2. Identifies new dates not yet processed
3. Generates URLs only for new dates
4. Appends new URLs to existing JSON files
5. Reports summary of what needs processing

After running, use process scripts with `--incremental` flag to extract ages.

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

### Bortz Blood Age Calculator (22 biomarkers)

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

See `biomarkers.py` for the complete Bortz mapping.

### Levine PhenoAge Calculator (9 biomarkers + age)

**Required biomarkers:**
- Albumin (g/dL)
- Creatinine (mg/dL)
- Glucose (mg/dL)
- hsCRP (mg/L)
- Lymphocyte % (%)
- MCV (fL)
- RDW (%)
- ALP (U/L)
- WBC (10^9/L)
- Age (calculated automatically from birthdate)

See `levine_biomarkers.py` for the complete Levine mapping.

## File Structure

```
bloodwork_age/
├── Core Python Scripts
│   ├── config.py                         # Configuration (birthdate, settings)
│   ├── biomarkers.py                     # Bortz biomarker mappings and utilities
│   ├── levine_biomarkers.py              # Levine biomarker mappings and validation
│   ├── logger_config.py                  # Logging configuration
│   │
│   ├── Bortz Blood Age Calculator
│   │   ├── generate_calculator_url.py    # Single Bortz URL generator
│   │   ├── generate_batch_urls.py        # Batch Bortz URL generator
│   │   ├── process_batch_urls.py         # Selenium automation for Bortz
│   │   └── visualize_age.py              # Bortz visualization generator
│   │
│   ├── Levine PhenoAge Calculator
│   │   ├── generate_levine_url.py        # Single Levine URL generator
│   │   ├── generate_levine_batch_urls.py # Batch Levine URL generator
│   │   └── process_levine_batch_urls.py  # Selenium automation for Levine
│   │
│   ├── Combined Visualization
│   │   └── visualize_combined_age.py     # Combined dashboard generator
│   │
│   ├── Siphox Integration
│   │   └── convert_siphox_to_pdf.py      # Convert Siphox CSV to LabCorp-style PDFs
│   │
│   └── debug_biomarkers.py               # Data validation utility
│
├── Automation Scripts
│   ├── Run-BloodworkAnalysis.ps1         # Complete workflow automation (PowerShell)
│   ├── Quick-Visualize.ps1               # Quick visualization update (PowerShell)
│   ├── run.bat                           # Simple batch file workflow
│   ├── open_batch_urls.py                # Semi-automated browser helper
│   └── inspect_page.py                   # Page inspection utility
│
├── Templates & Tests
│   ├── age_trend_template.html           # Bortz visualization template
│   ├── combined_age_trend_template.html  # Combined dashboard template
│   └── test_biomarkers.py                # Unit tests (22 tests)
│
├── Data Files (input)
│   ├── bloodwork.csv                     # Your input data (gitignored)
│   └── siphox_*.csv                      # Siphox export data (gitignored)
│
├── Generated Files (output - gitignored)
│   ├── Bortz Output
│   │   ├── output_url.txt                # Single Bortz calculator URL
│   │   ├── batch_urls.json               # Bortz historical URLs
│   │   ├── age_history.csv               # Extracted biological ages
│   │   └── age_trend.html                # Bortz dashboard
│   │
│   ├── Levine Output
│   │   ├── levine_url.txt                # Single Levine calculator URL
│   │   ├── levine_batch_urls.json        # Levine historical URLs
│   │   └── levine_age_history.csv        # Extracted phenotypic ages
│   │
│   ├── Combined Output
│   │   └── combined_age_trend.html       # Combined dashboard
│   │
│   └── Siphox Reports (gitignored)
│       └── LabReport_YYYY-MM-DD.pdf      # Individual LabCorp-style PDF reports
│
└── Documentation
    ├── README.md                         # This file
    ├── REFACTORING_SUMMARY.md            # Development history
    └── requirements.txt                  # Python dependencies
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
