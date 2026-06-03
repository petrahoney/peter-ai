import os
import sys
sys.path.append("C:\\peter-ai")

from PIL import Image, ImageDraw
import cv2

INPUT  = "C:\\peter-ai\\data\\presenter_saya.jpg"
OUTPUT = "C:\\peter-ai\\data\\presenter_saya_crop.jpg"

print(f"Memproses: {INPUT}")

if not os.path.exists(INPUT):
    print(f"File tidak ditemukan: {INPUT}")
    sys.exit(1)

# Load dengan OpenCV untuk deteksi wajah
img_cv   = cv2.imread(INPUT)
gray     = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)
faces = detector.detectMultiScale(
    gray, scaleFactor=1.1,
    minNeighbors=5, minSize=(80, 80)
)

img_pil = Image.open(INPUT).convert("RGB")
W, H    = img_pil.size
print(f"Ukuran asli: {W}x{H}")

if len(faces) == 0:
    print("Wajah tidak terdeteksi — crop manual ke tengah")
    target_w = min(W, H * 4 // 5)
    target_h = min(H, W * 5 // 4)
    left     = (W - target_w) // 2
    top      = max(0, (H - target_h) // 2 - H // 10)
    right    = left + target_w
    bottom   = top  + target_h
    cropped  = img_pil.crop([left, top, right, bottom])
else:
    print(f"Wajah terdeteksi: {len(faces)}")
    x, y, fw, fh = max(faces, key=lambda f: f[2]*f[3])
    pad_x   = int(fw * 1.2)
    pad_top = int(fh * 0.8)
    pad_bot = int(fh * 2.5)
    left    = max(0, x - pad_x)
    top     = max(0, y - pad_top)
    right   = min(W, x + fw + pad_x)
    bottom  = min(H, y + fh + pad_bot)
    cropped = img_pil.crop([left, top, right, bottom])
    print(f"Crop: {left},{top} → {right},{bottom}")

# Resize ke 512x640 optimal D-ID
final = cropped.resize((512, 640), Image.LANCZOS)
final.save(OUTPUT, "JPEG", quality=95)
size  = os.path.getsize(OUTPUT)
print(f"\nHasil: {OUTPUT}")
print(f"Size : {size:,} bytes")
print(f"Dim  : {final.size}")

# Preview
final.show()

# Update .env
env_path = "C:\\peter-ai\\.env"
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        content = f.read()
    if "PRESENTER_IMAGE=" in content:
        lines   = content.split("\n")
        lines   = [
            f"PRESENTER_IMAGE={OUTPUT}"
            if l.startswith("PRESENTER_IMAGE=") else l
            for l in lines
        ]
        content = "\n".join(lines)
    else:
        content += f"\nPRESENTER_IMAGE={OUTPUT}"
    with open(env_path, "w") as f:
        f.write(content)
    print(f"\n.env diupdate: PRESENTER_IMAGE={OUTPUT}")

print("\nSekarang jalankan:")
print("  python make_pro_video.py")
print("  Pilih [2] untuk avatar presenter!")