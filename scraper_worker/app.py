from flask import Flask, jsonify
import os
from scraper import main as run_scraper

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Worker is running!"})

@app.route("/trigger-scrape", methods=["POST"])
def trigger_scrape():
    try:
        trend_id = run_scraper()  # This returns UUID from save_to_db
        if trend_id:
            return jsonify({
                "status": "success",
                "trend_id": str(trend_id)
            })
        else:
            return jsonify({
                "status": "success",
                "trend_id": None,
                "message": "No trends were fetched"
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
