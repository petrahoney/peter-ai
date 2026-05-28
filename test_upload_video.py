import sys
import os
sys.path.append("C:\\peter-ai")

from content.video_editor import photo_to_video
from content.thumbnail_agent import generate_thumbnail
from publishers.youtube_pub import upload_youtube

print("=" * 50)
print("  PETER — Test Upload YouTube")
print("=" * 50)

# Step 1: Buat video test dari foto
print("\nStep 1: Buat video test...")

# Cek apakah ada foto di outputs
foto = None
outputs = "C:\\peter-ai\\data\\outputs"
for f in os.listdir(outputs):
    if f.endswith(('.jpg', '.png', '.jpeg')):
        foto = os.path.join(outputs, f)
        break

if not foto:
    # Buat foto test sederhana dengan PIL
    from PIL import Image, ImageDraw
    img  = Image.new('RGB', (1920, 1080), (30, 30, 60))
    draw = ImageDraw.Draw(img)
    draw.text((400, 400), "PETER AI Test Video", fill=(255, 255, 0))
    foto = os.path.join(outputs, "test_photo.jpg")
    img.save(foto)
    print(f"Foto test dibuat: {foto}")
else:
    print(f"Pakai foto: {foto}")

# Step 2: Convert foto ke video
print("\nStep 2: Convert foto ke video...")
video_path = photo_to_video(
    photo_path  = foto,
    duration    = 10,
    output_name = "peter_test_video.mp4",
    effect      = "zoom"
)
print(f"Video dibuat: {video_path}")

if "Error" in str(video_path):
    print("Video gagal dibuat!")
    sys.exit(1)

# Step 3: Generate thumbnail
print("\nStep 3: Generate thumbnail...")
thumb = generate_thumbnail(
    title       = "PETER AI — Test Video Pertama",
    output_name = "peter_test_thumb.png"
)
print(f"Thumbnail dibuat: {thumb}")

# Step 4: Upload ke YouTube
print("\nStep 4: Upload ke YouTube...")
konfirmasi = input("Upload video test ke YouTube? (y/n): ")

if konfirmasi.lower() == 'y':
    result = upload_youtube(
        video_path  = video_path,
        title       = "PETER AI Test — Ignore This Video",
        description = """Video test dari PETER AI System.
Sistem AI personal untuk otomasi konten YouTube.

Ini adalah video test — bisa dihapus setelah upload berhasil.""",
        tags        = ["peter ai", "test", "ai automation"],
        privacy     = "unlisted"  # Private/unlisted dulu untuk test
    )

    if result.get("success"):
        print(f"\nUpload BERHASIL!")
        print(f"URL    : {result['url']}")
        print(f"Video ID: {result['video_id']}")
        print("\nCek di YouTube Studio kamu!")
    else:
        print(f"\nUpload gagal: {result.get('error')}")
else:
    print("Upload dibatalkan.")

print("\nTest selesai!")