#!/usr/bin/env python3
"""
HTTP/HTTPS Proxy Server with CONNECT Tunneling Support
Supports bidirectional tunneling for HTTPS connections
Enhanced with Cursor AI servers and wildcard pattern matching
"""

import socket
import threading
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import fnmatch  # For wildcard pattern matching

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/proxy_server.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Supported hosts with wildcard patterns
SUPPORTED_HOSTS = {
    # Cursor AI Servers - specific + wildcard
    'api2.cursor.sh': True,
    'marketplace.cursorapi.com': True,
    'prod.authentication.cursor.sh': True,
    'api.cursor.sh': True,
    'cursor.sh': True,
    'cursorapi.com': True,
    '*.cursor.sh': True,
    '*.cursor.com': True,
    '*.cursorapi.com': True,
    
    # Qoder Servers
    'api1.qoder.sh': True,
    'api2.qoder.sh': True,
    'api3.qoder.sh': True,
    'center.qoder.sh': True,
    'qts2.qoder.sh': True,
    'repo2.qoder.sh': True,
    'download.qoder.com': True,
    '*.qoder.sh': True,
    '*.qoder.com': True,
    
    # Test servers
    'example.com': True,
    'google.com': True,
    'github.com': True,
}

def is_host_allowed(hostname: str) -> bool:
    """
    Check if hostname is allowed using exact match or wildcard patterns.
    Also intercepts localhost requests to local agent.
    """
    # Localhost/127.0.0.1 - redirect to local agent
    if hostname in ['localhost', '127.0.0.1', 'localhost:8001', '127.0.0.1:8001']:
        logger.info(f"[INTERCEPT] Local agent request: {hostname} -> forwarding to local agent")
        return True
    
    # Direct match
    if hostname in SUPPORTED_HOSTS:
        logger.info(f"[ALLOW] Host allowed (exact): {hostname}")
        return True
    
    # Wildcard pattern matching
    for pattern in SUPPORTED_HOSTS.keys():
        if fnmatch.fnmatch(hostname, pattern):
            logger.info(f"[ALLOW] Host {hostname} matches pattern {pattern}")
            return True
    
    # Catch-all: All *.cursor.* domains
    if fnmatch.fnmatch(hostname, '*.cursor.*'):
        logger.info(f"[ALLOW] Host {hostname} matches *.cursor.* pattern")
        return True
    
    # Catch-all: All *.qoder.* domains
    if fnmatch.fnmatch(hostname, '*.qoder.*'):
        logger.info(f"[ALLOW] Host {hostname} matches *.qoder.* pattern")
        return True
    
    logger.warning(f"[BLOCK] Host NOT allowed: {hostname}")
    return False


class ProxyHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler with CONNECT tunneling support"""
    
    timeout = 600  # 10 minutes for long-lived connections
    
    def do_GET(self):
        """Handle GET requests"""
        self.handle_request()
    
    def do_POST(self):
        """Handle POST requests"""
        self.handle_request()
    
    def do_PUT(self):
        """Handle PUT requests"""
        self.handle_request()
    
    def do_DELETE(self):
        """Handle DELETE requests"""
        self.handle_request()
    
    def do_HEAD(self):
        """Handle HEAD requests"""
        self.handle_request()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests"""
        self.handle_request()
    
    def do_PATCH(self):
        """Handle PATCH requests"""
        self.handle_request()
    
    def do_CONNECT(self):
        """
        Handle CONNECT requests for HTTPS tunneling.
        Establishes secure tunnel to remote server.
        """
        try:
            # Parse host and port from request path
            host, port_str = self.path.split(':')
            port = int(port_str)
        except (ValueError, IndexError):
            self.send_error(400, "Bad CONNECT request")
            return
        
        # Check if host is allowed
        if not is_host_allowed(host):
            logger.warning(f"[BLOCKED] CONNECT to {host}:{port} - host not in whitelist")
            self.send_error(403, "Forbidden")
            return
        
        logger.info(f"[CONNECT] Establishing tunnel to {host}:{port}")
        
        try:
            # Create socket to remote server
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.settimeout(self.timeout)
            remote_socket.connect((host, port))
            
            # Send HTTP 200 response to client
            self.send_response(200, 'Connection established')
            self.end_headers()
            
            logger.info(f"[SUCCESS] Connected to {host}:{port}")
            
            # Create bidirectional tunnel
            self._tunnel(self.connection, remote_socket)
            
        except socket.timeout:
            logger.error(f"[ERROR] Timeout: {host}:{port}")
            self.send_error(504, "Gateway Timeout")
        except socket.gaierror as e:
            logger.error(f"[ERROR] DNS error for {host}: {e}")
            self.send_error(503, "Service Unavailable")
        except ConnectionRefusedError:
            logger.error(f"[ERROR] Connection refused: {host}:{port}")
            self.send_error(503, "Service Unavailable")
        except Exception as e:
            logger.error(f"[ERROR] CONNECT error: {e}")
            self.send_error(500, "Internal Server Error")
        finally:
            try:
                remote_socket.close()
            except:
                pass
    
    def _tunnel(self, client_socket, remote_socket):
        """
        Bidirectional tunnel using two daemon threads.
        """
        def forward_data(src, dst, name):
            """Forward data between sockets"""
            try:
                while True:
                    data = src.recv(8192)
                    if not data:
                        break
                    dst.sendall(data)
            except Exception as e:
                logger.debug(f"[TUNNEL] {name}: {e}")
            finally:
                try:
                    dst.shutdown(socket.SHUT_WR)
                except:
                    pass
        
        # Two-way tunneling threads
        t1 = threading.Thread(
            target=forward_data,
            args=(client_socket, remote_socket, "Client->Server"),
            daemon=True
        )
        t2 = threading.Thread(
            target=forward_data,
            args=(remote_socket, client_socket, "Server->Client"),
            daemon=True
        )
        
        t1.start()
        t2.start()
        
        logger.info("[TUNNEL] Bidirectional tunnel active")
        
        t1.join()
        t2.join()
        
        logger.info("[TUNNEL] Tunnel closed")
    
    def handle_request(self):
        """Handle HTTP requests (GET, POST, etc.)"""
        try:
            # Extract host from URL or Host header
            if self.path.startswith('http'):
                from urllib.parse import urlparse
                parsed = urlparse(self.path)
                host = parsed.netloc
                path = parsed.path or '/'
                if parsed.query:
                    path += '?' + parsed.query
            else:
                host = self.headers.get('Host', 'localhost')
                path = self.path
            
            # Split host and port
            if ':' in host:
                hostname, port_str = host.rsplit(':', 1)
                port = int(port_str)
            else:
                hostname = host
                port = 443 if self.path.startswith('https') else 80
            
            logger.info(f"[REQUEST] {self.command} {path} to {hostname}:{port}")
            
            # Create connection to remote server
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.settimeout(self.timeout)
            remote_socket.connect((hostname, port))
            
            # Build request
            request_line = f"{self.command} {path} {self.request_version}\r\n"
            headers = ""
            for header, value in self.headers.items():
                if header.lower() != 'proxy-connection':
                    headers += f"{header}: {value}\r\n"
            
            request = request_line + headers + "\r\n"
            
            # Send to remote
            if self.command in ['POST', 'PUT', 'PATCH']:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                remote_socket.sendall(request.encode() + body)
            else:
                remote_socket.sendall(request.encode())
            
            # Receive response
            response = b""
            while True:
                try:
                    chunk = remote_socket.recv(8192)
                    if not chunk:
                        break
                    response += chunk
                except:
                    break
            
            remote_socket.close()
            
            # Send response to client
            if response:
                self.wfile.write(response)
            else:
                self.send_error(502, "Bad Gateway")
                
        except Exception as e:
            logger.error(f"[ERROR] Request handler: {e}")
            self.send_error(500, "Internal Server Error")


def run_proxy():
    """Start the proxy server"""
    import os
    os.makedirs('logs', exist_ok=True)
    
    server_address = ('127.0.0.1', 5010)
    httpd = HTTPServer(server_address, ProxyHandler)
    
    logger.info("="*70)
    logger.info("Proxy Server Starting")
    logger.info("="*70)
    logger.info(f"[SERVER] Listening on {server_address[0]}:{server_address[1]}")
    logger.info(f"[CONFIG] Timeout: {ProxyHandler.timeout} seconds")
    logger.info(f"[WHITELIST] Supporting {len(SUPPORTED_HOSTS)} patterns")
    logger.info("")
    logger.info("Supported hosts:")
    for host in sorted(SUPPORTED_HOSTS.keys()):
        logger.info(f"   {host}")
    logger.info("")
    logger.info("="*70)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n[STOP] Shutting down...")
        httpd.shutdown()
        logger.info("[STOP] Proxy server stopped")


if __name__ == '__main__':
    run_proxy()
