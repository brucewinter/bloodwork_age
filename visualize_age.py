"""
Generate interactive HTML visualization of biological age trends.

This script reads historical biological age data and creates an interactive
Chart.js dashboard showing trends over time.
"""

import argparse
import csv
import json
import os
from typing import List, Tuple, Optional

from logger_config import setup_logger
from config import get_birthdate, calculate_age

# Column names
COL_DATE = 'Measurement Date'
COL_BIO_AGE = 'Bortz Biological Age'

# Outlier detection threshold
MAX_REASONABLE_AGE = 150.0

logger = setup_logger(__name__)


def load_age_data(csv_path: str) -> Tuple[List[str], List[float], List[float], List[float]]:
    """
    Load biological age data from CSV and calculate chronological ages.

    Args:
        csv_path: Path to the age history CSV file

    Returns:
        Tuple of (dates list, biological ages list, chronological ages list, delta list)

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV is missing required columns
    """
    dates = []
    bio_ages = []
    chron_ages = []
    deltas = []

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")

    # Get birthdate for chronological age calculation
    try:
        birthdate = get_birthdate()
    except ValueError as e:
        logger.error(f"Error loading birthdate: {e}")
        raise

    skipped_invalid = 0
    skipped_zero = 0
    skipped_outliers = 0

    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        if COL_DATE not in reader.fieldnames or COL_BIO_AGE not in reader.fieldnames:
            raise ValueError(f"CSV must contain '{COL_DATE}' and '{COL_BIO_AGE}' columns")

        for row in reader:
            date_str = row[COL_DATE].strip()
            try:
                bio_age = float(row[COL_BIO_AGE])

                # Filter out zero values (missing data)
                if bio_age == 0.0:
                    skipped_zero += 1
                    logger.debug(f"Skipped zero age for date {date_str}")
                    continue

                # Filter out unreasonable outliers
                if bio_age < 0 or bio_age > MAX_REASONABLE_AGE:
                    skipped_outliers += 1
                    logger.warning(f"Skipped outlier age {bio_age} for date {date_str}")
                    continue

                # Calculate chronological age at this measurement date
                from datetime import datetime
                measurement_date = datetime.strptime(date_str, '%Y-%m-%d')
                chron_age = calculate_age(birthdate, measurement_date)

                # Calculate delta (biological age - chronological age)
                delta = round(bio_age - chron_age, 1)

                dates.append(date_str)
                bio_ages.append(bio_age)
                chron_ages.append(chron_age)
                deltas.append(delta)

            except (ValueError, KeyError) as e:
                skipped_invalid += 1
                logger.debug(f"Skipped invalid age value for date {date_str}: {e}")
                continue

    if skipped_zero:
        logger.info(f"Skipped {skipped_zero} row(s) with zero age values")
    if skipped_invalid:
        logger.info(f"Skipped {skipped_invalid} row(s) with invalid age values")
    if skipped_outliers:
        logger.warning(f"Skipped {skipped_outliers} outlier(s) (age < 0 or > {MAX_REASONABLE_AGE})")

    return dates, bio_ages, chron_ages, deltas


def generate_visualization(
    csv_path: str,
    html_output: str,
    template_path: str = 'age_trend_template.html'
) -> bool:
    """
    Generate HTML visualization from age history data.

    Args:
        csv_path: Path to the age history CSV file
        html_output: Path to save the generated HTML file
        template_path: Path to the HTML template file

    Returns:
        True if successful, False otherwise
    """
    try:
        dates, bio_ages, chron_ages, deltas = load_age_data(csv_path)
    except FileNotFoundError as e:
        logger.error(str(e))
        return False
    except ValueError as e:
        logger.error(str(e))
        return False

    if not dates:
        logger.error("No valid data points found for visualization")
        return False

    logger.info(f"Loaded {len(dates)} data point(s) for visualization")

    # Read template
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        logger.error(f"Template file not found: {template_path}")
        return False

    # Replace placeholders with JSON data
    html_content = template.replace('{{DATES_JSON}}', json.dumps(dates))
    html_content = html_content.replace('{{BIO_AGES_JSON}}', json.dumps(bio_ages))
    html_content = html_content.replace('{{CHRON_AGES_JSON}}', json.dumps(chron_ages))
    html_content = html_content.replace('{{DELTAS_JSON}}', json.dumps(deltas))

    # Write output
    try:
        with open(html_output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Visualization generated: {html_output}")
        return True
    except IOError as e:
        logger.error(f"Failed to write output file: {e}")
        return False


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Generate interactive HTML visualization of biological age trends.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python visualize_age.py
  python visualize_age.py --input data.csv --output dashboard.html
  python visualize_age.py --verbose
        """
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Path to input age history CSV file (default: age_history.csv)',
        default='age_history.csv'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Path to output HTML file (default: age_trend.html)',
        default='age_trend.html'
    )
    parser.add_argument(
        '--template',
        type=str,
        help='Path to HTML template file (default: age_trend_template.html)',
        default='age_trend_template.html'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logger.setLevel('DEBUG')

    success = generate_visualization(args.input, args.output, args.template)

    if not success:
        exit(1)


if __name__ == "__main__":
    main()
