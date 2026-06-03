import sys
sys.path.append("C:\\peter-ai")
from dotenv import load_dotenv
load_dotenv()
import os, glob

OUTPUT = "C:\\peter-ai\\data\\outputs"

# Ambil judul dari script
title = "Cara Menghasilkan Uang dari AI di Indonesia 2026"
import re
scripts = glob.glob(f"{OUTPUT}\\script_*.txt")
if scripts:
    with open(scripts[-1], "r", encoding="utf-8") as f:
        for line in f.read().split("\n"):
            line = re.sub(
                r'^(Topic|TOPIC|Topik|TITLE|Title)[\s:]+',
                '', line.strip()
            ).lstrip("0123456789. *\"'").strip()
            if 20 < len(line) < 90:
                title = line
                break

print(f"Judul: {title}")

from publishers.youtube_pub import upload_youtube
yt = upload_youtube(
    video_path  = f"{OUTPUT}\\pro_final_new.mp4",
    title       = title,
    description = f"""{title}

Di video ini kita bahas cara nyata menghasilkan uang dari AI di Indonesia 2026.
Cocok untuk pemula yang ingin mulai dari nol.

00:00 Intro
00:30 Pembahasan Utama
02:00 Tips Penting
02:20 Outro

Subscribe untuk konten AI terbaik setiap hari!

#AI #Indonesia #PenghasilanOnline #teknologi #2026 #PETERAI""",
    tags        = [
        "AI Indonesia", "cara menghasilkan uang dari AI",
        "teknologi AI 2026", "passive income Indonesia",
        "tutorial AI pemula", "ChatGPT Indonesia",
        "bisnis online AI", "PETER AI", "konten otomatis"
    ],
    privacy     = "public"
)

if yt.get("success"):
    print(f"\n✅ YouTube: {yt['url']}")
else:
    print(f"\n❌ Gagal: {yt.get('error')}")