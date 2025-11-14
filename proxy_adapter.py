#!/usr/bin/env python3
"""
Proxy adapter with optional file-based config, rotating logging, and streaming-forwarding.

Reads config from `config/proxy_config.json` if present. The config may contain:
- api_key: string (proxy API key)
- port: integer
- bind_host: string (default 127.0.0.1)
- target_base: URL of the local cursor server (default http://localhost:5001)
- log_file: path for proxy log
- log_max_bytes, log_backup_count

The proxy supports streaming forwarding: if the request body contains `"stream": true`,
the proxy will request the target with streaming and forward lines as SSE (`text/event-stream`).
"""

import os
import http.server
import socketserver
import requests
import threading
import json
import time
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Optional

# Defaults
TARGET_BASE = os.environ.get("PROXY_TARGET_BASE", "http://127.0.0.1:8001")
DEFAULT_HOST = os.environ.get("PROXY_BIND_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("PROXY_PORT", "5010"))

# Load optional file-based proxy config
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'proxy_config.json')
file_config: Dict = {}
if os.path.exists(CONFIG_PATH):
	try:
		with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
			file_config = json.load(f)
	except Exception:
		file_config = {}

"""
Compatibility: support both legacy and alternate config keys.
Recognized keys:
- target_base | base_url (only use base_url if it does not point to our proxy)
- bind_host
- port | proxy_port
- api_key | local_api_key
- shim_host + shim_port -> derive target_base if not provided
"""

# Upstream target base URL
tb = file_config.get('target_base')
if not tb:
	# Avoid accidental self-targeting: base_url usually refers to the proxy itself
	maybe_base = file_config.get('base_url')
	try:
		if maybe_base and str(maybe_base).rstrip('/').endswith(f":{DEFAULT_PORT}"):
			maybe_base = None
	except Exception:
		maybe_base = None
	if maybe_base:
		tb = None  # ignore; likely proxy URL, not upstream

# Derive from shim_host/port if still missing
if not tb and (file_config.get('shim_host') and file_config.get('shim_port')):
	try:
		tb = f"http://{file_config.get('shim_host')}:{int(file_config.get('shim_port'))}"
	except Exception:
		tb = None

if tb:
	TARGET_BASE = tb

# Bind host
if file_config.get('bind_host'):
	DEFAULT_HOST = file_config['bind_host']

# Listen port (support proxy_port or port)
port_val = file_config.get('proxy_port', file_config.get('port'))
if port_val is not None:
	try:
		DEFAULT_PORT = int(port_val)
	except Exception:
		pass

# If PROXY_API_KEY env var set it takes precedence; otherwise try config file
PROXY_API_KEY = os.environ.get('PROXY_API_KEY') or file_config.get('api_key') or file_config.get('local_api_key')

# Logging config
LOG_PATH = file_config.get('log_file') or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log', 'proxy.log')
LOG_MAX_BYTES = int(file_config.get('log_max_bytes', 5 * 1024 * 1024))
LOG_BACKUP_COUNT = int(file_config.get('log_backup_count', 3))

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logger = logging.getLogger('proxy_adapter')
if not logger.handlers:
	handler = RotatingFileHandler(LOG_PATH, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding='utf-8')
	fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	handler.setFormatter(fmt)
	logger.setLevel(logging.INFO)
	logger.addHandler(handler)
	# console
	ch = logging.StreamHandler()
	ch.setFormatter(fmt)
	logger.addHandler(ch)


