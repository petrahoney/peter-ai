"""
test_vision.py
Test semua kemampuan PETER Vision
"""

from peter_vision import PeterVision
from dotenv import load_dotenv
import os

load_dotenv()
USER_NAME = os.getenv("USER_NAME", "Sir")

print("=" * 50)
print("  PETER Vision — Test Lengkap")
print("=" * 50)

vision = PeterVision()

print("\n[TEST] Menganalisis kamera...")
print("[TEST] Pastikan wajah menghadap webcam!\n")

result = vision.capture_and_analyze()

print("\n" + "=" * 50)
print("  HASIL ANALISIS PETER VISION:")
print("=" * 50)

# Wajah
face = result.get("face")
if face:
    if face == USER_NAME:
        print(f"  Wajah    : ✓ {USER_NAME} dikenali!")
    else:
        print(f"  Wajah    : {face}")
else:
    print("  Wajah    : Tidak terdeteksi")

# Gesture
gesture = result.get("gesture")
gestures = {
    "thumbs_up" : "Jempol ke atas 👍",
    "fist"      : "Tinju ✊",
    "open_hand" : "Tangan terbuka 🖐",
    "pointing"  : "Menunjuk ☝️",
    "peace"     : "Peace ✌️"
}
print(f"  Gesture  : {gestures.get(gesture, 'Tidak ada')}")

# Emosi
emotion = result.get("emotion")
emotions = {
    "happy"   : "Senang 😊",
    "sad"     : "Sedih 😢",
    "angry"   : "Marah 😠",
    "neutral" : "Normal 😐",
    "surprise": "Terkejut 😲",
    "fear"    : "Takut 😨",
    "disgust" : "Jijik 🤢"
}
print(f"  Emosi    : {emotions.get(emotion, 'Tidak terdeteksi')}")

# Objek
objects = result.get("objects", [])
if objects:
    print(f"  Objek    : {', '.join(objects[:5])}")
else:
    print("  Objek    : Tidak ada")

print("=" * 50)

# Format natural
print("\n[PETER] Laporan vision:")
print(f"[PETER] {vision.format_result(result)}")

# Simpan foto
print(f"\n[TEST] Foto tersimpan: C:\\peter-ai\\last_vision.jpg")
print("[TEST] Buka foto untuk lihat hasil!")