#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized ZombieCoder Launcher - Keeps Model Loaded
Fixes model unload issue and runs everything in background
"""

import subprocess
import requests
import time
import threading
import os
import psutil
from pathlib import Path

class OptimizedLauncher:
    def __init__(self):
        self.base_dir = Path("C:\\Users\\sahon\\.zombie_model")
        self.servers = {
            "zombiecoder": {
                "name": "ZombieCoder Server",
                "port": 8155,
                "url": "http://localhost:8155",
                "path": "C:\\model",
                "command": "python model_server.py",
                "process": None,
                "status": "stopped"
            },
            "cursor_fast": {
                "name": "Cursor Fast API", 
                "port": 5002,
                "url": "http://localhost:5002",
                "path": str(self.base_dir / "scripts"),
                "command": "python fast_cursor_server.py",
                "process": None,
                "status": "stopped"
            }
        }
        
        self.model_loaded = False
        self.keepalive_running = False
    
    def kill_existing_processes(self):
        """Kill all existing processes"""
        print("🛑 Killing existing processes...")
        try:
            # Kill Python processes
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == 'python.exe':
                    try:
                        proc.kill()
                        print(f"   ✅ Killed Python process {proc.info['pid']}")
                    except:
                        pass
            
            # Kill processes on our ports
            ports_to_kill = [8155, 5000, 5001, 5002, 5003]
            for port in ports_to_kill:
                try:
                    for conn in psutil.net_connections():
                        if conn.laddr.port == port:
                            try:
                                proc = psutil.Process(conn.pid)
                                proc.kill()
                                print(f"   ✅ Killed process on port {port}")
                            except:
                                pass
                except:
                    pass
            
            time.sleep(3)
            print("✅ All processes killed")
        except Exception as e:
            print(f"❌ Error killing processes: {e}")
    
    def start_server_background(self, server_id):
        """Start server in background without opening window"""
        server = self.servers[server_id]
        try:
            print(f"🚀 Starting {server['name']} in background...")
            
            # Start in background without window
            process = subprocess.Popen(
                server['command'],
                cwd=server['path'],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            server['process'] = process
            server['status'] = 'starting'
            
            # Wait for server to start
            time.sleep(8)
            
            # Test if server is responding
            try:
                response = requests.get(f"{server['url']}/health", timeout=10)
                if response.status_code == 200:
                    server['status'] = 'running'
                    print(f"✅ {server['name']} started successfully")
                    return True
                else:
                    server['status'] = 'failed'
                    print(f"❌ {server['name']} failed to start (HTTP {response.status_code})")
                    return False
            except Exception as e:
                server['status'] = 'failed'
                print(f"❌ {server['name']} not responding: {e}")
                return False
                
        except Exception as e:
            server['status'] = 'failed'
            print(f"❌ Error starting {server['name']}: {e}")
            return False
    
    def ensure_model_loaded(self):
        """Ensure model is loaded and stays loaded"""
        try:
            print("🤖 Ensuring model is loaded...")
            
            # Check if model is already loaded
            response = requests.get("http://localhost:8155/runtime/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                
                for model in models:
                    if model.get('model') == 'tinyllama-gguf' and model.get('status') == 'ready':
                        print("✅ Model is already loaded")
                        self.model_loaded = True
                        return True
            
            # Load model if not loaded
            print("🔄 Loading model...")
            load_response = requests.post(
                "http://localhost:8155/runtime/load/tinyllama-gguf?threads=4",
                timeout=30
            )
            
            if load_response.status_code == 200:
                print("✅ Model loaded successfully")
                self.model_loaded = True
                return True
            else:
                print(f"❌ Failed to load model: {load_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error ensuring model loaded: {e}")
            return False
    
    def model_keepalive(self):
        """Keep model loaded by sending periodic requests"""
        print("🔄 Starting model keepalive...")
        self.keepalive_running = True
        
        while self.keepalive_running:
            try:
                # Send status check to keep model alive
                response = requests.get("http://localhost:8155/runtime/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    models = data.get('models', [])
                    
                    # Check if model is still loaded
                    model_loaded = False
                    for model in models:
                        if model.get('model') == 'tinyllama-gguf' and model.get('status') == 'ready':
                            model_loaded = True
                            break
                    
                    if not model_loaded:
                        print("⚠️  Model unloaded, reloading...")
                        self.ensure_model_loaded()
                    else:
                        print("✅ Model is loaded and ready")
                
                # Wait before next check
                time.sleep(30)
                
            except Exception as e:
                print(f"❌ Keepalive error: {e}")
                time.sleep(10)
    
    def start_keepalive_thread(self):
        """Start model keepalive in background thread"""
        if not self.keepalive_running:
            thread = threading.Thread(target=self.model_keepalive, daemon=True)
            thread.start()
            print("🔄 Model keepalive thread started")
    
    def test_system(self):
        """Test the complete system"""
        print("🧪 Testing system...")
        
        # Test ZombieCoder server
        try:
            response = requests.get("http://localhost:8155/health", timeout=5)
            if response.status_code == 200:
                print("✅ ZombieCoder Server: ONLINE")
            else:
                print("❌ ZombieCoder Server: OFFLINE")
                return False
        except:
            print("❌ ZombieCoder Server: OFFLINE")
            return False
        
        # Test Cursor API
        try:
            response = requests.get("http://localhost:5002/health", timeout=5)
            if response.status_code == 200:
                print("✅ Cursor Fast API: ONLINE")
            else:
                print("❌ Cursor Fast API: OFFLINE")
                return False
        except:
            print("❌ Cursor Fast API: OFFLINE")
            return False
        
        # Test model
        try:
            response = requests.get("http://localhost:8155/runtime/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                for model in models:
                    if model.get('model') == 'tinyllama-gguf' and model.get('status') == 'ready':
                        print("✅ Model: LOADED")
                        return True
                print("❌ Model: NOT LOADED")
                return False
            else:
                print("❌ Model: NOT LOADED")
                return False
        except:
            print("❌ Model: NOT LOADED")
            return False
    
    def start_system(self):
        """Start the complete system"""
        print("🚀 Optimized ZombieCoder Launcher")
        print("=" * 50)
        print("🎯 Fixes model unload issue")
        print("🔄 Keeps model loaded automatically")
        print("📊 Runs everything in background")
        print("=" * 50)
        
        # Step 1: Kill existing processes
        print("\n🛑 Step 1: Killing existing processes...")
        self.kill_existing_processes()
        
        # Step 2: Start ZombieCoder server
        print("\n🚀 Step 2: Starting ZombieCoder server...")
        if not self.start_server_background("zombiecoder"):
            print("❌ Failed to start ZombieCoder server")
            return False
        
        # Step 3: Ensure model is loaded
        print("\n🤖 Step 3: Loading model...")
        if not self.ensure_model_loaded():
            print("❌ Failed to load model")
            return False
        
        # Step 4: Start Cursor API
        print("\n🌐 Step 4: Starting Cursor API...")
        if not self.start_server_background("cursor_fast"):
            print("❌ Failed to start Cursor API")
            return False
        
        # Step 5: Start model keepalive
        print("\n🔄 Step 5: Starting model keepalive...")
        self.start_keepalive_thread()
        
        # Step 6: Test system
        print("\n🧪 Step 6: Testing system...")
        if not self.test_system():
            print("❌ System test failed")
            return False
        
        print("\n✅ System started successfully!")
        print("\n📊 System Status:")
        print("   ✅ ZombieCoder Server: http://localhost:8155")
        print("   ✅ Cursor Fast API: http://localhost:5002")
        print("   ✅ Model: tinyllama-gguf (LOADED)")
        print("   ✅ Model Keepalive: ACTIVE")
        
        print("\n🎯 Cursor AI Configuration:")
        print("   Model Name: ZombieCoder Local AI")
        print("   API Base URL: http://localhost:5002")
        print("   API Key: (leave empty)")
        print("   Model ID: tinyllama-gguf")
        
        print("\n🔄 Model will stay loaded automatically")
        print("📊 All servers running in background")
        print("\nPress Ctrl+C to stop...")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            self.keepalive_running = False
            for server in self.servers.values():
                if server['process']:
                    server['process'].terminate()
            print("✅ All servers stopped")

def main():
    launcher = OptimizedLauncher()
    launcher.start_system()

if __name__ == "__main__":
    main()
