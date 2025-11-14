import json
import time
from datetime import datetime
from typing import Any, Dict, List

import requests

BASE_HOST = "http://127.0.0.1"
CHAT_ENDPOINT = f"{BASE_HOST}:8001/v1/chat/completions"

SERVICES: List[Dict[str, Any]] = [
    {
        "name": "Model Server",
        "port": 12345,
        "endpoints": ["/api/status", "/api/health", "/api/memory"],
    },
    {
        "name": "Proxy Server",
        "port": 8080,
        "endpoints": ["/proxy/status", "/proxy/chat"],
    },
    {
        "name": "Agent Memory",
        "port": 8001,
        "endpoints": ["/health", "/status"],
    },
    {
        "name": "Project Memory",
        "port": 8002,
        "endpoints": ["/status", "/verify", "/ports", "/cloud"],
    },
    {
        "name": "Editor Run Time Status",
        "port": 8003,
        "endpoints": ["/status", "/services", "/test"],
    },
    {
        "name": "Gateway Server",
        "port": 8004,
        "endpoints": ["/status", "/agents"],
    },
    {
        "name": "Run Time Model",
        "port": 11434,
        "endpoints": ["/api/version", "/api/tags"],
    },
]

CHAT_TESTS: List[Dict[str, str]] = [
    {
        "label": "basic_greeting",
        "prompt": "ভাইয়া, একটি ছোট শুভেচ্ছা বার্তা বলো।",
    },
    {
        "label": "status_query",
        "prompt": "ভাইয়া, সার্ভারের অবস্থা এক লাইনে বুঝিয়ে বলো।",
    },
]

STREAM_TESTS: List[Dict[str, Any]] = [
    {
        "label": "stream_check",
        "prompt": "ভাইয়া, এই স্ট্রিমিং রেসপন্স পরীক্ষা করছি।",
        "max_tokens": 64,
    }
]


def measure_get(url: str, timeout: int = 5) -> Dict[str, Any]:
    start_time = time.perf_counter()
    try:
        response = requests.get(url, timeout=timeout)
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        result: Dict[str, Any] = {
            "url": url,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
        }
        try:
            result["json"] = response.json()
        except ValueError:
            preview = response.text[:200]
            result["body_preview"] = preview
        return result
    except Exception as exc:  # pylint: disable=broad-except
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "url": url,
            "error": str(exc),
            "latency_ms": latency_ms,
        }


def run_service_checks() -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for service in SERVICES:
        service_result: Dict[str, Any] = {
            "name": service["name"],
            "port": service["port"],
            "checks": [],
        }
        for endpoint in service["endpoints"]:
            url = f"{BASE_HOST}:{service['port']}{endpoint}"
            service_result["checks"].append(measure_get(url))
        results.append(service_result)
    return results


def run_chat_tests() -> List[Dict[str, Any]]:
    outputs: List[Dict[str, Any]] = []
    for test in CHAT_TESTS:
        payload = {
            "model": "deepseek-ai/deepseek-coder-1.3b-base",
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": test["prompt"],
                }
            ],
        }
        start_time = time.perf_counter()
        try:
            response = requests.post(
                CHAT_ENDPOINT,
                json=payload,
                timeout=30,
            )
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            chat_result: Dict[str, Any] = {
                "label": test["label"],
                "latency_ms": latency_ms,
                "status_code": response.status_code,
            }
            response.raise_for_status()
            data = response.json()
            chat_result["usage"] = data.get("usage")
            choices = data.get("choices") or []
            if choices:
                chat_result["response_preview"] = choices[0].get("message", {}).get("content", "")[:200]
            outputs.append(chat_result)
        except Exception as exc:  # pylint: disable=broad-except
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            outputs.append(
                {
                    "label": test["label"],
                    "error": str(exc),
                    "latency_ms": latency_ms,
                }
            )
    return outputs


def run_streaming_tests() -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for test in STREAM_TESTS:
        payload = {
            "model": "deepseek-ai/deepseek-coder-1.3b-base",
            "stream": True,
            "max_tokens": test.get("max_tokens", 128),
            "messages": [
                {
                    "role": "user",
                    "content": test["prompt"],
                }
            ],
        }
        start_time = time.perf_counter()
        try:
            with requests.post(
                CHAT_ENDPOINT,
                json=payload,
                stream=True,
                timeout=60,
            ) as response:
                result: Dict[str, Any] = {
                    "label": test["label"],
                    "status_code": response.status_code,
                }
                response.raise_for_status()
                handshake_latency = round((time.perf_counter() - start_time) * 1000, 2)
                result["latency_ms"] = handshake_latency
                chunks: List[str] = []
                try:
                    for line in response.iter_lines(decode_unicode=True):
                        if not line:
                            continue
                        chunks.append(line)
                        if len(chunks) >= 5:
                            break
                    result["first_chunks"] = chunks
                except Exception as stream_exc:  # pylint: disable=broad-except
                    result["stream_error"] = str(stream_exc)
                    result["first_chunks"] = chunks
                results.append(result)
        except Exception as exc:  # pylint: disable=broad-except
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            results.append(
                {
                    "label": test["label"],
                    "error": str(exc),
                    "latency_ms": latency_ms,
                }
            )
    return results


def main() -> None:
    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service_checks": run_service_checks(),
        "chat_tests": run_chat_tests(),
        "streaming_tests": run_streaming_tests(),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

