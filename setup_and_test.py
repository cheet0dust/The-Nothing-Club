#!/usr/bin/env python3
"""
Quick Setup and Test Script
==========================

This script helps you get started quickly by:
1. Checking if dependencies are installed
2. Starting the backend server
3. Opening your frontend in the browser
4. Running integration tests

Usage:
    python setup_and_test.py
"""

import subprocess
import sys
import time
import webbrowser
import requests
from pathlib import Path

def check_dependencies():
    """Check if required Python packages are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = ['flask', 'flask_cors', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Installing missing packages...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please run: pip install -r requirements.txt")
            return False
    else:
        print("✅ All dependencies are installed!")
    
    return True

def start_backend():
    """Start the backend server in a separate process"""
    print("🚀 Starting backend server...")
    
    try:
        # Start backend server
        process = subprocess.Popen([sys.executable, 'backend.py'])
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        for i in range(10):
            try:
                response = requests.get('http://localhost:5000/', timeout=1)
                if response.status_code == 200:
                    print("✅ Backend server is running!")
                    return process
            except:
                time.sleep(1)
        
        print("❌ Backend server failed to start")
        process.terminate()
        return None
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def open_frontend():
    """Open the frontend in the default browser"""
    print("🌐 Opening frontend in browser...")
    
    frontend_path = Path('index.html').absolute()
    if frontend_path.exists():
        webbrowser.open(f'file://{frontend_path}')
        print("✅ Frontend opened in browser!")
        return True
    else:
        print("❌ Frontend file (index.html) not found!")
        return False

def run_integration_test():
    """Run a quick integration test"""
    print("🧪 Running integration test...")
    
    try:
        # Test backend health
        response = requests.get('http://localhost:5000/')
        if response.status_code != 200:
            print("❌ Backend health check failed")
            return False
        
        # Test session submission
        test_response = requests.post('http://localhost:5000/api/session', 
            json={"duration": 60})
        
        if test_response.status_code == 200:
            data = test_response.json()
            print("✅ Integration test passed!")
            print(f"📜 Test message: {data['message']}")
            return True
        else:
            print(f"❌ Session submission failed: {test_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    print("🧘 Stillness Timer - Quick Setup & Test")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    print()
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        return
    
    print()
    
    try:
        # Open frontend
        open_frontend()
        print()
        
        # Run integration test
        run_integration_test()
        print()
        
        print("🎉 Setup complete!")
        print()
        print("📝 Instructions:")
        print("   1. Your timer website is now open in the browser")
        print("   2. The backend server is running on http://localhost:5000")
        print("   3. When you switch tabs, your session will be submitted")
        print("   4. Check the browser console for session messages")
        print("   5. Visit http://localhost:5000/api/stats to see statistics")
        print()
        print("⏹️  Press Ctrl+C to stop the backend server")
        
        # Keep the backend running
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping backend server...")
            backend_process.terminate()
            backend_process.wait()
            print("✅ Backend server stopped!")
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping backend server...")
        backend_process.terminate()
        backend_process.wait()
        print("✅ Backend server stopped!")

if __name__ == "__main__":
    main()