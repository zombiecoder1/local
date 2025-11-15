#!/usr/bin/env python3
"""
Script to check if all required ZombieCoder services are running
"""

import requests
import json
import sys
from typing import Dict, Any

SERVICES = {
    "Proxy Server": {"port": 5051, "url": "http://127.0.0.1:5051/v1/models"},
    "API Gateway": {"port": 5050, "url": "http://127.0.0.1:5050/health"},
    "Python Agent": {"port": 8001, "url": "http://127.0.0.1:8001/v1/agent/info"},
    "Ollama Model Server": {"port": 8007, "url": "http://127.0.0.1:8007/api/tags"}
}

def check_service(name: str, service: Dict[str, Any]) -> Dict[str, Any]:
    """Check if a service is running"""
    try:
        response = requests.get(service["url"], timeout=5)
        return {
            "name": name,
            "port": service["port"],
            "status": "OK" if response.status_code == 200 else "ERROR",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else {"error": f"HTTP {response.status_code}"}
        }
    except requests.exceptions.RequestException as e:
        return {
            "name": name,
            "port": service["port"],
            "status": "ERROR",
            "status_code": "N/A",
            "response": {"error": str(e)}
        }

def main():
    """Main function to check all services"""
    print("🔍 Checking ZombieCoder Services...\n")
    
    results = []
    all_ok = True
    
    for name, service in SERVICES.items():
        result = check_service(name, service)
        results.append(result)
        
        status_icon = "✅" if result["status"] == "OK" else "❌"
        print(f"{status_icon} {result['name']} (Port {result['port']}): {result['status']}")
        
        if result["status"] != "OK":
            all_ok = False
            print(f"   Error: {result['response']['error']}")
    
    print("\n" + "="*50)
    if all_ok:
        print("🎉 All services are running correctly!")
        print("You can now start the dashboard with: npm start")
    else:
        print("⚠️  Some services are not running correctly.")
        print("Please check the errors above and ensure all services are started.")
    
    # Save results to file
    with open("service_status.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📝 Detailed status saved to service_status.json")

if __name__ == "__main__":
    main()