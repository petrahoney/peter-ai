"""
peter_vision_agent.py
PETER Vision Agent — Complete System
Face Recognition + Gesture + Emotion + Object Detection
"""

import cv2
import os
import sys
import time
import threading
import pickle
import numpy as np
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

USER_NAME  = os.getenv("USER_NAME", "Sir")
FACES_DB   = "C:\\peter-ai\\data\\faces\\known_faces.pkl"
OUTPUT_DIR = "C:\\peter-ai\\data\\outputs"

os.makedirs("C:\\peter-ai\\data\\faces", exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

CONFIG = {
    "face_tolerance"      : 0.5,
    "face_interval_sec"   : 3.0,
    "gesture_confidence"  : 0.5,
    "gesture_interval_sec": 1.0,
    "emotion_interval_sec": 5.0,
    "object_confidence"   : 0.5,
    "object_interval_sec" : 10.0,
    "camera_index"        : int(os.getenv("CAMERA_INDEX", 0)),
    "frame_width"         : 1280,
    "frame_height"        : 720,
}


class FaceRecognizer:
    def __init__(self):
        self.known_faces = []
        self._load()

    def _load(self):
        if os.path.exists(FACES_DB):
            with open(FACES_DB, "rb") as f:
                self.known_faces = pickle.load(f)
            names = [d["name"] for d in self.known_faces]
            print(f"[FACE] Loaded: {names}")
        else:
            print("[FACE] Belum ada wajah terdaftar")

    def register(self, name: str, num_photos: int = 5) -> bool:
        try:
            import face_recognition
            print(f"\n[FACE] Mendaftarkan: {name}")
            cap    = cv2.VideoCapture(CONFIG["camera_index"])
            photos = []

            for i in range(num_photos):
                input(f"  Tekan Enter untuk foto {i+1}/{num_photos}...")
                ret, frame = cap.read()
                if not ret:
                    continue
                rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                locs = face_recognition.face_locations(rgb)
                if locs:
                    enc = face_recognition.face_encodings(rgb, locs)[0]
                    photos.append(enc)
                    foto_path = f"C:\\peter-ai\\data\\faces\\{name}_{i+1}.jpg"
                    cv2.imwrite(foto_path, frame)
                    print(f"  ✅ Foto {i+1} OK")
                else:
                    print(f"  ❌ Foto {i+1} gagal")

            cap.release()

            if not photos:
                return False

            avg_enc  = np.mean(photos, axis=0)
            existing = []
            if os.path.exists(FACES_DB):
                with open(FACES_DB, "rb") as f:
                    existing = pickle.load(f)
            existing = [d for d in existing if d["name"] != name]
            existing.append({
                "name"    : name,
                "encoding": avg_enc,
                "photos"  : len(photos)
            })
            with open(FACES_DB, "wb") as f:
                pickle.dump(existing, f)
            self.known_faces = existing
            print(f"[FACE] ✅ {name} didaftarkan ({len(photos)} foto)")
            return True

        except Exception as e:
            print(f"[FACE] Register error: {e}")
            return False

    def identify(self, frame) -> dict:
        result = {
            "detected"  : False,
            "name"      : None,
            "confidence": 0.0,
            "locations" : []
        }
        if not self.known_faces:
            return result
        try:
            import face_recognition
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            small = cv2.resize(rgb, (0, 0), fx=0.5, fy=0.5)
            locs  = face_recognition.face_locations(small)
            if not locs:
                return result

            result["detected"]  = True
            result["locations"] = [
                (t*2, r*2, b*2, l*2) for t, r, b, l in locs
            ]
            encs        = face_recognition.face_encodings(small, locs)
            known_encs  = [d["encoding"] for d in self.known_faces]
            known_names = [d["name"] for d in self.known_faces]

            for enc in encs:
                matches   = face_recognition.compare_faces(
                    known_encs, enc,
                    tolerance=CONFIG["face_tolerance"]
                )
                distances = face_recognition.face_distance(known_encs, enc)
                if True in matches:
                    best               = int(np.argmin(distances))
                    result["name"]     = known_names[best]
                    result["confidence"] = round(
                        (1 - distances[best]) * 100, 1
                    )
                else:
                    result["name"] = "Unknown"
            return result

        except Exception as e:
            return result


class GestureDetector:
    def __init__(self):
        self.hands = None
        self._init()

    def _init(self):
        try:
            import mediapipe as mp
            self.hands = mp.solutions.hands.Hands(
                static_image_mode        = False,
                max_num_hands            = 1,
                min_detection_confidence = 0.5,
                min_tracking_confidence  = 0.5
            )
            print("[GESTURE] MediaPipe Hands OK")
        except Exception as e:
            print(f"[GESTURE] Init error: {e}")

    def _get_gesture(self, lm, handedness="Right") -> str:
        index_up  = lm[8].y  < lm[6].y
        middle_up = lm[12].y < lm[10].y
        ring_up   = lm[16].y < lm[14].y
        pinky_up  = lm[20].y < lm[18].y

        thumb_tip      = lm[4]
        thumb_ip       = lm[3]
        thumb_mcp      = lm[2]
        thumb_vertical = thumb_tip.y < thumb_mcp.y - 0.05

        if handedness == "Right":
            thumb_up = thumb_tip.x < thumb_ip.x
        else:
            thumb_up = thumb_tip.x > thumb_ip.x

        if not any([index_up, middle_up, ring_up, pinky_up]):
            if thumb_vertical:
                return "thumbs_up"
            return "fist"

        if all([index_up, middle_up, ring_up, pinky_up]):
            return "open_hand"

        if index_up and not middle_up and not ring_up and not pinky_up:
            return "pointing"

        if index_up and middle_up and not ring_up and not pinky_up:
            return "peace"

        if index_up and not middle_up and not ring_up and pinky_up:
            return "rock"

        return None

    def detect(self, frame) -> dict:
        result = {"gesture": None, "confidence": 0.0}
        if not self.hands:
            return result
        try:
            rgb     = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)
            if not results.multi_hand_landmarks:
                return result

            lm          = results.multi_hand_landmarks[0].landmark
            handedness  = "Right"
            if results.multi_handedness:
                handedness = (
                    results.multi_handedness[0]
                    .classification[0].label
                )
            gesture = self._get_gesture(lm, handedness)
            if gesture:
                result["gesture"]    = gesture
                result["confidence"] = 0.8
            return result

        except Exception as e:
            return result

    def kalibrasi(self):
        print("\n[GESTURE] Kalibrasi dimulai...")
        cap = cv2.VideoCapture(CONFIG["camera_index"])
        for _ in range(10):
            cap.read()
            time.sleep(0.05)

        tests = [
            ("thumbs_up", "Acungkan jempol ke atas 👍"),
            ("open_hand", "Buka semua jari 🖐"),
            ("fist",      "Kepalkan tangan ✊"),
            ("peace",     "Tanda peace ✌️"),
            ("pointing",  "Tunjuk telunjuk ☝️"),
        ]

        scores = []
        for name, instruksi in tests:
            print(f"\n  {instruksi}")
            input("  Tekan Enter saat siap...")
            sukses  = 0
            timeout = time.time() + 3
            while time.time() < timeout:
                ret, frame = cap.read()
                if not ret:
                    continue
                result = self.detect(frame)
                if result["gesture"] == name:
                    sukses += 1
                time.sleep(0.05)

            score  = min(sukses / 10 * 100, 100)
            scores.append(score)
            status = "✅" if score >= 50 else "⚠️"
            print(f"  {status} {name}: {score:.0f}%")

        cap.release()
        avg = sum(scores) / len(scores) if scores else 0
        print(f"\n[GESTURE] Akurasi rata-rata: {avg:.0f}%")

        if avg < 30:
            CONFIG["gesture_confidence"] = 0.4
        elif avg < 60:
            CONFIG["gesture_confidence"] = 0.5
        else:
            CONFIG["gesture_confidence"] = 0.7

        print(f"[GESTURE] Threshold: {CONFIG['gesture_confidence']}")
        return avg


