"""
register_face.py
Daftarkan wajah kamu ke PETER
"""

from peter_vision import PeterVision
from dotenv import load_dotenv
import os

load_dotenv()
USER_NAME = os.getenv("USER_NAME", "Sir")

print("=" * 50)
print("  PETER — Daftarkan Wajah")
print("=" * 50)
print(f"\nHalo {USER_NAME}!")
print("PETER akan mengambil 5 foto wajah kamu.")
print("Pastikan:")
print("  - Webcam terpasang dan aktif")
print("  - Pencahayaan cukup terang")
print("  - Wajah menghadap langsung ke kamera")
print("  - Jarak sekitar 50-80cm dari webcam")
print()

vision = PeterVision()

# Daftarkan wajah
berhasil = vision.register_face(
    name=USER_NAME,
    num_photos=5
)

if berhasil:
    print("\n" + "=" * 50)
    print(f"  Wajah {USER_NAME} berhasil didaftarkan!")
    print("  PETER sekarang bisa mengenali kamu.")
    print("=" * 50)
    print("\nTest sekarang dengan:")
    print("  python test_vision.py")
else:
    print("\nGagal mendaftarkan wajah.")
    print("Coba lagi dengan pencahayaan lebih baik.")