import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

import os
import sys
import time
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

OUTPUT = "C:\\peter-ai\\data\\outputs"

print("=" * 60)
print("  PETER Pro Video Pipeline")
print("  D-ID Avatar + Runway B-Roll + ElevenLabs Voice")
print("=" * 60)

TOPIC = "Cara menghasilkan uang dari AI di Indonesia 2026"

# ── STEP 1: SCRIPT ────────────────────────────────────────
print("\n[STEP 1] Generate Script...")
from content.script_writer import write_script
script_result = write_script(
    topic           = TOPIC,
    duration        = "5 menit",
    style           = "informatif engaging viral",
    target_audience = "pemula Indonesia"
)

# Ambil script — coba semua kemungkinan key
script = (
    script_result.get("script", "") or
    script_result.get("raw", "") or
    ""
)

# Jika script masih ada prefix --- bersihkan
if script.startswith("---"):
    lines  = script.split("\n")
    lines  = [l for l in lines if not l.strip().startswith("---")]
    script = "\n".join(lines).strip()

titles = script_result.get("title_options", [])
print(f"Script: {len(script)} karakter")
print(f"Judul : {titles[0] if titles else TOPIC}")

if len(script) < 100:
    print("Script terlalu pendek! Gunakan raw output...")
    script = script_result.get("raw", TOPIC * 10)

# ── STEP 2: VOICEOVER ─────────────────────────────────────
print("\n[STEP 2] Generate Voiceover...")
from peter_tts import generate_voiceover
audio = generate_voiceover(
    script      = script,
    output_name = "pro_voiceover.mp3",
    max_words   = 250
)
if audio and os.path.exists(audio):
    size = os.path.getsize(audio)
    print(f"Audio OK: {size:,} bytes")
else:
    print("Audio gagal!")
    sys.exit(1)

# ── STEP 3: D-ID AVATAR ───────────────────────────────────
print("\n[STEP 3] Generate D-ID Avatar Presenter...")
from content.pro_video_engine import DIDPresenter
did          = DIDPresenter()
avatar_video = did.create_talking_avatar(
    audio_path  = audio,
    output_name = "pro_avatar.mp4"
)

if avatar_video and os.path.exists(avatar_video):
    size = os.path.getsize(avatar_video)
    print(f"Avatar OK: {size:,} bytes")
else:
    print("Avatar gagal — lanjut tanpa avatar")
    avatar_video = None

# ── STEP 4: RUNWAY B-ROLL ─────────────────────────────────
print("\n[STEP 4] Generate Runway B-Roll...")
from content.pro_video_engine import (
    RunwayBRoll,
    generate_broll_prompts
)

runway  = RunwayBRoll()
prompts = generate_broll_prompts(
    script    = script,
    topic     = TOPIC,
    num_clips = 4
)

print(f"Prompts: {len(prompts)} scenes")
broll_videos = runway.generate_multiple_clips(
    prompts       = prompts,
    duration_each = 5
)
print(f"B-Roll OK: {len(broll_videos)} clips")

# ── STEP 5: COMPOSITE ─────────────────────────────────────
print("\n[STEP 5] Compositing Video Final...")
from content.pro_video_engine import VideoCompositor
compositor = VideoCompositor()

final = compositor.compose(
    avatar_video = avatar_video,
    broll_videos = broll_videos,
    audio_path   = audio,
    script       = script,
    output_name  = "pro_final.mp4"
)

# ── STEP 6: PORTRAIT VERSION ──────────────────────────────
if final and os.path.exists(final):
    print("\n[STEP 6] Buat Portrait Version...")
    from content.video_editor import convert_to_portrait
    portrait = convert_to_portrait(
        video_path  = final,
        output_name = "pro_portrait.mp4"
    )
    print(f"Portrait OK: {portrait}")

# ── HASIL ─────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  HASIL PRO VIDEO PIPELINE")
print("=" * 60)

files = {
    "Avatar"   : "pro_avatar.mp4",
    "B-Roll"   : f"broll_000.mp4",
    "Final"    : "pro_final.mp4",
    "Portrait" : "pro_portrait.mp4",
    "Audio"    : "pro_voiceover.mp3",
}

for name, fname in files.items():
    path = os.path.join(OUTPUT, fname)
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  ✅ {name:10}: {fname} ({size:,} bytes)")
    else:
        print(f"  ❌ {name:10}: tidak ada")

print("=" * 60)

# Buka video final
final_path = os.path.join(OUTPUT, "pro_final.mp4")
if os.path.exists(final_path):
    print("\nMembuka video final...")
    os.startfile(final_path)
    print("✅ Pipeline selesai!")
else:
    print("\n❌ Video final tidak terbuat!")

# ── OPTIONAL: UPLOAD YOUTUBE ──────────────────────────────
upload = input("\nUpload ke YouTube? (y/n): ").strip().lower()
if upload == 'y':
    try:
        from publishers.youtube_pub import upload_youtube
        title = titles[0] if titles else TOPIC
        yt    = upload_youtube(
            video_path  = final_path,
            title       = title,
            description = script_result.get("description", TOPIC),
            tags        = script_result.get("tags", []),
            privacy     = "unlisted"
        )
        if yt.get("success"):
            print(f"\n✅ YouTube: {yt['url']}")
        else:
            print(f"\n❌ Upload gagal: {yt.get('error')}")
    except Exception as e:
        print(f"Upload error: {e}")

print("\nSelesai!")