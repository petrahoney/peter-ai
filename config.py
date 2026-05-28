"""
config.py
Semua settings dan konfigurasi PETER AI
"""

from dotenv import load_dotenv
import os

load_dotenv()

# ── IDENTITAS ────────────────────────────────────
AI_NAME   = os.getenv("AI_NAME", "PETER")
USER_NAME = os.getenv("USER_NAME", "Sir")
WAKE_WORD = os.getenv("WAKE_WORD", "peter")

# ── MODE ─────────────────────────────────────────
LOCAL_MODE = os.getenv("LOCAL_MODE", "false").lower() == "true"

# ── API KEYS ─────────────────────────────────────
ANTHROPIC_KEY    = os.getenv("ANTHROPIC_API_KEY", "")
ELEVENLABS_KEY   = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")

# ── PLATFORM API KEYS ────────────────────────────
YOUTUBE_CLIENT_ID     = os.getenv("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")
INSTAGRAM_TOKEN       = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_USER_ID     = os.getenv("INSTAGRAM_USER_ID", "")
TIKTOK_TOKEN          = os.getenv("TIKTOK_ACCESS_TOKEN", "")

# ── LOCAL SETTINGS ───────────────────────────────
OLLAMA_URL        = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL      = os.getenv("OLLAMA_MODEL", "llama3.3")
OLLAMA_FAST_MODEL = os.getenv("OLLAMA_FAST_MODEL", "llama3.2:3b")
WHISPER_MODEL     = os.getenv("WHISPER_MODEL", "large-v3")

# ── LLM MODEL ────────────────────────────────────
if LOCAL_MODE:
    LLM_MODEL      = f"ollama/{OLLAMA_MODEL}"
    LLM_FAST_MODEL = f"ollama/{OLLAMA_FAST_MODEL}"
    LLM_BASE_URL   = OLLAMA_URL
else:
    LLM_MODEL      = "anthropic/claude-sonnet-4-6"
    LLM_FAST_MODEL = "anthropic/claude-haiku-4-5-20251001"
    LLM_BASE_URL   = None

# ── PATHS ─────────────────────────────────────────
BASE_DIR   = "C:\\peter-ai"
DATA_DIR   = f"{BASE_DIR}\\data"
OUTPUT_DIR = f"{DATA_DIR}\\outputs"
MEMORY_DIR = f"{DATA_DIR}\\memory"
FACES_DIR  = f"{DATA_DIR}\\faces"
LOGS_DIR   = f"{DATA_DIR}\\logs"

# ── DASHBOARD ─────────────────────────────────────
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 8080))
ENABLE_VISION  = os.getenv("ENABLE_VISION", "true").lower() == "true"
CAMERA_INDEX   = int(os.getenv("CAMERA_INDEX", 0))

# ── VALIDASI ──────────────────────────────────────
def validate():
    errors = []
    if not LOCAL_MODE and not ANTHROPIC_KEY:
        errors.append("ANTHROPIC_API_KEY tidak ditemukan di .env")
    if not ELEVENLABS_KEY:
        errors.append("ELEVENLABS_API_KEY tidak ditemukan di .env")
    if errors:
        print("[CONFIG] WARNING:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("[CONFIG] Semua API keys OK!")
    return len(errors) == 0

if __name__ == "__main__":
    print("=" * 50)
    print("  PETER AI — Konfigurasi")
    print("=" * 50)
    print(f"  Mode      : {'LOCAL (Ollama)' if LOCAL_MODE else 'CLOUD (Claude)'}")
    print(f"  User      : {USER_NAME}")
    print(f"  LLM Model : {LLM_MODEL}")
    print(f"  Whisper   : {WHISPER_MODEL}")
    print(f"  Vision    : {ENABLE_VISION}")
    print(f"  Dashboard : port {DASHBOARD_PORT}")
    validate()