# এই ফাইলটি scripts/ ডিরেক্টরিতে তৈরি করুন
#!/usr/bin/env python3
"""
Health Check Script for ZombieCoder Agent
"""

import requests
import sys
import os
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

def health_check():
    port = os.getenv("AGENT_PORT", "8001")
    base_url = f"http://localhost:{port}"
    
    endpoints = {
        "Home": "/",
        "Health": "/health",
        "Status": "/status",
        "Memory": "/memory"
    }
    
    print("🔍 Running ZombieCoder Health Check...")
    print("=" * 50)
    
    all_healthy = True
    
    for name, endpoint in endpoints.items():
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: HEALTHY (Status: {response.status_code})")
            else:
                print(f"❌ {name}: UNHEALTHY (Status: {response.status_code})")
                all_healthy = False
        except Exception as e:
            print(f"❌ {name}: ERROR ({str(e)})")
            all_healthy = False
    
    print("=" * 50)
    
    if all_healthy:
        print("🎉 All systems are healthy!")
        return 0
    else:
        print("⚠️  Some systems are having issues.")
        return 1

if __name__ == "__main__":
    sys.exit(health_check())