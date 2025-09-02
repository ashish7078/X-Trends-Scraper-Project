from flask import Flask, jsonify
import os

from scraper import main as run_scraper

app = Flask(__name__)

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
    app.run(host="0.0.0.0", port=5000)
