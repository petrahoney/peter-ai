import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)
import os, sys, subprocess, shutil, re, textwrap
sys.path.append("C:\\peter-ai")
from dotenv import load_dotenv
load_dotenv()

OUTPUT = "C:/peter-ai/data/outputs"
os.makedirs(OUTPUT, exist_ok=True)


def run_ff(cmd: str) -> bool:
    r = subprocess.run(cmd, shell=True, capture_output=True)
    return r.returncode == 0


def find_font() -> str:
    for f in [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/tahoma.ttf",
    ]:
        if os.path.exists(f):
            return f
    return None


def get_video_info(path: str) -> tuple:
    r = subprocess.run(
        ['ffprobe', '-v', 'error',
         '-select_streams', 'v:0',
         '-show_entries', 'stream=width,height,r_frame_rate',
         '-of', 'default=noprint_wrappers=1', path],
        capture_output=True, text=True
    )
    w, h, fps = 1280, 720, 24
    for line in r.stdout.split('\n'):
        if 'width=' in line:
            try: w = int(line.split('=')[1])
            except: pass
        elif 'height=' in line:
            try: h = int(line.split('=')[1])
            except: pass
        elif 'r_frame_rate=' in line:
            val = line.split('=')[1].strip()
            if '/' in val:
                try:
                    a, b = val.split('/')
                    fps  = round(int(a) / int(b))
                except: pass
    return w, h, fps


def add_branding(video_path: str, output_path: str) -> bool:
    from PIL import Image, ImageDraw, ImageFont
    font_path = find_font()
    try:
        font = ImageFont.truetype(font_path, 28) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    wm_path = f"{OUTPUT}/_wm.png"
    try:
        wm   = Image.new("RGBA", (180, 44), (0, 0, 0, 0))
        draw = ImageDraw.Draw(wm)
        draw.rectangle([0, 0, 179, 43], fill=(0, 0, 0, 120))
        draw.text((10, 6), "PETER AI", font=font, fill=(255, 255, 255, 220))
        wm.save(wm_path, "PNG")
    except Exception as e:
        print(f"    Watermark error: {e}")
        return False

    ok = run_ff(
        f'ffmpeg -y '
        f'-i "{video_path}" '
        f'-i "{wm_path}" '
        f'-filter_complex "overlay=20:20" '
        f'-c:a copy '
        f'"{output_path}"'
    )
    if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
        return True
    return False


