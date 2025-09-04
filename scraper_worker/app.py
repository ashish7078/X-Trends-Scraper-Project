from flask import Flask, jsonify
import os
from scraper import main as run_scraper
import subprocess

app = Flask(__name__)

print("=== DEBUG: Checking installed paths ===")
print("chromedriver:", subprocess.getoutput("which chromedriver"))
print("chromium-browser:", subprocess.getoutput("which chromium-browser"))
print("chromium:", subprocess.getoutput("which chromium"))
print("ls /usr/bin:", subprocess.getoutput("ls /usr/bin | grep chrom"))

@app.route("/")
def home():
    return jsonify({"message": "Worker is running!"})

@app.route("/trigger-scrape", methods=["POST"])
def trigger_scrape():
    try:
        obj = run_scraper()
        return jsonify({
            "status": "success",
            "trend_id": str(obj.id),
            "trends": [obj.trend1, obj.trend2, obj.trend3, obj.trend4, obj.trend5]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
