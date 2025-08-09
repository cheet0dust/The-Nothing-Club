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
    port = int(os.environ.get("PORT", 3001))
    app.run(debug=False, host='0.0.0.0', port=port)