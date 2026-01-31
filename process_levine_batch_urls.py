"""
Automate processing of Levine PhenoAge batch URLs using Selenium WebDriver.

This script opens each URL from levine_batch_urls.json in a browser,
waits for the Levine Calculator to compute the phenotypic age,
and extracts the result.

Requirements:
    pip install selenium
    Download ChromeDriver: https://chromedriver.chromium.org/
"""

import json
import csv
import os
import time
import argparse
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from logger_config import setup_logger

logger = setup_logger(__name__)


def process_levine_urls_automated(
    batch_file: str,
    output_file: str,
    wait_time: int = 10,
    headless: bool = False,
    incremental: bool = False
) -> bool:
    """
    Process Levine batch URLs and extract phenotypic age results.

    Args:
        batch_file: Path to levine_batch_urls.json
        output_file: Path to save results CSV
        wait_time: Seconds to wait for page load (default: 10)
        headless: Run browser in headless mode (default: False)
        incremental: Only process new dates not in output_file (default: False)

    Returns:
        True if successful, False otherwise
    """
    # Load URLs
    try:
        with open(batch_file, 'r', encoding='utf-8') as f:
            urls_data = json.load(f)
        logger.info(f"Loaded {len(urls_data)} URLs from {batch_file}")
    except FileNotFoundError:
        logger.error(f"File not found: {batch_file}")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return False

    # If incremental mode, filter out already-processed dates
    if incremental and os.path.exists(output_file):
        processed_dates = set()
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    processed_dates.add(row['Measurement Date'])
            logger.info(f"Found {len(processed_dates)} already-processed dates in {output_file}")

            # Filter to only new dates
            original_count = len(urls_data)
            urls_data = [entry for entry in urls_data if entry['date'] not in processed_dates]
            logger.info(f"Incremental mode: processing {len(urls_data)}/{original_count} new dates")

            if not urls_data:
                logger.info("No new dates to process!")
                return True
        except Exception as e:
            logger.warning(f"Could not read existing results, will process all: {e}")

    # Setup Selenium WebDriver
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    try:
        driver = webdriver.Chrome(options=options)
        logger.info("Chrome WebDriver initialized")
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        logger.error("Make sure ChromeDriver is installed and in PATH")
        return False

    results = []

    try:
        for i, entry in enumerate(urls_data, 1):
            date = entry['date']
            url = entry['url']

            logger.info(f"Processing {i}/{len(urls_data)}: {date}")

            try:
                # Load the URL
                driver.get(url)

                # Wait for the page to load
                wait = WebDriverWait(driver, wait_time)

                # The Levine phenotypic age appears in a span with class 'text-4xl'
                # inside bg-primary-100 div, similar to Bortz
                pheno_age = None

                try:
                    # Wait for the result container to appear
                    result_container = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='bg-primary-100']"))
                    )

                    # Find the span with the phenotypic age number
                    age_span = result_container.find_element(By.CSS_SELECTOR, "span.text-4xl")

                    # Wait for the value to change from "00" (initial placeholder)
                    for attempt in range(wait_time * 2):  # Check every 0.5 seconds
                        time.sleep(0.5)
                        age_value = age_span.text.strip()

                        # Check if we have a real result (not "00")
                        if age_value and age_value != "00" and age_value.replace('.', '').isdigit():
                            pheno_age = age_value
                            logger.debug(f"Calculation complete: {pheno_age} years")
                            break

                    if not pheno_age or pheno_age == "00":
                        logger.warning(f"Phenotypic age still showing '00' for {date} - may need manual check")
                        pheno_age = "00 (needs verification)"

                except TimeoutException:
                    logger.warning(f"Timeout waiting for result for {date}")
                    pheno_age = "TIMEOUT"
                except Exception as e:
                    logger.error(f"Error extracting phenotypic age: {e}")
                    pheno_age = "ERROR"

                results.append({
                    'Measurement Date': date,
                    'Levine Phenotypic Age': pheno_age,
                    'Notes': 'Auto-extracted'
                })

                logger.info(f"  Phenotypic Age: {pheno_age}")

                # Small delay to avoid overwhelming the server
                time.sleep(1)

            except Exception as e:
                logger.error(f"Error processing {date}: {e}")
                results.append({
                    'Measurement Date': date,
                    'Levine Phenotypic Age': 'ERROR',
                    'Notes': str(e)
                })

    finally:
        driver.quit()
        logger.info("WebDriver closed")

    # Save results
    if results:
        try:
            # In incremental mode, append to existing file
            if incremental and os.path.exists(output_file):
                # Read existing data
                existing_results = []
                with open(output_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    existing_results = list(reader)

                # Append new results
                all_results = existing_results + results

                # Sort by date
                from datetime import datetime
                all_results.sort(key=lambda x: datetime.strptime(x['Measurement Date'], '%Y-%m-%d'))

                # Write all results
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['Measurement Date', 'Levine Phenotypic Age', 'Notes'])
                    writer.writeheader()
                    writer.writerows(all_results)
                logger.info(f"Appended {len(results)} new results to: {output_file}")
            else:
                # Normal mode - overwrite file
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['Measurement Date', 'Levine Phenotypic Age', 'Notes'])
                    writer.writeheader()
                    writer.writerows(results)
                logger.info(f"Results saved to: {output_file}")
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
        description='Automate processing of batch Levine PhenoAge Calculator URLs.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process_levine_batch_urls.py
  python process_levine_batch_urls.py --headless
  python process_levine_batch_urls.py --wait 15 --verbose

Note: Requires ChromeDriver to be installed and in PATH.
      Download from: https://chromedriver.chromium.org/
        """
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Path to batch URLs JSON file (default: levine_batch_urls.json)',
        default='levine_batch_urls.json'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Path to output CSV file (default: levine_age_history.csv)',
        default='levine_age_history.csv'
    )
    parser.add_argument(
        '--wait',
        type=int,
        help='Seconds to wait for page load (default: 10)',
        default=10
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (no GUI)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--incremental',
        action='store_true',
        help='Only process new dates not already in output file (append mode)'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel('DEBUG')

    logger.warning("NOTE: This script uses the same page structure detection as Bortz.")
    logger.warning("If extraction fails, the page structure may have changed.")

    success = process_levine_urls_automated(args.input, args.output, args.wait, args.headless, args.incremental)

    if not success:
        exit(1)


if __name__ == "__main__":
    main()
