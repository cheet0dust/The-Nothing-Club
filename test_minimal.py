#!/usr/bin/env python3
"""
Minimal Flask app to test Railway deployment
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "Minimal app is working", "test": True})

@app.route('/health')
def health():
    return jsonify({"health": "OK"})

if __name__ == '__main__':
    import os
    # Railway provides PORT, default to 8080 for local testing
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting on 0.0.0.0:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)