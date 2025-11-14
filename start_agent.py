#!/usr/bin/env python3
"""
ZombieCoder Agent Smart Startup
Detects available Ollama server and starts the agent
"""

import os
import sys
import time
import requests
import subprocess
import threading
from pathlib import Path

def check_ollama_server(url, timeout=5):
    """Check if Ollama server is running"""
    try:
        response = requests.get(f"{url}/api/tags", timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False

def detect_ollama_servers():
    """Detect all available Ollama servers"""
    ports = [
        os.getenv("OLLAMA_PORT", "8007"),
        "8155",
        "11434"
    ]
    
    available_servers = []
    for port in ports:
        url = f"http://127.0.0.1:{port}"
        if check_ollama_server(url):
            available_servers.append(url)
            print(f"✓ Found Ollama server at {url}")
    
    return available_servers

def wait_for_ollama(timeout=60):
    """Wait for any Ollama server to become available"""
    print("\n" + "="*50)
    print("ZombieCoder Agent Startup")
    print("="*50)
    print("\nWaiting for Ollama server to be available...")
    print(f"Checking ports: 8007, 8155, 11434")
    print(f"Timeout: {timeout} seconds\n")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        servers = detect_ollama_servers()
        if servers:
            print(f"\n✓ Ollama server ready at: {servers[0]}")
            return servers[0]
        
        elapsed = int(time.time() - start_time)
        print(f"[{elapsed}s] Checking for Ollama server...", end='\r')
        time.sleep(2)
    
    print("\n✗ No Ollama server found within timeout period")
    print("You can still run the agent in offline mode")
    return None

def run_agent_server():
    """Start the unified agent server"""
    print("\nStarting ZombieCoder Agent Server...")
    print("Port: 8001")
    print("="*50 + "\n")
    
    # Run the agent
    try:
        subprocess.run([sys.executable, "unified_agent_system.py"], check=False)
    except KeyboardInterrupt:
        print("\nAgent server stopped")
    except Exception as e:
        print(f"Error running agent: {e}")

def main():
    """Main startup function"""
    # Check if running from portable package
    lock_file = Path(".LOCK")
    portable = lock_file.exists()
    
    if portable:
        print("\n🎒 ZombieCoder Portable Edition")
    else:
        print("\n🤖 ZombieCoder Agent System")
    
    # Check if we should wait for Ollama
    wait_for_ollama_env = os.getenv("WAIT_FOR_OLLAMA", "true").lower() == "true"
    timeout = int(os.getenv("OLLAMA_DETECTION_TIMEOUT", "30"))
    
    if wait_for_ollama_env:
        server = wait_for_ollama(timeout)
        if not server:
            print("\nℹ️  Agent will run in offline mode")
            print("   To use Ollama, ensure a server is running on port 8007, 8155, or 11434")
    
    # Start the agent server
    run_agent_server()

if __name__ == "__main__":
    main()
