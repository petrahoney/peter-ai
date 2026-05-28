import sys
import os
sys.path.append("C:\\peter-ai")

from content.pipeline import ContentPipeline

print("=" * 60)
print("  PETER — Test Content Pipeline")
print("=" * 60)

pipeline = ContentPipeline()

# Pakai foto spesifik
foto = "C:\\peter-ai\\data\\outputs\\ai_photo.jpg"

# Jika tidak ada pakai yang tersedia
if not os.path.exists(foto):
    for f in os.listdir("C:\\peter-ai\\data\\outputs"):
        if f.endswith(('.jpg', '.png', '.jpeg')):
            foto = f"C:\\peter-ai\\data\\outputs\\{f}"
            break
if not foto:
    from PIL import Image, ImageDraw
    img  = Image.new('RGB', (1920, 1080), (20, 20, 60))
    draw = ImageDraw.Draw(img)
    draw.text((500, 500), "PETER AI Content", fill=(255, 255, 0))
    foto = "C:\\peter-ai\\data\\outputs\\test_input.jpg"
    img.save(foto)
    print(f"Foto test dibuat: {foto}")

prompt = "Cara Install dan Pakai AI di PC Sendiri untuk Pemula Indonesia 2026"
print(f"\nPrompt: {prompt}")
print("\nMemulai pipeline...")

result = pipeline.run(
    photo_path = foto,
    prompt     = prompt,
    platforms  = ["youtube"],
    privacy    = "unlisted"
)

print("\nPipeline selesai!")
print(f"Berhasil : {result['success']}")
print(f"Gagal    : {result['failed']}")
if result.get('urls'):
    for p, url in result['urls'].items():
        print(f"{p}: {url}")