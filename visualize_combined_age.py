"""
Generate combined visualization of Bortz and Levine biological age trends.

This script reads both Bortz and Levine age history data and creates
an interactive dashboard comparing both calculators.
"""

import argparse
import csv
import json
import os
from typing import List, Tuple, Optional
from datetime import datetime

from logger_config import setup_logger
from config import get_birthdate, calculate_age

# Column names
COL_DATE = 'Measurement Date'
COL_BORTZ_AGE = 'Bortz Biological Age'
COL_LEVINE_AGE = 'Levine Phenotypic Age'

# Outlier detection threshold
MAX_REASONABLE_AGE = 150.0

logger = setup_logger(__name__)


def load_combined_age_data(
    bortz_csv: str,
    levine_csv: str
) -> Tuple[List[str], List[float], List[float], List[float], List[float], List[float]]:
    """
    Load both Bortz and Levine age data and combine by date.

    Args:
        bortz_csv: Path to Bortz age history CSV
        levine_csv: Path to Levine age history CSV

    Returns:
        Tuple of (dates, bortz_bio_ages, bortz_chron_ages, bortz_deltas,
                  levine_pheno_ages, levine_deltas)
    """
    # Get birthdate for chronological age calculation
    try:
        birthdate = get_birthdate()
    except ValueError as e:
        logger.error(f"Error loading birthdate: {e}")
        raise

    # Load Bortz data
    bortz_data = {}
    if os.path.exists(bortz_csv):
        with open(bortz_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_str = row[COL_DATE].strip()
                try:
                    bio_age = float(row[COL_BORTZ_AGE])
                    if bio_age > 0 and bio_age < MAX_REASONABLE_AGE:
                        bortz_data[date_str] = bio_age
                except (ValueError, KeyError):
                    continue
        logger.info(f"Loaded {len(bortz_data)} Bortz data points")
    else:
        logger.warning(f"Bortz file not found: {bortz_csv}")

    # Load Levine data
    levine_data = {}
    if os.path.exists(levine_csv):
        with open(levine_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date_str = row[COL_DATE].strip()
                try:
                    pheno_age = float(row[COL_LEVINE_AGE])
                    if pheno_age > 0 and pheno_age < MAX_REASONABLE_AGE:
                        levine_data[date_str] = pheno_age
                except (ValueError, KeyError):
                    continue
        logger.info(f"Loaded {len(levine_data)} Levine data points")
    else:
        logger.warning(f"Levine file not found: {levine_csv}")

    if not bortz_data and not levine_data:
        raise ValueError("No valid data found in either Bortz or Levine files")

    # Combine data by date
    all_dates = sorted(set(bortz_data.keys()) | set(levine_data.keys()))

    dates = []
    bortz_bio_ages = []
    bortz_chron_ages = []
    bortz_deltas = []
    levine_pheno_ages = []
    levine_deltas = []

    for date_str in all_dates:
        measurement_date = datetime.strptime(date_str, '%Y-%m-%d')
        chron_age = calculate_age(birthdate, measurement_date)

        # Include date if we have at least one measurement
        if date_str in bortz_data or date_str in levine_data:
            dates.append(date_str)
            bortz_chron_ages.append(chron_age)

            # Bortz data
            if date_str in bortz_data:
                bio_age = bortz_data[date_str]
                bortz_bio_ages.append(bio_age)
                bortz_deltas.append(round(bio_age - chron_age, 1))
            else:
                bortz_bio_ages.append(None)
                bortz_deltas.append(None)

            # Levine data
            if date_str in levine_data:
                pheno_age = levine_data[date_str]
                levine_pheno_ages.append(pheno_age)
                levine_deltas.append(round(pheno_age - chron_age, 1))
            else:
                levine_pheno_ages.append(None)
                levine_deltas.append(None)

    logger.info(f"Combined {len(dates)} total measurement dates")

    return dates, bortz_bio_ages, bortz_chron_ages, bortz_deltas, levine_pheno_ages, levine_deltas


def generate_combined_visualization(
    bortz_csv: str,
    levine_csv: str,
    html_output: str,
    template_path: str = 'combined_age_trend_template.html'
) -> bool:
    """
    Generate combined HTML visualization from both age history files.

    Args:
        bortz_csv: Path to Bortz age history CSV
        levine_csv: Path to Levine age history CSV
        html_output: Path to save the generated HTML file
        template_path: Path to the HTML template file

    Returns:
        True if successful, False otherwise
    """
    try:
        dates, bortz_bio, bortz_chron, bortz_delta, levine_pheno, levine_delta = load_combined_age_data(
            bortz_csv, levine_csv
        )
    except FileNotFoundError as e:
        logger.error(str(e))
        return False
    except ValueError as e:
        logger.error(str(e))
        return False

    if not dates:
        logger.error("No valid data points found for visualization")
        return False

    logger.info(f"Generating visualization with {len(dates)} data points")

    # Read template
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        logger.error(f"Template file not found: {template_path}")
        return False

    # Replace placeholders with JSON data
    html_content = template.replace('{{DATES_JSON}}', json.dumps(dates))
    html_content = html_content.replace('{{BORTZ_BIO_AGES_JSON}}', json.dumps(bortz_bio))
    html_content = html_content.replace('{{CHRON_AGES_JSON}}', json.dumps(bortz_chron))
    html_content = html_content.replace('{{BORTZ_DELTAS_JSON}}', json.dumps(bortz_delta))
    html_content = html_content.replace('{{LEVINE_PHENO_AGES_JSON}}', json.dumps(levine_pheno))
    html_content = html_content.replace('{{LEVINE_DELTAS_JSON}}', json.dumps(levine_delta))

    # Write output
    try:
        with open(html_output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Combined visualization generated: {html_output}")
        return True
    except IOError as e:
        logger.error(f"Failed to write output file: {e}")
        return False


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Generate combined visualization of Bortz and Levine biological age trends.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python visualize_combined_age.py
  python visualize_combined_age.py --bortz age_history.csv --levine levine_age_history.csv
  python visualize_combined_age.py --output combined_dashboard.html --verbose
        """
    )
    parser.add_argument(
        '--bortz',
        type=str,
        help='Path to Bortz age history CSV (default: age_history.csv)',
        default='age_history.csv'
    )
    parser.add_argument(
        '--levine',
        type=str,
        help='Path to Levine age history CSV (default: levine_age_history.csv)',
        default='levine_age_history.csv'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Path to output HTML file (default: combined_age_trend.html)',
        default='combined_age_trend.html'
    )
    parser.add_argument(
        '--template',
        type=str,
        help='Path to HTML template file (default: combined_age_trend_template.html)',
        default='combined_age_trend_template.html'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel('DEBUG')

    success = generate_combined_visualization(args.bortz, args.levine, args.output, args.template)

    if not success:
        exit(1)


if __name__ == "__main__":
    main()
