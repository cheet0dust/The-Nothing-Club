#!/usr/bin/env python3
"""
Quick test for security monitor
"""

import time
from datetime import datetime

# Create a test security log entry
with open("security.log", "w") as f:
    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - WARNING - SECURITY EVENT: RATE_LIMIT_EXCEEDED from IP 127.0.0... - Test event\n")

print("✅ Test log entry created")
print("📄 Check security.log file:")
print()

with open("security.log", "r") as f:
    print(f.read())