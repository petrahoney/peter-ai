"""
test_video_editor.py
Test video editor versi final
"""
import os
import sys
sys.path.append("C:\\peter-ai")

from content.video_editor import (
    create_slideshow,
    add_audio_to_video,
    add_intro_slide,
    convert_to_portrait,
    get_font_path
)

OUTPUT = "C:\\peter-ai\\data\\outputs"

print("=" * 50)
print("  Test Video Editor PETER Final")
print("=" * 50)
print(f"Font: {get_font_path()}")

# Cari foto yang ada
photos = []
for f in os.listdir(OUTPUT):
    if f.endswith(('.jpg', '.png', '.jpeg')):
        path = os.path.join(OUTPUT, f)
        if os.path.getsize(path) > 5000:
            photos.append(path)

print(f"\nFoto ditemukan: {len(photos)}")
for p in photos[:5]:
    print(f"  - {os.path.basename(p)}")

if not photos:
    print("ERROR: Tidak ada foto!")
    sys.exit(1)

# Test 1 — Slideshow dengan teks
print("\n[TEST 1] Buat slideshow dengan teks judul...")
result = create_slideshow(
    photo_list         = photos[:3],
    duration_per_photo = 5,
    output_name        = "test_slideshow.mp4",
    title              = "Cara Menghasilkan Uang dari AI 2026"
)
print(f"Hasil: {result}")
if os.path.exists(result):
    size = os.path.getsize(result)
    print(f"Size: {size:,} bytes — {'OK!' if size > 100000 else 'WARNING kecil!'}")

# Test 2 — Tambah intro/outro
print("\n[TEST 2] Tambah intro dan outro...")
result2 = add_intro_slide(
    video_path   = result,
    channel_name = "PETER AI",
    output_name  = "test_with_intro.mp4"
)
print(f"Hasil: {result2}")
if os.path.exists(result2):
    size2 = os.path.getsize(result2)
    print(f"Size: {size2:,} bytes — {'OK!' if size2 > 100000 else 'WARNING!'}")

# Test 3 — Cek durasi
print("\n[TEST 3] Cek durasi video...")
import subprocess
for vid in ["test_slideshow.mp4", "test_with_intro.mp4"]:
    path = os.path.join(OUTPUT, vid)
    if os.path.exists(path):
        r = subprocess.run(
            ['ffprobe', '-v', 'error',
             '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1',
             path],
            capture_output=True, text=True
        )
        dur = r.stdout.strip()
        print(f"  {vid}: {dur} detik")

# Test 4 — Buka video hasil
print("\n[TEST 4] Buka video untuk cek visual...")
final = os.path.join(OUTPUT, "test_with_intro.mp4")
if os.path.exists(final):
    os.startfile(final)
    print("Video dibuka — cek apakah:")
    print("  ✓ Slideshow berganti antar foto")
    print("  ✓ Teks judul muncul di setiap slide")
    print("  ✓ Intro PETER AI muncul di awal")
    print("  ✓ Outro Terima Kasih muncul di akhir")

print("\nTest selesai!")