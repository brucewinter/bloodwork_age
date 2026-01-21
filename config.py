"""
Configuration settings for bloodwork age calculator.

Edit this file to set your personal information.
"""

from datetime import datetime

# Your birthdate in YYYY-MM-DD format
# This is used to automatically calculate your chronological age at each test date
BIRTHDATE = "1958-07-08"  # UPDATE THIS WITH YOUR ACTUAL BIRTHDATE

def get_birthdate() -> datetime:
    """
    Get the configured birthdate as a datetime object.

    Returns:
        datetime object of the birthdate

    Raises:
        ValueError: If birthdate format is invalid
    """
    try:
        return datetime.strptime(BIRTHDATE, '%Y-%m-%d')
    except ValueError as e:
        raise ValueError(f"Invalid birthdate format in config.py. Use YYYY-MM-DD format. Error: {e}")


def calculate_age(birthdate: datetime, test_date: datetime) -> float:
    """
    Calculate age in years at a given test date.

    Args:
        birthdate: Date of birth
        test_date: Date of the test

    Returns:
        Age in years (with decimal precision)
    """
    # Calculate age in days and convert to years
    age_days = (test_date - birthdate).days
    age_years = age_days / 365.25  # Account for leap years

    return round(age_years, 1)
