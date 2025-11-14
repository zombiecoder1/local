#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart ZombieCoder Launcher
- Kills ALL existing processes first
- Runs only ONE instance
- No duplicate processes
- Background + Frontend management
"""

import subprocess
import requests
import time
import threading
import os
import psutil
import signal
import sys
from pathlib import Path

class SmartLauncher:
    def __init__(self):
        self.base_dir = Path("C:\\Users\\sahon\\.zombie_model")
        self.ports = [8155, 5000, 5001, 5002, 5003]
        self.running = False
        
        # Server configurations
        self.servers = {
            "zombiecoder": {
                "name": "ZombieCoder Server",
                "port": 8155,
                "url": "http://localhost:8155",
                "path": "C:\\model",
                "command": "python model_server.py",
                "process": None,
                "pid": None
            },
            "cursor_fast": {
                "name": "Cursor Fast API",
                "port": 5002,
                "url": "http://localhost:5002", 
                "path": str(self.base_dir),
                "command": "python fast_cursor_server.py",
                "process": None,
                "pid": None
            }
        }
    
    def kill_all_processes(self):
        """Kill ALL existing processes - No mercy!"""
        print("🛑 KILLING ALL EXISTING PROCESSES...")
        print("=" * 50)
        
        killed_count = 0
        
        # Kill all Python processes
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python.exe':
                        # Check if it's our process
                        cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                        if any(keyword in cmdline.lower() for keyword in ['model_server', 'cursor_server', 'fast_cursor', 'zombiecoder']):
                            proc.kill()
                            killed_count += 1
                            print(f"   ✅ Killed Python process {proc.info['pid']}: {cmdline[:50]}...")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            print(f"   ⚠️  Error killing Python processes: {e}")
        
        # Kill processes on our ports
        for port in self.ports:
            try:
                for conn in psutil.net_connections():
                    if conn.laddr.port == port:
                        try:
                            proc = psutil.Process(conn.pid)
                            proc.kill()
                            killed_count += 1
                            print(f"   ✅ Killed process {conn.pid} on port {port}")
                        except:
                            pass
            except:
                pass
        
        # Force kill any remaining processes
        try:
            subprocess.run("taskkill /f /im python.exe", shell=True, capture_output=True)
            subprocess.run("taskkill /f /im cmd.exe", shell=True, capture_output=True)
        except:
            pass
        
        print(f"✅ Killed {killed_count} processes")
        time.sleep(3)
        print("✅ All processes cleared")
    
    def check_if_already_running(self):
        """Check if our system is already running"""
        print("🔍 Checking if system is already running...")
        
        for server_id, server in self.servers.items():
            try:
                response = requests.get(f"{server['url']}/health", timeout=2)
                if response.status_code == 200:
                    print(f"   ⚠️  {server['name']} is already running!")
                    return True
            except:
                pass
        
        return False
    
    def start_server_smart(self, server_id):
        """Start server smartly - only if not running"""
        server = self.servers[server_id]
        
        try:
            print(f"🚀 Starting {server['name']}...")
            
            # Check if already running
            try:
                response = requests.get(f"{server['url']}/health", timeout=2)
                if response.status_code == 200:
                    print(f"   ✅ {server['name']} already running")
                    return True
            except:
                pass
            
            # Start new process
            process = subprocess.Popen(
                server['command'],
                cwd=server['path'],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            server['process'] = process
            server['pid'] = process.pid
            
            # Wait for server to start
            print(f"   ⏳ Waiting for {server['name']} to start...")
            time.sleep(8)
            
            # Test server
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    response = requests.get(f"{server['url']}/health", timeout=5)
                    if response.status_code == 200:
                        print(f"   ✅ {server['name']} started successfully (PID: {process.pid})")
                        return True
                except:
                    if attempt < max_retries - 1:
                        print(f"   ⏳ Attempt {attempt + 1}/{max_retries} - waiting...")
                        time.sleep(3)
                    else:
                        print(f"   ❌ {server['name']} failed to start")
                        return False
            
            return False
            
        except Exception as e:
            print(f"   ❌ Error starting {server['name']}: {e}")
            return False
    
    def ensure_model_loaded(self):
        """Ensure model is loaded and stays loaded"""
        try:
            print("🤖 Ensuring model is loaded...")
            
            # Check current status
            response = requests.get("http://localhost:8155/runtime/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                for model in models:
                    if model.get('model') == 'tinyllama-gguf' and model.get('status') == 'ready':
                        print("   ✅ Model is already loaded")
                        return True
            
            # Load model
            print("   🔄 Loading model...")
            load_response = requests.post(
                "http://localhost:8155/runtime/load/tinyllama-gguf?threads=4",
                timeout=30
            )
            
            if load_response.status_code == 200:
                print("   ✅ Model loaded successfully")
                return True
            else:
                print(f"   ❌ Failed to load model: {load_response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error loading model: {e}")
            return False
    
    def model_keepalive(self):
        """Keep model loaded - Background thread"""
        print("🔄 Starting model keepalive...")
        
        while self.running:
            try:
                # Check model status
                response = requests.get("http://localhost:8155/runtime/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    models = data.get('models', [])
                    
                    model_loaded = False
                    for model in models:
                        if model.get('model') == 'tinyllama-gguf' and model.get('status') == 'ready':
                            model_loaded = True
                            break
                    
                    if not model_loaded:
                        print("   ⚠️  Model unloaded, reloading...")
                        self.ensure_model_loaded()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"   ❌ Keepalive error: {e}")
                time.sleep(10)
    
    def start_keepalive(self):
        """Start model keepalive thread"""
        if not self.running:
            self.running = True
            thread = threading.Thread(target=self.model_keepalive, daemon=True)
            thread.start()
            print("✅ Model keepalive started")
    
    def test_system(self):
        """Test complete system"""
        print("🧪 Testing system...")
        
        tests = [
            ("ZombieCoder Server", "http://localhost:8155/health"),
            ("Cursor Fast API", "http://localhost:5002/health"),
            ("Model Status", "http://localhost:8155/runtime/status")
        ]
        
        all_passed = True
        
        for test_name, url in tests:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {test_name}: ONLINE")
                else:
                    print(f"   ❌ {test_name}: OFFLINE")
                    all_passed = False
            except:
                print(f"   ❌ {test_name}: OFFLINE")
                all_passed = False
        
        return all_passed
    
    def show_status(self):
        """Show system status"""
        print("\n📊 SYSTEM STATUS")
        print("=" * 30)
        
        for server_id, server in self.servers.items():
            try:
                response = requests.get(f"{server['url']}/health", timeout=2)
                if response.status_code == 200:
                    print(f"✅ {server['name']:20} | Port {server['port']:4} | PID {server.get('pid', 'N/A'):4} | ONLINE")
                else:
                    print(f"❌ {server['name']:20} | Port {server['port']:4} | PID {server.get('pid', 'N/A'):4} | OFFLINE")
            except:
                print(f"❌ {server['name']:20} | Port {server['port']:4} | PID {server.get('pid', 'N/A'):4} | OFFLINE")
    
    def cleanup(self):
        """Cleanup on exit"""
        print("\n🛑 Cleaning up...")
        self.running = False
        
        for server_id, server in self.servers.items():
            if server['process']:
                try:
                    server['process'].terminate()
                    print(f"   ✅ Stopped {server['name']}")
                except:
                    pass
    
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C"""
        print("\n🛑 Shutdown signal received...")
        self.cleanup()
        sys.exit(0)
    
    def launch_system(self):
        """Launch the complete system"""
        print("🚀 SMART ZOMBIECODER LAUNCHER")
        print("=" * 50)
        print("🎯 Kills ALL existing processes")
        print("🔄 Runs only ONE instance")
        print("📊 Background + Frontend management")
        print("=" * 50)
        
        # Set up signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Step 1: Kill all existing processes
        print("\n🛑 Step 1: Killing ALL existing processes...")
        self.kill_all_processes()
        
        # Step 2: Check if already running
        print("\n🔍 Step 2: Checking for existing instances...")
        if self.check_if_already_running():
            print("⚠️  System already running! Killing and restarting...")
            self.kill_all_processes()
        
        # Step 3: Start ZombieCoder server
        print("\n🚀 Step 3: Starting ZombieCoder server...")
        if not self.start_server_smart("zombiecoder"):
            print("❌ Failed to start ZombieCoder server")
            return False
        
        # Step 4: Load model
        print("\n🤖 Step 4: Loading model...")
        if not self.ensure_model_loaded():
            print("❌ Failed to load model")
            return False
        
        # Step 5: Start Cursor API
        print("\n🌐 Step 5: Starting Cursor API...")
        if not self.start_server_smart("cursor_fast"):
            print("❌ Failed to start Cursor API")
            return False
        
        # Step 6: Start keepalive
        print("\n🔄 Step 6: Starting model keepalive...")
        self.start_keepalive()
        
        # Step 7: Test system
        print("\n🧪 Step 7: Testing system...")
        if not self.test_system():
            print("❌ System test failed")
            return False
        
        # Step 8: Show status
        self.show_status()
        
        print("\n✅ SYSTEM STARTED SUCCESSFULLY!")
        print("=" * 50)
        print("📊 All servers running in background")
        print("🔄 Model will stay loaded automatically")
        print("🎯 No duplicate processes")
        print("=" * 50)
        
        print("\n🎯 CURSOR AI CONFIGURATION:")
        print("   Model Name: ZombieCoder Local AI")
        print("   API Base URL: http://localhost:5002")
        print("   API Key: (leave empty)")
        print("   Model ID: tinyllama-gguf")
        
        print("\n🚀 QUICK START:")
        print("   1. Open Cursor")
        print("   2. Press Ctrl+K")
        print("   3. Your local AI will respond!")
        
        print("\n📊 MONITORING:")
        print("   - Model keepalive: ACTIVE")
        print("   - Auto-restart: ENABLED")
        print("   - Background mode: ON")
        
        print("\nPress Ctrl+C to stop...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.cleanup()

def main():
    launcher = SmartLauncher()
    launcher.launch_system()

if __name__ == "__main__":
    main()
