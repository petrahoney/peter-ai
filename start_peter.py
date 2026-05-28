"""
start_peter.py
Entry point utama PETER AI
Menjalankan semua sistem sekaligus
"""

import os
import sys
import threading
import time
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

USER_NAME  = os.getenv("USER_NAME", "Sir")
DASHBOARD  = int(os.getenv("DASHBOARD_PORT", 8080))
LOCAL_MODE = os.getenv("LOCAL_MODE", "false").lower() == "true"

def print_banner():
    print("""
╔══════════════════════════════════════════════════╗
║           P E T E R   A I   v2.0               ║
║    Personal Enhanced Thinking & Execution       ║
║    CrewAI + Claude + Whisper + Vision + Memory  ║
╚══════════════════════════════════════════════════╝""")
    print(f"  Mode    : {'LOCAL (Ollama)' if LOCAL_MODE else 'CLOUD (Claude API)'}")
    print(f"  User    : {USER_NAME}")
    print()


def start_dashboard():
    """Jalankan web dashboard di background"""
    try:
        import uvicorn
        from web.server import app
        print(f"[SERVER] Dashboard: http://localhost:{DASHBOARD}")
        uvicorn.run(
            app,
            host      = "0.0.0.0",
            port      = DASHBOARD,
            log_level = "error"
        )
    except Exception as e:
        print(f"[SERVER] Dashboard error: {e}")


def init_systems() -> dict:
    """Inisialisasi semua sistem PETER"""
    systems = {}

    # Vision
    print("[BOOT] Inisialisasi Vision...")
    try:
        from peter_vision import PeterVision
        systems["vision"]    = PeterVision()
        systems["vision_ok"] = True
        print("[VISION] Camera online — Face recognition active")
    except Exception as e:
        systems["vision_ok"] = False
        print(f"[VISION] Offline: {e}")

    # Memory
    print("[BOOT] Inisialisasi Memory...")
    try:
        from peter_memory import PeterMemory
        systems["memory"]    = PeterMemory()
        systems["memory_ok"] = True
        stats = systems["memory"].get_stats()
        print(f"[MEMORY] Online — {stats['long_term_count']} memories")
    except Exception as e:
        systems["memory_ok"] = False
        print(f"[MEMORY] Offline: {e}")

    # CrewAI
    print("[BOOT] Inisialisasi CrewAI...")
    try:
        from crewai import LLM
        systems["crew_ok"] = True
        print("[CREW] 5 agents standing by")
    except Exception as e:
        systems["crew_ok"] = False
        print(f"[CREW] Offline: {e}")

    # Voice
    print("[BOOT] Inisialisasi Voice...")
    try:
        import whisper
        import sounddevice
        systems["voice_ok"] = True
        print("[VOICE] Wake word detector active")
    except Exception as e:
        systems["voice_ok"] = False
        print(f"[VOICE] Offline: {e}")

     # Self-Heal — Auto diagnosa saat startup
    print("[BOOT] Menjalankan self-diagnosa...")
    try:
        from peter_self_heal import PeterSelfHeal
        healer = PeterSelfHeal()
        report = healer.check_all()
        issues = report.get("issues", [])
        if issues:
            print(f"[SELF-HEAL] {len(issues)} masalah — auto-fixing...")
            healer.auto_fix_all(report)
        else:
            print("[SELF-HEAL] ✅ Semua sistem sehat!")
        systems["heal_ok"] = True
    except Exception as e:
        print(f"[SELF-HEAL] Error: {e}")
        systems["heal_ok"] = False    

    return systems


def greeting(systems: dict):
    """Sapaan awal PETER"""
    try:
        from elevenlabs import ElevenLabs, VoiceSettings
        api_key  = os.getenv("ELEVENLABS_API_KEY", "")
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "")

        if not api_key or not voice_id:
            print(f"\n[PETER] Semua sistem online. Selamat datang, {USER_NAME}!")
            return

        client = ElevenLabs(api_key=api_key)
        text   = f"Semua sistem online. Selamat datang, {USER_NAME}. Saya siap membantu."

        audio  = client.text_to_speech.convert(
            voice_id       = voice_id,
            text           = text,
            model_id       = "eleven_multilingual_v2",
            voice_settings = VoiceSettings(
                stability        = 0.45,
                similarity_boost = 0.82
            )
        )
        audio_file = "C:\\peter-ai\\data\\outputs\\greeting.mp3"
        with open(audio_file, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)
        os.startfile(audio_file)
        time.sleep(3)

    except Exception as e:
        print(f"\n[PETER] Semua sistem online. Selamat datang, {USER_NAME}!")


def main():
    print_banner()

    # Start dashboard di background thread
    print("[BOOT] Memulai Dashboard...")
    dash_thread = threading.Thread(
        target = start_dashboard,
        daemon = True
    )
    dash_thread.start()
    time.sleep(2)
    print(f"[SERVER] Dashboard: http://localhost:{DASHBOARD}")

    # Init semua sistem
    print("\n[BOOT] Memulai semua sistem...\n")
    systems = init_systems()

    # Greeting suara
    print()
    greeting(systems)

    # Import dan jalankan main menu
    print("\n" + "=" * 52)
    print("  PETER AI v2.0 — Semua Sistem Online")
    print("=" * 52)

    # Inject systems ke main_peter
    import main_peter as peter
    peter.vision    = systems.get("vision")
    peter.VISION_OK = systems.get("vision_ok", False)
    peter.memory    = systems.get("memory")
    peter.MEMORY_OK = systems.get("memory_ok", False)

    # Jalankan menu utama
    peter.main()


if __name__ == "__main__":
    main()