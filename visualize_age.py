import csv
import json
import os

def generate_visualization(csv_path, html_output):
    dates = []
    ages = []
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    with open(csv_path, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row['Measurement Date']
            try:
                age = float(row['Bortz Biological Age'])
                # Filter out 0.0 results (missing data)
                if age > 0:
                    dates.append(date)
                    ages.append(age)
            except ValueError:
                continue

    if not dates:
        print("No valid data points found for visualization.")
        return

    # Use a modern, premium Chart.js template
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bio-Age Trends</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-color: #f8fafc;
            --primary: #38bdf8;
            --secondary: #818cf8;
            --accent: #f472b6;
        }}
        body {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Outfit', sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            width: 100%;
            max-width: 1000px;
            background: var(--card-bg);
            padding: 40px;
            border-radius: 24px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        h1 {{
            font-weight: 600;
            font-size: 2.5rem;
            margin-bottom: 8px;
            background: linear-gradient(to right, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        p.subtitle {{
            color: #94a3b8;
            margin-bottom: 40px;
            font-size: 1.1rem;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            width: 100%;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }}
        .stat-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 16px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .stat-value {{
            font-size: 2rem;
            font-weight: 600;
            color: var(--primary);
        }}
        .stat-label {{
            color: #94a3b8;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Bio-Age Trends</h1>
        <p class="subtitle">Historical analysis of Humanity's Bortz Biological Age</p>
        
        <div class="chart-container">
            <canvas id="ageChart"></canvas>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="minAge">-</div>
                <div class="stat-label">Lowest Bio-Age</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="maxAge">-</div>
                <div class="stat-label">Highest Bio-Age</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avgAge">-</div>
                <div class="stat-label">Average Bio-Age</div>
            </div>
        </div>
    </div>

    <script>
        const dates = {json.dumps(dates)};
        const ages = {json.dumps(ages)};

        const ctx = document.getElementById('ageChart').getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(56, 189, 248, 0.4)');
        gradient.addColorStop(1, 'rgba(56, 189, 248, 0)');

        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: dates,
                datasets: [{{
                    label: 'Biological Age',
                    data: ages,
                    borderColor: '#38bdf8',
                    backgroundColor: gradient,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointBackgroundColor: '#38bdf8',
                    pointBorderColor: '#0f172a',
                    pointBorderWidth: 2,
                    pointHoverRadius: 8,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        backgroundColor: '#1e293b',
                        titleColor: '#38bdf8',
                        bodyColor: '#f8fafc',
                        padding: 12,
                        cornerRadius: 8,
                        displayColors: false
                    }}
                }},
                scales: {{
                    x: {{
                        grid: {{ display: false }},
                        ticks: {{ color: '#64748b' }}
                    }},
                    y: {{
                        grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                        ticks: {{ color: '#64748b' }}
                    }}
                }}
            }}
        }});

        // Calculate and display stats
        document.getElementById('minAge').innerText = Math.min(...ages).toFixed(1);
        document.getElementById('maxAge').innerText = Math.max(...ages).toFixed(1);
        document.getElementById('avgAge').innerText = (ages.reduce((a, b) => a + b, 0) / ages.length).toFixed(1);
    </script>
</body>
</html>
    """
    
    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"Visualization generated: {html_output}")

if __name__ == "__main__":
    generate_visualization('age_history.csv', 'age_trend.html')
