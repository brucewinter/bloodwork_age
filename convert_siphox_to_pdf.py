"""
Convert Siphox CSV data to individual LabCorp-style PDF reports.

This script reads the wide-format Siphox CSV and generates separate PDF files
for each test date, formatted like LabCorp lab reports.

Requirements:
    pip install reportlab
"""

import csv
import os
import argparse
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from logger_config import setup_logger

logger = setup_logger(__name__)


def parse_siphox_csv(csv_file: str) -> Tuple[List[str], Dict[str, Dict[str, any]]]:
    """
    Parse the wide-format Siphox CSV file.

    Args:
        csv_file: Path to the Siphox CSV file

    Returns:
        Tuple of (dates list, data dictionary)
        data dictionary structure: {date: {biomarker: {value, unit, optimal, good, fair, category}}}
    """
    dates = []
    data = {}

    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)

        # Read first row - dates
        header_row = next(reader)
        # Skip first 5 columns (empty/metadata), rest are dates
        dates = [date.strip() for date in header_row[5:] if date.strip()]

        # Initialize data structure
        for date in dates:
            data[date] = {}

        # Read second row - contains "Unit, Optimal, Good, Fair" labels
        next(reader)

        current_category = "General"

        # Read remaining rows
        for row in reader:
            if not row or not row[0].strip():
                continue

            biomarker_name = row[0].strip()

            # Check if this is a category header (no unit)
            if len(row) > 1 and not row[1].strip():
                current_category = biomarker_name
                continue

            # Skip reference-only rows
            if len(row) > 1 and row[1].strip().lower() == 'reference':
                continue

            unit = row[1].strip() if len(row) > 1 else ""
            optimal = row[2].strip() if len(row) > 2 else ""
            good = row[3].strip() if len(row) > 3 else ""
            fair = row[4].strip() if len(row) > 4 else ""

            # Parse values for each date
            for i, date in enumerate(dates):
                value_idx = 5 + i
                if value_idx < len(row):
                    value = row[value_idx].strip()
                    if value and value != '-':
                        data[date][biomarker_name] = {
                            'value': value,
                            'unit': unit,
                            'optimal': optimal,
                            'good': good,
                            'fair': fair,
                            'category': current_category
                        }

    logger.info(f"Parsed {len(dates)} test dates with data")
    return dates, data


def determine_flag(value_str: str, optimal: str, good: str, fair: str) -> str:
    """
    Determine if a value is out of range.

    Args:
        value_str: The measured value as string
        optimal: Optimal range string
        good: Good range string
        fair: Fair range string

    Returns:
        'L' for low, 'H' for high, or '' for normal
    """
    # Handle non-numeric values
    if not value_str or value_str in ['-', 'N/A']:
        return ''

    # Handle special prefixes
    if value_str.startswith('<') or value_str.startswith('>'):
        return ''

    try:
        value = float(value_str)
    except ValueError:
        return ''

    # Try to parse ranges
    def parse_range(range_str: str) -> Tuple[Optional[float], Optional[float]]:
        """Parse range string like '40 - 90' or '> 60' or '< 130'"""
        if not range_str or range_str == '-':
            return None, None

        range_str = range_str.strip()

        # Handle '> X' format
        if range_str.startswith('>'):
            try:
                return float(range_str[1:].strip()), None
            except ValueError:
                return None, None

        # Handle '< X' format
        if range_str.startswith('<'):
            try:
                return None, float(range_str[1:].strip())
            except ValueError:
                return None, None

        # Handle 'X - Y' format
        if ' - ' in range_str:
            parts = range_str.split(' - ')
            try:
                return float(parts[0].strip()), float(parts[1].strip())
            except (ValueError, IndexError):
                return None, None

        return None, None

    # Check against optimal first, then good, then fair
    for range_str in [optimal, good, fair]:
        min_val, max_val = parse_range(range_str)

        if min_val is not None and value < min_val:
            return 'L'
        if max_val is not None and value > max_val:
            return 'H'

        # If we're within this range, no flag
        if min_val is not None or max_val is not None:
            if (min_val is None or value >= min_val) and \
               (max_val is None or value <= max_val):
                return ''

    return ''


