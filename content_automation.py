"""
content_automation.py
PETER Content Automation — Full Pipeline
Script Writer → Voice → Video → Upload YouTube
100% otomatis tanpa intervensi manual
"""

import os
import sys
import time
import schedule
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

USER_NAME = os.getenv("USER_NAME", "Sir")
OUTPUT_DIR = "C:\\peter-ai\\data\\outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Topik konten otomatis ─────────────────────────────────
CONTENT_TOPICS = [
    "Cara menghasilkan uang dari AI di Indonesia 2026",
    "Tool AI gratis terbaik untuk content creator Indonesia",
    "Tutorial ChatGPT untuk bisnis online pemula",
    "Cara buat konten viral dengan AI tanpa skill desain",
    "Passive income dari YouTube dengan bantuan AI",
    "Review tool AI terbaik minggu ini untuk kreator",
    "Cara otomasi bisnis online dengan AI 2026",
    "5 cara AI mengubah cara kerja orang Indonesia",
    "Dari nol ke 1000 subscriber YouTube dengan AI",
    "Cara pakai Midjourney untuk bisnis di Indonesia",
    "AI untuk UMKM Indonesia — panduan lengkap",
    "Cara buat thumbnail YouTube viral dengan AI gratis",
    "Tutorial Whisper AI untuk subtitle otomatis",
    "Strategi konten TikTok dengan bantuan AI 2026",
    "Cara monetisasi blog dengan AI writing tools",
]

topic_index = 0


def run_full_pipeline(topic: str,
                      photo_path: str = None,
                      privacy: str = "unlisted",
                      platforms: list = None) -> dict:
    """
    Jalankan pipeline konten penuh:
    Topic → Script → Voice → Video → Upload
    """
    if platforms is None:
        platforms = ["youtube"]

    print("\n" + "=" * 60)
    print("  PETER CONTENT AUTOMATION")
    print("=" * 60)
    print(f"  Topik    : {topic}")
    print(f"  Platform : {', '.join(platforms)}")
    print(f"  Privacy  : {privacy}")
    print("=" * 60)

    start_time = time.time()
    result     = {
        "topic"   : topic,
        "success" : False,
        "urls"    : {},
        "files"   : [],
        "errors"  : []
    }

    # Cari foto jika tidak disediakan
    if not photo_path or not os.path.exists(photo_path):
        photo_path = _find_best_photo()

    print(f"\n[AUTO] Foto: {os.path.basename(photo_path) if photo_path else 'Tidak ada'}")

    # Jalankan pipeline
    try:
        from content.pipeline import ContentPipeline
        pipeline  = ContentPipeline()
        pipe_result = pipeline.run(
            photo_path = photo_path or _create_default_photo(topic),
            prompt     = topic,
            platforms  = platforms,
            privacy    = privacy
        )

        result["success"] = bool(pipe_result.get("success"))
        result["urls"]    = pipe_result.get("urls", {})
        result["files"]   = pipe_result.get("thumbnails", [])

        elapsed = time.time() - start_time
        print(f"\n[AUTO] Total waktu: {elapsed:.0f} detik")

        # Log hasil
        _log_result(topic, result)

    except Exception as e:
        print(f"\n[AUTO] Pipeline error: {e}")
        result["errors"].append(str(e))
        import traceback
        traceback.print_exc()

    return result


def _find_best_photo() -> str:
    """Cari foto terbaik dari folder outputs"""
    import glob

    # Prioritas: foto dari Unsplash (bukan grafik)
    all_photos = []
    for ext in ['*.jpg', '*.jpeg']:
        all_photos.extend(
            glob.glob(os.path.join(OUTPUT_DIR, ext))
        )

    # Filter foto yang bukan grafik/chart
    good_photos = [
        p for p in all_photos
        if not any(
            x in os.path.basename(p).lower()
            for x in ['grafik', 'chart', 'thumb',
                       'test', 'titled', 'slide']
        )
        and os.path.getsize(p) > 50000
    ]

    if good_photos:
        # Pakai foto terbaru
        return max(good_photos, key=os.path.getmtime)

    # Fallback ke semua foto
    if all_photos:
        return max(all_photos, key=os.path.getmtime)

    return None


