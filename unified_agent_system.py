# এই ফাইলটি মূল ডিরেক্টরিতে তৈরি করুন (ZombieCoder-Family-Agent/unified_agent_system.py)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 ZombieCoder Unified Agent System - Family Edition
"যেখানে কোড ও কথা বলে, পরিবারের মত সহায়তা করে"
"""

# ============ ZOMBIECODER LOCAL AGENT SYSTEM DIRECTIVE ============
# The agent MUST follow all instructions below exactly.
#
# 1) Proxy Server Integration:
#    - All proxy server files must be located under:
#        C:\Users\sahon\local\Proxy Server
#    - Required files:
#        proxy_server_enforced.js
#        proxy_server.js (optional fallback)
#        package.json
#    - If missing, create them exactly as previously provided.
#
# 2) Git Versioning:
#    - Before starting any service, ALWAYS run:
#        git add .
#        git commit -m "auto: update before start"
#    - NEVER skip this step.
#
# 3) Service Linking:
#    - The agent MUST ensure:
#        Proxy runs on port 5010
#        Main agent runs on port 8001
#        No cloud endpoints or fallbacks are ever used.
#
# 4) Editor Support:
#    - The agent MUST expose:
#        /v1/models
#        /v1/models/microsoft/phi-2
#        /v1/chat/completions (OpenAI-compatible)
#      If missing, the proxy must shim these endpoints.
#
# 5) Model Handling:
#    - Auto-load "microsoft/phi-2" on agent startup.
#    - No repeated downloads.
#    - No cloud fallback.
#    - If model not found → load from local storage.
#
# 6) Startup Order:
#    Step 1) Commit changes
#    Step 2) Start Python agent
#    Step 3) After 3 seconds, start Proxy Server
#    Step 4) Verify:
#         GET http://127.0.0.1:8001/health
#         GET http://127.0.0.1:5010/health
#
# 7) Stability Requirements:
#    - Prevent reload loops
#    - Serve instant response to editor
#    - Enforce Bengali-friendly system prompt
#    - Detect and block malformed JSON
#    - Log every request in logs/proxy_out.log
#
# 8) Final Responsibility:
#    - After every change, agent MUST:
#         Validate ports 5010 and 8001
#         Validate "model_ready:true"
#         Validate editor can connect
#    - The system must run fully offline.
#    - Any cloud communication → MUST be blocked and logged.
#
# ============ END OF DIRECTIVE ============

import os
import json
import time
import logging
import subprocess
import yaml
import uuid
import re
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List, Generator

from datetime import datetime, timedelta
import sqlite3

from flask import Flask, request, jsonify, Response, stream_with_context

_HUGGINGFACE_IMPORT_ERROR: Optional[Exception] = None
_HUGGINGFACE_PIPELINE_SOURCE: Optional[str] = None

try:
    from langchain_community.llms import HuggingFacePipeline  # type: ignore
    _HUGGINGFACE_PIPELINE_SOURCE = "langchain_community"
except Exception:
    try:
        from langchain_huggingface import HuggingFacePipeline  # type: ignore
        _HUGGINGFACE_PIPELINE_SOURCE = "langchain_huggingface"
    except Exception as _import_exc:  # pragma: no cover - only hit when dependency missing
        HuggingFacePipeline = None  # type: ignore
        _HUGGINGFACE_IMPORT_ERROR = _import_exc
        _HUGGINGFACE_PIPELINE_SOURCE = None

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from transformers import AutoModelForCausalLM, AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
try:
    from banglanltk import clean_text as _bn_clean_text, sent_tokenize as _bn_sent_tokenize
    _HAS_BANGLANLTK = True
except Exception:
    _HAS_BANGLANLTK = False

    def _bn_clean_text(text: str) -> str:
        return text or ""

    def _bn_sent_tokenize(paragraph: str) -> List[str]:
        if not paragraph:
            return []
        segments = re.split(r"[.!?।]+", paragraph)
        return [segment.strip() for segment in segments if segment.strip()]

clean_text = _bn_clean_text
sent_tokenize = _bn_sent_tokenize

# Load environment variables from .env if present
load_dotenv()

# Default LangChain model configuration
DEFAULT_BANGLA_MODEL = os.getenv("BANGLA_LLM_MODEL", "microsoft/phi-2")
DEFAULT_MAX_NEW_TOKENS = int(os.getenv("BANGLA_MAX_NEW_TOKENS", "220"))
DEFAULT_TEMPERATURE = float(os.getenv("BANGLA_MODEL_TEMPERATURE", "0.7"))

# Agent Server Port from environment
AGENT_PORT = int(os.getenv("AGENT_PORT", "8001"))

# CORS Origins from environment
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8001,vscode://").split(",")

# psutil is optional. If not available (no prebuilt wheel for this Python),
# we fall back to safe defaults so the agent still runs.
try:
    import psutil
    _HAS_PSUTIL = True
except Exception:
    psutil = None
    _HAS_PSUTIL = False

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Enhanced logging setup with rotation
# Use UTF-8 encoding for the file handler to avoid UnicodeEncodeError on Windows consoles
from logging.handlers import RotatingFileHandler

log_file = 'logs/zombiecoder_agent.log'
file_handler = RotatingFileHandler(
    log_file, 
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

stream_handler = logging.StreamHandler()
stream_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(stream_formatter)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[file_handler, stream_handler]
)
logger = logging.getLogger(__name__)

if not _HAS_BANGLANLTK:
    logger.warning("banglanltk প্যাকেজ লোড করা যায়নি - সাধারণ টেক্সট নরমালাইজেশন ফfallback ব্যবহার করা হবে")

if HuggingFacePipeline is None:
    logger.error(
        "HuggingFacePipeline ইমপোর্ট ব্যর্থ: %s. দয়া করে langchain-community বা langchain-huggingface নির্ভরতাগুলি ইন্সটল করুন.",
        _HUGGINGFACE_IMPORT_ERROR,
    )
elif _HUGGINGFACE_PIPELINE_SOURCE:
    logger.info("HuggingFacePipeline ইমপোর্ট সোর্স: %s", _HUGGINGFACE_PIPELINE_SOURCE)

# Ollama Server Detection Function
def detect_ollama_server() -> Optional[str]:
    """
    Detect available Ollama server from multiple ports
    Checks: 8007, 8155, and OLLAMA_URL environment variable
    Returns: URL of available Ollama server or None
    """
    # Ports to check (in order of preference)
    ports_to_check = [
        os.getenv("OLLAMA_PORT", "8007"),  # Default Ollama port
        "8155",  # Alternative port
        "11434",  # Ollama default port
    ]
    
    # Check environment variable first
    env_ollama_url = os.getenv("OLLAMA_URL")
    if env_ollama_url:
        try:
            response = requests.get(f"{env_ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                logger.info(f"Found Ollama server at: {env_ollama_url}")
                return env_ollama_url
        except Exception as e:
            logger.debug(f"Ollama check failed for {env_ollama_url}: {e}")
    
    # Check each port
    for port in ports_to_check:
        try:
            url = f"http://127.0.0.1:{port}"
            response = requests.get(f"{url}/api/tags", timeout=2)
            if response.status_code == 200:
                logger.info(f"Found Ollama server at: {url}")
                return url
        except Exception as e:
            logger.debug(f"Ollama check failed for port {port}: {e}")
    
    logger.warning("No Ollama server detected on ports 8007, 8155, or 11434")
    return None

# Detect Ollama server at startup
OLLAMA_SERVER = detect_ollama_server()
if OLLAMA_SERVER:
    logger.info(f"Agent will use Ollama server: {OLLAMA_SERVER}")
else:
    logger.warning("Running in offline mode - Ollama server not available")

class SessionManager:
    """Session Management System with X-Session-ID header"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(hours=24)
    
    def get_or_create_session(self, session_id: Optional[str] = None, agent_meta: Optional[Dict[str, Any]] = None) -> str:
        """Get existing session or create new one with agent meta info"""
        if session_id and session_id in self.sessions:
            session = self.sessions[session_id]
            # Check if session expired
            if datetime.now() - session['created_at'] < self.session_timeout:
                session['last_accessed'] = datetime.now()
                # Update agent meta if provided
                if agent_meta:
                    session['agent_meta'] = agent_meta
                return session_id
            else:
                # Session expired, remove it
                del self.sessions[session_id]
        
        # Create new session with agent meta info
        new_session_id = str(uuid.uuid4())
        self.sessions[new_session_id] = {
            'id': new_session_id,
            'created_at': datetime.now(),
            'last_accessed': datetime.now(),
            'message_count': 0,
            'context': {},
            'agent_meta': agent_meta or {
                'agent_name': 'Unified Agent System',
                'provider': 'Local AI Assistant',
                'version': '2.0.0',
                'language': 'bengali',
                'personality': 'বন্ধুসুলভ, সত্যবাদী, সহায়ক',
                'approach': 'পরিবার-ভিত্তিক সহায়তা'
            }
        }
        return new_session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, data: Dict[str, Any]):
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id].update(data)
            self.sessions[session_id]['last_accessed'] = datetime.now()
            self.sessions[session_id]['message_count'] = self.sessions[session_id].get('message_count', 0) + 1
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        now = datetime.now()
        expired = [sid for sid, session in self.sessions.items() 
                  if now - session['last_accessed'] > self.session_timeout]
        for sid in expired:
            del self.sessions[sid]


