#!/usr/bin/env python3
"""
Proxy Server Launcher for ZombieCoder Agent
Routes Cursor AI calls to local ZombieCoder Agent on port 8001
Proxy listens on port 5010
"""

import sys
import os
import subprocess

# Add the project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Environment setup
os.environ['PROXY_PORT'] = '5010'
os.environ['PROXY_BIND_HOST'] = '127.0.0.1'
os.environ['PROXY_TARGET_BASE'] = 'http://127.0.0.1:8001'
os.environ['PROXY_API_KEY'] = 'DUMMY_API_KEY_FOR_LOCAL'

def main():
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   ZombieCoder Proxy Adapter                                ║
    ║   Intercepting Cursor AI calls → Local Agent               ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    print(f"🚀 Proxy Server Starting...")
    print(f"📍 Listening on:     http://127.0.0.1:5010")
    print(f"🎯 Forwarding to:    http://127.0.0.1:8001")
    print(f"🔐 API Key:          DUMMY_API_KEY_FOR_LOCAL")
    print(f"📝 Log File:         logs/proxy_adapter.log")
    print("")
    print("⚠️  Configuration:")
    print("   - Cursor AI should point to: http://127.0.0.1:5010/v1")
    print("   - All calls will be intercepted and routed to ZombieCoder")
    print("")
    
    # Import and run proxy adapter
    try:
        from proxy_adapter import run_server, TARGET_BASE, DEFAULT_HOST, DEFAULT_PORT
        print(f"✅ Proxy Adapter Module Loaded")
        print(f"   Target Base: {TARGET_BASE}")
        print("")
        run_server(DEFAULT_HOST, DEFAULT_PORT)
    except ImportError as e:
        print(f"❌ Error: Could not import proxy_adapter: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
