# 🚨 Attack Detection & Response Guide

## How to Know if You're Being Attacked

### 🔍 **Real-Time Monitoring**

#### **1. Security Monitor Dashboard**
```bash
# Run the live security monitor
python3 security_monitor.py
```

**What You'll See:**
- 📊 **Event counts** - number of security violations
- 🌐 **Suspicious IPs** - repeat offenders  
- ⏰ **Live events** - attacks happening right now
- 🔴 **Risk levels** - high/medium/low threat assessment

#### **2. Security Log File**
```bash
# View security log
tail -f security.log

# Search for specific attack types
grep "CRITICAL" security.log
grep "RATE_LIMIT_EXCEEDED" security.log
```

### 🚨 **Attack Indicators to Watch For**

#### **🔴 CRITICAL Alerts (Immediate Action Needed)**
- **`BLOCKED_IP_ACCESS`** - Previously blocked IP trying to access
- **`RAPID_FIRE_ATTACK`** - 20+ requests in 1 minute
- **IP automatically blocked** - System detected repeat offender

#### **🟡 WARNING Alerts (Monitor Closely)**
- **`RATE_LIMIT_EXCEEDED`** - Too many requests from single IP
- **`INVALID_DATA`** - Malformed data submissions
- **`DAILY_LIMIT_EXCEEDED`** - Unusual usage patterns
- **`POSSIBLE_SCRAPING`** - 50+ requests in 1 hour

#### **🟠 SUSPICIOUS Patterns**
- **`SYSTEMATIC_PROBING`** - Different types of invalid requests
- **Multiple event types** from same IP
- **Requests outside normal hours**
- **Geographic anomalies** (if you add IP geolocation)

### 📧 **Email Alert Setup (Optional)**

#### **Step 1: Configure Email Settings**
Edit `backend.py`:
```python
# Alert configuration
ALERT_EMAIL_FROM = "your-gmail@gmail.com"
ALERT_EMAIL_TO = "your-gmail@gmail.com"  
ALERT_EMAIL_PASSWORD = "your-app-password"  # NOT your regular password!
ENABLE_EMAIL_ALERTS = True  # Enable email notifications
```

#### **Step 2: Gmail App Password Setup**
1. **Enable 2-Factor Authentication** on your Gmail
2. **Go to:** Google Account → Security → 2-Step Verification → App passwords
3. **Generate** app password for "Stillness Timer"
4. **Use this password** (not your regular Gmail password)

#### **Step 3: Test Email Alerts**
```bash
# Trigger rate limit to test alerts
for i in {1..15}; do curl -X POST http://127.0.0.1:3001/api/session -H "Content-Type: application/json" -d '{"duration": 60}'; done
```

**Expected Email:**
```
🚨 Security Alert: Repeated violations from IP 127.0.0...

Alert Type: MODERATE
Time: 2024-01-15 14:30:22

Details:
IP 127.0.0.1 has violated security rules 5 times. Recent events: [...]
```

### 🎯 **Common Attack Scenarios & Detection**

#### **Scenario 1: DDoS/Rate Limit Attack**
**Indicators:**
- Multiple `RATE_LIMIT_EXCEEDED` from same IP
- Rapid succession of requests
- High request volume in short time

**System Response:**
- Automatic rate limiting kicks in
- IP gets temporarily blocked after 10 violations
- Alert sent immediately

#### **Scenario 2: Data Scraping**
**Indicators:**
- `POSSIBLE_SCRAPING` alerts
- Steady stream of requests over hours
- Systematic data collection patterns

**System Response:**
- Long-term monitoring of IP
- Progressive alerts at 50+ requests/hour
- Automatic blocking after sustained activity

#### **Scenario 3: Injection Attacks**
**Indicators:**
- Multiple `INVALID_DATA` events
- Different types of malformed requests
- `SYSTEMATIC_PROBING` alerts

**System Response:**
- Input validation blocks malicious payloads
- Pattern detection flags coordinated attempts
- IP blocking after repeated violations

#### **Scenario 4: Reconnaissance**
**Indicators:**
- Various attack types from same IP
- Probing different endpoints
- Testing different vulnerability types

**System Response:**
- Multi-vector attack detection
- Escalating alert levels
- Rapid IP blocking for persistent threats

### 📊 **Attack Response Levels**

#### **Level 1: Normal Security Events**
- **Action:** Monitor logs
- **Response Time:** Daily review
- **Example:** Single rate limit violation

#### **Level 2: Suspicious Activity**
- **Action:** Real-time monitoring
- **Response Time:** Hourly checks
- **Example:** 5 violations from same IP

#### **Level 3: Active Attack**
- **Action:** Immediate investigation
- **Response Time:** Real-time response
- **Example:** Systematic probing, IP auto-blocked

#### **Level 4: Critical Breach Attempt**
- **Action:** Emergency response
- **Response Time:** Immediate
- **Example:** Blocked IP repeatedly trying access

### 🛠️ **Manual Response Actions**

#### **Block Specific IP Manually**
```python
# Add to backend.py
MANUAL_BLOCKED_IPS = {"1.2.3.4", "5.6.7.8"}  # Add suspicious IPs

# In check_rate_limit function, add:
if ip_address in MANUAL_BLOCKED_IPS:
    log_security_event("MANUAL_BLOCK", ip_address, "Manually blocked IP", "CRITICAL")
    return False
```

#### **Adjust Security Thresholds**
```python
# Make more/less strict in backend.py
MAX_REQUESTS_PER_MINUTE = 5   # More strict
MAX_SESSIONS_PER_DAY = 50     # More strict

# Or less strict for legitimate heavy usage
MAX_REQUESTS_PER_MINUTE = 20
```

#### **Emergency Shutdown**
```bash
# Stop backend server immediately
pkill -f "python3 backend.py"

# Or use Ctrl+C in backend terminal
```

### 📈 **Security Metrics Dashboard**

#### **Daily Security Report**
```bash
# Get daily summary
grep "$(date +%Y-%m-%d)" security.log | wc -l  # Total events today
grep "CRITICAL" security.log | grep "$(date +%Y-%m-%d)" | wc -l  # Critical events today
```

#### **Top Threat IPs**
```bash
# Most active attacking IPs
grep "SECURITY EVENT" security.log | grep -o "IP [0-9a-f]*\.\.\." | sort | uniq -c | sort -nr | head -10
```

#### **Attack Timeline**
```bash
# Show timeline of attacks
grep "SECURITY EVENT" security.log | tail -20
```

### ⚡ **Quick Response Checklist**

When you detect an attack:

#### **Immediate (0-5 minutes):**
- [ ] Check security monitor dashboard
- [ ] Identify attack type and source IP
- [ ] Verify system is blocking attacker
- [ ] Check if legitimate users affected

#### **Short-term (5-30 minutes):**
- [ ] Review full attack timeline in logs
- [ ] Assess if manual IP blocking needed
- [ ] Check for data integrity issues
- [ ] Document attack details

#### **Follow-up (30+ minutes):**
- [ ] Analyze attack patterns for improvements
- [ ] Update security thresholds if needed
- [ ] Report to authorities if severe
- [ ] Implement additional protections

### 🎯 **Success Metrics**

Your security system is working when you see:
- ✅ **Fast detection** - alerts within minutes
- ✅ **Automatic blocking** - repeat offenders stopped
- ✅ **No data corruption** - backend data stays clean
- ✅ **Minimal false positives** - legitimate users not blocked
- ✅ **Clear forensics** - detailed attack logs for analysis

---

**Remember: Most attacks will be automatically blocked. This system gives you visibility and control, but handles 95% of threats automatically.**