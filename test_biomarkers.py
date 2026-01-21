"""
Unit tests for biomarker processing functions.

Run with: python -m pytest test_biomarkers.py -v
Or: python test_biomarkers.py
"""

import unittest
from biomarkers import clean_value, is_valid_numeric, normalize_unit, BIOMARKER_MAP


class TestCleanValue(unittest.TestCase):
    """Test the clean_value function."""

    def test_clean_with_less_than(self):
        """Test cleaning values with '<' prefix."""
        self.assertEqual(clean_value('<5.0'), '5.0')

    def test_clean_with_greater_than(self):
        """Test cleaning values with '>' prefix."""
        self.assertEqual(clean_value('>10.0'), '10.0')

    def test_clean_with_equals(self):
        """Test cleaning values with '=' prefix."""
        self.assertEqual(clean_value('=7.5'), '7.5')

    def test_clean_with_whitespace(self):
        """Test cleaning values with extra whitespace."""
        self.assertEqual(clean_value('  12.3  '), '12.3')

    def test_clean_multiple_operators(self):
        """Test cleaning values with multiple operators."""
        self.assertEqual(clean_value('<=5.0'), '5.0')

    def test_clean_empty_string(self):
        """Test cleaning empty string."""
        self.assertEqual(clean_value(''), '')

    def test_clean_none(self):
        """Test cleaning None value."""
        self.assertEqual(clean_value(None), '')


class TestIsValidNumeric(unittest.TestCase):
    """Test the is_valid_numeric function."""

    def test_valid_integer(self):
        """Test valid integer string."""
        self.assertTrue(is_valid_numeric('42'))

    def test_valid_float(self):
        """Test valid float string."""
        self.assertTrue(is_valid_numeric('3.14'))

    def test_valid_negative(self):
        """Test valid negative number."""
        self.assertTrue(is_valid_numeric('-5.5'))

    def test_valid_scientific_notation(self):
        """Test valid scientific notation."""
        self.assertTrue(is_valid_numeric('1.5e-10'))

    def test_invalid_data_not_available(self):
        """Test 'data not available' string."""
        self.assertFalse(is_valid_numeric('data not available'))

    def test_invalid_na(self):
        """Test 'N/A' string."""
        self.assertFalse(is_valid_numeric('N/A'))

    def test_invalid_pending(self):
        """Test 'pending' string."""
        self.assertFalse(is_valid_numeric('pending'))

    def test_invalid_text(self):
        """Test random text."""
        self.assertFalse(is_valid_numeric('not a number'))

    def test_invalid_empty(self):
        """Test empty string."""
        self.assertFalse(is_valid_numeric(''))

    def test_invalid_mixed(self):
        """Test mixed alphanumeric string."""
        self.assertFalse(is_valid_numeric('12abc'))


class TestNormalizeUnit(unittest.TestCase):
    """Test the normalize_unit function."""

    def test_normalize_percent(self):
        """Test normalization of percent sign."""
        self.assertEqual(normalize_unit('%'), '%25')

    def test_normalize_regular_unit(self):
        """Test that regular units pass through unchanged."""
        self.assertEqual(normalize_unit('mg/dL'), 'mg/dL')
        self.assertEqual(normalize_unit('mmol/L'), 'mmol/L')
        self.assertEqual(normalize_unit('g/L'), 'g/L')


class TestBiomarkerMap(unittest.TestCase):
    """Test the biomarker mapping dictionary."""

    def test_map_contains_key_markers(self):
        """Test that key biomarkers are mapped."""
        essential_markers = [
            'Age', 'Albumin', 'ALP', 'Creatinine', 'Glucose',
            'HbA1c', 'Cholesterol', 'RBC', 'MCV'
        ]
        for marker in essential_markers:
            self.assertIn(marker, BIOMARKER_MAP)

    def test_map_has_aliases(self):
        """Test that common aliases are included."""
        self.assertIn('Total Cholesterol', BIOMARKER_MAP)
        self.assertIn('Glucose (Fasting)', BIOMARKER_MAP)
        self.assertIn('Vitamin D, 25-Hydroxy', BIOMARKER_MAP)

    def test_map_aliases_point_to_same_id(self):
        """Test that aliases map to the same ID."""
        self.assertEqual(BIOMARKER_MAP['Cholesterol'], BIOMARKER_MAP['Total Cholesterol'])
        self.assertEqual(BIOMARKER_MAP['Glucose'], BIOMARKER_MAP['Glucose (Fasting)'])


if __name__ == '__main__':
    unittest.main()
