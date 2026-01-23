"""
Generate Levine PhenoAge Calculator URL from bloodwork CSV data.

This script processes bloodwork measurements from a CSV file and generates
a URL for the Levine PhenoAge Calculator with the latest biomarker values.
"""

import argparse
import csv
import urllib.parse
from datetime import datetime
from typing import Optional, Dict, Any

from biomarkers import clean_value, is_valid_numeric
from levine_biomarkers import LEVINE_BIOMARKER_MAP, LEVINE_BASE_URL, validate_levine_data
from logger_config import setup_logger
from config import get_birthdate, calculate_age

# Column names
COL_BIOMARKER = 'Biomarker'
COL_VALUE = 'Value'
COL_UNIT = 'Unit'
COL_DATE = 'Measurement Date'

logger = setup_logger(__name__)


def generate_levine_url(
    csv_file: str,
    output_file: str,
    cutoff_date_str: Optional[str] = None
) -> Optional[str]:
    """
    Generate Levine PhenoAge Calculator URL from CSV data.

    Args:
        csv_file: Path to the bloodwork CSV file
        output_file: Path to save the generated URL
        cutoff_date_str: Optional cutoff date (YYYY-MM-DD). Only uses data on or before this date.

    Returns:
        The generated URL string, or None if generation failed
    """
    data: Dict[str, Dict[str, Any]] = {}

    cutoff_date = None
    if cutoff_date_str:
        try:
            cutoff_date = datetime.strptime(cutoff_date_str, '%Y-%m-%d')
            logger.info(f"Using cutoff date: {cutoff_date_str}")
        except ValueError:
            logger.error(f"Invalid date format '{cutoff_date_str}'. Please use YYYY-MM-DD.")
            return None

    try:
        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [fn.strip() for fn in reader.fieldnames]

            skipped_unknown = set()
            skipped_invalid = 0
            skipped_date_errors = 0

            for row in reader:
                raw_marker = row[COL_BIOMARKER].strip()

                # Skip unknown biomarkers
                if raw_marker not in LEVINE_BIOMARKER_MAP:
                    skipped_unknown.add(raw_marker)
                    continue

                marker_id = LEVINE_BIOMARKER_MAP[raw_marker]

                # Skip Age - we'll calculate it automatically from birthdate
                if marker_id == 'age':
                    logger.debug(f"Skipping Age from CSV - will calculate from birthdate")
                    continue

                raw_value = row[COL_VALUE].strip()
                value = clean_value(raw_value)

                # Validate numeric value
                if not is_valid_numeric(value):
                    skipped_invalid += 1
                    logger.debug(f"Skipped invalid value for {raw_marker}: '{raw_value}'")
                    continue

                unit = row[COL_UNIT].strip()
                date_str = row[COL_DATE].strip()

                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    skipped_date_errors += 1
                    logger.warning(f"Invalid date format for {raw_marker}: '{date_str}'")
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

            # Log skipped data
            if skipped_unknown:
                logger.debug(f"Skipped {len(skipped_unknown)} unknown biomarker(s) for Levine")
            if skipped_invalid:
                logger.info(f"Skipped {skipped_invalid} row(s) with invalid values")
            if skipped_date_errors:
                logger.warning(f"Skipped {skipped_date_errors} row(s) with invalid dates")

    except FileNotFoundError:
        logger.error(f"File not found: {csv_file}")
        return None
    except KeyError as e:
        logger.error(f"Missing required column in CSV: {e}")
        return None

    if not data:
        logger.warning(f"No valid biomarkers found in CSV {'before ' + cutoff_date_str if cutoff_date_str else ''}")
        return None

    logger.info(f"Successfully loaded {len(data)} biomarker(s) for Levine")

    # Calculate age automatically from birthdate and most recent measurement date
    try:
        birthdate = get_birthdate()
        most_recent_date = max(info['date'] for info in data.values())
        calculated_age = calculate_age(birthdate, most_recent_date)

        # Add age to the data
        data['age'] = {
            'value': str(calculated_age),
            'unit': 'years',
            'date': most_recent_date
        }
        logger.info(f"Calculated age at {most_recent_date.strftime('%Y-%m-%d')}: {calculated_age} years")
    except ValueError as e:
        logger.error(f"Error calculating age: {e}")
        logger.error("Please update BIRTHDATE in config.py with format YYYY-MM-DD")
        return None

    # Validate we have all required biomarkers for Levine
    is_valid, missing = validate_levine_data(data)
    if not is_valid:
        logger.error(f"Missing required biomarkers for Levine calculator: {', '.join(missing)}")
        logger.error("Levine requires: albumin, creatinine, glucose, hsCRP, lymphocyte %, MCV, RDW, ALP, WBC, age")
        return None

    # Construct the query parameters (Levine uses simple format: biomarker=value)
    params = []

    # Sort markers by ID for consistent URL generation
    for marker_id in sorted(data.keys()):
        info = data[marker_id]
        # Levine uses simple value format without units in URL
        params.append(f"{marker_id}={info['value']}")

    final_url = LEVINE_BASE_URL + '&'.join(params)

    # Save to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_url)
        logger.info(f"Levine URL saved to: {output_file}")
    except IOError as e:
        logger.error(f"Failed to write output file: {e}")
        return None

    date_context = f" (data on or before {cutoff_date_str})" if cutoff_date_str else ""
    logger.info(f"Generated Levine PhenoAge Calculator URL{date_context}")
    print(f"\n{final_url}\n")

    return final_url


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Generate Levine PhenoAge Calculator URL from bloodwork CSV.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_levine_url.py
  python generate_levine_url.py --date 2024-12-31
  python generate_levine_url.py --input data.csv --output levine_url.txt
  python generate_levine_url.py --verbose
        """
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Cutoff date (YYYY-MM-DD). Only uses data on or before this date.',
        default=None
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Path to input CSV file (default: bloodwork.csv)',
        default='bloodwork.csv'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Path to output URL file (default: levine_url.txt)',
        default='levine_url.txt'
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

    generate_levine_url(args.input, args.output, args.date)


if __name__ == "__main__":
    main()