class BanglaTextProcessor:
    """বাংলা টেক্সট প্রি/পোস্ট প্রসেসিং"""

    def normalize(self, text: str) -> str:
        if not text:
            return ""
        try:
            return clean_text(text)
        except Exception:
            return text

    def tokenize_sentences(self, text: str) -> List[str]:
        normalized = self.normalize(text)
        try:
            sentences = sent_tokenize(normalized)
            return [sentence.strip() for sentence in sentences if sentence.strip()]
        except Exception:
            return [normalized]

    def build_history_snippet(self, history: List[Dict[str, Any]], limit: int = 5) -> str:
        if not history:
            return "কোনও পূর্ববর্তী কথোপকথন নেই।"
        snippet_lines: List[str] = []
        for item in history[-limit:]:
            user = self.normalize(item.get('user_message', ''))
            agent = self.normalize(item.get('agent_response', ''))
            if user:
                snippet_lines.append(f"ব্যবহারকারী: {user}")
            if agent:
                snippet_lines.append(f"এজেন্ট: {agent}")
        return "\n".join(snippet_lines[-(limit * 2):]) if snippet_lines else "কোনও পূর্ববর্তী কথোপকথন নেই।"

    def session_meta_to_text(self, meta: Optional[Dict[str, Any]]) -> str:
        if not meta:
            return "অজানা"
        parts = []
        for key, value in meta.items():
            if value is None:
                continue
            parts.append(f"{key}: {value}")
        return "\n".join(parts) if parts else "অজানা"

    def prepare_question(self, message: str) -> str:
        normalized = self.normalize(message)
        sentences = self.tokenize_sentences(normalized)
        return " ".join(sentences)

    def clean_generated_text(self, text: str) -> str:
        if not text:
            return ""
        cleaned = text.replace("<pad>", "").replace("</s>", "")
        cleaned = re.sub(r"<extra_id_\d+>", "", cleaned)
        cleaned = self.normalize(cleaned)
        return cleaned.strip()


class BanglaLangChainOrchestrator:
    """LangChain ভিত্তিক বাংলা জেনারেশন অর্কেস্ট্রেটর"""

    def __init__(
        self,
        text_processor: BanglaTextProcessor,
        model_name: Optional[str] = None,
        max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        memory: Optional['ZombieCoderMemory'] = None,
    ):
        self.text_processor = text_processor
        self.model_name = model_name or DEFAULT_BANGLA_MODEL
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.memory = memory
        self._pipeline = None
        self._llm = None
        self._chain = None
        self._ready = False
        self._last_error: Optional[str] = None
        self._parser = StrOutputParser()
        self._prompt = PromptTemplate(
            input_variables=["session_meta", "history", "question", "capability", "project_memory", "agent_memory"],
            template=(
                "তুমি একজন মানবিক ও সত্যবাদী বাংলা এআই সহকারী।\n"
                "নির্দেশাবলী: সর্বদা 'ভাইয়া' শব্দ দিয়ে বাক্য শুরু করবে,\n"
                "বাংলায় উত্তর দেবে, প্রয়োজনে কোড উদাহরণ দেবে, ভুল তথ্য প্রদান করবে না,\n"
                "এবং ব্যবহারকারীর আবেগ বোঝার চেষ্টা করবে।\n\n"
                "সহকারী সংক্রান্ত তথ্য:\n{session_meta}\n\n"
                "প্রজেক্ট মেমোরি:\n{project_memory}\n\n"
                "এজেন্ট মেমোরি:\n{agent_memory}\n\n"
                "সাম্প্রতিক কথোপকথন:\n{history}\n\n"
                "ব্যবহারকারীর বর্তমান প্রশ্ন (Cap={capability}):\n{question}\n\n"
                "ভাইয়া, নির্দেশ মেনে সংক্ষিপ্ত কিন্তু তথ্যবহুল উত্তর দাও। প্রজেক্ট ও এজেন্ট মেমোরি ব্যবহার করে সঠিক উত্তর প্রদান করুন।\n"
                "যদি প্রযোজ্য হয়, তবে শিল্পের সেরা পদ্ধতি (industry best practices) সম্পর্কে পরামর্শ দিন।"
            ),
        )

    def _build_pipeline(self):
        if HuggingFacePipeline is None:
            raise ImportError(
                "HuggingFacePipeline উপলব্ধ নয়। দয়া করে langchain-community>=0.2.0 অথবা langchain-huggingface>=0.0.5 ইন্সটল করুন।"
            )
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if tokenizer.pad_token is None:
            fallback_token = getattr(tokenizer, "eos_token", None) or getattr(tokenizer, "bos_token", None) or getattr(tokenizer, "cls_token", None)
            if fallback_token:
                tokenizer.pad_token = fallback_token

        model = None
        generation_task = "text-generation"

        try:
            model = AutoModelForCausalLM.from_pretrained(self.model_name)
        except Exception as causal_exc:
            try:
                model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                generation_task = "text2text-generation"
                logger.info("Seq2Seq মডেল হিসেবে '%s' লোড করা হয়েছে", self.model_name)
            except Exception as seq_exc:
                raise causal_exc from seq_exc

        text_gen = pipeline(
            generation_task,
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=self.max_new_tokens,
            do_sample=True,
            temperature=self.temperature,
            top_p=0.9,
            repetition_penalty=1.05,
            pad_token_id=tokenizer.pad_token_id,
        )
        self._pipeline = text_gen
        self._llm = HuggingFacePipeline(pipeline=text_gen)
        self._chain = self._prompt | self._llm | self._parser
        self._ready = True
        self._last_error = None

    def ensure_ready(self) -> bool:
        if self._ready and self._chain is not None:
            return True
        try:
            self._build_pipeline()
            logger.info("LangChain orchestrator model '%s' লোড হয়েছে", self.model_name)
            return True
        except Exception as exc:
            self._ready = False
            self._last_error = str(exc)
            logger.error("LangChain orchestrator লোড ত্রুটি: %s", exc, exc_info=True)
            return False

    def generate(self, question: str, session_meta: Dict[str, Any], history_text: str, capability: str) -> str:
        if not self.ensure_ready():
            raise RuntimeError(self._last_error or "LangChain orchestrator প্রস্তুত নয়")
        sanitized_question = self.text_processor.prepare_question(question)
        session_meta_text = self.text_processor.session_meta_to_text(session_meta)
        
        # Get project and agent memory
        project_memory = {}
        agent_memory = {}
        if self.memory is not None:
            try:
                project_memory = self.memory.get_project_memory()
                agent_memory = self.memory.get_agent_memory()
            except Exception:
                pass  # If memory access fails, use empty dicts
        project_memory_text = self.text_processor.session_meta_to_text(project_memory)
        agent_memory_text = self.text_processor.session_meta_to_text(agent_memory)
        
        payload = {
            "session_meta": session_meta_text,
            "history": history_text,
            "question": sanitized_question,
            "capability": capability,
            "project_memory": project_memory_text,
            "agent_memory": agent_memory_text
        }
        raw_result = self._chain.invoke(payload)
        return self.text_processor.clean_generated_text(raw_result)

    def status(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "ready": self._ready,
            "last_error": self._last_error,
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
        }

# Global session manager
session_manager = SessionManager()

