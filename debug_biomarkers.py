"""
Analyze and validate biomarker data from bloodwork CSV.

This script extracts all unique biomarkers from the CSV and samples their values
for data quality verification and debugging purposes.
"""

import argparse
import csv
from collections import defaultdict
from typing import Dict, List

from logger_config import setup_logger

logger = setup_logger(__name__)


def analyze_csv(
    input_file: str,
    output_file: str,
    sample_size: int = 5
) -> bool:
    """
    Analyze biomarker data and generate debug report.

    Args:
        input_file: Path to the bloodwork CSV file
        output_file: Path to save the debug report
        sample_size: Number of sample values to display per biomarker

    Returns:
        True if successful, False otherwise
    """
    markers: Dict[str, List[str]] = defaultdict(list)

    try:
        with open(input_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            if 'Biomarker' not in reader.fieldnames or 'Value' not in reader.fieldnames:
                logger.error("CSV must contain 'Biomarker' and 'Value' columns")
                return False

            row_count = 0
            for row in reader:
                m = row['Biomarker'].strip()
                v = row['Value'].strip()
                markers[m].append(v)
                row_count += 1

            logger.info(f"Processed {row_count} row(s) with {len(markers)} unique biomarker(s)")

    except FileNotFoundError:
        logger.error(f"File not found: {input_file}")
        return False
    except KeyError as e:
        logger.error(f"Missing required column in CSV: {e}")
        return False

    # Write debug report
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Biomarker Analysis Report\n")
            f.write("=" * 80 + "\n\n")

            for m in sorted(markers.keys()):
                unique_vals = list(set(markers[m]))
                total_count = len(markers[m])
                unique_count = len(unique_vals)

                f.write(f"Biomarker: {m}\n")
                f.write(f"  Total measurements: {total_count}\n")
                f.write(f"  Unique values: {unique_count}\n")
                f.write(f"  Sample values (up to {sample_size}): {unique_vals[:sample_size]}\n\n")

        logger.info(f"Debug report saved to: {output_file}")
        return True

    except IOError as e:
        logger.error(f"Failed to write output file: {e}")
        return False


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Analyze and validate biomarker data from bloodwork CSV.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python debug_biomarkers.py
  python debug_biomarkers.py --input data.csv --output report.txt
  python debug_biomarkers.py --samples 10 --verbose
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
        help='Path to output debug report (default: debug_markers.txt)',
        default='debug_markers.txt'
    )
    parser.add_argument(
        '--samples',
        type=int,
        help='Number of sample values to show per biomarker (default: 5)',
        default=5
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

    success = analyze_csv(args.input, args.output, args.samples)

    if not success:
        exit(1)


if __name__ == "__main__":
    main()
