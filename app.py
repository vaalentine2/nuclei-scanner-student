from flask import Flask, request, render_template, jsonify
import subprocess
import os
import uuid
import json
from pathlib import Path

app = Flask(__name__)
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/scan", methods=["POST"])
def scan():
    target = request.form.get("target")
    scan_id = str(uuid.uuid4())
    output_path = RESULTS_DIR / f"{scan_id}.json"

    # Execute Nuclei as a sub-process
    # Using list format is safe against injection
    cmd = ["nuclei", "-u", target, "-json-export", str(output_path)]
    
    # In a production app, use a task queue like Celery here.
    # For a demo, subprocess.Popen runs it in the background.
    subprocess.Popen(cmd)

    return f"Scan triggered! ID: {scan_id}. Check back shortly."

@app.route("/results/<scan_id>")
def get_results(scan_id):
    result_file = RESULTS_DIR / f"{scan_id}.json"
    if not result_file.exists():
        return "Scan in progress or not found", 404
    
    # Read JSONL file (Nuclei outputs one JSON object per line)
    with open(result_file, "r") as f:
        data = [json.loads(line) for line in f]
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
