#!/usr/bin/env python3
"""
Simple Backend for Stillness Timer
==================================

A lightweight Flask API that:
1. Accepts session duration from users
2. Stores durations in memory (resets when server restarts)
3. Calculates percentiles compared to other users today
4. Returns encouraging messages about stillness performance

Usage:
    python backend.py
    
Then send POST requests to: http://localhost:5000/api/session
"""

from flask import Flask, request, jsonify, abort, make_response
from flask_cors import CORS
from datetime import datetime, date
import json
import os
import re
import time
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List
from collections import defaultdict, deque
from datetime import timedelta

app = Flask(__name__)

# Secure CORS - allow localhost for testing and production domains
CORS(app, origins=["http://localhost:8000", "http://127.0.0.1:8000", "https://thenothingclub.netlify.app"], 
     methods=["GET", "POST"], 
     allow_headers=["Content-Type"])

# In-memory storage for session data
# Format: {"2024-01-15": [120, 45, 300, 67, ...], "2024-01-16": [...]}
sessions_by_date: Dict[str, List[int]] = {}

# Rate limiting storage (IP -> [timestamps])
rate_limit_storage: Dict[str, deque] = defaultdict(lambda: deque())

# File to persist data (optional - survives server restarts)
DATA_FILE = "session_data.json"

# Security constants
MAX_REQUESTS_PER_MINUTE = 10
MAX_SESSION_DURATION = 14400  # 4 hours in seconds
MIN_SESSION_DURATION = 1      # 1 second minimum
MAX_SESSIONS_PER_DAY = 100

# Security monitoring
IP_VIOLATIONS = defaultdict(int)
BLOCKED_IPS = set()
ATTACK_PATTERNS = defaultdict(list)
ALERT_COOLDOWN = defaultdict(float)

# Alert configuration (CHANGE THESE TO YOUR EMAIL)
SMTP_SERVER = "smtp.gmail.com"  # Change to your email provider
SMTP_PORT = 587
ALERT_EMAIL_FROM = "your-email@gmail.com"  # Your email
ALERT_EMAIL_TO = "your-email@gmail.com"    # Where to send alerts
ALERT_EMAIL_PASSWORD = "your-app-password"  # App password (not regular password)
ENABLE_EMAIL_ALERTS = False  # Set to True when you configure email

@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'none'; script-src 'none'; style-src 'none'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

def setup_logging():
    """Setup security logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('security.log'),
            logging.StreamHandler()
        ]
    )

def send_security_alert(subject: str, message: str, alert_type: str = "security"):
    """Send security alert via email"""
    if not ENABLE_EMAIL_ALERTS:
        print(f"🚨 ALERT ({alert_type}): {subject} - {message}")
        return
    
    # Check cooldown to prevent spam
    cooldown_key = f"{alert_type}_{subject}"
    current_time = time.time()
    
    if cooldown_key in ALERT_COOLDOWN:
        if current_time - ALERT_COOLDOWN[cooldown_key] < 300:  # 5 minute cooldown
            return
    
    ALERT_COOLDOWN[cooldown_key] = current_time
    
    try:
        msg = MIMEMultipart()
        msg['From'] = ALERT_EMAIL_FROM
        msg['To'] = ALERT_EMAIL_TO
        msg['Subject'] = f"🚨 Security Alert: {subject}"
        
        body = f"""
Security Alert for Stillness Timer

Alert Type: {alert_type.upper()}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Details:
{message}

