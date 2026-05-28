"""
install_peter.py
Auto installer untuk PETER AI
"""

import os
import sys
import subprocess

print("""
╔══════════════════════════════════════════════════╗
║         PETER AI — Auto Installer               ║
║   Personal Enhanced Thinking & Execution        ║
╚══════════════════════════════════════════════════╝
""")

def run(cmd: str) -> bool:
    result = subprocess.run(
        cmd, shell=True,
        capture_output=True, text=True
    )
    return result.returncode == 0

def check(name: str, import_name: str) -> bool:
    try:
        __import__(import_name)
        print(f"  ✅ {name}")
        return True
    except ImportError:
        print(f"  ❌ {name} — tidak terinstall")
        return False

print("Mengecek dependencies...")
print("-" * 40)

packages = [
    ("Anthropic",        "anthropic"),
    ("CrewAI",           "crewai"),
    ("ElevenLabs",       "elevenlabs"),
    ("Whisper",          "whisper"),
    ("OpenCV",           "cv2"),
    ("MediaPipe",        "mediapipe"),
    ("Face Recognition", "face_recognition"),
    ("ChromaDB",         "chromadb"),
    ("FastAPI",          "fastapi"),
    ("PyAudio",          "pyaudio"),
    ("SoundDevice",      "sounddevice"),
    ("PIL/Pillow",       "PIL"),
    ("PyAutoGUI",        "pyautogui"),
    ("Torch",            "torch"),
    ("DuckDuckGo",       "duckduckgo_search"),
]

missing = []
for name, imp in packages:
    if not check(name, imp):
        missing.append(name)

print("-" * 40)

if missing:
    print(f"\n⚠️  {len(missing)} package belum terinstall")
    install = input("Install sekarang? (y/n): ").strip().lower()
    if install == 'y':
        print("\nInstalling...")
        run(f'pip install -r requirements.txt')
        print("Install selesai!")
else:
    print("\n✅ Semua dependencies OK!")

# Cek folder
print("\nMembuat folder...")
folders = [
    "data/faces", "data/outputs", "data/memory",
    "data/logs", "core", "tools", "content",
    "publishers", "web"
]
for f in folders:
    os.makedirs(f"C:\\peter-ai\\{f}", exist_ok=True)
    print(f"  ✅ {f}")

# Cek .env
print("\nMengecek konfigurasi...")
if not os.path.exists("C:\\peter-ai\\.env"):
    print("  ⚠️  .env tidak ditemukan!")
    print("  Copy .env.example ke .env dan isi API keys")
else:
    print("  ✅ .env ditemukan")

# Cek face registration
faces_db = "C:\\peter-ai\\data\\faces\\known_faces.pkl"
if os.path.exists(faces_db):
    print("  ✅ Face recognition sudah terdaftar")
else:
    print("  ⚠️  Wajah belum didaftarkan")
    reg = input("  Daftarkan wajah sekarang? (y/n): ").strip().lower()
    if reg == 'y':
        run('python register_face.py')

# Cek Ollama
print("\nMengecek Ollama...")
result = subprocess.run(
    'ollama list', shell=True,
    capture_output=True, text=True
)
if result.returncode == 0:
    print("  ✅ Ollama berjalan")
    print(f"  Models: {result.stdout.strip()[:100]}")
else:
    print("  ❌ Ollama tidak berjalan")
    print("  Download: https://ollama.ai")

print("""
╔══════════════════════════════════════════════════╗
║           Instalasi Selesai!                    ║
║   Jalankan: python start_peter.py               ║
╚══════════════════════════════════════════════════╝
""")