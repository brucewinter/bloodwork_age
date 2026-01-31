"""
Incremental update script for bloodwork age analysis.

This script processes only new measurement dates that aren't already in
the existing batch_urls.json and age_history.csv files, avoiding
reprocessing of historical data.

Usage:
    python update_incremental.py
    python update_incremental.py --input new_bloodwork.csv --calculator Both
"""

import argparse
import json
import csv
import os
from typing import Set, List, Dict
from datetime import datetime

from logger_config import setup_logger
from generate_batch_urls import get_all_bortz_urls
from generate_levine_batch_urls import get_all_levine_urls

logger = setup_logger(__name__)


def get_existing_dates(json_file: str) -> Set[str]:
    """
    Get set of dates already processed in batch URLs file.

    Args:
        json_file: Path to batch_urls.json or levine_batch_urls.json

    Returns:
        Set of date strings already processed
    """
    if not os.path.exists(json_file):
        logger.info(f"{json_file} not found, will process all dates")
        return set()

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            dates = {entry['date'] for entry in data}
            logger.info(f"Found {len(dates)} existing dates in {json_file}")
            return dates
    except Exception as e:
        logger.error(f"Error reading {json_file}: {e}")
        return set()


def get_csv_dates(csv_file: str) -> Set[str]:
    """
    Get all unique measurement dates from CSV.

    Args:
        csv_file: Path to bloodwork CSV

    Returns:
        Set of all date strings in CSV
    """
    dates = set()
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                date = row.get('Measurement Date', '').strip()
                if date:
                    dates.add(date)
        logger.info(f"Found {len(dates)} unique dates in {csv_file}")
        return dates
    except Exception as e:
        logger.error(f"Error reading {csv_file}: {e}")
        return set()


def append_to_batch_urls(json_file: str, new_entries: List[Dict]) -> bool:
    """
    Append new URL entries to existing batch_urls.json.

    Args:
        json_file: Path to batch_urls.json
        new_entries: List of new {date, url} entries

    Returns:
        True if successful
    """
    # Load existing data
    existing_data = []
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except Exception as e:
            logger.error(f"Error reading {json_file}: {e}")
            return False

    # Append new entries
    existing_data.extend(new_entries)

    # Sort by date
    existing_data.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))

    # Save back
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2)
        logger.info(f"Appended {len(new_entries)} new entries to {json_file}")
        return True
    except Exception as e:
        logger.error(f"Error writing {json_file}: {e}")
        return False


def filter_new_dates_from_urls(all_urls: List[Dict], existing_dates: Set[str]) -> List[Dict]:
    """
    Filter URL list to only include new dates.

    Args:
        all_urls: Full list of URL entries from generator
        existing_dates: Set of dates already processed

    Returns:
        List of URL entries for new dates only
    """
    new_urls = [entry for entry in all_urls if entry['date'] not in existing_dates]
    logger.info(f"Filtered to {len(new_urls)} new dates (from {len(all_urls)} total)")
    return new_urls


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Incremental update for bloodwork age analysis.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python update_incremental.py
  python update_incremental.py --input new_bloodwork.csv
  python update_incremental.py --calculator Bortz
  python update_incremental.py --calculator Both --verbose

This script:
  1. Identifies dates not yet in batch_urls.json/levine_batch_urls.json
  2. Generates URLs only for new dates
  3. Appends new URLs to existing JSON files
  4. Displays summary of what needs to be processed

After running, use process_batch_urls.py with --incremental flag
to process only the new URLs.
        """
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Path to bloodwork CSV (default: bloodwork.csv)',
        default='bloodwork.csv'
    )
    parser.add_argument(
        '--calculator',
        type=str,
        choices=['Bortz', 'Levine', 'Both'],
        help='Which calculator to update (default: Both)',
        default='Both'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel('DEBUG')

    # Check input file
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return

    # Get all dates from CSV
    csv_dates = get_csv_dates(args.input)
    if not csv_dates:
        logger.error("No dates found in CSV")
        return

    run_bortz = args.calculator in ['Bortz', 'Both']
    run_levine = args.calculator in ['Levine', 'Both']

    # Process Bortz
    if run_bortz:
        logger.info("\n=== Processing Bortz Blood Age Calculator ===")
        existing_bortz_dates = get_existing_dates('batch_urls.json')
        new_bortz_dates = csv_dates - existing_bortz_dates

        if new_bortz_dates:
            logger.info(f"Found {len(new_bortz_dates)} new dates for Bortz")
            logger.info(f"New dates: {sorted(new_bortz_dates)}")

            # Generate URLs for ALL dates (generator handles filtering internally)
            # but we'll need to filter the output
            from generate_batch_urls import get_all_bortz_urls

            # Temporarily save to get full output
            temp_file = 'temp_batch_urls.json'
            all_urls = get_all_bortz_urls(args.input, temp_file)

            if all_urls:
                # Filter to only new dates
                new_urls = filter_new_dates_from_urls(all_urls, existing_bortz_dates)

                if new_urls:
                    # Append to existing batch_urls.json
                    if append_to_batch_urls('batch_urls.json', new_urls):
                        logger.info(f"✓ Added {len(new_urls)} new Bortz URLs")
                    else:
                        logger.error("Failed to append Bortz URLs")
                else:
                    logger.info("No new valid Bortz URLs to add")

            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
        else:
            logger.info("✓ No new dates for Bortz - already up to date")

    # Process Levine
    if run_levine:
        logger.info("\n=== Processing Levine PhenoAge Calculator ===")
        existing_levine_dates = get_existing_dates('levine_batch_urls.json')
        new_levine_dates = csv_dates - existing_levine_dates

        if new_levine_dates:
            logger.info(f"Found {len(new_levine_dates)} new dates for Levine")
            logger.info(f"New dates: {sorted(new_levine_dates)}")

            # Generate URLs for ALL dates
            from generate_levine_batch_urls import get_all_levine_urls

            temp_file = 'temp_levine_batch_urls.json'
            all_urls = get_all_levine_urls(args.input, temp_file)

            if all_urls:
                # Filter to only new dates
                new_urls = filter_new_dates_from_urls(all_urls, existing_levine_dates)

                if new_urls:
                    # Append to existing levine_batch_urls.json
                    if append_to_batch_urls('levine_batch_urls.json', new_urls):
                        logger.info(f"✓ Added {len(new_urls)} new Levine URLs")
                    else:
                        logger.error("Failed to append Levine URLs")
                else:
                    logger.info("No new valid Levine URLs to add")

            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
        else:
            logger.info("✓ No new dates for Levine - already up to date")

    # Summary
    logger.info("\n=== Summary ===")
    logger.info("Next steps:")
    logger.info("1. Run process scripts to extract ages for new dates:")

    if run_bortz:
        bortz_count = len(csv_dates - get_existing_dates('batch_urls.json'))
        if bortz_count > 0:
            logger.info(f"   python process_batch_urls.py --incremental  ({bortz_count} new dates)")

    if run_levine:
        levine_count = len(csv_dates - get_existing_dates('levine_batch_urls.json'))
        if levine_count > 0:
            logger.info(f"   python process_levine_batch_urls.py --incremental  ({levine_count} new dates)")

    logger.info("2. Regenerate visualizations:")
    logger.info("   .\\Quick-Visualize.ps1")


if __name__ == "__main__":
    main()
