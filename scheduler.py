"""
scheduler.py
PETER Scheduler — Produksi konten otomatis setiap hari
"""

import schedule
import time
import os
import sys
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

from content.pipeline import ContentPipeline


# Topik konten yang akan diproduksi otomatis
DAILY_TOPICS = [
    "Cara menghasilkan uang dari AI di Indonesia 2026",
    "Tool AI terbaik untuk content creator Indonesia",
    "Tutorial ChatGPT untuk bisnis online pemula",
    "Cara buat konten viral dengan AI tanpa skill desain",
    "Passive income dari YouTube dengan bantuan AI",
    "Review tool AI gratis terbaik minggu ini",
    "Cara otomasi bisnis online dengan AI 2026",
]

topic_index = 0


def daily_content():
    """Produksi konten harian otomatis"""
    global topic_index

    print(f"\n[SCHEDULER] Memulai produksi konten harian...")
    print(f"[SCHEDULER] Waktu: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Pilih topik hari ini
    topic = DAILY_TOPICS[topic_index % len(DAILY_TOPICS)]
    topic_index += 1

    print(f"[SCHEDULER] Topik: {topic}")

    # Cari foto terbaru
    outputs = "C:\\peter-ai\\data\\outputs"
    foto    = None
    for f in sorted(os.listdir(outputs), reverse=True):
        if f.endswith(('.jpg', '.png', '.jpeg')):
            foto = os.path.join(outputs, f)
            break

    if not foto:
        # Buat foto default
        try:
            from PIL import Image, ImageDraw
            img  = Image.new('RGB', (1920, 1080), (20, 20, 60))
            draw = ImageDraw.Draw(img)
            draw.text((500, 500), "PETER AI Content", fill=(255, 255, 0))
            foto = os.path.join(outputs, "daily_default.jpg")
            img.save(foto)
        except Exception as e:
            print(f"[SCHEDULER] Error buat foto: {e}")
            return

    # Jalankan pipeline
    try:
        pipeline = ContentPipeline()
        result   = pipeline.run(
            photo_path = foto,
            prompt     = topic,
            platforms  = ["youtube"],
            privacy    = "public"  # Public untuk konten harian
        )

        if result["success"]:
            print(f"[SCHEDULER] Berhasil upload ke: {result['success']}")
            for p, url in result["urls"].items():
                print(f"[SCHEDULER] {p}: {url}")

            # Log hasil
            log_file = "C:\\peter-ai\\data\\logs\\scheduler_log.txt"
            os.makedirs("C:\\peter-ai\\data\\logs", exist_ok=True)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n{time.strftime('%Y-%m-%d %H:%M')}\n")
                f.write(f"Topic: {topic}\n")
                for p, url in result["urls"].items():
                    f.write(f"{p}: {url}\n")
        else:
            print(f"[SCHEDULER] Gagal: {result['failed']}")

    except Exception as e:
        print(f"[SCHEDULER] Error: {e}")


def run_scheduler():
    """Jalankan scheduler"""
    print("=" * 60)
    print("  PETER Scheduler Aktif")
    print("=" * 60)
    print(f"  Jadwal : Setiap hari jam 09:00")
    print(f"  Topik  : {len(DAILY_TOPICS)} topik tersedia")
    print(f"  Status : Berjalan...")
    print("\nTekan Ctrl+C untuk berhenti\n")

    # Jadwal harian jam 9 pagi
    schedule.every().day.at("09:00").do(daily_content)

    # Untuk test — jalankan setiap 1 jam
    # schedule.every(1).hours.do(daily_content)

    # Test langsung saat start
    test = input("Test pipeline sekarang? (y/n): ").strip().lower()
    if test == 'y':
        daily_content()

    while True:
        schedule.run_pending()
        time.sleep(60)
        print(".", end="", flush=True)


if __name__ == "__main__":
    pip_check = os.system("python -c \"import schedule\" 2>nul")
    if pip_check != 0:
        os.system("pip install schedule")
    run_scheduler()