def create_pdf_report(date: str, biomarkers: Dict[str, Dict], output_file: str) -> bool:
    """
    Create a LabCorp-style PDF report for a single test date.

    Args:
        date: Test date string
        biomarkers: Dictionary of biomarker data
        output_file: Path to save the PDF

    Returns:
        True if successful, False otherwise
    """
    try:
        # Parse date for formatting
        try:
            date_obj = datetime.strptime(date, '%b %d, %Y')
            formatted_date = date_obj.strftime('%m/%d/%Y')
        except ValueError:
            formatted_date = date

        # Create PDF document
        doc = SimpleDocTemplate(
            output_file,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )

        # Container for elements
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            alignment=TA_CENTER
        )

        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        )

        category_style = ParagraphStyle(
            'CategoryHeader',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#003366'),
            spaceAfter=6,
            spaceBefore=12,
            leftIndent=0
        )

        # Header
        elements.append(Paragraph("LABORATORY REPORT", title_style))
        elements.append(Paragraph(f"Collection Date: {formatted_date}", header_style))
        elements.append(Spacer(1, 0.2*inch))

        # Group biomarkers by category
        categories = {}
        for biomarker, data in biomarkers.items():
            category = data.get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append((biomarker, data))

        # Generate tables for each category
        for category, biomarker_list in sorted(categories.items()):
            if category != "General":
                elements.append(Paragraph(category, category_style))

            # Table data
            table_data = [[
                Paragraph('<b>Test Name</b>', styles['Normal']),
                Paragraph('<b>Result</b>', styles['Normal']),
                Paragraph('<b>Flag</b>', styles['Normal']),
                Paragraph('<b>Unit</b>', styles['Normal']),
                Paragraph('<b>Reference Range</b>', styles['Normal'])
            ]]

            for biomarker, data in sorted(biomarker_list):
                value = data['value']
                unit = data['unit']

                # Build reference range string
                ref_range = data.get('optimal', '')
                if not ref_range and data.get('good'):
                    ref_range = data['good']
                if not ref_range and data.get('fair'):
                    ref_range = data['fair']

                # Determine flag
                flag = determine_flag(
                    value,
                    data.get('optimal', ''),
                    data.get('good', ''),
                    data.get('fair', '')
                )

                # Format flag with color
                if flag == 'H':
                    flag_text = '<font color="red"><b>H</b></font>'
                elif flag == 'L':
                    flag_text = '<font color="blue"><b>L</b></font>'
                else:
                    flag_text = ''

                table_data.append([
                    Paragraph(biomarker, styles['Normal']),
                    Paragraph(f'<b>{value}</b>', styles['Normal']),
                    Paragraph(flag_text, styles['Normal']),
                    Paragraph(unit, styles['Normal']),
                    Paragraph(ref_range, styles['Normal'])
                ])

            # Create table
            table = Table(table_data, colWidths=[3*inch, 1*inch, 0.5*inch, 0.8*inch, 1.7*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8E8E8')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#003366')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#003366')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 0.15*inch))

        # Footer
        elements.append(Spacer(1, 0.2*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER
        )
        elements.append(Paragraph(
            f"Report generated from Siphox data | {formatted_date}<br/>"
            "H = High, L = Low | Reference ranges based on Optimal/Good/Fair criteria",
            footer_style
        ))

        # Build PDF
        doc.build(elements)
        logger.info(f"Generated PDF: {output_file}")
        return True

    except Exception as e:
        logger.error(f"Error creating PDF for {date}: {e}")
        return False


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Convert Siphox CSV to LabCorp-style PDF reports.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python convert_siphox_to_pdf.py
  python convert_siphox_to_pdf.py --input siphox_data.csv --output-dir reports/
  python convert_siphox_to_pdf.py --verbose

Output:
  Creates individual PDF files named: LabReport_YYYY-MM-DD.pdf
        """
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Path to input Siphox CSV file (default: siphox_2025_08b.csv)',
        default='siphox_2025_08b.csv'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Directory to save PDF reports (default: siphox_reports/)',
        default='siphox_reports'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel('DEBUG')

    # Check input file exists
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    logger.info(f"Output directory: {args.output_dir}")

    # Parse CSV
    try:
        dates, data = parse_siphox_csv(args.input)
    except Exception as e:
        logger.error(f"Error parsing CSV: {e}")
        return

    # Generate PDFs
    success_count = 0
    for date in dates:
        biomarkers = data.get(date, {})

        if not biomarkers:
            logger.warning(f"No data for date: {date}")
            continue

        # Create safe filename from date
        try:
            date_obj = datetime.strptime(date, '%b %d, %Y')
            filename = f"LabReport_{date_obj.strftime('%Y-%m-%d')}.pdf"
        except ValueError:
            # Fallback to sanitized date string
            filename = f"LabReport_{date.replace(' ', '_').replace(',', '')}.pdf"

        output_path = os.path.join(args.output_dir, filename)

        if create_pdf_report(date, biomarkers, output_path):
            success_count += 1

    logger.info(f"\nSuccessfully generated {success_count}/{len(dates)} PDF reports")
    logger.info(f"Reports saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
