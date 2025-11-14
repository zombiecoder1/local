#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Force Cursor AI Connector
This script forces Cursor AI to connect to our local servers
"""

import os
import json
import shutil
import requests
import time
from pathlib import Path

class ForceCursorConnector:
    def __init__(self):
        self.cursor_config_paths = [
            os.path.expanduser("~/.cursor"),
            os.path.expanduser("~/AppData/Roaming/Cursor"),
            os.path.expanduser("~/AppData/Local/Cursor"),
            "C:\\Users\\{}\\AppData\\Roaming\\Cursor".format(os.getenv('USERNAME', '')),
            "C:\\Users\\{}\\AppData\\Local\\Cursor".format(os.getenv('USERNAME', ''))
        ]
        
        self.our_server_config = {
            "name": "ZombieCoder Local AI",
            "baseURL": "http://localhost:5002",
            "apiKey": "",
            "model": "tinyllama-gguf",
            "priority": 1,
            "enabled": True,
            "force_connect": True
        }
    
    def find_cursor_config(self):
        """Find Cursor configuration directory"""
        for path in self.cursor_config_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path):
                print(f"✅ Found Cursor config at: {expanded_path}")
                return expanded_path
        
        print("❌ Cursor configuration not found")
        return None
    
    def create_cursor_config(self, config_dir):
        """Create/update Cursor configuration"""
        try:
            # Create config directory if it doesn't exist
            os.makedirs(config_dir, exist_ok=True)
            
            # Create settings.json
            settings_path = os.path.join(config_dir, "settings.json")
            
            # Load existing settings or create new
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
            else:
                settings = {}
            
            # Force our configuration
            if "ai" not in settings:
                settings["ai"] = {}
            
            if "customModels" not in settings["ai"]:
                settings["ai"]["customModels"] = []
            
            # Remove any existing ZombieCoder configs
            settings["ai"]["customModels"] = [
                model for model in settings["ai"]["customModels"] 
                if not model.get("name", "").startswith("ZombieCoder")
            ]
            
            # Add our configuration as the first (highest priority)
            settings["ai"]["customModels"].insert(0, self.our_server_config)
            
            # Force default model
            settings["ai"]["defaultModel"] = "ZombieCoder Local AI"
            settings["ai"]["preferredModel"] = "ZombieCoder Local AI"
            
            # Save settings
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
            
            print(f"✅ Cursor configuration updated at: {settings_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating Cursor config: {e}")
            return False
    
    def create_registry_entries(self):
        """Create Windows registry entries to force Cursor to use our server"""
        try:
            import winreg
            
            # Registry paths for Cursor
            registry_paths = [
                r"SOFTWARE\Cursor\AI",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\ZoneMap\Domains\localhost",
                r"SOFTWARE\Cursor\Settings"
            ]
            
            for path in registry_paths:
                try:
                    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
                    winreg.SetValueEx(key, "DefaultAIProvider", 0, winreg.REG_SZ, "ZombieCoder Local AI")
                    winreg.SetValueEx(key, "AIEndpoint", 0, winreg.REG_SZ, "http://localhost:5002")
                    winreg.SetValueEx(key, "ForceLocalAI", 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(key)
                    print(f"✅ Registry entry created: {path}")
                except:
                    pass
            
            return True
            
        except ImportError:
            print("⚠️  winreg not available, skipping registry entries")
            return False
        except Exception as e:
            print(f"❌ Error creating registry entries: {e}")
            return False
    
    def create_hosts_file_entry(self):
        """Create hosts file entry to redirect AI requests to our server"""
        try:
            hosts_file = r"C:\Windows\System32\drivers\etc\hosts"
            
            # Read current hosts file
            with open(hosts_file, 'r') as f:
                content = f.read()
            
            # Remove any existing ZombieCoder entries
            lines = content.split('\n')
            lines = [line for line in lines if 'zombiecoder' not in line.lower()]
            
            # Add our entry
            lines.append("# ZombieCoder AI Redirect")
            lines.append("127.0.0.1 localhost")
            
            # Write back
            with open(hosts_file, 'w') as f:
                f.write('\n'.join(lines))
            
            print("✅ Hosts file updated")
            return True
            
        except Exception as e:
            print(f"❌ Error updating hosts file: {e}")
            return False
    
    def create_cursor_shortcut(self):
        """Create Cursor shortcut with forced configuration"""
        try:
            # Find Cursor executable
            cursor_paths = [
                r"C:\Users\{}\AppData\Local\Programs\cursor\Cursor.exe".format(os.getenv('USERNAME', '')),
                r"C:\Program Files\Cursor\Cursor.exe",
                r"C:\Program Files (x86)\Cursor\Cursor.exe"
            ]
            
            cursor_exe = None
            for path in cursor_paths:
                if os.path.exists(path):
                    cursor_exe = path
                    break
            
            if not cursor_exe:
                print("❌ Cursor executable not found")
                return False
            
            # Create shortcut with our configuration
            shortcut_path = os.path.expanduser("~/Desktop/ZombieCoder_Cursor.lnk")
            
            # Create batch file to launch Cursor with our config
            batch_content = f'''@echo off
echo 🚀 Starting Cursor with ZombieCoder AI...
echo 📡 Forcing connection to local AI server...
echo.

REM Set environment variables to force our configuration
set CURSOR_AI_ENDPOINT=http://localhost:5002
set CURSOR_AI_MODEL=tinyllama-gguf
set CURSOR_FORCE_LOCAL_AI=1

REM Start Cursor
start "" "{cursor_exe}"

echo ✅ Cursor started with ZombieCoder AI configuration
pause
'''
            
            batch_path = os.path.expanduser("~/Desktop/Start_Cursor_with_ZombieCoder.bat")
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            print(f"✅ Cursor launcher created: {batch_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating Cursor shortcut: {e}")
            return False
    
    def test_our_server(self):
        """Test if our server is running and responding"""
        try:
            print("🧪 Testing our AI server...")
            
            # Test health
            response = requests.get("http://localhost:5002/health", timeout=5)
            if response.status_code == 200:
                print("✅ Our AI server is healthy")
            else:
                print("❌ Our AI server is not responding")
                return False
            
            # Test text generation
            payload = {
                "model": "tinyllama-gguf",
                "messages": [{"role": "user", "content": "Hello, test message"}],
                "max_tokens": 50
            }
            
            response = requests.post("http://localhost:5002/v1/chat/completions", json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"✅ Text generation working: {content[:50]}...")
                return True
            else:
                print("❌ Text generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Server test failed: {e}")
            return False
    
    def force_connect(self):
        """Force Cursor to connect to our server"""
        print("🚀 Force Cursor AI Connector")
        print("=" * 40)
        print("🎯 Forcing Cursor to use our local AI server")
        print("⚡ Bypassing cloud AI services")
        print("=" * 40)
        
        # Step 1: Test our server
        print("\n🧪 Step 1: Testing our AI server...")
        if not self.test_our_server():
            print("❌ Our AI server is not running!")
            print("💡 Please start the ZombieCoder launcher first:")
            print("   python ZombieCoder_Launcher.py")
            return False
        
        # Step 2: Find Cursor config
        print("\n🔍 Step 2: Finding Cursor configuration...")
        config_dir = self.find_cursor_config()
        if not config_dir:
            print("❌ Cursor not found or not installed")
            return False
        
        # Step 3: Update Cursor config
        print("\n⚙️ Step 3: Updating Cursor configuration...")
        if not self.create_cursor_config(config_dir):
            print("❌ Failed to update Cursor configuration")
            return False
        
        # Step 4: Create registry entries
        print("\n🔧 Step 4: Creating system registry entries...")
        self.create_registry_entries()
        
        # Step 5: Update hosts file
        print("\n🌐 Step 5: Updating network configuration...")
        self.create_hosts_file_entry()
        
        # Step 6: Create launcher
        print("\n🚀 Step 6: Creating Cursor launcher...")
        self.create_cursor_shortcut()
        
        print("\n✅ Force connection setup complete!")
        print("\n📋 Next steps:")
        print("1. Close Cursor if it's running")
        print("2. Run: Start_Cursor_with_ZombieCoder.bat")
        print("3. Cursor will now use our local AI server")
        print("4. Press Ctrl+K in Cursor to test")
        
        return True

def main():
    """Main function"""
    connector = ForceCursorConnector()
    connector.force_connect()

if __name__ == "__main__":
    main()