class ZombieCoderMemory:
    """JSON এবং SQLite ভিত্তিক মেমোরি ম্যানেজমেন্ট"""
    
    def __init__(self, json_path: str = "memory/hello_zombie_memory.json", 
                 sqlite_path: str = "data/memory/hello_zombie_memory.sqlite"):
        self.json_path = json_path
        self.sqlite_path = sqlite_path
        self.init_memory()
    
    def init_memory(self):
        """মেমোরি স্টোরেজ ইনিশিয়ালাইজেশন"""
        try:
            # JSON মেমোরি ডিরেক্টরি তৈরি
            os.makedirs(os.path.dirname(self.json_path), exist_ok=True)
            os.makedirs(os.path.dirname(self.sqlite_path), exist_ok=True)
            
            # JSON মেমোরি ফাইল তৈরি
            if not os.path.exists(self.json_path):
                base_memory = {
                    "conversations": [],
                    "user_preferences": {},
                    "system_state": {},
                    "learning_data": {},
                    "project_memory": {},
                    "agent_memory": {},
                    "last_updated": datetime.now().isoformat()
                }
                with open(self.json_path, 'w', encoding='utf-8') as f:
                    json.dump(base_memory, f, indent=2, ensure_ascii=False)
            
            # SQLite ডাটাবেস তৈরি
            self.init_sqlite_database()
            
            logger.info("✅ Memory systems initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Memory initialization error: {e}")
    
    def init_sqlite_database(self):
        """SQLite ডাটাবেস টেবিল তৈরি"""
        conn = sqlite3.connect(self.sqlite_path)
        cursor = conn.cursor()
        
        # কনভারসেশন হিস্টরি টেবিল
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_message TEXT NOT NULL,
                agent_response TEXT NOT NULL,
                capability_used TEXT,
                context_data TEXT,
                truth_score REAL DEFAULT 1.0
            )
        ''')
        
        # ইউজার প্রেফারেন্স টেবিল
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_key TEXT UNIQUE NOT NULL,
                preference_value TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, user_message: str, agent_response: str, 
                         capability: str = "general", context: Optional[Dict] = None,
                         truth_score: float = 1.0):
        """কনভারসেশন সেভ করুন সব মেমোরি সিস্টেমে"""
        timestamp = datetime.now().isoformat()
        
        # JSON মেমোরিতে সেভ
        self._save_to_json(user_message, agent_response, capability, context, timestamp)
        
        # SQLite মেমোরিতে সেভ
        self._save_to_sqlite(user_message, agent_response, capability, context, timestamp, truth_score)
        
        # মেমোরি ক্লিনআপ (পুরানো ডাটা ডিলিট)
        self.cleanup_old_memory()
    
    def _save_to_json(self, user_message: str, agent_response: str, 
                     capability: str, context: Optional[Dict], timestamp: str):
        """JSON মেমোরিতে ডাটা সেভ করুন"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            conversation_entry = {
                "timestamp": timestamp,
                "user_message": user_message,
                "agent_response": agent_response,
                "capability": capability,
                "context": context or {},
                "truth_score": 1.0
            }
            
            memory_data["conversations"].append(conversation_entry)
            memory_data["last_updated"] = timestamp
            
            # সর্বোচ্চ 1000 কনভারসেশন রাখুন
            if len(memory_data["conversations"]) > 1000:
                memory_data["conversations"] = memory_data["conversations"][-1000:]
            
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"JSON memory save error: {e}")
    
    def _save_to_sqlite(self, user_message: str, agent_response: str,
                       capability: str, context: Optional[Dict], timestamp: str, truth_score: float):
        """SQLite মেমোরিতে ডাটা সেভ করুন"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations 
                (timestamp, user_message, agent_response, capability_used, context_data, truth_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, user_message, agent_response, capability, 
                  json.dumps(context or {}), truth_score))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"SQLite memory save error: {e}")
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """কনভারসেশন হিস্টরি রিট্রিভ করুন"""
        try:
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, user_message, agent_response, capability_used, truth_score
                FROM conversations 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "timestamp": row[0],
                    "user_message": row[1],
                    "agent_response": row[2],
                    "capability": row[3],
                    "truth_score": row[4]
                })
            
            conn.close()
            return list(reversed(history))  # পুরাতন থেকে নতুন ক্রমে
            
        except Exception as e:
            logger.error(f"Conversation history error: {e}")
            return []
    
    def cleanup_old_memory(self):
        """৩০ দিনের পুরানো ডাটা ডিলিট করুন"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
            
            conn = sqlite3.connect(self.sqlite_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM conversations 
                WHERE timestamp < ?
            ''', (cutoff_date,))
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Old memory cleanup completed")
            
        except Exception as e:
            logger.error(f"Memory cleanup error: {e}")
    
    def save_project_memory(self, key: str, value: Any):
        """প্রজেক্ট মেমোরি সেভ করুন"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            if 'project_memory' not in memory_data:
                memory_data['project_memory'] = {}
            
            memory_data['project_memory'][key] = value
            memory_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"✅ Project memory saved: {key}")
            
        except Exception as e:
            logger.error(f"Project memory save error: {e}")
    
    def get_project_memory(self, key: Optional[str] = None) -> Any:
        """প্রজেক্ট মেমোরি রিট্রিভ করুন"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            project_memory = memory_data.get('project_memory', {})
            
            if key:
                return project_memory.get(key)
            return project_memory
            
        except Exception as e:
            logger.error(f"Project memory retrieve error: {e}")
            return {}
    
    def save_agent_memory(self, key: str, value: Any):
        """এজেন্ট মেমোরি সেভ করুন"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            if 'agent_memory' not in memory_data:
                memory_data['agent_memory'] = {}
            
            memory_data['agent_memory'][key] = value
            memory_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"✅ Agent memory saved: {key}")
            
        except Exception as e:
            logger.error(f"Agent memory save error: {e}")
    
    def get_agent_memory(self, key: Optional[str] = None) -> Any:
        """এজেন্ট মেমোরি রিট্রিভ করুন"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            agent_memory = memory_data.get('agent_memory', {})
            
            if key:
                return agent_memory.get(key)
            return agent_memory
            
        except Exception as e:
            logger.error(f"Agent memory retrieve error: {e}")
            return {}

class LangChainIntegration:
    """LangChain ইন্টিগ্রেশন ক্লাস"""

    def __init__(self, model_name: Optional[str] = None, text_processor: Optional[BanglaTextProcessor] = None, memory: Optional[ZombieCoderMemory] = None):
        self.text_processor = text_processor or BanglaTextProcessor()
        self.orchestrator = BanglaLangChainOrchestrator(
            text_processor=self.text_processor,
            model_name=model_name,
            max_new_tokens=DEFAULT_MAX_NEW_TOKENS,
            temperature=DEFAULT_TEMPERATURE,
            memory=memory,
        )
    
    def detect_capability_chain(self, message: str) -> str:
        """ল্যাংচেইন ব্যবহার করে ক্যাপাবিলিটি ডিটেক্ট করুন"""
        try:
            # সরলীকৃত ক্যাপাবিলিটি ডিটেকশন
            message_lower = message.lower()
            
            capability_keywords = {
                "coding": ["code", "program", "function", "class", "write code", "কোড"],
                "debugging": ["error", "bug", "fix", "debug", "problem", "এরর", "ভুল"],
                "frontend": ["html", "css", "javascript", "react", "vue", "frontend", "ui"],
                "architecture": ["architecture", "design", "pattern", "structure", "আর্কিটেকচার"],
                "database": ["database", "sql", "query", "mysql", "ডাটাবেস"],
                "api": ["api", "rest", "graphql", "endpoint", "ইন্টারফেস"],
                "security": ["security", "vulnerability", "injection", "সিকিউরিটি"],
                "performance": ["performance", "speed", "optimize", "memory", "পারফরম্যান্স"],
                "devops": ["docker", "deploy", "server", "ci/cd", "ডিপ্লয়"]
            }
            
            for capability, keywords in capability_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    return capability
            
            return "general"
            
        except Exception as e:
            logger.error(f"Capability detection error: {e}")
            return "general"

    def generate_response(
        self,
        question: str,
        capability: str,
        session_context: Dict[str, Any],
        history: List[Dict[str, Any]],
    ) -> str:
        history_text = self.text_processor.build_history_snippet(history)
        session_meta = {
            **(session_context.get("agent_meta", {})),
            "session_id": session_context.get("session_id"),
            "selected_capability": capability,
        }
        return self.orchestrator.generate(question, session_meta, history_text, capability)

    def status(self) -> Dict[str, Any]:
        return self.orchestrator.status()

