#!/usr/bin/env python3
"""
Generator script to auto-create a server status test script.
Creates a test script to check all services and capture real responses.
"""

import json
import os

def generate_test_script():
    """Generate the server status test script"""
    script_content = '''#!/usr/bin/env python3
"""
Auto-generated server status test script.
Checks all local servers and captures their real responses.
"""

import requests
import json
import sys
import socket

def check_port(host, port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def get_service_status(url, headers=None):
    """Get service status and response"""
    try:
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        response = requests.get(url, headers=headers, timeout=5)
        return {
            'status': 'OK' if response.status_code == 200 else f'ERROR {response.status_code}',
            'status_code': response.status_code,
            'response': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:200]
        }
    except requests.exceptions.RequestException as e:
        return {
            'status': 'FAIL',
            'error': str(e),
            'response': None
        }
    except json.JSONDecodeError:
        return {
            'status': 'OK',
            'status_code': response.status_code,
            'response': 'Non-JSON response'
        }

def get_models_info():
    """Get models information from Ollama"""
    try:
        response = requests.get('http://127.0.0.1:8007/api/tags', timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return {
                'status': 'OK',
                'models': models
            }
        else:
            return {
                'status': f'ERROR {response.status_code}',
                'models': []
            }
    except Exception as e:
        return {
            'status': 'FAIL',
            'error': str(e),
            'models': []
        }

def main():
    """Main function to check all services"""
    print("🔍 Checking all local servers...")
    
    result = {
        'proxy': {
            'port': 5051,
            'status': 'UNKNOWN',
            'response': None
        },
        'gateway': {
            'port': 5050,
            'status': 'UNKNOWN',
            'response': None
        },
        'agent': {
            'port': 8001,
            'status': 'UNKNOWN',
            'response': None
        },
        'ollama': {
            'port': 8007,
            'status': 'UNKNOWN',
            'models': []
        }
    }
    
    # Check if ports are open
    services = [
        {'name': 'proxy', 'port': 5051, 'url': 'http://127.0.0.1:5051/v1/models'},
        {'name': 'gateway', 'port': 5050, 'url': 'http://127.0.0.1:5050/health'},
        {'name': 'agent', 'port': 8001, 'url': 'http://127.0.0.1:8001/v1/agent/info'}
    ]
    
    for service in services:
        print(f"Checking {service['name']} on port {service['port']}...")
        if check_port('127.0.0.1', service['port']):
            status_info = get_service_status(service['url'])
            result[service['name']]['status'] = status_info['status']
            result[service['name']]['response'] = status_info['response']
        else:
            result[service['name']]['status'] = 'FAIL'
            result[service['name']]['response'] = 'Port not open'
    
    # Check Ollama models
    print("Checking Ollama on port 8007...")
    if check_port('127.0.0.1', 8007):
        models_info = get_models_info()
        result['ollama']['status'] = models_info['status']
        result['ollama']['models'] = models_info['models']
    else:
        result['ollama']['status'] = 'FAIL'
        result['ollama']['models'] = []
    
    # Print JSON output
    print("\\n" + "="*50)
    print("📋 FINAL SYSTEM STATUS REPORT")
    print("="*50)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
'''
    
    return script_content

def main():
    """Main function to generate the test script"""
    print("🔧 Generating server status test script...")
    
    # Generate the test script
    test_script_content = generate_test_script()
    
    # Write the test script to file
    test_script_path = 'server_status_test.py'
    with open(test_script_path, 'w', encoding='utf-8') as f:
        f.write(test_script_content)
    
    print(f"✅ Generated test script: {test_script_path}")
    
    # Make the script executable
    try:
        os.chmod(test_script_path, 0o755)
    except:
        pass  # Ignore if chmod fails on Windows
    
    print("\\n📋 Deliverables:")
    print(f"1. generator.py (this script) - ✓ Created")
    print(f"2. server_status_test.py - ✓ Generated")
    print(f"3. Final JSON output - Run server_status_test.py to generate")
    
    print("\\n🚀 To run the test:")
    print("   python server_status_test.py")

if __name__ == "__main__":
    main()