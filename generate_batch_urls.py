"""
Generate batch Bortz Blood Age Calculator URLs for all historical dates.

This script processes bloodwork measurements and creates a separate URL for
each unique measurement date, allowing historical trend analysis.
"""

import argparse
import csv
import json
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any, Optional

from biomarkers import BIOMARKER_MAP, BASE_URL, clean_value, is_valid_numeric, normalize_unit
from logger_config import setup_logger
from config import get_birthdate, calculate_age

# Column names
COL_BIOMARKER = 'Biomarker'
COL_VALUE = 'Value'
COL_UNIT = 'Unit'
COL_DATE = 'Measurement Date'

logger = setup_logger(__name__)


def get_all_urls(csv_file: str, output_file: str) -> Optional[List[Dict[str, str]]]:
    """
    Generate Bortz Calculator URLs for all unique measurement dates.

    For each unique date in the CSV, this function creates a URL containing
    the latest values of each biomarker up to and including that date.

    Args:
        csv_file: Path to the bloodwork CSV file
        output_file: Path to save the batch URLs JSON

    Returns:
        List of dictionaries with 'date' and 'url' keys, or None on error
    """
    # Load all data
    all_rows = []
    unique_dates = set()

    try:
        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Strip whitespace from field names
            reader.fieldnames = [fn.strip() for fn in reader.fieldnames]

            for row in reader:
                all_rows.append(row)
                unique_dates.add(row[COL_DATE].strip())

        logger.info(f"Loaded {len(all_rows)} rows with {len(unique_dates)} unique date(s)")

    except FileNotFoundError:
        logger.error(f"File not found: {csv_file}")
        return None
    except KeyError as e:
        logger.error(f"Missing required column in CSV: {e}")
        return None

    sorted_dates = sorted(list(unique_dates))
    results = []
    skipped_dates = []

    for cutoff_str in sorted_dates:
        try:
            cutoff_date = datetime.strptime(cutoff_str, '%Y-%m-%d')
        except ValueError:
            logger.warning(f"Invalid date format: '{cutoff_str}'")
            skipped_dates.append(cutoff_str)
            continue

        data: Dict[str, Dict[str, Any]] = {}
        skipped_invalid = 0

        for row in all_rows:
            raw_marker = row[COL_BIOMARKER].strip()
            if raw_marker not in BIOMARKER_MAP:
                continue

            marker_id = BIOMARKER_MAP[raw_marker]

            # Skip Age - we'll calculate it automatically from birthdate
            if marker_id == 'age':
                continue

            value = clean_value(row[COL_VALUE].strip())

            if not is_valid_numeric(value):
                skipped_invalid += 1
                continue

            unit = row[COL_UNIT].strip()
            date_str = row[COL_DATE].strip()

            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                continue

            # Only include data up to and including the cutoff date
            if date_obj <= cutoff_date:
                if marker_id not in data or date_obj > data[marker_id]['date']:
                    data[marker_id] = {'value': value, 'unit': unit, 'date': date_obj}

        if not data:
            logger.warning(f"No valid data for date {cutoff_str}, skipping")
            continue

        # Calculate age automatically from birthdate and cutoff date
        try:
            birthdate = get_birthdate()
            calculated_age = calculate_age(birthdate, cutoff_date)

            # Add age to the data
            data['age'] = {
                'value': str(calculated_age),
                'unit': 'years',
                'date': cutoff_date
            }
            logger.debug(f"Calculated age for {cutoff_str}: {calculated_age} years")
        except ValueError as e:
            logger.error(f"Error calculating age: {e}")
            logger.error("Please update BIRTHDATE in config.py with format YYYY-MM-DD")
            return None

        # Construct URL parameters
        params = []
        for marker_id in sorted(data.keys()):
            info = data[marker_id]
            unit = normalize_unit(info['unit'])
            val_unit = f"{info['value']}_{unit}"
            params.append(f"{marker_id}={urllib.parse.quote(val_unit, safe='')}")

        results.append({
            "date": cutoff_str,
            "url": BASE_URL + '&'.join(params)
        })

        logger.debug(f"Generated URL for {cutoff_str} with {len(data)} biomarker(s)")

    if skipped_dates:
        logger.warning(f"Skipped {len(skipped_dates)} date(s) with invalid format")

    # Save results to JSON
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Generated {len(results)} URL(s) and saved to: {output_file}")
    except IOError as e:
        logger.error(f"Failed to write output file: {e}")
        return None

    return results


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Generate batch Bortz Blood Age Calculator URLs for historical analysis.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_batch_urls.py
  python generate_batch_urls.py --input data.csv --output urls.json
  python generate_batch_urls.py --verbose
        """
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
        help='Path to output JSON file (default: batch_urls.json)',
        default='batch_urls.json'
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

    get_all_urls(args.input, args.output)


if __name__ == "__main__":
    main()
