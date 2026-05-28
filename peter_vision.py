"""
peter_vision.py
OpenCV Vision System untuk PETER
Face Recognition + Gesture + Emotion + Object Detection
"""

import cv2
import numpy as np
import os
import time
import threading
import pickle
from dotenv import load_dotenv

load_dotenv()
USER_NAME = os.getenv("USER_NAME", "Sir")
FACES_DB  = "C:\\peter-ai\\data\\faces\\known_faces.pkl"

class PeterVision:
    def __init__(self):
        self.known_faces   = []
        self.current_user  = None
        self.is_running    = False
        self.last_gesture  = None
        self.last_emotion  = None
        os.makedirs("C:\\peter-ai\\data\\faces", exist_ok=True)
        self._load_known_faces()
        print("[VISION] Peter Vision initialized!")
        print("[VISION] dlib + MediaPipe + DeepFace aktif!")

    def _load_known_faces(self):
        """Load wajah yang sudah didaftarkan"""
        if os.path.exists(FACES_DB):
            with open(FACES_DB, "rb") as f:
                self.known_faces = pickle.load(f)
            names = [f["name"] for f in self.known_faces]
            print(f"[VISION] Wajah terdaftar: {names}")
        else:
            print("[VISION] Belum ada wajah terdaftar")
            print("[VISION] Jalankan register_face.py dulu!")

    def identify_face(self, frame) -> str:
        """Identifikasi wajah dengan face_recognition"""
        try:
            import face_recognition
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            small = cv2.resize(rgb, (0,0), fx=0.5, fy=0.5)
            locs  = face_recognition.face_locations(small)

            if not locs:
                return None

            encs = face_recognition.face_encodings(small, locs)
            for enc in encs:
                if self.known_faces:
                    known_encs  = [f["encoding"] for f in self.known_faces]
                    known_names = [f["name"] for f in self.known_faces]
                    matches     = face_recognition.compare_faces(
                        known_encs, enc, tolerance=0.5
                    )
                    distances = face_recognition.face_distance(
                        known_encs, enc
                    )
                    if True in matches:
                        best  = np.argmin(distances)
                        return known_names[best]
                    return "Unknown"
                else:
                    return f"Wajah terdeteksi ({len(locs)} orang)"
            return None

        except Exception as e:
            print(f"[VISION] Face error: {e}")
            return None

    def detect_gesture(self, frame) -> str:
        """Deteksi gesture tangan dengan MediaPipe"""
        try:
            import mediapipe as mp
            mp_hands = mp.solutions.hands
            hands    = mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=1,
                min_detection_confidence=0.7
            )
            rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            if not results.multi_hand_landmarks:
                return None

            lm  = results.multi_hand_landmarks[0].landmark
            up  = {
                "thumb" : lm[4].x < lm[3].x,
                "index" : lm[8].y < lm[6].y,
                "middle": lm[12].y < lm[10].y,
                "ring"  : lm[16].y < lm[14].y,
                "pinky" : lm[20].y < lm[18].y,
            }
            count = sum(up.values())

            if up["thumb"] and count == 1:
                return "thumbs_up"
            elif not any(up.values()):
                return "fist"
            elif count == 5:
                return "open_hand"
            elif up["index"] and count == 1:
                return "pointing"
            elif up["index"] and up["middle"] and count == 2:
                return "peace"
            return None

        except Exception:
            return None

    def detect_emotion(self, frame) -> str:
        """Deteksi emosi dengan DeepFace"""
        try:
            from deepface import DeepFace
            result = DeepFace.analyze(
                frame,
                actions=["emotion"],
                enforce_detection=False,
                silent=True
            )
            return result[0]["dominant_emotion"]
        except Exception:
            return None

    def detect_objects(self, frame) -> list:
        """Deteksi objek dengan YOLO"""
        try:
            from ultralytics import YOLO
            model   = YOLO("yolov8n.pt")
            results = model(frame, verbose=False)
            objects = []
            for r in results:
                for box in r.boxes:
                    label = model.names[int(box.cls)]
                    conf  = float(box.conf)
                    if conf > 0.5:
                        objects.append(
                            f"{label} ({conf:.0%})"
                        )
            return objects
        except Exception:
            return []

    def capture_and_analyze(self) -> dict:
        """Ambil foto webcam dan analisis semuanya"""
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return {"error": "Webcam tidak tersedia"}

        print("[VISION] Menganalisis...")

        result = {
            "face"   : self.identify_face(frame),
            "gesture": self.detect_gesture(frame),
            "emotion": self.detect_emotion(frame),
            "objects": self.detect_objects(frame),
        }

        # Simpan foto terakhir
        cv2.imwrite("C:\\peter-ai\\last_vision.jpg", frame)
        return result

    def register_face(self, name: str, num_photos: int = 5):
        """Daftarkan wajah baru"""
        import face_recognition
        print(f"\n[VISION] Mendaftarkan wajah: {name}")
        print(f"[VISION] Akan ambil {num_photos} foto")

        photos = []
        cap    = cv2.VideoCapture(0)

        for i in range(num_photos):
            input(f"  Tekan Enter untuk foto ke-{i+1}...")
            ret, frame = cap.read()
            if not ret:
                print("  ERROR: Webcam gagal")
                continue

            rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locs = face_recognition.face_locations(rgb)

            if locs:
                enc = face_recognition.face_encodings(rgb, locs)[0]
                photos.append(enc)
                path = f"C:\\peter-ai\\data\\faces\\{name}_{i+1}.jpg"
                cv2.imwrite(path, frame)
                print(f"  Foto {i+1} OK!")
            else:
                print(f"  Foto {i+1} gagal — wajah tidak terdeteksi")

        cap.release()

        if not photos:
            print("[VISION] Gagal — tidak ada foto berhasil")
            return False

        # Hitung rata-rata encoding
        avg_enc = np.mean(photos, axis=0)

        # Load data existing
        existing = []
        if os.path.exists(FACES_DB):
            with open(FACES_DB, "rb") as f:
                existing = pickle.load(f)

        # Hapus data lama dengan nama sama
        existing = [f for f in existing if f["name"] != name]

        # Tambah data baru
        existing.append({
            "name"        : name,
            "encoding"    : avg_enc,
            "photos_count": len(photos)
        })

        # Simpan
        with open(FACES_DB, "wb") as f:
            pickle.dump(existing, f)

        self.known_faces = existing
        print(f"\n[VISION] Wajah {name} berhasil didaftarkan!")
        print(f"[VISION] Total foto: {len(photos)}/{num_photos}")
        return True

    def start_monitor(self,
                      on_face=None,
                      on_gesture=None,
                      on_emotion=None):
        """Monitor kamera di background"""
        self.is_running = True

        def _loop():
            cap          = cv2.VideoCapture(0)
            last_face    = 0
            last_gesture = 0
            last_emotion = 0

            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue

                now = time.time()

                # Face: setiap 3 detik
                if now - last_face > 3.0:
                    name = self.identify_face(frame)
                    if name and name != self.current_user:
                        self.current_user = name
                        print(f"\n[VISION] Wajah: {name}")
                        if on_face:
                            on_face(name)
                    last_face = now

                # Gesture: setiap 1 detik
                if now - last_gesture > 1.0:
                    gesture = self.detect_gesture(frame)
                    if gesture and gesture != self.last_gesture:
                        self.last_gesture = gesture
                        print(f"\n[VISION] Gesture: {gesture}")
                        if on_gesture:
                            on_gesture(gesture)
                    last_gesture = now

                # Emotion: setiap 5 detik
                if now - last_emotion > 5.0:
                    emotion = self.detect_emotion(frame)
                    if emotion and emotion != self.last_emotion:
                        self.last_emotion = emotion
                        if on_emotion:
                            on_emotion(emotion)
                    last_emotion = now

                time.sleep(0.1)

            cap.release()

        thread = threading.Thread(
            target=_loop, daemon=True
        )
        thread.start()
        print("[VISION] Monitor background aktif!")

    def stop_monitor(self):
        self.is_running = False

    def format_result(self, result) -> str:
        """Format hasil analisis jadi kalimat natural"""
        parts = []

        face = result.get("face")
        if face:
            if face == USER_NAME:
                parts.append(f"Saya melihat {USER_NAME}")
            elif face == "Unknown":
                parts.append("Ada orang yang tidak dikenal")
            else:
                parts.append(f"Terdeteksi: {face}")

        gesture = result.get("gesture")
        if gesture:
            g_map = {
                "thumbs_up" : "memberi jempol",
                "fist"      : "mengepalkan tangan",
                "open_hand" : "membuka tangan",
                "pointing"  : "menunjuk",
                "peace"     : "tanda peace"
            }
            parts.append(g_map.get(gesture, gesture))

        emotion = result.get("emotion")
        if emotion:
            e_map = {
                "happy"   : "terlihat senang",
                "sad"     : "terlihat sedih",
                "angry"   : "terlihat marah",
                "neutral" : "ekspresi normal",
                "surprise": "terlihat terkejut",
                "fear"    : "terlihat takut"
            }
            parts.append(e_map.get(emotion, emotion))

        objects = result.get("objects", [])
        if objects:
            parts.append(f"Ada {', '.join(objects[:3])}")

        if not parts:
            return "Tidak ada yang terdeteksi"

        return ". ".join(parts)