def _create_default_photo(topic: str) -> str:
    """Buat foto default jika tidak ada foto"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import textwrap

        img  = Image.new('RGB', (1920, 1080), (15, 15, 40))
        draw = ImageDraw.Draw(img)

        # Gradient background
        for y in range(1080):
            ratio = y / 1080
            r = int(15  + (30  - 15)  * ratio)
            g = int(15  + (25  - 15)  * ratio)
            b = int(40  + (80  - 40)  * ratio)
            draw.line([(0, y), (1920, y)], fill=(r, g, b))

        # Teks topik
        try:
            font = ImageFont.truetype(
                "C:/Windows/Fonts/arialbd.ttf", 72
            )
            font_sub = ImageFont.truetype(
                "C:/Windows/Fonts/arial.ttf", 40
            )
        except Exception:
            font     = ImageFont.load_default()
            font_sub = font

        # Wrap dan tampilkan teks
        lines = textwrap.wrap(topic, width=30)
        y     = 400
        for line in lines[:3]:
            bbox = draw.textbbox((0, 0), line, font=font)
            w    = bbox[2] - bbox[0]
            x    = (1920 - w) // 2
            draw.text((x+3, y+3), line, font=font,
                      fill=(0, 0, 0, 128))
            draw.text((x, y), line, font=font,
                      fill=(255, 220, 50))
            y += 90

        # Watermark PETER AI
        draw.text((10, 1040), "PETER AI",
                  font=font_sub, fill=(100, 100, 150))

        path = os.path.join(OUTPUT_DIR, "auto_default_photo.jpg")
        img.save(path, "JPEG", quality=95)
        print(f"[AUTO] Default photo dibuat: {path}")
        return path

    except Exception as e:
        print(f"[AUTO] Default photo error: {e}")
        return None


def _log_result(topic: str, result: dict):
    """Log hasil ke file"""
    log_dir  = "C:\\peter-ai\\data\\logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "content_automation_log.txt")

    with open(log_file, "a", encoding="utf-8") as f:
        from datetime import datetime
        f.write(f"\n{'='*50}\n")
        f.write(f"Waktu   : {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Topik   : {topic}\n")
        f.write(f"Status  : {'✅ Berhasil' if result['success'] else '❌ Gagal'}\n")
        for p, url in result.get("urls", {}).items():
            f.write(f"{p.upper():12}: {url}\n")
        if result.get("errors"):
            f.write(f"Errors  : {result['errors']}\n")

    print(f"[AUTO] Log: {log_file}")


def run_daily_automation():
    """Produksi konten harian otomatis"""
    global topic_index

    print(f"\n[SCHEDULER] Memulai produksi harian...")
    print(f"[SCHEDULER] {time.strftime('%Y-%m-%d %H:%M:%S')}")

    topic = CONTENT_TOPICS[topic_index % len(CONTENT_TOPICS)]
    topic_index += 1

    print(f"[SCHEDULER] Topik hari ini: {topic}")

    result = run_full_pipeline(
        topic     = topic,
        privacy   = "public",
        platforms = ["youtube"]
    )

    if result["success"]:
        print(f"\n[SCHEDULER] ✅ Konten berhasil dipublish!")
        for p, url in result["urls"].items():
            print(f"[SCHEDULER] {p}: {url}")
    else:
        print(f"\n[SCHEDULER] ❌ Gagal: {result['errors']}")


def start_scheduler(jam: str = "09:00"):
    """Jalankan scheduler harian"""
    print("\n" + "=" * 60)
    print("  PETER Content Automation Scheduler")
    print("=" * 60)
    print(f"  Jadwal  : Setiap hari jam {jam}")
    print(f"  Topik   : {len(CONTENT_TOPICS)} topik tersedia")
    print(f"  Platform: YouTube")
    print("\nTekan Ctrl+C untuk berhenti\n")

    schedule.every().day.at(jam).do(run_daily_automation)
    print(f"[SCHEDULER] Menunggu jadwal {jam}...")
    print("[SCHEDULER] Ketik 'test' untuk test sekarang\n")

    while True:
        try:
            schedule.run_pending()
            time.sleep(30)
            print(".", end="", flush=True)
        except KeyboardInterrupt:
            print("\n[SCHEDULER] Berhenti.")
            break


def run_automation_menu():
    """Menu interaktif Content Automation"""
    print("\n" + "=" * 60)
    print("  PETER Content Automation")
    print("=" * 60)

    while True:
        print("\n  [1] Jalankan pipeline sekarang (manual)")
        print("  [2] Jalankan dengan topik custom")
        print("  [3] Start scheduler harian otomatis")
        print("  [4] Lihat log hasil")
        print("  [5] Edit daftar topik")
        print("  [6] Kembali")
        print("-" * 40)

        pilihan = input(
            f"\n[{USER_NAME}] Pilih (1-6): "
        ).strip()

        if pilihan == "1":
            # Pilih topik dari daftar
            print(f"\nDaftar topik ({len(CONTENT_TOPICS)}):")
            for i, t in enumerate(CONTENT_TOPICS[:10], 1):
                print(f"  {i}. {t}")

            idx = input(
                "\nPilih nomor topik (Enter = acak): "
            ).strip()

            if idx.isdigit():
                topic = CONTENT_TOPICS[
                    (int(idx) - 1) % len(CONTENT_TOPICS)
                ]
            else:
                import random
                topic = random.choice(CONTENT_TOPICS)

            privacy = input(
                "Privacy (public/unlisted, default: unlisted): "
            ).strip() or "unlisted"

            result = run_full_pipeline(
                topic   = topic,
                privacy = privacy
            )

            if result["success"]:
                print(f"\n✅ Berhasil!")
                for p, url in result["urls"].items():
                    print(f"  {p}: {url}")
            else:
                print(f"\n❌ Gagal: {result['errors']}")

        elif pilihan == "2":
            topic = input("\nTopik custom: ").strip()
            if not topic:
                continue

            photo = input(
                "Path foto (Enter = auto): "
            ).strip() or None

            privacy = input(
                "Privacy (public/unlisted): "
            ).strip() or "unlisted"

            result = run_full_pipeline(
                topic      = topic,
                photo_path = photo,
                privacy    = privacy
            )

            if result["success"]:
                print(f"\n✅ Berhasil!")
                for p, url in result["urls"].items():
                    print(f"  {p}: {url}")

        elif pilihan == "3":
            jam = input(
                "Jam berapa? (default: 09:00): "
            ).strip() or "09:00"
            start_scheduler(jam)

        elif pilihan == "4":
            log_file = "C:\\peter-ai\\data\\logs\\content_automation_log.txt"
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    content = f.read()
                # Tampilkan 20 baris terakhir
                lines = content.split("\n")
                print("\n--- Log terbaru ---")
                print("\n".join(lines[-30:]))
            else:
                print("\nBelum ada log.")

        elif pilihan == "5":
            print("\nDaftar topik saat ini:")
            for i, t in enumerate(CONTENT_TOPICS, 1):
                print(f"  {i}. {t}")
            print("\nEdit CONTENT_TOPICS di file content_automation.py")
            print("Tambah topik sesuai niche channel kamu!")

        elif pilihan == "6":
            break


if __name__ == "__main__":
    run_automation_menu()