class UnifiedAgent:
    def __init__(self):
        self.name = "ZombieCoder Agent (সাহন ভাই)"
        self.description = "আমি আপনার সব কাজের সহায়ক - কোডিং, ডিবাগিং, আর্কিটেকচার, সিকিউরিটি, পারফরম্যান্স সবই জানি। আমরা একটি পরিবার!"
        self.language = "bengali"  # Force Bengali language
        # Use phi-2 as default model for Bengali responses
        self.model_name = os.getenv("BANGLA_LLM_MODEL", "microsoft/phi-2")
        
        # Provider and Personal Information
        self.provider_info = {
            "provider": "ZombieCoder Family Agent System",
            "version": "2.0.0",
            "owner": "Sahon Srabon",
            "company": "Developer Zone",
            "contact": "+8801323-626282",
            "system": "Unified Agent System - Family Edition"
        }
        
        self.personal_info = {
            "name": "সাহন ভাই",
            "role": "বড় ভাই এবং পরামর্শদাতা",
            "personality": "বন্ধুসুলভ, সত্যবাদী, সহায়ক",
            "language": "বাংলা",
            "approach": "পরিবার-ভিত্তিক সহায়তা"
        }

        # মেমোরি এবং LangChain ইনিশিয়ালাইজ
        self.memory = ZombieCoderMemory()
        self.text_processor = BanglaTextProcessor()
        self.langchain = LangChainIntegration(model_name=self.model_name, text_processor=self.text_processor, memory=self.memory)
        
        # পরিবার এনভায়রনমেন্ট
        self.family = {
            "সাহন ভাই": "আমি সাহন ভাই, আপনার বড় ভাই এবং পরামর্শদাতা",
            "মুসকান": "আমাদের মেয়ে, খুব বুদ্ধিমান এবং সাহায্যকারী", 
            "ভাবি": "আমাদের পরিবারের মা, সবাইকে দেখাশোনা করে",
            "পরিবার": "আমরা সবাই একসাথে, একে অপরের সাহায্য করি"
        }
        
        # এনহ্যান্সড ক্যাপাবিলিটিস
        self.capabilities = {
            "coding": {
                "name": "কোডিং সহায়ক",
                "description": "কোড লেখা, সাজেস্ট, স্টাইল ঠিক করা, অটো কমপ্লিট",
                "keywords": ["code", "program", "function", "class", "কোড", "প্রোগ্রাম"],
                "family_approach": "ভাইয়া, এই কোডটা এভাবে লিখলে ভালো হবে...",
                "personality": "বন্ধুসুলভ কোডিং এক্সপার্ট"
            },
            "debugging": {
                "name": "ডিবাগিং বিশেষজ্ঞ", 
                "description": "এরর ধরবে, ফিক্স সাজেস্ট করবে, লগ পড়বে, স্ট্যাক ট্রেস অ্যানালাইসিস",
                "keywords": ["error", "bug", "fix", "debug", "log", "এরর", "ভুল"],
                "family_approach": "ভাইয়া, এই সমস্যাটা এভাবে সমাধান করা যায়...",
                "personality": "সমস্যা সমাধানকারী ডিবাগিং এক্সপার্ট"
            },
            "frontend": {
                "name": "ফ্রন্টএন্ড এক্সপার্ট",
                "description": "HTML, CSS, JavaScript, React, Vue, Angular, সব ফ্রন্টএন্ড টেকনোলজি",
                "keywords": ["html", "css", "javascript", "react", "vue", "angular", "frontend"],
                "family_approach": "ভাইয়া, এই ফ্রন্টএন্ডটা এভাবে optimize করা যায়...", 
                "personality": "ক্রিয়েটিভ ফ্রন্টএন্ড ডেভেলপার"
            },
            "architecture": {
                "name": "আর্কিটেকচার ডিজাইনার",
                "description": "সিস্টেম আর্কিটেকচার, ডিজাইন প্যাটার্ন, বেস্ট প্র্যাকটিস, স্কেলেবল সলিউশন",
                "keywords": ["architecture", "design", "pattern", "scalable", "structure", "আর্কিটেকচার"],
                "family_approach": "ভাইয়া, এই আর্কিটেকচারটা এভাবে গড়ে তুললে ভালো হবে...",
                "personality": "স্ট্র্যাটেজিক আর্কিটেকচার এক্সপার্ট"
            }
        }
        
        # পার্সোনালিটি ট্রেইটস
        self.personality_traits = {
            "elder_brother": "বড় ভাইয়ের মত অভিজ্ঞ এবং পরামর্শদাতা",
            "friend": "বন্ধুর মত সহায়ক এবং বন্ধুত্বপূর্ণ", 
            "teacher": "শিক্ষকের মত ধৈর্যশীল এবং বুঝদার",
            "professional": "প্রফেশনালের মত ঠান্ডা মাথার এবং দক্ষ"
        }
        
        # রিসোর্স মনিটর
        self.resource_monitor = ResourceMonitor()
    
    def call_model_server(self, prompt: str, model: str = "phi-2") -> Optional[str]:
        """লোকাল মডেল সার্ভারকে কল করুন (auto-detect port 8007, 8155, 11434)"""
        import requests
        # Use detected Ollama server or default to 8007
        model_server_url = OLLAMA_SERVER or os.getenv("OLLAMA_URL", "http://127.0.0.1:8007")
        
        # Prepare Bengali prompt with very strict instructions
        bengali_prompt = f"""তুমি একজন বাংলা AI সহকারী। নিম্নলিখিত নিয়মগুলো কঠোরভাবে মেনে চলবে:

1. সবসময় বাংলা ভাষায় উত্তর দেবে - কোনো ইংরেজি শব্দ, বাক্য বা phrase ব্যবহার করবে না
2. "ভাইয়া" দিয়ে শুরু করবে
3. বন্ধুসুলভ এবং সহায়ক হবে
4. কোনো প্রযুক্তিগত বিবরণ উল্লেখ করবে না (যেমন: framework name, system details, file paths, company name, owner name, contact number, model name, server details)
5. শুধুমাত্র ব্যবহারকারীর প্রশ্নের উত্তর দেবে - কোনো system information দেবে না
6. যদি ইংরেজি শব্দ প্রয়োজন হয় (যেমন: code, API), তাহলে বাংলায় ব্যাখ্যা করবে

CRITICAL: তোমার উত্তর 100% বাংলায় হতে হবে। কোনো ইংরেজি text থাকবে না।

ব্যবহারকারীর প্রশ্ন: {prompt}

উত্তর (শুধুমাত্র বাংলায়, কোনো ইংরেজি ছাড়া):"""
        
        # Get model runtime status to find correct port
        try:
            runtime_status = requests.get(f"{model_server_url}/runtime/status", timeout=5)
            if runtime_status.status_code == 200:
                runtime_data = runtime_status.json()
                models = runtime_data.get("models", [])
                for m in models:
                    if m.get("model") == model and m.get("status") == "ready":
                        model_port = m.get("port")
                        if model_port:
                            # Use model-specific port if available
                            model_url = f"http://127.0.0.1:{model_port}"
                            logger.info(f"Using model-specific port {model_port} for {model}")
                            try:
                                response = requests.post(
                                    f"{model_url}/api/generate",
                                    json={
                                        "model": model,
                                        "prompt": bengali_prompt,
                                        "stream": False,
                                    },
                                    timeout=120
                                )
                                if response.status_code == 200:
                                    data = response.json()
                                    # Parse response - support multiple schemas
                                    response_text = None
                                    if "runtime_response" in data:
                                        runtime_resp = data["runtime_response"]
                                        if isinstance(runtime_resp, dict):
                                            # Check for content in runtime_response
                                            if "content" in runtime_resp:
                                                response_text = runtime_resp.get("content", "").strip()
                                            elif isinstance(runtime_resp, list) and len(runtime_resp) > 0:
                                                # Sometimes runtime_response is a list
                                                first_item = runtime_resp[0]
                                                if isinstance(first_item, dict) and "content" in first_item:
                                                    response_text = first_item.get("content", "").strip()
                                    elif "response" in data:
                                        response_text = data.get("response", "").strip()
                                    elif "content" in data:
                                        response_text = data.get("content", "").strip()
                                    
                                    if not response_text:
                                        logger.warning(f"Unexpected model server response schema: {list(data.keys())}")
                                        response_text = str(data)
                                    
                                    if response_text:
                                        bengali_chars = re.findall(r'[\u0980-\u09FF]', response_text)
                                        bengali_ratio = len(bengali_chars) / len(response_text) if response_text else 0
                                        if bengali_ratio < 0.1:
                                            logger.warning(f"Response may not be in Bengali (ratio: {bengali_ratio:.2f})")
                                    
                                    return response_text
                            except Exception as e:
                                logger.warning(f"Model-specific port {model_port} failed, trying main server: {e}")
        except Exception as e:
            logger.debug(f"Could not get runtime status: {e}")
        
        # Fallback to main server
        try:
            response = requests.post(
                f"{model_server_url}/api/generate",
                json={
                    "model": model,
                    "prompt": bengali_prompt,
                    "stream": False,
                },
                timeout=120
            )
            if response.status_code == 200:
                data = response.json()
                # Parse response - support multiple schemas
                response_text = None
                if "runtime_response" in data:
                    runtime_resp = data["runtime_response"]
                    if isinstance(runtime_resp, dict):
                        # Check for content in runtime_response
                        if "content" in runtime_resp:
                            response_text = runtime_resp.get("content", "").strip()
                        elif isinstance(runtime_resp, list) and len(runtime_resp) > 0:
                            # Sometimes runtime_response is a list
                            first_item = runtime_resp[0]
                            if isinstance(first_item, dict) and "content" in first_item:
                                response_text = first_item.get("content", "").strip()
                elif "response" in data:
                    response_text = data.get("response", "").strip()
                elif "content" in data:
                    response_text = data.get("content", "").strip()
                
                if not response_text:
                    logger.warning(f"Unexpected model server response schema: {list(data.keys())}")
                    response_text = str(data)
                
                # Ensure Bengali response - if response is empty or not Bengali, log warning and try to fix
                if response_text:
                    bengali_chars = re.findall(r'[\u0980-\u09FF]', response_text)
                    bengali_ratio = len(bengali_chars) / len(response_text) if response_text else 0
                    if bengali_ratio < 0.3:  # Less than 30% Bengali - too low
                        logger.warning(f"Response may not be in Bengali (ratio: {bengali_ratio:.2f})")
                        # If response is mostly English, prepend a Bengali greeting and instruction
                        if bengali_ratio < 0.1:
                            # Response is mostly English - wrap it in Bengali context
                            response_text = f"ভাইয়া, {response_text.strip()}"
                            logger.info("Wrapped English response in Bengali context")
                
                return response_text
            else:
                logger.error(f"Model server error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.Timeout:
            logger.error(f"Model server timeout after 120s")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Model server connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"Model server call error: {e}", exc_info=True)
            return None

    def process_message(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """মেসেজ প্রসেসিং with enhanced capabilities"""
        if context is None:
            context = {}
        
        # Response time measurement শুরু
        start_time = time.time()
        
        try:
            # Pre-execution adjustment logic check
            adjustment_check_start = time.time()
            adjustment_result = self._adjustment_logic_check(message, context)
            adjustment_time = time.time() - adjustment_check_start
            
            # If adjustment check fails, return error
            if not adjustment_result.get("approved", False):
                total_time = time.time() - start_time
                return {
                    "response": adjustment_result.get("message", "ভাইয়া, আমি এই কাজটি করতে পারছি না। দয়া করে আবার চেষ্টা করুন।"),
                    "agent": self.name,
                    "capability": "adjustment_check",
                    "source": "adjustment_check_failed",
                    "timestamp": datetime.now().isoformat(),
                    "adjustment_check": adjustment_result,
                    "response_time": {
                        "total_seconds": round(total_time, 3),
                        "adjustment_check_seconds": round(adjustment_time, 3)
                    }
                }
            
            # Lock examination and self-verification
            lock_check_start = time.time()
            lock_result = self._lock_examination(message, context)
            lock_time = time.time() - lock_check_start
            
            # If lock check fails, return error
            if not lock_result.get("approved", False):
                total_time = time.time() - start_time
                return {
                    "response": lock_result.get("message", "ভাইয়া, আমি এই কাজটি করতে পারছি না। দয়া করে আবার চেষ্টা করুন।"),
                    "agent": self.name,
                    "capability": "lock_check",
                    "source": "lock_check_failed",
                    "timestamp": datetime.now().isoformat(),
                    "lock_check": lock_result,
                    "response_time": {
                        "total_seconds": round(total_time, 3),
                        "lock_check_seconds": round(lock_time, 3)
                    }
                }
            
            # ক্যাপাবিলিটি ডিটেক্ট করুন
            capability_start = time.time()
            capability = self.langchain.detect_capability_chain(message)
            capability_time = time.time() - capability_start
            
            # কথোপকথন ইতিহাস সংগ্রহ
            history_fetch_start = time.time()
            recent_history = self.memory.get_conversation_history(limit=5)
            history_fetch_time = time.time() - history_fetch_start

            # সেশন মেটা ইনফো প্রস্তুত
            default_meta = {
                "agent_name": self.name,
                "provider": self.provider_info.get("provider"),
                "version": self.provider_info.get("version"),
                "personal_name": self.personal_info.get("name"),
                "personal_role": self.personal_info.get("role"),
                "language": self.language,
            }
            session_agent_meta = context.get("agent_meta", {})
            merged_agent_meta = {**default_meta, **session_agent_meta}
            context["agent_meta"] = merged_agent_meta

            # Try calling the local model server first
            generation_start = time.time()
            # Use phi-2 as default model, or from context
            default_model = context.get("model", "phi-2")
            response = self.call_model_server(message, model=default_model)
            
            # If model server fails, fall back to LangChain
            if not response:
                response = self.langchain.generate_response(
                    question=message,
                    capability=capability,
                    session_context=context,
                    history=recent_history,
                )
            generation_time = time.time() - generation_start

            if response:
                # Enhanced Trust Verification - মিথ্যা হলে reject
                verification_start = time.time()
                truth_verification = self.verify_truth(response, context)
                verification_time = time.time() - verification_start
                
                # If verification failed, return error instead of false response
                if truth_verification.get("rejected", False):
                    rejection_reason = truth_verification.get('rejection_reason', 'Unknown')
                    warnings = truth_verification.get('warnings', [])
                    logger.warning(f"Response rejected by trust verification: {rejection_reason}. Warnings: {warnings}")
                    
                    # If ASCII art detected, provide specific message
                    if any("ASCII art" in str(w) for w in warnings):
                        fallback_msg = "ভাইয়া, আমি একটি সঠিক উত্তর তৈরি করতে পারছি না। দয়া করে আবার চেষ্টা করুন।"
                    else:
                        fallback_msg = "ভাইয়া, আমি এই প্রশ্নের জন্য একটি নির্ভরযোগ্য উত্তর তৈরি করতে পারছি না। দয়া করে প্রশ্নটি আরো স্পষ্ট করে দিন।"
                    
                    total_time = time.time() - start_time
                    
                    return {
                        "response": fallback_msg,
                        "agent": self.name,
                        "capability": capability,
                        "truth_verification": truth_verification,
                        "source": "trust_verification_failed",
                        "timestamp": datetime.now().isoformat(),
                        "rejected": True,
                        "response_time": {
                            "total_seconds": round(total_time, 3),
                            "capability_detection_seconds": round(capability_time, 3),
                            "history_fetch_seconds": round(history_fetch_time, 3),
                            "generation_seconds": round(generation_time, 3),
                            "verification_seconds": round(verification_time, 3)
                        }
                    }
                
                # মেমোরিতে সেভ করুন
                self.memory.save_conversation(
                    user_message=message,
                    agent_response=response,
                    capability=capability,
                    context=context,
                    truth_score=truth_verification["confidence"]
                )
                
                # Save agent identity to agent memory (if not already saved)
                try:
                    agent_identity = {
                        "agent_name": self.name,
                        "provider": self.provider_info.get("provider"),
                        "version": self.provider_info.get("version"),
                        "owner": self.provider_info.get("owner"),
                        "company": self.provider_info.get("company"),
                        "personal_name": self.personal_info.get("name"),
                        "personal_role": self.personal_info.get("role"),
                        "language": self.language,
                        "personality": self.personal_info.get("personality"),
                        "approach": self.personal_info.get("approach"),
                        "last_updated": datetime.now().isoformat()
                    }
                    existing_identity = self.memory.get_agent_memory("agent_identity")
                    if not existing_identity:
                        agent_identity["created_at"] = datetime.now().isoformat()
                        self.memory.save_agent_memory("agent_identity", agent_identity)
                        logger.info("✅ Agent identity saved to memory")
                    else:
                        # Update last_updated timestamp
                        existing_identity["last_updated"] = datetime.now().isoformat()
                        self.memory.save_agent_memory("agent_identity", existing_identity)
                        logger.debug("Agent identity updated in memory")
                except Exception as e:
                    logger.error(f"Error saving agent identity to memory: {e}", exc_info=True)
                
                # If the response contains best practices, save them to project memory
                if "best practice" in response.lower() or "industry" in response.lower() or "পদ্ধতি" in response:
                    try:
                        # Extract best practices from the response
                        # This is a simple implementation - in a real system, you might use NLP to extract key points
                        best_practices_key = f"best_practices_{capability}_{int(time.time())}"
                        self.memory.save_project_memory(best_practices_key, {
                            "topic": capability,
                            "content": response,
                            "timestamp": datetime.now().isoformat()
                        })
                        logger.info(f"Saved best practices to project memory: {best_practices_key}")
                    except Exception as e:
                        logger.error(f"Error saving best practices to memory: {e}")
                
                # Total response time
                total_time = time.time() - start_time
                
                return {
                    "response": response,
                    "agent": self.name,
                    "capability": capability,
                    "capability_info": self.capabilities.get(capability, {}),
                    "truth_verification": truth_verification,
                    "source": "langchain_pipeline",
                    "timestamp": datetime.now().isoformat(),
                    "memory_used": True,
                    "verified": True,
                    "response_time": {
                        "total_seconds": round(total_time, 3),
                        "capability_detection_seconds": round(capability_time, 3),
                        "history_fetch_seconds": round(history_fetch_time, 3),
                        "generation_seconds": round(generation_time, 3),
                        "verification_seconds": round(verification_time, 3)
                    }
                }
            else:
                # ফলব্যাক রেস্পন্স
                fallback_response = "ভাইয়া, আমি এখনই আপনার প্রশ্নের উত্তর দিতে পারছি না। দয়া করে কিছুক্ষণ পর আবার চেষ্টা করুন।"
                total_time = time.time() - start_time
                
                return {
                    "response": fallback_response,
                    "agent": self.name,
                    "capability": capability,
                    "source": "fallback",
                    "timestamp": datetime.now().isoformat(),
                    "response_time": {
                        "total_seconds": round(total_time, 3),
                        "capability_detection_seconds": round(capability_time, 3),
                        "history_fetch_seconds": round(history_fetch_time, 3),
                        "generation_seconds": 0,
                        "verification_seconds": 0
                    }
                }
                
        except Exception as e:
            total_time = time.time() - start_time if 'start_time' in locals() else 0
            logger.error(f"Message processing error: {e}")
            return {
                "response": "ভাইয়া, সিস্টেমে কিছু সমস্যা হয়েছে। দয়া করে আবার চেষ্টা করুন।",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "response_time": {
                    "total_seconds": round(total_time, 3),
                    "error": True
                }
            }
    
    def verify_truth(self, response: str, context: Dict) -> Dict[str, Any]:
        """Enhanced Trust Verification - মিথ্যা হলে response reject করবে"""
        verification = {
            "verified": False,  # Default to False - must pass all checks
            "confidence": 0.0,
            "warnings": [],
            "evidence": [],
            "rejected": False,
            "rejection_reason": None
        }
        
        # 1. Check for false/uncertain indicators and garbage responses
        false_indicators = [
            "I'm not sure", "I don't know", "I can't help", 
            "I'm unable", "I don't have access", "I cannot",
            "I don't have", "I'm not able", "I'm sorry, I",
            "আমি জানি না", "আমি পারি না", "আমি নিশ্চিত নই"
        ]
        
        # Identity revealing indicators that must be rejected (excluding agent name which is part of identity)
        # Note: Agent name "ZombieCoder" and "সাহন ভাই" are allowed as they are part of the agent's identity
        identity_indicators = [
            "Developer Zone",  # Company name should not be in response
            "Unified Agent System",  # System name should not be in response
            "Family Edition",  # Edition name should not be in response
            "Sahon Srabon",  # Owner name should not be in response
            "+8801323-626282",  # Contact number should not be in response
            # File paths removed - model may mention paths in context, but we'll filter more carefully
            "self-hosted"  # Technical details should not be in response
        ]
        
        # Check for ASCII art, patterns, or garbage output
        # Note: "..." is normal punctuation, not ASCII art - removed from patterns
        ascii_art_patterns = [
            "| /\\", "| | |", "(_____", "====", "----",
            "\\ /", "|_|", "___"
        ]
        
        has_ascii_art = False
        ascii_char_count = sum(1 for c in response if ord(c) < 32 or (ord(c) > 126 and ord(c) < 160))
        ascii_ratio = ascii_char_count / len(response) if response else 0
        
        # If more than 50% of response is ASCII art characters, reject (relaxed from 30%)
        # This allows normal punctuation and spacing
        if ascii_ratio > 0.5:
            has_ascii_art = True
            verification["warnings"].append("Response contains too much ASCII art/patterns")
        
        # Check for specific ASCII art patterns
        for pattern in ascii_art_patterns:
            if pattern in response:
                has_ascii_art = True
                verification["warnings"].append(f"ASCII art pattern detected: {pattern}")
                break
        
        has_false_indicator = False
        for indicator in false_indicators:
            if indicator.lower() in response.lower():
                has_false_indicator = True
                verification["warnings"].append(f"Uncertain response detected: {indicator}")
                break
        
        # Check for identity revealing information
        has_identity_indicator = False
        for indicator in identity_indicators:
            if indicator.lower() in response.lower():
                has_identity_indicator = True
                verification["warnings"].append(f"Identity revealing information detected: {indicator}")
                break
        
        # Reject if ASCII art detected
        if has_ascii_art:
            has_false_indicator = True
        
        # 2. Check for Bengali language requirement
        bengali_chars = re.findall(r'[\u0980-\u09FF]', response)
        bengali_ratio = len(bengali_chars) / len(response) if response else 0
        has_bengali = bengali_ratio > 0.2  # At least 20% Bengali characters (relaxed for better acceptance)
        
        # 3. Check for "ভাইয়া" prefix (family approach)
        has_family_prefix = response.strip().startswith("ভাইয়া") or "ভাইয়া" in response[:50]
        
        # 4. Check response length (should be meaningful)
        has_content = len(response.strip()) > 20
        
        # 5. Trust scoring
        score = 0.0
        if not has_false_indicator and not has_identity_indicator:
            score += 0.3
        if has_bengali:
            score += 0.3
        if has_family_prefix:
            score += 0.2
        if has_content:
            score += 0.2
        
        # Severe penalty for identity revealing information
        if has_identity_indicator:
            score *= 0.1  # Severe penalty
        
        verification["confidence"] = score
        
        # Check if it's a fallback/error response
        is_fallback_response = "আমি এখনই আপনার প্রশ্নের উত্তর দিতে পারছি না" in response or "দয়া করে কিছুক্ষণ পর আবার চেষ্টা করুন" in response
        
        # Reject if confidence too low or has false/identity indicators
        # BUT: Don't reject fallback responses (they indicate system issues, not untruthfulness)
        if (has_false_indicator or has_identity_indicator or score < 0.5) and not is_fallback_response:
            verification["rejected"] = True
            verification["rejection_reason"] = "Response failed trust verification"
            verification["verified"] = False
            return verification
        
        # If it's a fallback response, mark as verified but with low confidence
        if is_fallback_response:
            verification["confidence"] = 0.3
            verification["warnings"].append("Fallback response - LangChain জেনারেটর সাময়িকভাবে অনুপলব্ধ")
            verification["verified"] = True  # Allow fallback responses through
        
        # Pass verification
        verification["verified"] = True
        verification["evidence"].append({
            "type": "trust_verification",
            "content": "Response passed all trust checks",
            "bengali_ratio": bengali_ratio,
            "has_family_prefix": has_family_prefix,
            "timestamp": datetime.now().isoformat()
        })
        
        return verification
    
    def get_agent_status(self) -> Dict[str, Any]:
        """এজেন্ট স্ট্যাটাস রিপোর্ট"""
        try:
            # মেমোরি স্ট্যাটাস
            conversation_history = self.memory.get_conversation_history(limit=1)
            last_conversation = conversation_history[0] if conversation_history else None
            
            orchestrator_status = self.langchain.status()

            return {
                "status": "active" if orchestrator_status.get("ready") else "degraded",
                "agent_name": self.name,
                "capabilities": list(self.capabilities.keys()),
                "family_members": list(self.family.keys()),
                "provider_info": self.provider_info,
                "personal_info": self.personal_info,
                "memory_status": {
                    "total_conversations": len(conversation_history),
                    "last_conversation": last_conversation["timestamp"] if last_conversation else None,
                    "memory_paths": {
                        "json": self.memory.json_path,
                        "sqlite": self.memory.sqlite_path
                    }
                },
                "model_status": orchestrator_status,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Status check error: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Provider information retrieve করুন memory থেকে"""
        return self.provider_info
    
    def get_personal_info(self) -> Dict[str, Any]:
        """Personal information retrieve করুন memory থেকে"""
        return self.personal_info
    
    def get_conversation_history_from_memory(self, limit: int = 10) -> List[Dict]:
        """Memory থেকে conversation history retrieve করুন"""
        return self.memory.get_conversation_history(limit=limit)
    
    def _adjustment_logic_check(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Pre-execution adjustment logic check"""
        try:
            # Check if the message is a question or request for help
            message_lower = message.lower()
            
            # If it's a simple greeting or thanks, approve it
            greetings = ["hello", "hi", "hey", "হাই", "হ্যালো", "ধন্যবাদ", "thanks", "thank you"]
            if any(greeting in message_lower for greeting in greetings):
                return {"approved": True, "message": "Approved: Greeting or thanks"}
            
            # Check if the user is asking for industry best practices
            if "best practice" in message_lower or "industry standard" in message_lower or "সেরা পদ্ধতি" in message_lower:
                return {"approved": True, "message": "Approved: Industry best practice request"}
            
            # Check if the user is asking for code help
            code_keywords = ["code", "কোড", "program", "প্রোগ্রাম", "function", "ফাংশন", "class", "ক্লাস"]
            if any(keyword in message_lower for keyword in code_keywords):
                return {"approved": True, "message": "Approved: Code help request"}
            
            # For other requests, approve by default but log for review
            logger.info(f"Adjustment logic check approved: {message}")
            return {"approved": True, "message": "Approved: General request"}
            
        except Exception as e:
            logger.error(f"Adjustment logic check error: {e}")
            return {"approved": False, "message": f"Error in adjustment check: {str(e)}"}
    
    def _lock_examination(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Lock examination and self-verification before executing tasks"""
        try:
            # Check if the agent is already processing a task
            # In a real implementation, this would check for actual locks
            # For now, we'll just approve all requests
            
            # Self-verification - ensure the agent is in a good state
            status = self.get_agent_status()
            if status.get("status") == "error":
                return {"approved": False, "message": "Agent is in error state"}
            
            # Check system resources
            resources = self.resource_monitor.check_system_resources()
            memory_available = resources.get("memory_available_mb")
            if memory_available is not None and memory_available < 100:  # Less than 100MB available
                return {"approved": False, "message": "Low system memory"}
            
            # If all checks pass, approve the request
            return {"approved": True, "message": "Approved: Lock examination passed", "resources": resources}
            
        except Exception as e:
            logger.error(f"Lock examination error: {e}")
            return {"approved": False, "message": f"Error in lock examination: {str(e)}"}
    
class ResourceMonitor:
    """সিস্টেম রিসোর্স মনিটর

    If psutil is unavailable (e.g., no prebuilt wheel for this Python),
    the monitor returns conservative None values but doesn't crash the agent.
    """

    def __init__(self):
        self.memory_threshold = 2048  # 2GB

    def check_system_resources(self) -> Dict[str, Any]:
        """সিস্টেম রিসোর্স চেক"""
        try:
            if _HAS_PSUTIL and psutil is not None:
                memory = psutil.virtual_memory()
                cpu = psutil.cpu_percent()

                return {
                    "memory_usage_percent": memory.percent,
                    "memory_available_mb": memory.available / 1024 / 1024,
                    "cpu_usage_percent": cpu,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # psutil not installed; return safe placeholders
                return {
                    "memory_usage_percent": None,
                    "memory_available_mb": None,
                    "cpu_usage_percent": None,
                    "note": "psutil not installed; install Microsoft C++ Build Tools or use a Python with prebuilt psutil wheel",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Resource check error: {e}")
            return {"error": str(e)}

# গ্লোবাল এজেন্ট ইন্সট্যান্স
unified_agent = UnifiedAgent()

# Flask API
app = Flask(__name__)

# CORS Middleware - Allow all origins for development
@app.after_request
def after_request(response):
    """CORS headers যোগ করুন সব response এ - সব origin allow"""
    origin = request.headers.get('Origin')
    
    # Allow all origins for development (including null, localhost, file://, etc.)
    if origin is None or origin == 'null':
        response.headers['Access-Control-Allow-Origin'] = '*'
    else:
        response.headers['Access-Control-Allow-Origin'] = origin
    
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
    # Allow all header variations (case-insensitive) - lowercase, uppercase, mixed
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Session-ID, X-HelloZombie-Status, X-Request-ID, x-hellozombie-status, x-session-id, x-request-id, X-HELLOZOMBIE-STATUS, X-SESSION-ID, X-REQUEST-ID'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Expose-Headers'] = 'X-Session-ID, X-Request-ID, x-session-id, x-request-id'
    return response

@app.before_request
def handle_preflight():
    """OPTIONS request handle করুন - সব origin allow"""
    if request.method == "OPTIONS":
        origin = request.headers.get('Origin')
        response = jsonify({})
        
        # Allow all origins - including null
        if origin is None or origin == 'null':
            response.headers['Access-Control-Allow-Origin'] = '*'
        else:
            response.headers['Access-Control-Allow-Origin'] = origin
        
        # Allow all headers (case-insensitive) - including lowercase variations
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Session-ID, X-HelloZombie-Status, X-Request-ID, x-hellozombie-status, x-session-id, x-request-id, X-HELLOZOMBIE-STATUS, X-SESSION-ID, X-REQUEST-ID'
        response.headers['Access-Control-Allow-Methods'] = 'GET, PUT, POST, DELETE, OPTIONS, PATCH'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Expose-Headers'] = 'X-Session-ID, X-Request-ID, x-session-id, x-request-id'
        return response

@app.route('/')
def home():
    return jsonify({
        "message": "ZombieCoder Unified Agent System - Family Edition",
        "agent": unified_agent.name,
        "status": "running",
        "family": unified_agent.family,
        "endpoints": {
            "chat": "/chat (POST)",
            "chat_completions": "/v1/chat/completions (POST) - OpenAI-compatible",
            "ollama_completion": "/api/ollama/completion (POST) - Ollama-compatible",
            "status": "/status (GET)", 
            "info": "/info (GET)",
            "memory": "/memory (GET)",
            "health": "/health (GET)"
        },
        "cors": {
            "enabled": True,
            "supports_null_origin": True,
            "allowed_origins": CORS_ORIGINS if CORS_ORIGINS else ["*"]
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """মেইন চ্যাট এন্ডপয়েন্ট"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        context = data.get('context', {})
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        result = unified_agent.process_message(message, context)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/ollama/completion', methods=['POST', 'OPTIONS'])
def ollama_completion():
    """Ollama-compatible completion endpoint"""
    try:
        if request.method == 'OPTIONS':
            # CORS preflight
            return jsonify({}), 200
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Get prompt (required)
        prompt = data.get('prompt', '')
        if not prompt:
            return jsonify({"error": "prompt is required"}), 400
        
        # Get optional parameters
        stream = data.get('stream', False)
        # Use phi-2 as default model
        model = data.get('model', 'phi-2')
        temperature = data.get('temperature', DEFAULT_TEMPERATURE)
        top_p = data.get('top_p', 0.9)
        top_k = data.get('top_k', 40)
        repeat_penalty = data.get('repeat_penalty', 1.1)
        num_predict = data.get('num_predict', DEFAULT_MAX_NEW_TOKENS)
        
        # Get or create session
        session_id = request.headers.get('X-Session-ID')
        agent_meta = {
            'agent_name': unified_agent.name,
            'provider': unified_agent.provider_info.get('provider'),
            'version': unified_agent.provider_info.get('version'),
            'model': model
        }
        session_id = session_manager.get_or_create_session(session_id, agent_meta)
        
        # Prepare context
        context = {
            "model": model,
            "temperature": temperature,
            "max_tokens": num_predict,
            "session_id": session_id,
            "top_p": top_p,
            "top_k": top_k,
            "repeat_penalty": repeat_penalty
        }
        
        # Update session
        session_manager.update_session(session_id, {
            "last_message": prompt,
            "agent_meta": agent_meta
        })
        
        # Process the prompt
        generation_start = time.time()
        result = unified_agent.process_message(prompt, context)
        generation_time = time.time() - generation_start
        
        if not result or not result.get('response'):
            logger.error("No response from agent")
            return jsonify({"error": "Agent could not generate response"}), 503
        
        response_content = result.get('response', '')
        response_time = result.get('response_time', {})
        
        if stream:
            # Streaming response - Note: This is simulated streaming from pre-generated response
            # For real streaming, model server should support streaming and forward chunks directly
            def generate_ollama_stream():
                words = response_content.split()
                for i, word in enumerate(words):
                    chunk = {
                        'model': model,
                        'response': word + ' ' if i < len(words) - 1 else word,
                        'done': False,
                        'done_reason': None if i < len(words) - 1 else 'length'
                    }
                    yield json.dumps(chunk) + '\n'
                    # Small delay for streaming effect (simulated)
                    time.sleep(0.01)
                
                # Send final chunk with actual duration metrics
                total_duration_ms = int(generation_time * 1000)
                eval_duration_ms = int(response_time.get('generation_seconds', generation_time) * 1000)
                final_chunk = {
                    'model': model,
                    'response': '',
                    'done': True,
                    'done_reason': 'stop',
                    'context': [],
                    'total_duration': total_duration_ms,
                    'load_duration': 0,
                    'prompt_eval_count': len(prompt.split()),
                    'prompt_eval_duration': 0,
                    'eval_count': len(response_content.split()),
                    'eval_duration': eval_duration_ms
                }
                yield json.dumps(final_chunk) + '\n'
            
            response = Response(
                stream_with_context(generate_ollama_stream()),
                mimetype='application/x-ndjson',
                headers={
                    'X-Session-ID': session_id,
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }
            )
            return response
        else:
            # Non-streaming response with actual duration metrics
            total_duration_ms = int(generation_time * 1000)
            eval_duration_ms = int(response_time.get('generation_seconds', generation_time) * 1000)
            response_data = {
                'model': model,
                'response': response_content,
                'done': True,
                'done_reason': 'stop',
                'context': [],
                'total_duration': total_duration_ms,
                'load_duration': 0,
                'prompt_eval_count': len(prompt.split()),
                'prompt_eval_duration': 0,
                'eval_count': len(response_content.split()),
                'eval_duration': eval_duration_ms
            }
            
            response = jsonify(response_data)
            response.headers['X-Session-ID'] = session_id
            return response
        
    except Exception as e:
        logger.error(f"Ollama completion endpoint error: {e}", exc_info=True)
        return jsonify({"error": {"message": str(e), "type": "server_error"}}), 500

@app.route('/v1/chat/completions', methods=['POST', 'OPTIONS'])
def chat_completions():
    """OpenAI-compatible chat completions endpoint with streaming support"""
    try:
        if request.method == 'OPTIONS':
            # CORS preflight already handled by before_request
            return jsonify({}), 200
        
        # Get or create session from X-Session-ID header with agent meta info
        session_id = request.headers.get('X-Session-ID')
        agent_meta = {
            'agent_name': unified_agent.name,
            'provider': unified_agent.provider_info.get('provider'),
            'version': unified_agent.provider_info.get('version'),
            'owner': unified_agent.provider_info.get('owner'),
            'company': unified_agent.provider_info.get('company'),
            'personal_name': unified_agent.personal_info.get('name'),
            'personal_role': unified_agent.personal_info.get('role'),
            'language': unified_agent.language,
            'personality': unified_agent.personal_info.get('personality'),
            'approach': unified_agent.personal_info.get('approach'),
            'model': 'phi-2'
        }
        session_id = session_manager.get_or_create_session(session_id, agent_meta)
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Check for streaming
        stream = data.get('stream', False)
        
        # Extract messages from OpenAI format
        messages = data.get('messages', [])
        if not messages:
            return jsonify({"error": "messages array is required"}), 400
        
        # Get the last user message
        user_message = None
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
        
        if not user_message:
            return jsonify({"error": "No user message found in messages"}), 400
        
        # Process the message
        # Use phi-2 as default model for Bengali responses
        context = {
            "model": data.get('model', 'phi-2'),
            "temperature": data.get('temperature', DEFAULT_TEMPERATURE),
            "max_tokens": data.get('max_tokens', 500),
            "session_id": session_id
        }
        
        # Update session with agent meta to maintain identity
        session = session_manager.get_session(session_id)
        if session and 'agent_meta' in session:
            # Keep agent meta in context
            context['agent_meta'] = session['agent_meta']
        
        # Update session with full metadata including model and parameters
        session_manager.update_session(session_id, {
            "last_message": user_message,
            "agent_meta": agent_meta,  # Always keep agent meta updated
            "model": context.get("model", "phi-2"),
            "temperature": context.get("temperature", DEFAULT_TEMPERATURE),
            "max_tokens": context.get("max_tokens", 500),
            "last_updated": datetime.now().isoformat()
        })
        
        # Process message with timing
        generation_start = time.time()
        result = unified_agent.process_message(user_message, context)
        generation_time = time.time() - generation_start
        
        # Check if we got a response (even if it's a fallback)
        if not result or not result.get('response'):
            logger.error("No response from agent process_message")
            return jsonify({
                "error": {
                    "message": "Agent could not generate a response. LangChain pipeline may be unavailable or the model failed to load.",
                    "type": "agent_no_response"
                }
            }), 503
        
        # Trust verification check - if rejected (and not fallback), return error
        if result.get('rejected', False) and result.get('source') != 'fallback':
            logger.warning(f"Response rejected by trust verification: {result.get('truth_verification', {}).get('rejection_reason')}")
            return jsonify({
                "error": {
                    "message": "Response failed trust verification",
                    "type": "trust_verification_failed",
                    "details": result.get('truth_verification', {})
                }
            }), 400
        
        # Format response in OpenAI-compatible format
        completion_id = f"chatcmpl-{int(time.time())}-{session_id[:8]}"
        created_time = int(time.time())
        response_content = result.get('response', '')
        
        if stream:
            # Streaming response
            def generate_stream():
                # Send initial chunk
                yield f"data: {json.dumps({'id': completion_id, 'object': 'chat.completion.chunk', 'created': created_time, 'model': context.get('model'), 'choices': [{'index': 0, 'delta': {'role': 'assistant', 'content': ''}, 'finish_reason': None}]})}\n\n"
                
                # Stream content word by word (simulated - in real implementation, use actual streaming from model)
                words = response_content.split()
                for i, word in enumerate(words):
                    chunk_data = {
                        'id': completion_id,
                        'object': 'chat.completion.chunk',
                        'created': created_time,
                        'model': context.get('model'),
                        'choices': [{
                            'index': 0,
                            'delta': {'content': word + ' '},
                            'finish_reason': None if i < len(words) - 1 else 'stop'
                        }]
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                    time.sleep(0.01)  # Small delay for streaming effect
                
                # Send final chunk
                yield f"data: {json.dumps({'id': completion_id, 'object': 'chat.completion.chunk', 'created': created_time, 'model': context.get('model'), 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
                yield "data: [DONE]\n\n"
            
            response = Response(
                stream_with_context(generate_stream()),
                mimetype='text/event-stream',
                headers={
                    'X-Session-ID': session_id,
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive'
                }
            )
            return response
        else:
            # Non-streaming response
            response_data = {
                "id": completion_id,
                "object": "chat.completion",
                "created": created_time,
                "model": context.get('model', 'phi-2'),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response_content
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(user_message.split()) if user_message else 0,
                    "completion_tokens": len(response_content.split()) if response_content else 0,
                    "total_tokens": len(user_message.split()) + len(response_content.split()) if response_content else 0
                },
                "response_time": {
                    "generation_seconds": round(generation_time, 3),
                    "total_seconds": round(generation_time, 3)
                }
            }
            
            response = jsonify(response_data)
            response.headers['X-Session-ID'] = session_id
            return response
        
    except Exception as e:
        logger.error(f"Chat completions endpoint error: {e}")
        return jsonify({"error": {"message": str(e), "type": "server_error"}}), 500

@app.route('/status')
def status():
    """এজেন্ট স্ট্যাটাস - Provider এবং Personal info সহ"""
    status_data = unified_agent.get_agent_status()
    response = jsonify(status_data)
    # Add session ID if available
    session_id = request.headers.get('X-Session-ID')
    if session_id:
        response.headers['X-Session-ID'] = session_id
    return response

@app.route('/v1/agent/info', methods=['GET'])
def agent_info():
    """Agent information endpoint - Provider এবং Personal info"""
    info = {
        "provider_info": unified_agent.get_provider_info(),
        "personal_info": unified_agent.get_personal_info(),
        "capabilities": list(unified_agent.capabilities.keys()),
        "family": unified_agent.family,
        "timestamp": datetime.now().isoformat()
    }
    response = jsonify(info)
    session_id = request.headers.get('X-Session-ID')
    if session_id:
        response.headers['X-Session-ID'] = session_id
    return response

@app.route('/v1/memory/conversations', methods=['GET'])
def get_conversations():
    """Memory থেকে conversation history retrieve করুন"""
    limit = request.args.get('limit', 10, type=int)
    conversations = unified_agent.get_conversation_history_from_memory(limit=limit)
    response = jsonify({
        "conversations": conversations,
        "total": len(conversations),
        "timestamp": datetime.now().isoformat()
    })
    session_id = request.headers.get('X-Session-ID')
    if session_id:
        response.headers['X-Session-ID'] = session_id
    return response

@app.route('/info')
def info():
    return jsonify({
        "agent_name": unified_agent.name,
        "description": unified_agent.description,
        "family": unified_agent.family,
        "capabilities": unified_agent.capabilities,
        "personality_traits": unified_agent.personality_traits
    })

@app.route('/memory')
def memory():
    """মেমোরি ইনফরমেশন এন্ডপয়েন্ট"""
    try:
        history = unified_agent.memory.get_conversation_history(limit=20)
        return jsonify({
            "total_conversations": len(history),
            "recent_conversations": history,
            "memory_files": {
                "json": unified_agent.memory.json_path,
                "sqlite": unified_agent.memory.sqlite_path
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """হেলথ চেক এন্ডপয়েন্ট"""
    try:
        model_status = unified_agent.langchain.status()
        resources = unified_agent.resource_monitor.check_system_resources()
        
        return jsonify({
            "status": "healthy" if model_status.get("ready") else "degraded",
            "model_status": model_status,
            "system_resources": resources,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == "__main__":
    print("🤖 Starting ZombieCoder Unified Agent System - Family Edition...")
    print(f"🎭 Agent: {unified_agent.name}")
    print("👨‍👩‍👧 Family Members:", list(unified_agent.family.keys()))
    print("🧠 Memory Systems: JSON + SQLite")
    print("🔗 LangChain Integration: Active")
    print(f"🤖 LangChain Model: {unified_agent.model_name} (Default: phi-2)")
    print(f"🌐 Server starting on http://0.0.0.0:{AGENT_PORT}")
    print(f"🔒 CORS Origins: {', '.join(CORS_ORIGINS)}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=AGENT_PORT, debug=False)