---
This is an automated security alert from your meditation timer backend.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(ALERT_EMAIL_FROM, ALERT_EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(ALERT_EMAIL_FROM, ALERT_EMAIL_TO, text)
        server.quit()
        
        logging.warning(f"Security alert sent: {subject}")
        
    except Exception as e:
        logging.error(f"Failed to send security alert: {e}")
        print(f"🚨 ALERT (failed to send email): {subject} - {message}")

def log_security_event(event_type: str, ip: str, details: str, severity: str = "WARNING"):
    """Log security events and trigger alerts if needed"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"SECURITY EVENT: {event_type} from IP {ip[:8]}... - {details}"
    
    # Log to file and console
    if severity == "CRITICAL":
        logging.critical(log_message)
    elif severity == "ERROR":
        logging.error(log_message)
    else:
        logging.warning(log_message)
    
    # Track attack patterns
    ATTACK_PATTERNS[ip].append({
        'type': event_type,
        'time': time.time(),
        'details': details
    })
    
    # Clean old attack patterns (older than 24 hours)
    cutoff_time = time.time() - 86400
    for ip_addr in list(ATTACK_PATTERNS.keys()):
        ATTACK_PATTERNS[ip_addr] = [
            event for event in ATTACK_PATTERNS[ip_addr] 
            if event['time'] > cutoff_time
        ]
        if not ATTACK_PATTERNS[ip_addr]:
            del ATTACK_PATTERNS[ip_addr]
    
    # Trigger alerts for serious events
    if event_type in ["RATE_LIMIT_EXCEEDED", "INVALID_DATA", "BLOCKED_IP"]:
        IP_VIOLATIONS[ip] += 1
        
        # Progressive alerts
        if IP_VIOLATIONS[ip] == 5:
            send_security_alert(
                f"Repeated violations from IP {ip[:8]}...",
                f"IP {ip} has violated security rules 5 times. Recent events: {ATTACK_PATTERNS[ip][-3:]}",
                "moderate"
            )
        elif IP_VIOLATIONS[ip] >= 10:
            BLOCKED_IPS.add(ip)
            send_security_alert(
                f"IP {ip[:8]}... BLOCKED",
                f"IP {ip} has been automatically blocked after {IP_VIOLATIONS[ip]} violations. Recent events: {ATTACK_PATTERNS[ip][-5:]}",
                "critical"
            )

def detect_attack_patterns(ip: str):
    """Detect sophisticated attack patterns"""
    if ip not in ATTACK_PATTERNS:
        return
    
    recent_events = ATTACK_PATTERNS[ip]
    current_time = time.time()
    
    # Check for rapid fire attacks (more than 20 requests in 1 minute)
    recent_minute = [e for e in recent_events if current_time - e['time'] < 60]
    if len(recent_minute) > 20:
        log_security_event("RAPID_FIRE_ATTACK", ip, f"{len(recent_minute)} requests in 1 minute", "CRITICAL")
        return True
    
    # Check for data scraping attempts (many requests over time)
    recent_hour = [e for e in recent_events if current_time - e['time'] < 3600]
    if len(recent_hour) > 50:
        log_security_event("POSSIBLE_SCRAPING", ip, f"{len(recent_hour)} requests in 1 hour", "ERROR")
        return True
    
    # Check for systematic probing (different types of invalid requests)
    invalid_types = set(e['type'] for e in recent_events[-10:] if 'INVALID' in e['type'])
    if len(invalid_types) >= 3:
        log_security_event("SYSTEMATIC_PROBING", ip, f"Multiple attack types: {invalid_types}", "ERROR")
        return True
    
    return False

def load_data():
    """Load existing session data from file if it exists"""
    global sessions_by_date
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                sessions_by_date = json.load(f)
                print(f"📊 Loaded {sum(len(sessions) for sessions in sessions_by_date.values())} sessions from storage")
        except Exception as e:
            print(f"⚠️  Could not load data: {e}")
            sessions_by_date = {}

def save_data():
    """Save session data to file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(sessions_by_date, f)
    except Exception as e:
        print(f"⚠️  Could not save data: {e}")

def check_rate_limit(ip_address: str) -> bool:
    """Check if IP is within rate limits"""
    # Check if IP is blocked
    if ip_address in BLOCKED_IPS:
        log_security_event("BLOCKED_IP_ACCESS", ip_address, "Blocked IP attempted access", "CRITICAL")
        return False
    
    current_time = time.time()
    ip_requests = rate_limit_storage[ip_address]
    
    # Remove old requests (older than 1 minute)
    while ip_requests and current_time - ip_requests[0] > 60:
        ip_requests.popleft()
    
    # Check if under limit
    if len(ip_requests) >= MAX_REQUESTS_PER_MINUTE:
        log_security_event("RATE_LIMIT_EXCEEDED", ip_address, f"{len(ip_requests)} requests in 1 minute", "WARNING")
        detect_attack_patterns(ip_address)
        return False
    
    # Add current request
    ip_requests.append(current_time)
    return True

def validate_session_data(data: dict) -> tuple[bool, str]:
    """Validate incoming session data"""
    if not isinstance(data, dict):
        return False, "Invalid data format"
    
    if 'duration' not in data:
        return False, "Duration is required"
    
    try:
        duration = int(data['duration'])
    except (ValueError, TypeError):
        return False, "Duration must be a number"
    
    if duration < MIN_SESSION_DURATION:
        return False, f"Duration too short (minimum: {MIN_SESSION_DURATION}s)"
    
    if duration > MAX_SESSION_DURATION:
        return False, f"Duration too long (maximum: {MAX_SESSION_DURATION}s = 4 hours)"
    
    # Validate timestamp if provided
    if 'timestamp' in data:
        try:
            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            # Check if timestamp is reasonable (not too far in past/future)
            now = datetime.now()
            if abs((timestamp.replace(tzinfo=None) - now).total_seconds()) > 86400:  # 24 hours
                return False, "Timestamp too far from current time"
        except (ValueError, TypeError):
            return False, "Invalid timestamp format"
    
    return True, "Valid"

def sanitize_input(text: str) -> str:
    """Sanitize text input to prevent injection attacks"""
    if not isinstance(text, str):
        return ""
    
    # Remove any potentially dangerous characters
    # Keep only alphanumeric, spaces, and basic punctuation
    sanitized = re.sub(r'[^\w\s\-.:,!?]', '', text)
    
    # Limit length
    return sanitized[:1000]

def calculate_percentile(duration: int, all_durations: List[int]) -> int:
    """Calculate what percentile this duration is in"""
    if not all_durations:
        return 50  # Default if no other data
    
    # Count how many sessions were shorter than this one
    shorter_sessions = sum(1 for d in all_durations if d < duration)
    
    # Calculate percentile (what % of users this person beat)
    percentile = int((shorter_sessions / len(all_durations)) * 100)
    return percentile

def generate_message(duration: int, percentile: int, total_sessions: int) -> str:
    """Generate an encouraging message based on performance"""
    
    # Convert duration to human readable format
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    seconds = duration % 60
    
    if hours > 0:
        time_str = f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        time_str = f"{minutes}m {seconds}s"
    else:
        time_str = f"{seconds}s"
    
    # Generate message based on percentile
    if percentile >= 99:
        return f"welcome to the nothing club – you are in the top 1% of users."
    elif percentile >= 95:
        return f"stillness like this is rare – you're in the top {100-percentile}% of users."
    elif percentile >= 90:
        return f"exceptional focus – you outlasted {percentile}% of users today."
    elif percentile >= 75:
        return f"you were more still than {percentile}% of users today."
    elif percentile >= 50:
        return f"good practice – you were more still than {percentile}% of users today."
    elif percentile >= 25:
        return f"every moment of stillness counts. keep practicing."
    else:
        return f"stillness is a practice. this is a beautiful start."

@app.route('/')
def home():
    """Health check endpoint"""
    ensure_initialized()
    today = date.today().isoformat()
    today_sessions = sessions_by_date.get(today, [])
    total_sessions = sum(len(sessions) for sessions in sessions_by_date.values())
    
    return jsonify({
        "status": "🧘 Stillness API is running",
        "today_sessions": len(today_sessions),
        "total_sessions": total_sessions,
        "average_today": round(sum(today_sessions) / len(today_sessions), 1) if today_sessions else 0
    })

@app.route('/api/session', methods=['POST'])
def submit_session():
    """
    Accept a session duration and return percentile feedback
    
    Expected JSON body:
    {
        "duration": 120,  # Duration in seconds
        "timestamp": "2024-01-15T10:30:00"  # Optional, uses current time if not provided
    }
    """
    ensure_initialized()
    try:
        # Get client IP address
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
        
        # Check rate limiting
        if not check_rate_limit(client_ip):
            return jsonify({"error": "Rate limit exceeded. Try again later."}), 429
        
        # Validate request has JSON data
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        
        # Validate session data
        is_valid, error_msg = validate_session_data(data)
        if not is_valid:
            log_security_event("INVALID_DATA", client_ip, error_msg, "WARNING")
            return jsonify({"error": error_msg}), 400
        
        duration = int(data['duration'])
        
        # Use provided timestamp or current time
        if 'timestamp' in data:
            timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        else:
            timestamp = datetime.now()
        
        today = timestamp.date().isoformat()
        
        # Initialize today's sessions if needed
        if today not in sessions_by_date:
            sessions_by_date[today] = []
        
        # Check daily session limit
        if len(sessions_by_date[today]) >= MAX_SESSIONS_PER_DAY:
            log_security_event("DAILY_LIMIT_EXCEEDED", client_ip, f"{len(sessions_by_date[today])} sessions attempted", "WARNING")
            return jsonify({"error": "Daily session limit reached. Try again tomorrow."}), 429
        
        # Add this session to today's data
        sessions_by_date[today].append(duration)
        
        # Calculate percentile compared to all users today
        today_sessions = sessions_by_date[today][:-1]  # Exclude current session from comparison
        percentile = calculate_percentile(duration, today_sessions)
        
        # Generate encouraging message
        message = generate_message(duration, percentile, len(today_sessions))
        
        # Save data to file
        save_data()
        
        # Log the session (without exposing sensitive info)
        print(f"📝 New session: {duration}s (percentile: {percentile}%) from {client_ip[:7]}... - {len(today_sessions)+1} sessions today")
        
        return jsonify({
            "message": message,
            "duration": duration,
            "percentile": percentile,
            "sessions_today": len(sessions_by_date[today]),
            "total_sessions": sum(len(sessions) for sessions in sessions_by_date.values())
        })
        
    except ValueError:
        return jsonify({"error": "Invalid data format"}), 400
    except Exception as e:
        # Don't expose internal errors to client
        print(f"❌ Error processing session from {request.environ.get('REMOTE_ADDR', 'unknown')}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get current statistics"""
    ensure_initialized()
    today = date.today().isoformat()
    today_sessions = sessions_by_date.get(today, [])
    all_sessions = []
    for sessions in sessions_by_date.values():
        all_sessions.extend(sessions)
    
    return jsonify({
        "today": {
            "sessions": len(today_sessions),
            "average": round(sum(today_sessions) / len(today_sessions), 1) if today_sessions else 0,
            "longest": max(today_sessions) if today_sessions else 0
        },
        "all_time": {
            "total_sessions": len(all_sessions),
            "average": round(sum(all_sessions) / len(all_sessions), 1) if all_sessions else 0,
            "longest": max(all_sessions) if all_sessions else 0
        }
    })

# Lazy initialization flag
_app_initialized = False

def ensure_initialized():
    """Ensure the application is initialized"""
    global _app_initialized
    if not _app_initialized:
        try:
            print("🧘 Starting Stillness API Server...")
            print("🔒 Setting up security monitoring...")
            setup_logging()
            print("📊 Loading existing session data...")
            load_data()
            print("📡 API endpoint: POST /api/session")
            print("📈 Stats endpoint: GET /api/stats")
            print("🚨 Security logging: security.log")
            print("💾 Data will be saved to session_data.json")
            
            # Log startup
            logging.info("Stillness API server started with security monitoring")
            print("✅ Initialization complete")
            _app_initialized = True
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            _app_initialized = True  # Mark as initialized anyway to avoid loops

if __name__ == '__main__':
    # For local development only
    ensure_initialized()
    port = int(os.environ.get("PORT", 3001))
    print(f"🚀 Server starting at http://0.0.0.0:{port}")
    print("="*50)
    app.run(debug=False, host='0.0.0.0', port=port, threaded=True)
