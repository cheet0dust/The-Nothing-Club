#!/usr/bin/env python3
"""
Minimal Flask app to test Railway deployment
"""
from flask import Flask, jsonify
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    logger.info("Home route accessed")
    return jsonify({
        "status": "Minimal app is working", 
        "test": True,
        "port": os.environ.get("PORT", "not set"),
        "env": "railway" if "RAILWAY_ENVIRONMENT" in os.environ else "local"
    })

@app.route('/health')
def health():
    logger.info("Health check accessed")
    return "OK", 200

@app.route('/ping')
def ping():
    logger.info("Ping accessed")
    return "pong"

if __name__ == '__main__':
    import os
    # Railway provides PORT, default to 8080 for local testing
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting on 0.0.0.0:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)