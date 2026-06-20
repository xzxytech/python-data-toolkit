"""
🐍 Python Data Analysis API — Free & Open Source

Endpoints:
  POST /api/analyze     — Upload CSV/Excel, get instant analysis
  POST /api/scrape      — Scrape a URL, return structured data
  POST /api/convert     — Convert between CSV/Excel/JSON
  GET  /api/demo        — See a demo analysis
  GET  /health          — Health check
  GET  /                — Landing page
"""

from flask import Flask, request, jsonify, send_file, render_template_string
import pandas as pd
import io
import json
import os
import tempfile
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

LANDING_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐍 Python Data Analysis API — Free & Open Source</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a1a; color: #e0e0e0; line-height: 1.6; }
        .hero { text-align: center; padding: 80px 20px 40px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); }
        .hero h1 { font-size: 2.5em; margin-bottom: 10px; }
        .hero h1 span { color: #4fc3f7; }
        .hero p { font-size: 1.2em; color: #a0a0b0; max-width: 600px; margin: 0 auto; }
        .badge { display: inline-block; background: #4fc3f7; color: #0a0a1a; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; font-weight: bold; margin: 10px 5px; }
        .badge.green { background: #66bb6a; }
        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        .endpoint { background: #1a1a2e; border: 1px solid #2a2a4e; border-radius: 12px; padding: 24px; margin: 20px 0; }
        .endpoint h3 { color: #4fc3f7; margin-bottom: 8px; }
        .method { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; margin-right: 8px; }
        .method.post { background: #4caf50; color: white; }
        .method.get { background: #2196f3; color: white; }
        .endpoint code { background: #0d0d1a; padding: 2px 6px; border-radius: 4px; color: #ffd54f; }
        .endpoint pre { background: #0d0d1a; padding: 16px; border-radius: 8px; overflow-x: auto; margin: 12px 0; font-size: 0.9em; color: #a5d6a7; }
        .cta { text-align: center; padding: 40px 20px; }
        .cta a { display: inline-block; padding: 12px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; margin: 8px; }
        .cta .primary { background: #4fc3f7; color: #0a0a1a; }
        .cta .secondary { background: transparent; border: 2px solid #4fc3f7; color: #4fc3f7; }
        .footer { text-align: center; padding: 40px 20px; color: #606070; border-top: 1px solid #2a2a4e; }
        .stats { display: flex; justify-content: center; gap: 40px; margin: 30px 0; }
        .stat { text-align: center; }
        .stat .num { font-size: 2em; color: #4fc3f7; font-weight: bold; }
        .stat .label { font-size: 0.85em; color: #808090; }
    </style>
</head>
<body>
    <div class="hero">
        <h1>🐍 <span>Python Data API</span></h1>
        <p>Free, open-source data analysis API. Upload CSV/Excel, scrape websites, convert formats — all via simple HTTP requests.</p>
        <div>
            <span class="badge">100% Free</span>
            <span class="badge green">Open Source</span>
            <span class="badge">No API Key Required</span>
        </div>
    </div>
    
    <div class="container">
        <div class="endpoint">
            <h3><span class="method post">POST</span> /api/analyze</h3>
            <p>Upload a CSV or Excel file and get instant statistical analysis.</p>
            <pre>curl -X POST https://your-url/api/analyze \\
  -F "file=@data.csv"</pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method post">POST</span> /api/scrape</h3>
            <p>Scrape any URL and extract structured data (tables, links, text).</p>
            <pre>curl -X POST https://your-url/api/scrape \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://example.com", "extract": "tables"}'</pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method post">POST</span> /api/convert</h3>
            <p>Convert between CSV, Excel, and JSON formats.</p>
            <pre>curl -X POST https://your-url/api/convert \\
  -F "file=@data.csv" \\
  -F "to=excel"</pre>
        </div>
        
        <div class="endpoint">
            <h3><span class="method get">GET</span> /api/demo</h3>
            <p>See a demo analysis with sample data.</p>
            <pre>curl https://your-url/api/demo</pre>
        </div>
    </div>
    
    <div class="cta">
        <a href="https://github.com/xzxytech/python-data-toolkit" class="primary">⭐ Star on GitHub</a>
        <a href="https://github.com/xzxytech/python-data-toolkit#readme" class="secondary">📖 Documentation</a>
    </div>
    
    <div class="footer">
        <p>Built with ❤️ using Python, Flask, and pandas</p>
        <p>Open source under MIT License</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(LANDING_PAGE)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Upload CSV/Excel, get instant analysis."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded. Use -F 'file=@yourfile.csv'"}), 400
    
    f = request.files['file']
    filename = f.filename.lower()
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(f)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(f)
        elif filename.endswith('.json'):
            df = pd.read_json(f)
        else:
            return jsonify({"error": "Unsupported format. Use CSV, Excel, or JSON."}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to parse file: {str(e)}"}), 400
    
    # Analysis
    result = {
        "file": f.filename,
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": {col: int(count) for col, count in df.isnull().sum().items() if count > 0},
        "sample": df.head(5).to_dict(orient='records'),
    }
    
    # Numeric stats
    numeric = df.select_dtypes(include='number')
    if len(numeric.columns) > 0:
        result["statistics"] = {}
        for col in numeric.columns:
            result["statistics"][col] = {
                "mean": round(float(numeric[col].mean()), 4),
                "median": round(float(numeric[col].median()), 4),
                "std": round(float(numeric[col].std()), 4),
                "min": round(float(numeric[col].min()), 4),
                "max": round(float(numeric[col].max()), 4),
                "sum": round(float(numeric[col].sum()), 4),
            }
    
    # Text column stats
    text = df.select_dtypes(include='object')
    if len(text.columns) > 0:
        result["text_stats"] = {}
        for col in text.columns:
            result["text_stats"][col] = {
                "unique_values": int(text[col].nunique()),
                "top_values": text[col].value_counts().head(5).to_dict()
            }
    
    return jsonify(result)

@app.route('/api/scrape', methods=['POST'])
def scrape():
    """Scrape a URL and extract data."""
    data = request.get_json(silent=True) or {}
    url = data.get('url', '')
    extract = data.get('extract', 'text')  # text, tables, links
    
    if not url:
        return jsonify({"error": "No URL provided. Send {\"url\": \"https://...\"}"}), 400
    
    try:
        import requests as req
        from bs4 import BeautifulSoup
        
        resp = req.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        result = {"url": url, "status": resp.status_code}
        
        if extract == 'tables':
            tables = pd.read_html(resp.text)
            result["tables"] = [t.to_dict(orient='records') for t in tables[:5]]
            result["table_count"] = len(tables)
        elif extract == 'links':
            links = [{"text": a.get_text(strip=True), "href": a['href']} 
                     for a in soup.find_all('a', href=True)]
            result["links"] = links[:100]
            result["total_links"] = len(links)
        else:
            result["title"] = soup.title.string if soup.title else None
            result["text"] = soup.get_text(separator='\n', strip=True)[:5000]
            result["meta"] = {
                "description": soup.find('meta', attrs={'name': 'description'}),
            }
            if result["meta"]["description"]:
                result["meta"]["description"] = result["meta"]["description"].get('content', '')
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/convert', methods=['POST'])
def convert():
    """Convert between CSV, Excel, and JSON."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    f = request.files['file']
    to_format = request.form.get('to', 'json').lower()
    filename = f.filename.lower()
    
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(f)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(f)
        elif filename.endswith('.json'):
            df = pd.read_json(f)
        else:
            return jsonify({"error": "Unsupported input format"}), 400
        
        if to_format == 'json':
            return jsonify(df.to_dict(orient='records'))
        elif to_format == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False)
            return output.getvalue(), 200, {'Content-Type': 'text/csv'}
        elif to_format == 'excel':
            output = io.BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                           as_attachment=True, download_name='converted.xlsx')
        else:
            return jsonify({"error": "Supported formats: json, csv, excel"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/demo')
def demo():
    """Demo analysis with sample data."""
    import random
    data = {
        'Product': ['Widget A', 'Widget B', 'Gadget X', 'Gadget Y', 'Service Z'] * 20,
        'Revenue': [random.randint(1000, 50000) for _ in range(100)],
        'Units': [random.randint(10, 500) for _ in range(100)],
        'Region': random.choices(['North', 'South', 'East', 'West'], k=100),
    }
    df = pd.DataFrame(data)
    
    return jsonify({
        "demo": True,
        "description": "Sample analysis of 100 sales records",
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "statistics": {
            "Revenue": {
                "mean": round(float(df['Revenue'].mean()), 2),
                "total": round(float(df['Revenue'].sum()), 2),
                "min": round(float(df['Revenue'].min()), 2),
                "max": round(float(df['Revenue'].max()), 2),
            },
            "Units": {
                "mean": round(float(df['Units'].mean()), 2),
                "total": int(df['Units'].sum()),
            }
        },
        "by_region": df.groupby('Region')['Revenue'].sum().to_dict(),
        "top_products": df.groupby('Product')['Revenue'].sum().nlargest(5).to_dict(),
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🐍 Python Data Analysis API starting on port {port}")
    print(f"📡 Endpoints: /api/analyze, /api/scrape, /api/convert, /api/demo")
    app.run(host='0.0.0.0', port=port, debug=False)
