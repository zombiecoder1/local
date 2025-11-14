#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Final ZombieCoder System Verification
Verifies all components are working correctly
"""

import requests
import json
import time
import sys
from pathlib import Path

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}{text:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{RESET}")

def test_endpoint(name, url, method="GET", payload=None, headers=None):
    """Test an endpoint and return results"""
    try:
        if headers is None:
            headers = {}
        
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:  # POST
            response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code in [200, 201]:
            print_success(f"{name}: Status {response.status_code}")
            try:
                data = response.json()
                if "model_status" in data:
                    status = data.get("model_status", {})
                    model_ready = status.get("ready", False)
                    model_status = status.get("model_name", "Unknown")
                    print_info(f"  └─ Model: {model_status} (Ready: {model_ready})")
                elif "choices" in data:
                    content = data["choices"][0]["message"]["content"][:80]
                    print_info(f"  └─ Response: {content}...")
            except:
                pass
            return True
        else:
            print_error(f"{name}: Status {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print_error(f"{name}: Request timeout (>30s)")
        return False
    except Exception as e:
        print_error(f"{name}: {str(e)}")
        return False

def main():
    print_header("🤖 ZombieCoder System Final Verification")
    
    # Test configuration
    tests = [
        {
            "name": "Agent Health Check",
            "url": "http://127.0.0.1:8001/health",
            "method": "GET"
        },
        {
            "name": "Proxy Health Check",
            "url": "http://127.0.0.1:5010/health",
            "method": "GET"
        },
        {
            "name": "Agent Info",
            "url": "http://127.0.0.1:8001/info",
            "method": "GET"
        },
        {
            "name": "Direct Agent Chat",
            "url": "http://127.0.0.1:8001/v1/chat/completions",
            "method": "POST",
            "payload": {
                "model": "deepseek-coder-1.3b",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 50
            }
        },
        {
            "name": "Proxy Chat (with auth header)",
            "url": "http://127.0.0.1:5010/v1/chat/completions",
            "method": "POST",
            "payload": {
                "model": "deepseek-coder-1.3b",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 50
            },
            "headers": {
                "Authorization": "Bearer DUMMY_API_KEY_FOR_LOCAL"
            }
        }
    ]
    
    results = {}
    
    # Run tests
    for test in tests:
        name = test["name"]
        url = test["url"]
        method = test.get("method", "GET")
        payload = test.get("payload")
        headers = test.get("headers")
        
        results[name] = test_endpoint(name, url, method, payload, headers)
        time.sleep(0.5)  # Small delay between requests
    
    # Summary
    print_header("📊 Verification Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print_info(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print_success("All systems operational! ✨")
        print_info("\n🎯 Your Cursor AI is now configured to use the local ZombieCoder agent!")
        print_info("   - Cursor will send requests to: http://localhost:5010 (via proxy)")
        print_info("   - Responses come from: deepseek-coder-1.3b local model")
        print_info("   - No cloud services are used")
        return 0
    elif passed >= 4:
        print_warning("Most systems operational, some issues detected")
        print_info("\nThese are likely temporary (model loading, etc.)")
        print_info("Try running this script again in 30 seconds")
        return 1
    else:
        print_error("Critical systems not operational")
        print_info("\nTroubleshooting:")
        print_info("1. Verify all servers are running:")
        print_info("   - Agent: python full_auto_install.ps1")
        print_info("   - Proxy: ./scripts/start_proxy.ps1")
        return 2

if __name__ == "__main__":
    sys.exit(main())
