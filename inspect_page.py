"""
Helper script to inspect the Bortz Calculator page and find the biological age result element.
"""

import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Load first URL
with open('batch_urls.json', 'r') as f:
    urls_data = json.load(f)

first_url = urls_data[0]['url']
print(f"Opening first URL: {urls_data[0]['date']}")
print(f"URL: {first_url[:100]}...")

# Setup browser
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

try:
    # Open URL
    driver.get(first_url)

    print("\nWaiting for page to load and calculate...")
    time.sleep(10)  # Give page time to calculate biological age

    print("\n" + "="*60)
    print("PAGE INSPECTION")
    print("="*60)

    # First, try to find the biological age result directly
    print("\nLooking for biological age result...")
    try:
        # Look for elements with class containing "bg-primary"
        result_divs = driver.find_elements(By.CSS_SELECTOR, "[class*='bg-primary']")
        for div in result_divs:
            text = div.text
            if 'biological age' in text.lower() or 'bortz' in text.lower():
                print(f"\nFound result container:")
                print(f"Text: {text}")
                print(f"Classes: {div.get_attribute('class')}")

                # Look for the actual number (should be XX years)
                spans = div.find_elements(By.TAG_NAME, 'span')
                for span in spans:
                    span_text = span.text.strip()
                    if 'years' in span_text or span_text.replace('.', '').isdigit():
                        print(f"\n>>> BIOLOGICAL AGE FOUND: {span_text}")
                        print(f"    Element: <span class='{span.get_attribute('class')}'>")
                        print(f"    ID: {span.get_attribute('id')}")
    except Exception as e:
        print(f"Error searching for result: {e}")

    # Try to find elements that might contain the biological age
    print("\nSearching for possible biological age elements...\n")

    # Strategy 1: Look for text containing "age" or "biological"
    possible_elements = []

    # Try various tag types
    for tag in ['span', 'div', 'p', 'h1', 'h2', 'h3', 'td', 'strong']:
        elements = driver.find_elements(By.TAG_NAME, tag)
        for elem in elements:
            text = elem.text.strip()
            if text and any(keyword in text.lower() for keyword in ['age', 'biological', 'years']):
                # Check if it looks like a number
                if any(char.isdigit() for char in text):
                    try:
                        # Get element attributes
                        elem_id = elem.get_attribute('id')
                        elem_class = elem.get_attribute('class')
                        possible_elements.append({
                            'tag': tag,
                            'text': text,
                            'id': elem_id,
                            'class': elem_class
                        })
                    except:
                        pass

    # Print found elements
    if possible_elements:
        print("Found potential biological age elements:")
        for i, elem in enumerate(possible_elements[:10], 1):  # Show first 10
            print(f"\n{i}. <{elem['tag']}>")
            print(f"   Text: {elem['text'][:100]}")
            if elem['id']:
                print(f"   ID: {elem['id']}")
            if elem['class']:
                print(f"   Class: {elem['class']}")
    else:
        print("No obvious elements found. The page might use JavaScript to render results.")
        print("\nDumping page source for manual inspection...")
        print("="*60)
        # print(driver.page_source[:2000])  # First 2000 chars

    # Keep browser open for manual inspection
    print("\n" + "="*60)
    print("Browser will stay open for 30 seconds for manual inspection.")
    print("Please look at the browser and note:")
    print("1. Where the biological age result appears")
    print("2. Right-click the number → Inspect Element")
    print("3. Note the element's ID, class, or structure")
    print("="*60)

    time.sleep(30)

finally:
    driver.quit()
    print("\nBrowser closed.")
