# এই ফাইলটি config/ ডিরেক্টরিতে তৈরি করুন
"""
ZombieCoder Main Server Integration Guide
"""

import requests
import json

class ZombieCoderMainServer:
    def __init__(self, main_server_url: str = "http://localhost:12346"):
        self.main_server_url = main_server_url
        self.agent_url = "http://localhost:8001"
    
    def register_agent(self):
        """এজেন্টকে মেইন সার্ভারে রেজিস্টার করুন"""
        registration_data = {
            "agent_name": "ZombieCoder Family Agent",
            "agent_type": "unified_assistant",
            "capabilities": ["coding", "debugging", "frontend", "architecture", "database", "api", "security", "performance"],
            "endpoints": {
                "chat": f"{self.agent_url}/chat",
                "status": f"{self.agent_url}/status",
                "health": f"{self.agent_url}/health"
            },
            "metadata": {
                "version": "2.0.0",
                "family_approach": True,
                "truth_verification": True,
                "memory_system": "json+sqlite"
            }
        }
        
        try:
            response = requests.post(
                f"{self.main_server_url}/agents/configure",
                json=registration_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Agent registered successfully with main server")
                return True
            else:
                print(f"❌ Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def send_chat_to_agent(self, message: str, context: dict = None):
        """এজেন্টের মাধ্যমে চ্যাট সেন্ড করুন"""
        if context is None:
            context = {}
        
        chat_data = {
            "message": message,
            "context": context,
            "agent": "ZombieCoder"
        }
        
        try:
            response = requests.post(
                f"{self.agent_url}/chat",
                json=chat_data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Request failed: {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_agent_status(self):
        """এজেন্ট স্ট্যাটাস চেক করুন"""
        try:
            response = requests.get(f"{self.agent_url}/status", timeout=5)
            return response.json() if response.status_code == 200 else {"error": "Status check failed"}
        except Exception as e:
            return {"error": str(e)}
    
    def health_check(self):
        """সম্পূর্ণ হেলথ চেক"""
        try:
            # এজেন্ট হেলথ
            agent_health = requests.get(f"{self.agent_url}/health", timeout=5)
            
            # মেইন সার্ভার হেলথ
            main_health = requests.get(f"{self.main_server_url}/health", timeout=5)
            
            return {
                "agent_healthy": agent_health.status_code == 200,
                "main_server_healthy": main_health.status_code == 200,
                "timestamp": "2024-01-15T10:30:00"
            }
        except Exception as e:
            return {"error": str(e)}

# Usage Example
if __name__ == "__main__":
    integrator = ZombieCoderMainServer()
    
    # Register agent
    integrator.register_agent()
    
    # Test chat
    result = integrator.send_chat_to_agent(
        "ভাইয়া, Laravel এ routing error কিভাবে fix করব?",
        {"framework": "laravel", "issue_type": "routing"}
    )
    
    print("Chat Result:", json.dumps(result, indent=2))
    
    # Check status
    status = integrator.get_agent_status()
    print("Agent Status:", json.dumps(status, indent=2))