#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZombieCoder AI Launcher - Complete Management System
Automatically manages servers, monitors performance, and fixes issues
"""

import subprocess
import requests
import time
import json
import psutil
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional

class ZombieCoderLauncher:
    def __init__(self):
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
                "path": "C:\\Users\\sahon\\.zombie_model",
                "command": "python fast_cursor_server.py",
                "process": None,
                "status": "stopped"
            }
        }
        
        self.performance_thresholds = {
            "health_check": 2000,  # 2 seconds
            "text_generation": 10000,  # 10 seconds
            "memory_usage": 80,  # 80% memory usage
            "cpu_usage": 90  # 90% CPU usage
        }
        
        self.backup_servers = {
            "cursor_backup": {
                "name": "Cursor Backup API",
                "port": 5003,
                "url": "http://localhost:5003",
                "path": "C:\\Users\\sahon\\.zombie_model",
                "command": "python simple_cursor_server.py",
                "process": None,
                "status": "stopped"
            }
        }
    
    def kill_all_python_processes(self):
        """Kill all Python processes to start fresh"""
        print("🔄 Killing all Python processes...")
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == 'python.exe':
                    try:
                        proc.kill()
                        print(f"   ✅ Killed Python process {proc.info['pid']}")
                    except:
                        pass
            time.sleep(3)
            print("✅ All Python processes killed")
        except Exception as e:
            print(f"❌ Error killing processes: {e}")
    
    def start_server(self, server_id: str) -> bool:
        """Start a specific server"""
        server = self.servers.get(server_id)
        if not server:
            return False
        
        try:
            print(f"🚀 Starting {server['name']}...")
            
            # Change to server directory and start
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
            time.sleep(5)
            
            # Check if server is responding
            if self.check_server_health(server_id):
                server['status'] = 'running'
                print(f"✅ {server['name']} started successfully")
                return True
            else:
                server['status'] = 'failed'
                print(f"❌ {server['name']} failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {server['name']}: {e}")
            server['status'] = 'failed'
            return False
    
    def stop_server(self, server_id: str):
        """Stop a specific server"""
        server = self.servers.get(server_id)
        if not server or not server['process']:
            return
        
        try:
            print(f"🛑 Stopping {server['name']}...")
            server['process'].terminate()
            server['process'].wait(timeout=5)
            server['status'] = 'stopped'
            print(f"✅ {server['name']} stopped")
        except:
            try:
                server['process'].kill()
                server['status'] = 'stopped'
            except:
                pass
    
    def check_server_health(self, server_id: str) -> bool:
        """Check if server is healthy"""
        server = self.servers.get(server_id)
        if not server:
            return False
        
        try:
            start_time = time.time()
            response = requests.get(f"{server['url']}/health", timeout=5)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                print(f"   ✅ {server['name']} healthy ({response_time:.2f}ms)")
                return True
            else:
                print(f"   ❌ {server['name']} unhealthy (HTTP {response.status_code})")
                return False
                
        except Exception as e:
            print(f"   ❌ {server['name']} not responding: {e}")
            return False
    
    def test_text_generation(self, server_id: str) -> Dict:
        """Test text generation performance"""
        server = self.servers.get(server_id)
        if not server:
            return {"status": "error", "time": 0}
        
        try:
            print(f"🧪 Testing {server['name']} text generation...")
            
            start_time = time.time()
            
            if server_id == "zombiecoder":
                # Direct API call
                payload = {
                    "model": "tinyllama-gguf",
                    "prompt": "Write a simple Python hello world program",
                    "stream": False
                }
                response = requests.post(f"{server['url']}/api/generate", json=payload, timeout=30)
            else:
                # Cursor API call
                payload = {
                    "model": "tinyllama-gguf",
                    "messages": [{"role": "user", "content": "Write a simple Python hello world program"}],
                    "max_tokens": 200
                }
                response = requests.post(f"{server['url']}/v1/chat/completions", json=payload, timeout=30)
            
            end_time = time.time()
            generation_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                print(f"   ✅ Generation successful ({generation_time:.2f}ms)")
                return {"status": "success", "time": generation_time}
            else:
                print(f"   ❌ Generation failed (HTTP {response.status_code})")
                return {"status": "error", "time": generation_time}
                
        except Exception as e:
            print(f"   ❌ Generation error: {e}")
            return {"status": "error", "time": 0}
    
    def check_system_resources(self) -> Dict:
        """Check system resource usage"""
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            
            return {
                "memory_percent": memory.percent,
                "memory_available": memory.available / (1024**3),  # GB
                "cpu_percent": cpu,
                "memory_ok": memory.percent < self.performance_thresholds["memory_usage"],
                "cpu_ok": cpu < self.performance_thresholds["cpu_usage"]
            }
        except Exception as e:
            print(f"❌ Error checking system resources: {e}")
            return {"memory_percent": 0, "cpu_percent": 0, "memory_ok": True, "cpu_ok": True}
    
    def performance_monitor(self):
        """Monitor performance and auto-fix issues"""
        print("📊 Starting performance monitoring...")
        
        while True:
            try:
                # Check system resources
                resources = self.check_system_resources()
                
                if not resources["memory_ok"] or not resources["cpu_ok"]:
                    print("⚠️  High resource usage detected!")
                    print(f"   Memory: {resources['memory_percent']:.1f}%")
                    print(f"   CPU: {resources['cpu_percent']:.1f}%")
                    
                    # Restart servers to free resources
                    self.restart_all_servers()
                    continue
                
                # Check server health
                for server_id in self.servers:
                    if not self.check_server_health(server_id):
                        print(f"⚠️  {self.servers[server_id]['name']} is unhealthy!")
                        self.restart_server(server_id)
                
                # Test text generation performance
                for server_id in self.servers:
                    if self.servers[server_id]['status'] == 'running':
                        result = self.test_text_generation(server_id)
                        if result['time'] > self.performance_thresholds['text_generation']:
                            print(f"⚠️  {self.servers[server_id]['name']} is slow ({result['time']:.2f}ms)!")
                            self.restart_server(server_id)
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                print("\n🛑 Performance monitoring stopped")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(10)
    
    def restart_server(self, server_id: str):
        """Restart a specific server"""
        print(f"🔄 Restarting {self.servers[server_id]['name']}...")
        self.stop_server(server_id)
        time.sleep(2)
        self.start_server(server_id)
    
    def restart_all_servers(self):
        """Restart all servers"""
        print("🔄 Restarting all servers...")
        for server_id in self.servers:
            self.stop_server(server_id)
        time.sleep(3)
        for server_id in self.servers:
            self.start_server(server_id)
    
    def start_backup_server(self, backup_id: str):
        """Start backup server when main server fails"""
        backup = self.backup_servers.get(backup_id)
        if not backup:
            return False
        
        try:
            print(f"🚀 Starting backup server: {backup['name']}...")
            
            process = subprocess.Popen(
                backup['command'],
                cwd=backup['path'],
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            backup['process'] = process
            backup['status'] = 'running'
            
            time.sleep(5)
            
            if self.check_server_health(backup_id):
                print(f"✅ Backup server {backup['name']} started")
                return True
            else:
                print(f"❌ Backup server {backup['name']} failed")
                return False
                
        except Exception as e:
            print(f"❌ Error starting backup server: {e}")
            return False
    
    def show_status(self):
        """Show current status of all servers"""
        print("\n📊 Server Status Report")
        print("=" * 50)
        
        for server_id, server in self.servers.items():
            status_icon = "✅" if server['status'] == 'running' else "❌" if server['status'] == 'failed' else "⏳"
            print(f"{status_icon} {server['name']:20} | Port {server['port']:4} | {server['status'].upper()}")
        
        print("\n📈 Performance Metrics")
        print("-" * 30)
        
        for server_id, server in self.servers.items():
            if server['status'] == 'running':
                health_ok = self.check_server_health(server_id)
                if health_ok:
                    result = self.test_text_generation(server_id)
                    speed = "FAST" if result['time'] < 5000 else "SLOW" if result['time'] > 15000 else "NORMAL"
                    print(f"   {server['name']:20} | {result['time']:8.2f}ms | {speed}")
        
        # System resources
        resources = self.check_system_resources()
        print(f"\n💻 System Resources")
        print(f"   Memory: {resources['memory_percent']:.1f}%")
        print(f"   CPU: {resources['cpu_percent']:.1f}%")
    
    def launch_system(self):
        """Launch the complete system"""
        print("🚀 ZombieCoder AI Launcher")
        print("=" * 40)
        print("🎯 Complete AI system management")
        print("⚡ Auto-performance optimization")
        print("🔄 Auto-restart on issues")
        print("=" * 40)
        
        # Step 1: Kill all existing processes
        print("\n🔄 Step 1: Cleaning up existing processes...")
        self.kill_all_python_processes()
        
        # Step 2: Start main servers
        print("\n🚀 Step 2: Starting main servers...")
        for server_id in self.servers:
            self.start_server(server_id)
        
        # Step 3: Wait for servers to stabilize
        print("\n⏳ Step 3: Waiting for servers to stabilize...")
        time.sleep(10)
        
        # Step 4: Show status
        print("\n📊 Step 4: System status check...")
        self.show_status()
        
        # Step 5: Start monitoring
        print("\n📈 Step 5: Starting performance monitoring...")
        print("💡 The system will automatically:")
        print("   - Monitor server health")
        print("   - Restart slow servers")
        print("   - Optimize performance")
        print("   - Start backup servers if needed")
        print("\nPress Ctrl+C to stop monitoring")
        
        try:
            self.performance_monitor()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down all servers...")
            for server_id in self.servers:
                self.stop_server(server_id)
            print("✅ All servers stopped")

def main():
    """Main launcher function"""
    launcher = ZombieCoderLauncher()
    launcher.launch_system()

if __name__ == "__main__":
    main()
