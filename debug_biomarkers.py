import csv
from collections import defaultdict

def analyze_csv():
    markers = defaultdict(list)
    try:
        with open('bloodwork.csv', mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                m = row['Biomarker']
                v = row['Value']
                markers[m].append(v)
        
        with open('debug_markers.txt', 'w', encoding='utf-8') as f:
            for m in sorted(markers.keys()):
                unique_vals = list(set(markers[m]))[:2]
                f.write(f"{m} | Samples: {unique_vals}\n")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    analyze_csv()
