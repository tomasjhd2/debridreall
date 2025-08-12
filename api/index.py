import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
TOKEN = os.getenv("DEBRID_API_TOKEN", "oPpT1SUjPzraqDq_sI2-pKiSFUGjOtm08mtN81G_bs876gwQIcrieyoDhyCnHHrN")

@app.route('/')
def home():
    return '''<!DOCTYPE html>
<html>
<head><title>Debrid Link Generator</title></head>
<body>
    <h1>Debrid Link Generator</h1>
    <input type="url" id="url" placeholder="Enter URL">
    <button onclick="generate()">Generate</button>
    <div id="result"></div>
    <script>
    async function generate() {
        const url = document.getElementById('url').value;
        const response = await fetch('/json?url=' + encodeURIComponent(url));
        const data = await response.json();
        document.getElementById('result').innerHTML = data.success ? 
            `<p>File: ${data.filename}<br>Size: ${data.size_mb}MB<br><a href="${data.download_url}">Download</a></p>` :
            `<p style="color:red">Error: ${data.error}</p>`;
    }
    </script>
</body>
</html>'''

@app.route('/json')
def json_link():
    url = request.args.get('url')
    if not url:
        return jsonify({"success": False, "error": "URL required"}), 400
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        response = requests.post("https://debrid-link.com/api/v2/downloader/add",
                               headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
                               json={"url": url})
        result = response.json()
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "filename": result["value"]["name"],
                "size_bytes": result["value"]["size"],
                "size_mb": round(result["value"]["size"] / (1024 * 1024), 2),
                "download_url": result["value"]["downloadUrl"],
                "host": result["value"]["host"]
            })
        else:
            return jsonify({"success": False, "error": result.get('error', 'Unknown error')}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def handler(request):
    return app