class EmotionDetector:
    def detect(self, frame) -> dict:
        result = {"emotion": None, "scores": {}}
        try:
            from deepface import DeepFace
            analysis = DeepFace.analyze(
                frame,
                actions           = ["emotion"],
                enforce_detection = False,
                silent            = True
            )
            result["emotion"] = analysis[0]["dominant_emotion"]
            result["scores"]  = analysis[0]["emotion"]
            return result
        except Exception:
            return result


class ObjectDetector:
    def __init__(self):
        self.model = None
        self._init()

    def _init(self):
        try:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")
            print("[OBJECT] YOLO OK")
        except Exception as e:
            print(f"[OBJECT] Init error: {e}")

    def detect(self, frame) -> list:
        if not self.model:
            return []
        try:
            results  = self.model(frame, verbose=False)
            detected = []
            for r in results:
                for box in r.boxes:
                    label = self.model.names[int(box.cls)]
                    conf  = float(box.conf)
                    if conf >= CONFIG["object_confidence"]:
                        detected.append({
                            "label"     : label,
                            "confidence": round(conf * 100, 1)
                        })
            return detected
        except Exception:
            return []


class VisionTaskTrigger:
    def __init__(self):
        self.last_trigger = {}
        self.cooldown     = 30

    def should_trigger(self, event_type: str) -> bool:
        now  = time.time()
        last = self.last_trigger.get(event_type, 0)
        if now - last > self.cooldown:
            self.last_trigger[event_type] = now
            return True
        return False

    def on_owner_detected(self, name: str, confidence: float):
        if not self.should_trigger(f"face_{name}"):
            return
        print(f"\n[TRIGGER] Pemilik: {name} ({confidence}%)")
        try:
            from main_peter import peter_speak
            hour = time.localtime().tm_hour
            if hour < 12:
                msg = f"Selamat pagi {name}!"
            elif hour < 17:
                msg = f"Halo {name}! Ada yang bisa dibantu?"
            else:
                msg = f"Selamat malam {name}!"
            peter_speak(msg)
        except Exception:
            pass

    def on_unknown_detected(self):
        if not self.should_trigger("unknown"):
            return
        print("\n[TRIGGER] ⚠️ Orang tidak dikenal!")
        try:
            from main_peter import peter_speak
            peter_speak("Perhatian! Ada orang tidak dikenal.")
        except Exception:
            pass

    def on_gesture(self, gesture: str):
        if not self.should_trigger(f"gesture_{gesture}"):
            return
        print(f"\n[TRIGGER] Gesture: {gesture}")
        try:
            from main_peter import peter_speak
            responses = {
                "thumbs_up": "Siap bekerja!",
                "open_hand": "Baik, saya berhenti.",
                "fist"     : "Mode diam.",
                "peace"    : "Hai! Senang melihatmu.",
                "pointing" : "Apa yang ditunjuk?",
            }
            peter_speak(responses.get(gesture, "Gesture terdeteksi."))
        except Exception:
            pass

    def on_emotion(self, emotion: str):
        if not self.should_trigger(f"emotion_{emotion}"):
            return
        try:
            from main_peter import peter_speak
            if emotion == "sad":
                peter_speak(f"Kamu terlihat sedih. Ada yang bisa dibantu?")
            elif emotion == "happy":
                peter_speak(f"Senang melihatmu bahagia!")
        except Exception:
            pass


