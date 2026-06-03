import sys
import traceback
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

import os
USER_NAME        = os.getenv("USER_NAME", "Tjerlang")
ANTHROPIC_KEY    = os.getenv("ANTHROPIC_API_KEY", "")
ELEVENLABS_KEY   = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE_ID", "")
OLLAMA_URL       = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LOCAL_MODE       = os.getenv("LOCAL_MODE", "false").lower() == "true"

HEAL_OK   = False
VISION_OK = False
MEMORY_OK = False
healer    = None
vision    = None
memory    = None

try:
    from peter_self_heal import PeterSelfHeal
    healer  = PeterSelfHeal()
    HEAL_OK = True
except Exception as e:
    print(f"Self-heal skip: {e}")

try:
    from peter_memory import PeterMemory
    memory    = PeterMemory()
    MEMORY_OK = True
except Exception as e:
    print(f"Memory skip: {e}")

def peter_speak(text, play=True):
    try:
        from peter_tts import peter_speak as tts
        tts(text, play=play)
    except Exception as e:
        print(f"[TTS] {e}")

def chat_peter(message, use_memory=True):
    try:
        from core.brain import PeterBrain
        if not hasattr(chat_peter, '_brain'):
            chat_peter._brain = PeterBrain()
        return chat_peter._brain.think(message, use_memory=use_memory)
    except Exception as e:
        return f"Error: {e}"

print(f"USER_NAME: {USER_NAME}")
print("Test menu [1]...")

try:
    import time
    peter_speak(f"Halo {USER_NAME}! Peter Executor siap.")

    bukan_kode = [
        "script video", "script youtube", "strategi"
    ]
    kata_kode_list = [
        "buat file", "buat app", "tulis kode"
    ]

    user_input = "halo peter"

    is_bukan_kode = any(b in user_input.lower() for b in bukan_kode)
    butuh_kode    = any(k in user_input.lower() for k in kata_kode_list)
    if is_bukan_kode:
        butuh_kode = False

    print(f"Input    : {user_input}")
    print(f"Kode?    : {butuh_kode}")

    print("\nChat test...")
    response = chat_peter(user_input)
    print(f"Response : {response[:200]}")

except Exception as e:
    print(f"\nERROR: {e}")
    traceback.print_exc()