import sys
import traceback
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

import os
USER_NAME = os.getenv("USER_NAME", "Tjerlang")

# Simulasi menu 1
print(f"USER_NAME = {USER_NAME}")

try:
    # Import semua yang dipakai di run_peter_executor
    from peter_tts import peter_speak
    from peter_identity import BOOT_BANNER, get_greeting
    print("Import OK")

    # Test TTS
    peter_speak(f"Halo {USER_NAME}!")
    print("TTS OK")

    # Test chat
    from core.brain import PeterBrain
    brain    = PeterBrain()
    response = brain.think("halo peter")
    print(f"Brain OK: {response[:100]}")

except Exception as e:
    print(f"\nERROR DITEMUKAN: {e}")
    traceback.print_exc()