class PeterVisionAgent:
    def __init__(self):
        print("\n[VISION AGENT] Initializing...")
        self.face    = FaceRecognizer()
        self.gesture = GestureDetector()
        self.emotion = EmotionDetector()
        self.objects = ObjectDetector()
        self.trigger = VisionTaskTrigger()

        self.is_running      = False
        self.last_face_time  = 0
        self.last_gest_time  = 0
        self.last_emot_time  = 0
        self.current_face    = None
        self.current_gesture = None
        self.current_emotion = None
        print("[VISION AGENT] Semua modul siap!")

    def capture_and_analyze(self) -> dict:
        cap = cv2.VideoCapture(CONFIG["camera_index"])
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CONFIG["frame_width"])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CONFIG["frame_height"])

        # Warmup
        for _ in range(5):
            cap.read()

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return {"error": "Kamera tidak tersedia"}

        print("[VISION] Menganalisis...")
        result = {
            "face"   : self.face.identify(frame),
            "gesture": self.gesture.detect(frame),
            "emotion": self.emotion.detect(frame),
            "objects": self.objects.detect(frame),
        }

        cv2.imwrite(
            os.path.join(OUTPUT_DIR, "last_vision.jpg"),
            frame
        )
        return result

    def start_monitor(self,
                      on_face    = None,
                      on_gesture = None,
                      on_emotion = None,
                      show_window: bool = False):
        self.is_running = True

        def _loop():
            cap = cv2.VideoCapture(CONFIG["camera_index"])
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CONFIG["frame_width"])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CONFIG["frame_height"])
            print("[VISION] Monitor aktif...")

            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.5)
                    continue

                now = time.time()

                if now - self.last_face_time > CONFIG["face_interval_sec"]:
                    face = self.face.identify(frame)
                    if face["detected"]:
                        name = face["name"]
                        if name != self.current_face:
                            self.current_face = name
                            if name == USER_NAME:
                                self.trigger.on_owner_detected(
                                    name, face["confidence"]
                                )
                            elif name == "Unknown":
                                self.trigger.on_unknown_detected()
                            if on_face:
                                on_face(face)
                    self.last_face_time = now

                if now - self.last_gest_time > CONFIG["gesture_interval_sec"]:
                    gest = self.gesture.detect(frame)
                    g    = gest.get("gesture")
                    if g and g != self.current_gesture:
                        self.current_gesture = g
                        self.trigger.on_gesture(g)
                        if on_gesture:
                            on_gesture(gest)
                    self.last_gest_time = now

                if now - self.last_emot_time > CONFIG["emotion_interval_sec"]:
                    emot = self.emotion.detect(frame)
                    e    = emot.get("emotion")
                    if e and e != self.current_emotion:
                        self.current_emotion = e
                        self.trigger.on_emotion(e)
                        if on_emotion:
                            on_emotion(emot)
                    self.last_emot_time = now

                if show_window:
                    self._draw_overlay(frame)
                    cv2.imshow("PETER Vision", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                time.sleep(0.05)

            cap.release()
            if show_window:
                cv2.destroyAllWindows()
            print("[VISION] Monitor berhenti.")

        thread = threading.Thread(target=_loop, daemon=True)
        thread.start()
        return thread

    def _draw_overlay(self, frame):
        h, w = frame.shape[:2]
        cv2.rectangle(frame, (0, 0), (w, 35), (0, 0, 0), -1)
        cv2.putText(
            frame, f"PETER Vision | {USER_NAME}",
            (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 255, 0), 2
        )
        y = h - 100
        for label, value in [
            ("Wajah",   self.current_face    or "-"),
            ("Gesture", self.current_gesture or "-"),
            ("Emosi",   self.current_emotion or "-"),
        ]:
            cv2.putText(
                frame, f"{label}: {value}",
                (10, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 0), 2
            )
            y += 30

    def stop_monitor(self):
        self.is_running = False

    def format_result(self, result: dict) -> str:
        parts = []

        face = result.get("face", {})
        if face.get("detected"):
            name = face.get("name", "Unknown")
            conf = face.get("confidence", 0)
            if name == USER_NAME:
                parts.append(f"Saya melihat {name} ({conf}%)")
            elif name == "Unknown":
                parts.append("Ada orang tidak dikenal")
            else:
                parts.append(f"Terdeteksi: {name}")

        gest = result.get("gesture", {})
        g    = gest.get("gesture")
        if g:
            g_map = {
                "thumbs_up": "memberi jempol 👍",
                "open_hand": "tangan terbuka 🖐",
                "fist"     : "mengepal ✊",
                "peace"    : "tanda peace ✌️",
                "pointing" : "menunjuk ☝️",
                "rock"     : "tanda rock 🤘",
            }
            parts.append(g_map.get(g, g))

        emot = result.get("emotion", {})
        e    = emot.get("emotion")
        if e:
            e_map = {
                "happy"   : "terlihat senang 😊",
                "sad"     : "terlihat sedih 😢",
                "angry"   : "terlihat marah 😠",
                "neutral" : "ekspresi normal 😐",
                "surprise": "terlihat terkejut 😲",
            }
            parts.append(e_map.get(e, e))

        objs = result.get("objects", [])
        if objs:
            labels = [
                f"{o['label']} ({o['confidence']}%)"
                for o in objs[:3]
            ]
            parts.append(f"Objek: {', '.join(labels)}")

        return ". ".join(parts) if parts else "Tidak ada yang terdeteksi"


def test_vision_agent():
    print("\n" + "=" * 55)
    print("  PETER Vision Agent — Test")
    print("=" * 55)

    agent = PeterVisionAgent()

    while True:
        print("\n" + "-" * 40)
        print("  [1] Analisis kamera sekarang")
        print("  [2] Kalibrasi gesture")
        print("  [3] Daftarkan wajah baru")
        print("  [4] Monitor real-time (dengan window)")
        print("  [5] Monitor background")
        print("  [6] Test security layer")
        print("  [7] Keluar")
        print("-" * 40)

        pilihan = input("\nPilih (1-7): ").strip()

        if pilihan == "1":
            result  = agent.capture_and_analyze()
            laporan = agent.format_result(result)
            print(f"\n[PETER] {laporan}")

            face = result.get("face", {})
            if face.get("detected"):
                print(f"\n  Wajah      : {face.get('name')}")
                print(f"  Keyakinan  : {face.get('confidence')}%")

            gest = result.get("gesture", {})
            if gest.get("gesture"):
                print(f"  Gesture    : {gest['gesture']}")

            emot = result.get("emotion", {})
            if emot.get("emotion"):
                print(f"  Emosi      : {emot['emotion']}")

            objs = result.get("objects", [])
            if objs:
                print(f"  Objek      : {[o['label'] for o in objs]}")

        elif pilihan == "2":
            score = agent.gesture.kalibrasi()
            print(f"\nKalibrasi selesai! Akurasi: {score:.0f}%")

        elif pilihan == "3":
            nama = input("\nNama: ").strip()
            if nama:
                ok = agent.face.register(nama, num_photos=5)
                print(f"{'✅ Berhasil' if ok else '❌ Gagal'}!")

        elif pilihan == "4":
            print("\nTekan 'q' di window untuk berhenti")
            def on_face(f):
                print(f"[LIVE] Wajah: {f['name']} ({f['confidence']}%)")
            def on_gesture(g):
                print(f"[LIVE] Gesture: {g['gesture']}")
            def on_emotion(e):
                print(f"[LIVE] Emosi: {e['emotion']}")
            t = agent.start_monitor(
                on_face=on_face, on_gesture=on_gesture,
                on_emotion=on_emotion, show_window=True
            )
            t.join()

        elif pilihan == "5":
            print("\nMonitor background aktif. Enter untuk berhenti.")
            agent.start_monitor(show_window=False)
            input()
            agent.stop_monitor()

        elif pilihan == "6":
            result = agent.capture_and_analyze()
            face   = result.get("face", {})
            if face.get("name") == USER_NAME:
                print(f"✅ AKSES DITERIMA: {USER_NAME} ({face['confidence']}%)")
            elif face.get("detected"):
                print(f"❌ AKSES DITOLAK: {face.get('name', 'Unknown')}")
            else:
                print("⚠️ Tidak ada wajah terdeteksi")

        elif pilihan == "7":
            print("\n[VISION AGENT] Keluar.")
            break


if __name__ == "__main__":
    test_vision_agent()
