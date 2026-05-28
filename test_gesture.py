"""
Test gesture detection step by step
"""
import cv2
import mediapipe as mp
import time
import os

CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", 0))

print("=" * 50)
print("  Test Gesture Detection")
print("=" * 50)

# Test 1: Cek kamera bisa baca frame
print("\n[TEST 1] Cek kamera...")
cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    print(f"❌ Kamera {CAMERA_INDEX} tidak bisa dibuka!")
    print("Coba ganti CAMERA_INDEX di .env ke 1 atau 2")
    exit()

ret, frame = cap.read()
if not ret or frame is None:
    print("❌ Kamera terbuka tapi tidak bisa baca frame!")
    cap.release()
    exit()

print(f"✅ Kamera OK! Frame size: {frame.shape}")
cap.release()

# Test 2: Cek MediaPipe bisa detect tangan
print("\n[TEST 2] Test MediaPipe Hands...")
print("Tunjukkan tangan ke kamera lalu tekan Enter...")
input()

cap        = cv2.VideoCapture(CAMERA_INDEX)
mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode        = False,
    max_num_hands            = 1,
    min_detection_confidence = 0.5,
    min_tracking_confidence  = 0.5
)

found    = False
attempts = 0

print("Mencari tangan selama 5 detik...")
start = time.time()

while time.time() - start < 5:
    ret, frame = cap.read()
    if not ret:
        continue

    attempts += 1
    rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        found = True
        lm    = results.multi_hand_landmarks[0].landmark

        # Deteksi jari
        fingers = {
            "thumb" : lm[4].x < lm[3].x,
            "index" : lm[8].y < lm[6].y,
            "middle": lm[12].y < lm[10].y,
            "ring"  : lm[16].y < lm[14].y,
            "pinky" : lm[20].y < lm[18].y,
        }
        count = sum(fingers.values())

        print(f"✅ Tangan terdeteksi!")
        print(f"   Jari terangkat: {count}")
        print(f"   Detail: {fingers}")

        # Tentukan gesture
        if count == 0:
            gesture = "fist"
        elif count == 5:
            gesture = "open_hand"
        elif fingers["thumb"] and count == 1:
            gesture = "thumbs_up"
        elif fingers["index"] and count == 1:
            gesture = "pointing"
        elif fingers["index"] and fingers["middle"] and count == 2:
            gesture = "peace"
        else:
            gesture = f"unknown ({count} jari)"

        print(f"   Gesture: {gesture}")
        break

    time.sleep(0.1)

cap.release()

if not found:
    print(f"❌ Tangan tidak terdeteksi setelah {attempts} frame!")
    print("\nKemungkinan penyebab:")
    print("  1. Pencahayaan kurang — coba di tempat lebih terang")
    print("  2. Tangan terlalu jauh — dekatkan ke kamera")
    print("  3. Confidence terlalu tinggi — sudah diturunkan ke 0.5")
    print("  4. Kamera indeks salah — coba index 1")
else:
    print("\n✅ Gesture detection BERFUNGSI!")
    print("Jalankan lagi: python peter_vision_agent.py")