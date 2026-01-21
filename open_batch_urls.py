"""
Semi-automated batch URL processor.

Opens URLs one at a time in your default browser with pauses,
allowing you to manually record results.
"""

import json
import webbrowser
import time
import csv
import argparse
from typing import Optional

from logger_config import setup_logger

logger = setup_logger(__name__)


def open_urls_interactive(
    batch_file: str,
    output_file: str,
    delay: int = 5
) -> bool:
    """
    Open URLs interactively in browser with manual data entry.

    Args:
        batch_file: Path to batch_urls.json
        output_file: Path to save results CSV
        delay: Seconds to wait between URLs (default: 5)

    Returns:
        True if successful, False otherwise
    """
    # Load URLs
    try:
        with open(batch_file, 'r', encoding='utf-8') as f:
            urls_data = json.load(f)
        logger.info(f"Loaded {len(urls_data)} URLs to process")
    except FileNotFoundError:
        logger.error(f"File not found: {batch_file}")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return False

    results = []

    print("\n" + "="*60)
    print("INTERACTIVE URL PROCESSOR")
    print("="*60)
    print(f"Total URLs to process: {len(urls_data)}")
    print(f"Delay between URLs: {delay} seconds")
    print("\nInstructions:")
    print("1. Each URL will open in your browser")
    print("2. Note the biological age from the calculator")
    print("3. Enter it when prompted")
    print("4. Press Enter to continue to next URL")
    print("5. Enter 'skip' to skip a URL")
    print("6. Enter 'quit' to stop processing")
    print("="*60 + "\n")

    input("Press Enter to start...")

    for i, entry in enumerate(urls_data, 1):
        date = entry['date']
        url = entry['url']

        print(f"\n[{i}/{len(urls_data)}] Processing date: {date}")
        print(f"Opening URL in browser...")

        # Open URL in default browser
        webbrowser.open(url)

        # Wait for page to load
        time.sleep(delay)

        # Prompt for biological age
        while True:
            bio_age = input(f"Enter biological age for {date} (or 'skip'/'quit'): ").strip()

            if bio_age.lower() == 'quit':
                logger.info("User requested quit")
                print("\nStopping... Saving partial results.")
                break

            if bio_age.lower() == 'skip':
                logger.info(f"Skipping {date}")
                results.append({
                    'Measurement Date': date,
                    'Bortz Biological Age': '',
                    'Notes': 'Skipped'
                })
                break

            # Validate input is numeric
            try:
                float(bio_age)
                results.append({
                    'Measurement Date': date,
                    'Bortz Biological Age': bio_age,
                    'Notes': 'Manual entry'
                })
                logger.info(f"Recorded: {date} → {bio_age}")
                break
            except ValueError:
                print("Invalid input. Please enter a number, 'skip', or 'quit'.")

        if bio_age.lower() == 'quit':
            break

    # Save results
    if results:
        try:
            # Read existing data if file exists
            existing_data = {}
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        existing_data[row['Measurement Date']] = row
            except FileNotFoundError:
                pass

            # Merge new results with existing
            for result in results:
                existing_data[result['Measurement Date']] = result

            # Write combined data
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['Measurement Date', 'Bortz Biological Age', 'Notes'])
                writer.writeheader()
                for date in sorted(existing_data.keys()):
                    writer.writerow(existing_data[date])

            logger.info(f"Results saved to: {output_file}")
            print(f"\n✓ Saved {len(results)} result(s) to {output_file}")
            return True

        except IOError as e:
            logger.error(f"Failed to write output file: {e}")
            return False
    else:
        logger.warning("No results to save")
        return False


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Interactively process batch URLs with manual data entry.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python open_batch_urls.py
  python open_batch_urls.py --delay 10
  python open_batch_urls.py --input urls.json --output results.csv

This script opens each URL in your browser and prompts you to enter
the biological age result manually. Great for when automation isn't
working or you want more control.
        """
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Path to batch URLs JSON file (default: batch_urls.json)',
        default='batch_urls.json'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Path to output CSV file (default: age_history.csv)',
        default='age_history.csv'
    )
    parser.add_argument(
        '--delay',
        type=int,
        help='Seconds to wait after opening URL (default: 5)',
        default=5
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel('DEBUG')

    success = open_urls_interactive(args.input, args.output, args.delay)

    if not success:
        exit(1)


if __name__ == "__main__":
    main()
