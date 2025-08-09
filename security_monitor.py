#!/usr/bin/env python3
"""
Security Monitoring Dashboard
============================

Real-time monitoring script for your Stillness Timer security.
Shows live security events, blocked IPs, and attack patterns.

Usage:
    python3 security_monitor.py
"""

import time
import os
from datetime import datetime, timedelta
from collections import defaultdict
import re

class SecurityMonitor:
    def __init__(self):
        self.log_file = "security.log"
        self.last_position = 0
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def read_new_logs(self):
        """Read new lines from security log file"""
        if not os.path.exists(self.log_file):
            return []
        
        new_lines = []
        try:
            with open(self.log_file, 'r') as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()
        except Exception as e:
            print(f"Error reading log file: {e}")
        
        return new_lines
    
    def parse_log_line(self, line):
        """Parse a log line and extract security information"""
        if "SECURITY EVENT:" not in line:
            return None
        
        try:
            # Extract timestamp
            timestamp_match = re.search(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
            timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"
            
            # Extract event type
            event_match = re.search(r'SECURITY EVENT: (\w+)', line)
            event_type = event_match.group(1) if event_match else "Unknown"
            
            # Extract IP (partial)
            ip_match = re.search(r'from IP (\w+\.\.\.)', line)
            ip = ip_match.group(1) if ip_match else "Unknown"
            
            # Extract details
            details_match = re.search(r'- (.+)$', line)
            details = details_match.group(1) if details_match else ""
            
            return {
                'timestamp': timestamp,
                'event_type': event_type,
                'ip': ip,
                'details': details,
                'severity': 'WARNING' if 'WARNING' in line else 'ERROR' if 'ERROR' in line else 'CRITICAL' if 'CRITICAL' in line else 'INFO'
            }
        except Exception as e:
            return None
    
    def get_security_summary(self):
        """Get summary of recent security events"""
        if not os.path.exists(self.log_file):
            return {"events": [], "summary": {"total": 0, "by_type": {}, "by_ip": {}}}
        
        events = []
        event_counts = defaultdict(int)
        ip_counts = defaultdict(int)
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                
                # Process last 100 lines or 24 hours of data
                recent_lines = lines[-100:]
                
                for line in recent_lines:
                    event = self.parse_log_line(line)
                    if event:
                        events.append(event)
                        event_counts[event['event_type']] += 1
                        ip_counts[event['ip']] += 1
        
        except Exception as e:
            print(f"Error analyzing security log: {e}")
        
        return {
            "events": events[-20:],  # Last 20 events
            "summary": {
                "total": len(events),
                "by_type": dict(event_counts),
                "by_ip": dict(ip_counts)
            }
        }
    
    def display_dashboard(self):
        """Display the security monitoring dashboard"""
        summary = self.get_security_summary()
        
        print("🚨 SECURITY MONITORING DASHBOARD 🚨")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Total Security Events: {summary['summary']['total']}")
        print()
        
        # Event type summary
        if summary['summary']['by_type']:
            print("📈 EVENT TYPES:")
            for event_type, count in sorted(summary['summary']['by_type'].items(), key=lambda x: x[1], reverse=True):
                severity_icon = "🔴" if "CRITICAL" in event_type or "BLOCK" in event_type else "🟡" if "RATE_LIMIT" in event_type else "🟠"
                print(f"  {severity_icon} {event_type}: {count}")
            print()
        
        # IP summary
        if summary['summary']['by_ip']:
            print("🌐 TOP IPs BY VIOLATIONS:")
            for ip, count in sorted(summary['summary']['by_ip'].items(), key=lambda x: x[1], reverse=True)[:5]:
                risk_level = "🔴 HIGH" if count > 10 else "🟡 MEDIUM" if count > 5 else "🟢 LOW"
                print(f"  {ip}: {count} violations ({risk_level} RISK)")
            print()
        
        # Recent events
        print("⏰ RECENT SECURITY EVENTS:")
        print("-" * 60)
        if summary['events']:
            for event in summary['events'][-10:]:  # Last 10 events
                severity_icon = {"CRITICAL": "🔴", "ERROR": "🟠", "WARNING": "🟡", "INFO": "🔵"}.get(event['severity'], "⚪")
                print(f"{severity_icon} {event['timestamp']} | {event['event_type']} | {event['ip']}")
                if event['details']:
                    print(f"    └─ {event['details']}")
        else:
            print("  ✅ No security events detected - All systems secure!")
        
        print("\n" + "=" * 60)
        print("🔄 Monitoring... (Ctrl+C to exit)")
        print("📄 Full logs: security.log")
    
    def monitor(self):
        """Start real-time monitoring"""
        print("🚨 Starting Security Monitor...")
        print("📁 Watching: security.log")
        print("⌨️  Press Ctrl+C to stop monitoring")
        print()
        
        try:
            while True:
                # Check for new log entries
                new_logs = self.read_new_logs()
                
                # Always show dashboard (refresh every 5 seconds)
                self.clear_screen()
                self.display_dashboard()
                
                # Show real-time alerts for new events
                if new_logs:
                    print("\n🚨 NEW SECURITY EVENTS:")
                    for line in new_logs:
                        event = self.parse_log_line(line)
                        if event:
                            severity_icon = {"CRITICAL": "🔴", "ERROR": "🟠", "WARNING": "🟡", "INFO": "🔵"}.get(event['severity'], "⚪")
                            print(f"{severity_icon} {event['event_type']} from {event['ip']} - {event['details']}")
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Security monitoring stopped.")
            print("📊 Final summary saved to security.log")

def main():
    monitor = SecurityMonitor()
    monitor.monitor()

if __name__ == "__main__":
    main()