#!/usr/bin/env python3
"""
Test Script for Stillness API
=============================

This script demonstrates how to interact with the backend API.
Run this after starting the backend server to test functionality.

Usage:
    python test_backend.py
"""

import requests
import json
import time
from datetime import datetime

API_URL = "http://localhost:5000"

def test_session_submission():
    """Test submitting various session durations"""
    print("🧪 Testing session submissions...")
    
    # Test various session durations (in seconds)
    test_sessions = [
        30,    # 30 seconds - short session
        120,   # 2 minutes - medium session
        300,   # 5 minutes - good session
        600,   # 10 minutes - long session
        1800,  # 30 minutes - very long session
        45,    # 45 seconds - another short one
        180,   # 3 minutes - medium
    ]
    
    for i, duration in enumerate(test_sessions, 1):
        try:
            response = requests.post(f"{API_URL}/api/session", 
                json={
                    "duration": duration,
                    "timestamp": datetime.now().isoformat()
                })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Session {i}: {duration}s")
                print(f"   📜 {data['message']}")
                print(f"   📊 Percentile: {data['percentile']}%")
                print()
            else:
                print(f"❌ Error submitting session {i}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to server. Make sure backend.py is running!")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True

def test_stats():
    """Test getting statistics"""
    print("📊 Testing stats endpoint...")
    
    try:
        response = requests.get(f"{API_URL}/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Statistics retrieved:")
            print(f"   📅 Today: {stats['today']['sessions']} sessions, avg {stats['today']['average']}s")
            print(f"   📈 All time: {stats['all_time']['total_sessions']} sessions, avg {stats['all_time']['average']}s")
            print(f"   🏆 Longest today: {stats['today']['longest']}s")
            print(f"   🎯 Longest ever: {stats['all_time']['longest']}s")
        else:
            print(f"❌ Error getting stats: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health_check():
    """Test server health"""
    print("🏥 Testing server health...")
    
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            health = response.json()
            print("✅ Server is healthy:")
            print(f"   📡 {health['status']}")
            print(f"   📊 {health['today_sessions']} sessions today")
            print(f"   🎯 {health['total_sessions']} total sessions")
            return True
        else:
            print(f"❌ Server unhealthy: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure backend.py is running!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧘 Testing Stillness API")
    print("=" * 40)
    
    # Test server health first
    if not test_health_check():
        print("\n💡 To start the server, run: python backend.py")
        exit(1)
    
    print()
    
    # Test session submissions
    if test_session_submission():
        print()
        # Test stats
        test_stats()
    
    print("\n✨ Testing complete!")
    print("💡 Try different session durations to see various messages.")