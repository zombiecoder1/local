#!/usr/bin/env python3
"""
Test proxy adapter connectivity and forwarding
"""

import requests
import json
import sys
import time

def test_proxy():
    """Test proxy adapter is running and forwarding requests"""
    
    PROXY_URL = "http://127.0.0.1:5010"
    AGENT_URL = "http://127.0.0.1:8001"
    
    print("""
╔════════════════════════════════════════════════════════════╗
║   Proxy Adapter Connectivity Test                          ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Test 1: Check proxy is running
    print("🧪 Test 1: Proxy Server Health Check")
    print(f"   URL: {PROXY_URL}/health")
    try:
        r = requests.get(f"{PROXY_URL}/health", timeout=5)
        if r.status_code == 200:
            print(f"   ✅ Status: {r.status_code}")
            print(f"   Response: {r.json()}")
        else:
            print(f"   ⚠️  Status: {r.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Proxy not running! Start it with:")
        print("      .\scripts\start_proxy.ps1")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("")
    
    # Test 2: Check agent is running
    print("🧪 Test 2: Agent Server Health Check")
    print(f"   URL: {AGENT_URL}/health")
    try:
        r = requests.get(f"{AGENT_URL}/health", timeout=5)
        if r.status_code == 200:
            print(f"   ✅ Status: {r.status_code}")
        else:
            print(f"   ⚠️  Status: {r.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ❌ Agent not running!")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("")
    
    # Test 3: Proxy forwards chat request
    print("🧪 Test 3: Chat Request Through Proxy")
    print(f"   URL: {PROXY_URL}/v1/chat/completions")
    
    payload = {
        "model": "deepseek-coder-1.3b",
        "messages": [{"role": "user", "content": "Hello from proxy test"}],
        "max_tokens": 100,
        "temperature": 0.7,
        "stream": False
    }
    
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        start_time = time.time()
        r = requests.post(
            f"{PROXY_URL}/v1/chat/completions",
            json=payload,
            headers={"Authorization": "Bearer DUMMY_API_KEY_FOR_LOCAL"},
            timeout=30
        )
        elapsed = time.time() - start_time
        
        print(f"   ✅ Status: {r.status_code}")
        print(f"   ⏱️  Response Time: {elapsed:.2f}s")
        
        if r.status_code == 200:
            try:
                data = r.json()
                print(f"   Response Preview: {str(data)[:200]}...")
            except:
                print(f"   Response: {r.text[:200]}...")
        else:
            print(f"   Error Response: {r.text}")
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Request Timeout (30s)")
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection Error: {e}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("")
    
    # Test 4: Check logs
    print("🧪 Test 4: Log File Check")
    import os
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'proxy_adapter.log')
    if os.path.exists(log_path):
        print(f"   ✅ Log file exists: {log_path}")
        # Show last 5 lines
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-5:]
                print("   Recent logs:")
                for line in lines:
                    print(f"      {line.rstrip()}")
        except Exception as e:
            print(f"   ⚠️  Could not read logs: {e}")
    else:
        print(f"   ⚠️  Log file not found: {log_path}")
    
    print("")
    print("✅ Test Complete!")
    return True

if __name__ == '__main__':
    success = test_proxy()
    sys.exit(0 if success else 1)