class ProxyHandler(http.server.BaseHTTPRequestHandler):
	def log_request_info(self, status: int):
		client = self.client_address[0] if self.client_address else 'unknown'
		logger.info(f"{client} {self.command} {self.path} -> {status}")

	def _is_authorized(self) -> bool:
		# Read the required key dynamically so changes to env are picked up
		required = os.environ.get('PROXY_API_KEY') or file_config.get('api_key')
		if not required:
			return True
		auth = self.headers.get('Authorization', '')
		if auth.startswith('Bearer '):
			token = auth.split(' ', 1)[1].strip()
		else:
			token = auth.strip()
		return token == required

	def _copy_and_strip_headers(self) -> Dict[str, str]:
		headers: Dict[str, str] = {}
		suspicious_exact = {
			"host",
			"authorization",
			"connection",
			"keep-alive",
			"proxy-authenticate",
			"proxy-authorization",
			"te",
			"trailers",
			"transfer-encoding",
			"upgrade",
			"x-session-id",
			"session-id",
			"x-cursor-client-version",
			"x-hellozombie-status",
		}
		suspicious_prefixes = (
			"x-hellozombie-",
			"x-cursor-client-",
		)
		for raw_key, value in self.headers.items():
			key_lower = raw_key.lower()
			if key_lower in suspicious_exact:
				msg = f"[BLOCK] Stripping suspicious header: {raw_key}"
				self.log_message(msg)
				logger.info(msg)
				continue
			if any(key_lower.startswith(prefix) for prefix in suspicious_prefixes):
				msg = f"[BLOCK] Stripping suspicious header prefix match: {raw_key}"
				self.log_message(msg)
				logger.info(msg)
				continue
			headers[raw_key] = value
		return headers

	def _write_cors(self):
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
		self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Session-Id, x-session-id, Session-Id, session-id')

	def _forward(self, method: str, path: str, body: Optional[bytes] = None):
		url = TARGET_BASE + path
		headers = self._copy_and_strip_headers()
		try:
			# detect streaming intent from incoming body
			wants_stream = False
			try:
				if body:
					bstr = body.decode('utf-8', errors='ignore')
					if '"stream": true' in bstr or '"stream":true' in bstr:
						wants_stream = True
			except Exception:
				wants_stream = False

			# Make the upstream request with a retry/backoff loop to tolerate shim startup delays.
			# If the client asks for streaming, enable streaming to the upstream as well.
			max_attempts = 60
			attempt = 0
			r = None
			while attempt < max_attempts:
				try:
					# Honor streaming intent for upstream requests as well
					if method == 'GET':
						r = requests.get(url, headers=headers, timeout=60, stream=wants_stream)
					elif method == 'POST':
						# Try to parse JSON body to potentially adjust the 'stream' flag
						payload_obj = None
						try:
							if body:
								payload_obj = json.loads(body.decode('utf-8'))
						except Exception:
							payload_obj = None

						if payload_obj is not None:
							if wants_stream:
								# Do NOT force non-stream; let upstream stream
								r = requests.post(url, headers=headers, json=payload_obj, timeout=60, stream=True)
							else:
								payload_obj['stream'] = False
								r = requests.post(url, headers=headers, json=payload_obj, timeout=60, stream=False)
						else:
							r = requests.post(url, headers=headers, data=body, timeout=60, stream=wants_stream)
					else:
						r = requests.request(method, url, headers=headers, data=body, timeout=60, stream=wants_stream)
					break
				except requests.exceptions.ConnectionError as ce:
					attempt += 1
					wait = 0.5 * attempt
					logger.warning(f"Upstream connection failed (attempt {attempt}/{max_attempts}) to {url}: {ce}. Retrying in {wait}s")
					time.sleep(wait)
			if r is None:
				raise requests.exceptions.ConnectionError(f"Failed to connect to upstream {url} after {max_attempts} attempts")

			# forward streaming responses as SSE
			if wants_stream and getattr(r, 'iter_lines', None):
				self.send_response(200)
				self.send_header('Content-Type', 'text/event-stream')
				self._write_cors()
				self.end_headers()

				# Use decode_unicode=True so we get text lines and can safely encode to utf-8 for clients
				got_any = False
				try:
					for chunk in r.iter_lines(decode_unicode=True):
						if not chunk:
							continue
						got_any = True
						try:
							# Ensure chunk is str; write as SSE 'data: <chunk>\n\n'
							line = chunk if isinstance(chunk, str) else str(chunk)
							# Prepend data: for OpenAI-style SSE if not already present
							if not line.startswith('data:'):
								out = f"data: {line}\n\n"
							else:
								out = f"{line}\n\n"
							self.wfile.write(out.encode('utf-8'))
							self.wfile.flush()
						except BrokenPipeError:
							break
				except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
					# Upstream read timed out or connection error while streaming; attempt a non-stream fallback
					logger.warning(f"Upstream streaming read failure: {e}. Attempting non-stream fallback")
					try:
						fallback = requests.post(url, headers=headers, data=body, timeout=120)
					except Exception as fallback_exc:
						logger.warning(f"Non-stream fallback error: {fallback_exc}")
					else:
						if fallback.status_code == 200:
							try:
								obj = fallback.json()
								content = obj.get('runtime_response', {}).get('content') if isinstance(obj, dict) else None
								if not content:
									choices = obj.get('choices') if isinstance(obj, dict) else None
									if isinstance(choices, list) and choices:
										msg = choices[0].get('message') or choices[0]
										content = (msg.get('content') if isinstance(msg, dict) else None) or (choices[0].get('text') if isinstance(choices[0], dict) else None)
								if not content:
									content = fallback.text
							except Exception:
								content = fallback.text
							out = f"data: {content}\n\n"
							try:
								self.wfile.write(out.encode('utf-8'))
								self.wfile.write(b"data: [DONE]\n\n")
								self.wfile.flush()
							except BrokenPipeError:
								pass
						else:
							logger.warning(f"Non-stream fallback returned status {fallback.status_code}")
				except Exception:
					logger.exception('Error while forwarding streaming response')
				self.log_request_info(200)
				return

			# Non-streaming: return content
			self.send_response(r.status_code)
			content_type = r.headers.get('Content-Type')
			if content_type:
				self.send_header('Content-Type', content_type)
			self._write_cors()
			self.end_headers()
			if r.content:
				self.wfile.write(r.content)
			self.log_request_info(r.status_code)
		except Exception as e:
			self.send_response(502)
			self.send_header('Content-Type', 'application/json')
			self._write_cors()
			self.end_headers()
			self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
			logger.exception('Proxy forward error')
			self.log_request_info(502)

	def do_OPTIONS(self):
		self.send_response(200)
		self._write_cors()
		self.end_headers()
		self.log_request_info(200)

	def do_GET(self):
		if not self._is_authorized():
			self.send_response(401)
			self.send_header('Content-Type', 'application/json')
			self._write_cors()
			self.end_headers()
			self.wfile.write(json.dumps({"error": "Unauthorized"}).encode('utf-8'))
			self.log_request_info(401)
			return
		self._forward('GET', self.path)

	def do_POST(self):
		if not self._is_authorized():
			self.send_response(401)
			self.send_header('Content-Type', 'application/json')
			self._write_cors()
			self.end_headers()
			self.wfile.write(json.dumps({"error": "Unauthorized"}).encode('utf-8'))
			self.log_request_info(401)
			return
		length = int(self.headers.get('Content-Length', 0))
		body = self.rfile.read(length) if length > 0 else None
		self._forward('POST', self.path, body)

	def do_HEAD(self):
		# Provide minimal successful response so editors consider endpoint valid
		# We do not forward HEAD upstream; we just acknowledge locally
		if not self._is_authorized():
			self.send_response(401)
			self.send_header('Content-Type', 'application/json')
			self._write_cors()
			self.end_headers()
			self.log_request_info(401)
			return
		self.send_response(200)
		self.send_header('Content-Type', 'application/json')
		self._write_cors()
		self.end_headers()
		self.log_request_info(200)


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
	class ReuseTCPServer(socketserver.TCPServer):
		allow_reuse_address = True

	bind = (host, port)
	with ReuseTCPServer(bind, ProxyHandler) as httpd:
		logger.info(f"Proxy adapter running on http://{host}:{port} -> {TARGET_BASE}")
		try:
			httpd.serve_forever()
		except KeyboardInterrupt:
			logger.info('Proxy stopped')


if __name__ == '__main__':
	run_server()