def add_subtitle_timed(video_path: str,
                       sentences: list,
                       timings: list,
                       dur: int,
                       output_path: str) -> bool:
    from PIL import Image, ImageDraw, ImageFont

    font_path = find_font()
    try:
        font = ImageFont.truetype(font_path, 34) if font_path else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    w, h, fps = get_video_info(video_path)
    print(f"    Video: {w}x{h} @ {fps}fps")

    frames_dir = f"{OUTPUT}/_frames"
    os.makedirs(frames_dir, exist_ok=True)

    # Hapus frame lama
    for f in os.listdir(frames_dir):
        try: os.unlink(os.path.join(frames_dir, f))
        except: pass

    print(f"    Extract frames...")
    ok = run_ff(
        f'ffmpeg -y -i "{video_path}" '
        f'-t {dur} -vf "fps={fps}" '
        f'"{frames_dir}/f_%06d.jpg"'
    )
    if not ok:
        return False

    frames = sorted([
        os.path.join(frames_dir, f)
        for f in os.listdir(frames_dir)
        if f.endswith('.jpg')
    ])
    print(f"    Frames: {len(frames)}")

    print(f"    Render subtitles...")
    for i, frame_path in enumerate(frames):
        t = i / fps

        # Cari kalimat aktif
        sent = ""
        for j, (start, end) in enumerate(timings):
            if start <= t < end:
                sent = sentences[j]
                break

        if not sent:
            continue

        try:
            img  = Image.open(frame_path).convert("RGB")
            draw = ImageDraw.Draw(img)

            lines = textwrap.wrap(sent, width=46)[-2:]
            y     = h - 70

            for line in reversed(lines):
                try:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    tw   = bbox[2] - bbox[0]
                    th   = bbox[3] - bbox[1]
                except Exception:
                    tw, th = len(line) * 18, 38

                x   = max(0, (w - tw) // 2)
                pad = 8

                draw.rectangle(
                    [x-pad, y-pad, x+tw+pad, y+th+pad],
                    fill=(0, 0, 0, 170)
                )
                draw.text((x+2, y+2), line, font=font, fill=(0, 0, 0))
                draw.text((x, y), line, font=font, fill=(255, 255, 255))
                y -= th + 12

            img.save(frame_path, "JPEG", quality=88)

        except Exception:
            pass

    print(f"    Rebuild video...")
    ok = run_ff(
        f'ffmpeg -y '
        f'-framerate {fps} '
        f'-i "{frames_dir}/f_%06d.jpg" '
        f'-i "{video_path}" '
        f'-map 0:v -map 1:a '
        f'-c:v libx264 -preset fast -crf 20 '
        f'-pix_fmt yuv420p '
        f'-c:a copy -shortest '
        f'"{output_path}"'
    )

    # Cleanup
    for f in os.listdir(frames_dir):
        try: os.unlink(os.path.join(frames_dir, f))
        except: pass
    try: os.rmdir(frames_dir)
    except: pass

    if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
        print(f"    OK: {os.path.getsize(output_path):,} bytes")
        return True
    return False


# ── MAIN ──────────────────────────────────────────────────
print("=" * 55)
print("  PETER Make Final Video — PIL Timed Subtitle")
print("=" * 55)

broll = sorted([
    f"{OUTPUT}/broll_{i:03d}.mp4"
    for i in range(10)
    if os.path.exists(f"{OUTPUT}/broll_{i:03d}.mp4")
    and os.path.getsize(f"{OUTPUT}/broll_{i:03d}.mp4") > 100000
])
audio = f"{OUTPUT}/pro_voiceover.mp3"

print(f"B-Roll : {len(broll)} clips")
print(f"Audio  : {'OK' if os.path.exists(audio) else 'TIDAK ADA'}")
print(f"Font   : {find_font() or 'tidak ditemukan'}")

if not broll:
    print("Tidak ada B-Roll!")
    sys.exit(1)
if not os.path.exists(audio):
    print("Tidak ada audio!")
    sys.exit(1)

# Durasi audio
try:
    r   = subprocess.run(
        ['ffprobe', '-v', 'error',
         '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', audio],
        capture_output=True, text=True
    )
    dur = int(float(r.stdout.strip()))
except Exception:
    dur = 151
print(f"Durasi : {dur}s ({dur//60}:{dur%60:02d})\n")

# ── STEP 1 ────────────────────────────────────────────────
print("[1] Concat B-Roll...")
list_f = f"{OUTPUT}/_list.txt"
concat = f"{OUTPUT}/_concat.mp4"
with open(list_f, "w") as f:
    for v in broll:
        f.write(f"file '{v}'\n")
run_ff(f'ffmpeg -y -f concat -safe 0 -i "{list_f}" -c copy "{concat}"')
print(f"    {os.path.getsize(concat):,} bytes")

# ── STEP 2 ────────────────────────────────────────────────
print("\n[2] Gabung + Audio...")
base = f"{OUTPUT}/_base.mp4"
run_ff(
    f'ffmpeg -y '
    f'-stream_loop -1 -i "{concat}" '
    f'-i "{audio}" '
    f'-c:v libx264 -preset fast -crf 20 '
    f'-pix_fmt yuv420p '
    f'-c:a aac -b:a 192k '
    f'-t {dur + 2} '
    f'"{base}"'
)
print(f"    {os.path.getsize(base):,} bytes")
current = base

# ── STEP 3 ────────────────────────────────────────────────
print("\n[3] Branding PETER AI...")
brand_out   = f"{OUTPUT}/_branded.mp4"
branding_ok = add_branding(current, brand_out)
if branding_ok:
    current = brand_out
    print(f"    OK: {os.path.getsize(brand_out):,} bytes")
else:
    print("    Gagal — skip branding")

# ── STEP 4 ────────────────────────────────────────────────
print("\n[4] Subtitle timed...")
narasi_file = audio.replace('.mp3', '_teks.txt')
subtitle_ok = False

if os.path.exists(narasi_file):
    with open(narasi_file, "r", encoding="utf-8") as f:
        narasi = f.read()

    sents = [
        s.strip() for s in re.split(r'[.!?]+', narasi)
        if len(s.strip()) > 10
    ][:15]

    print(f"    Kalimat: {len(sents)}")

    if sents:
        # Timing proporsional berdasarkan jumlah kata
        total_words   = sum(len(s.split()) for s in sents)
        words_per_sec = total_words / dur

        timings      = []
        current_time = 0.0
        for sent in sents:
            wc  = len(sent.split())
            d   = max(1.5, min(wc / words_per_sec, 12.0))
            timings.append((current_time, current_time + d))
            current_time += d

        print(f"    Words/sec: {words_per_sec:.1f}")
        for i in range(min(3, len(sents))):
            s, e = timings[i]
            print(f"    [{i+1}] {s:.1f}s-{e:.1f}s: {sents[i][:40]}...")

        sub_out     = f"{OUTPUT}/_sub.mp4"
        subtitle_ok = add_subtitle_timed(
            current, sents, timings, dur, sub_out
        )
        if subtitle_ok:
            current = sub_out
        else:
            print("    Gagal — skip subtitle")
else:
    print(f"    Narasi tidak ada: {narasi_file}")

# ── STEP 5 ────────────────────────────────────────────────
print("\n[5] Simpan final...")
final = f"{OUTPUT}/pro_final_new.mp4"
shutil.copy(current, final)
print(f"    OK: {os.path.getsize(final):,} bytes")
print(f"    Subtitle : {'YES' if subtitle_ok else 'NO'}")
print(f"    Branding : {'YES' if branding_ok else 'NO'}")
print(f"    Durasi   : {dur//60}:{dur%60:02d}")

# ── STEP 6 ────────────────────────────────────────────────
print("\n[6] Portrait 9:16...")
portrait = f"{OUTPUT}/pro_portrait_new.mp4"
run_ff(
    f'ffmpeg -y -i "{final}" '
    f'-vf "scale=1080:1920:'
    f'force_original_aspect_ratio=decrease,'
    f'pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" '
    f'-c:a copy "{portrait}"'
)
if os.path.exists(portrait):
    print(f"    OK: {os.path.getsize(portrait):,} bytes")

# ── HASIL ─────────────────────────────────────────────────
print("\n" + "=" * 55)
print("  HASIL AKHIR")
print("=" * 55)
for label, path in [
    ("Final 16:9"   , final),
    ("Portrait 9:16", portrait),
    ("Audio"        , audio),
]:
    if os.path.exists(path):
        mb = os.path.getsize(path) / (1024*1024)
        print(f"  OK  {label:15}: {mb:.1f} MB")
    else:
        print(f"  ERR {label:15}: tidak ada")
print("=" * 55)

os.startfile(final.replace("/", "\\"))

upload = input("\nUpload ke YouTube? (y/n): ").strip().lower()
if upload == 'y':
    try:
        import glob
        title   = "Cara Menghasilkan Uang dari AI di Indonesia 2026"
        scripts = glob.glob(f"{OUTPUT}/script_*.txt")
        if scripts:
            with open(scripts[-1], "r", encoding="utf-8") as f:
                for line in f.read().split("\n"):
                    line = line.strip().lstrip("0123456789. *\"'")
                    if 20 < len(line) < 100:
                        title = line
                        break

        from publishers.youtube_pub import upload_youtube
        yt = upload_youtube(
            video_path  = final.replace("/", "\\"),
            title       = title,
            description = f"{title}\n\nDibuat otomatis oleh PETER AI.",
            tags        = ["AI", "teknologi", "Indonesia",
                           "penghasilan", "2026"],
            privacy     = "unlisted"
        )
        if yt.get("success"):
            print(f"\nYouTube: {yt['url']}")
        else:
            print(f"\nGagal: {yt.get('error')}")
    except Exception as e:
        import traceback
        traceback.print_exc()

print("\nSelesai!")