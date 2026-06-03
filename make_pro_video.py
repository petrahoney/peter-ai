import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)
import os, sys, subprocess, shutil, re, textwrap, glob
sys.path.append("C:\\peter-ai")
from dotenv import load_dotenv
load_dotenv()

OUTPUT = "C:/peter-ai/data/outputs"
os.makedirs(OUTPUT, exist_ok=True)


def run_ff(cmd: str) -> bool:
    r = subprocess.run(cmd, shell=True, capture_output=True)
    return r.returncode == 0


def get_duration(path: str) -> float:
    try:
        r = subprocess.run(
            ['ffprobe', '-v', 'error',
             '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', path],
            capture_output=True, text=True
        )
        return float(r.stdout.strip())
    except Exception:
        return 0.0


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


def find_font(bold: bool = True) -> str:
    fonts = (
        ["C:/Windows/Fonts/arialbd.ttf",
         "C:/Windows/Fonts/calibrib.ttf",
         "C:/Windows/Fonts/verdanab.ttf"]
        if bold else
        ["C:/Windows/Fonts/arial.ttf",
         "C:/Windows/Fonts/calibri.ttf",
         "C:/Windows/Fonts/verdana.ttf"]
    ) + ["C:/Windows/Fonts/tahoma.ttf"]
    for f in fonts:
        if os.path.exists(f):
            return f
    return None


def make_title_card(title: str,
                    subtitle: str = "PETER AI",
                    duration: int = 4,
                    output_path: str = None,
                    w: int = 1280,
                    h: int = 720) -> str:
    """Buat title card profesional"""
    from PIL import Image, ImageDraw, ImageFont

    if not output_path:
        output_path = f"{OUTPUT}/_title.mp4"
    img_path = f"{OUTPUT}/_title_img.jpg"

    try:
        fb = find_font(bold=True)
        fn = find_font(bold=False)
        try:
            f_title = ImageFont.truetype(fb, 64) if fb else ImageFont.load_default()
            f_sub   = ImageFont.truetype(fn, 34) if fn else ImageFont.load_default()
            f_brand = ImageFont.truetype(fb, 26) if fb else ImageFont.load_default()
        except Exception:
            f_title = f_sub = f_brand = ImageFont.load_default()

        img  = Image.new("RGB", (w, h), (8, 8, 20))
        draw = ImageDraw.Draw(img)

        # Gradient background
        for y in range(h):
            ratio = y / h
            r_    = int(8  + 12  * ratio)
            g_    = int(8  + 7   * ratio)
            b_    = int(20 + 20  * ratio)
            draw.line([(0, y), (w, y)], fill=(r_, g_, b_))

        # Garis aksen atas
        draw.rectangle([0, 0, w, 6], fill=(0, 150, 255))

        # Branding
        draw.text((25, 18), "PETER AI",
                  font=f_brand, fill=(0, 180, 255))

        # Wrap judul
        lines   = textwrap.wrap(title, width=30)
        total_h = len(lines) * 84
        y_pos   = (h - total_h) // 2 - 25

        for line in lines:
            try:
                bbox = draw.textbbox((0, 0), line, font=f_title)
                tw   = bbox[2] - bbox[0]
            except Exception:
                tw = len(line) * 32
            x = (w - tw) // 2
            draw.text((x+3, y_pos+3), line,
                      font=f_title, fill=(0, 0, 0))
            draw.text((x, y_pos), line,
                      font=f_title, fill=(255, 255, 255))
            y_pos += 84

        # Subtitle
        try:
            bbox = draw.textbbox((0, 0), subtitle, font=f_sub)
            tw   = bbox[2] - bbox[0]
        except Exception:
            tw = len(subtitle) * 17
        draw.text(((w-tw)//2, y_pos+10), subtitle,
                  font=f_sub, fill=(120, 180, 255))

        # Garis bawah
        draw.rectangle([0, h-6, w, h], fill=(0, 150, 255))

        img.save(img_path, "JPEG", quality=95)

        ok = run_ff(
            f'ffmpeg -y -loop 1 -i "{img_path}" '
            f'-vf "fade=in:0:24,fade=out:{duration*24-24}:24" '
            f'-t {duration} -c:v libx264 -preset fast '
            f'-crf 18 -pix_fmt yuv420p -r 24 '
            f'"{output_path}"'
        )
        if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            return output_path
        return None
    except Exception as e:
        print(f"    Title card error: {e}")
        return None


def make_outro_card(channel: str = "PETER AI",
                    cta: str = "Subscribe & Like!",
                    duration: int = 3,
                    output_path: str = None,
                    w: int = 1280,
                    h: int = 720) -> str:
    """Buat outro card"""
    from PIL import Image, ImageDraw, ImageFont

    if not output_path:
        output_path = f"{OUTPUT}/_outro.mp4"
    img_path = f"{OUTPUT}/_outro_img.jpg"

    try:
        fb = find_font(bold=True)
        try:
            f_big = ImageFont.truetype(fb, 52) if fb else ImageFont.load_default()
            f_cta = ImageFont.truetype(fb, 36) if fb else ImageFont.load_default()
        except Exception:
            f_big = f_cta = ImageFont.load_default()

        img  = Image.new("RGB", (w, h), (5, 15, 5))
        draw = ImageDraw.Draw(img)

        for y in range(h):
            ratio = y / h
            r_    = int(5  + 10  * ratio)
            g_    = int(15 + 20  * ratio)
            b_    = int(5  + 10  * ratio)
            draw.line([(0, y), (w, y)], fill=(r_, g_, b_))

        draw.rectangle([0, 0, w, 6], fill=(0, 200, 80))

        # Channel name
        try:
            bbox = draw.textbbox((0, 0), channel, font=f_big)
            tw   = bbox[2] - bbox[0]
        except Exception:
            tw = len(channel) * 26
        x = (w - tw) // 2
        draw.text((x+2, h//2-55+2), channel,
                  font=f_big, fill=(0, 0, 0))
        draw.text((x, h//2-55), channel,
                  font=f_big, fill=(255, 255, 255))

        # CTA
        try:
            bbox = draw.textbbox((0, 0), cta, font=f_cta)
            tw2  = bbox[2] - bbox[0]
        except Exception:
            tw2 = len(cta) * 18
        draw.text(((w-tw2)//2, h//2+15), cta,
                  font=f_cta, fill=(0, 230, 90))

        draw.rectangle([0, h-6, w, h], fill=(0, 200, 80))
        img.save(img_path, "JPEG", quality=95)

        ok = run_ff(
            f'ffmpeg -y -loop 1 -i "{img_path}" '
            f'-vf "fade=in:0:12" '
            f'-t {duration} -c:v libx264 -preset fast '
            f'-crf 18 -pix_fmt yuv420p -r 24 '
            f'"{output_path}"'
        )
        if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            return output_path
        return None
    except Exception as e:
        print(f"    Outro error: {e}")
        return None


def add_branding(video_path: str, output_path: str) -> bool:
    """Tambah watermark PETER AI"""
    from PIL import Image, ImageDraw, ImageFont

    fb = find_font(bold=True)
    try:
        font = ImageFont.truetype(fb, 26) if fb else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    wm_path = f"{OUTPUT}/_wm.png"
    try:
        wm   = Image.new("RGBA", (155, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(wm)
        draw.rectangle([0, 0, 154, 39], fill=(0, 0, 0, 130))
        draw.text((8, 6), "PETER AI", font=font,
                  fill=(0, 180, 255, 220))
        wm.save(wm_path, "PNG")
    except Exception as e:
        print(f"    WM create error: {e}")
        return False

    ok = run_ff(
        f'ffmpeg -y -i "{video_path}" -i "{wm_path}" '
        f'-filter_complex "overlay=20:20" '
        f'-c:a copy "{output_path}"'
    )
    return (os.path.exists(output_path) and
            os.path.getsize(output_path) > 100000)


def transcribe_audio_whisper(audio_path: str) -> list:
    """Transcribe audio dengan Whisper untuk timing akurat"""
    print("    Transcribe dengan Whisper GPU...")
    try:
        import whisper
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model  = whisper.load_model("small", device=device)
        result = model.transcribe(
            audio_path,
            language        = "id",
            word_timestamps = True,
            verbose         = False
        )
        segments = [
            {
                "text" : seg["text"].strip(),
                "start": seg["start"],
                "end"  : seg["end"]
            }
            for seg in result["segments"]
        ]
        print(f"    Segments: {len(segments)}")
        for s in segments[:3]:
            print(f"    [{s['start']:.1f}s-{s['end']:.1f}s] {s['text'][:40]}")
        return segments
    except Exception as e:
        print(f"    Whisper error: {e}")
        return []


def render_subtitle_whisper(video_path: str,
                             segments: list,
                             title_offset: float,
                             output_path: str) -> bool:
    """Render subtitle ke video dengan timing Whisper"""
    from PIL import Image, ImageDraw, ImageFont

    fn = find_font(bold=False)
    try:
        font = ImageFont.truetype(fn, 34) if fn else ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    w, h, fps = get_video_info(video_path)
    dur       = int(get_duration(video_path))

    # Offset segments
    segs_off = [
        {
            "text" : s["text"],
            "start": s["start"] + title_offset,
            "end"  : s["end"]   + title_offset
        }
        for s in segments
    ]

    frames_dir = f"{OUTPUT}/_frames_ws"
    os.makedirs(frames_dir, exist_ok=True)
    for f in os.listdir(frames_dir):
        try: os.unlink(os.path.join(frames_dir, f))
        except: pass

    print(f"    Extract frames ({dur}s @ {fps}fps)...")
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

    print("    Render subtitle...")
    for i, fp in enumerate(frames):
        t = i / fps

        active = ""
        for seg in segs_off:
            if seg["start"] <= t <= seg["end"]:
                active = seg["text"]
                break
        if not active:
            continue

        try:
            img  = Image.open(fp).convert("RGB")
            draw = ImageDraw.Draw(img)
            lines = textwrap.wrap(active.strip(), width=46)[-2:]
            y     = h - 75

            for line in reversed(lines):
                try:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    tw   = bbox[2] - bbox[0]
                    th   = bbox[3] - bbox[1]
                except Exception:
                    tw, th = len(line) * 17, 36

                x   = max(10, (w - tw) // 2)
                pad = 10
                draw.rectangle(
                    [x-pad, y-pad, x+tw+pad, y+th+pad],
                    fill=(0, 0, 0, 185)
                )
                draw.text((x+2, y+2), line, font=font,
                          fill=(0, 0, 0))
                draw.text((x, y), line, font=font,
                          fill=(255, 255, 255))
                y -= th + 14

            img.save(fp, "JPEG", quality=88)
        except Exception:
            pass

    print("    Rebuild video...")
    ok = run_ff(
        f'ffmpeg -y '
        f'-framerate {fps} '
        f'-i "{frames_dir}/f_%06d.jpg" '
        f'-i "{video_path}" '
        f'-map 0:v -map 1:a '
        f'-c:v libx264 -preset fast -crf 20 '
        f'-pix_fmt yuv420p -c:a copy -shortest '
        f'"{output_path}"'
    )

    for f in os.listdir(frames_dir):
        try: os.unlink(os.path.join(frames_dir, f))
        except: pass
    try: os.rmdir(frames_dir)
    except: pass

    if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
        print(f"    OK: {os.path.getsize(output_path):,} bytes")
        return True
    return False


def add_avatar_pip(video_path: str,
                   avatar_path: str,
                   output_path: str) -> bool:
    """Tambah avatar D-ID sebagai PiP pojok kanan bawah"""
    ok = run_ff(
        f'ffmpeg -y -i "{video_path}" -i "{avatar_path}" '
        f'-filter_complex '
        f'"[1:v]scale=300:380[av];'
        f'[0:v][av]overlay=x=W-320:y=H-400" '
        f'-c:v libx264 -preset fast -crf 20 '
        f'-pix_fmt yuv420p -c:a copy '
        f'"{output_path}"'
    )
    return (os.path.exists(output_path) and
            os.path.getsize(output_path) > 100000)


# ============================================================
# MAIN
# ============================================================
print("=" * 60)
print("  PETER Pro Video — Full Professional")
print("=" * 60)

# Kumpulkan file
broll = sorted([
    f"{OUTPUT}/broll_{i:03d}.mp4"
    for i in range(10)
    if os.path.exists(f"{OUTPUT}/broll_{i:03d}.mp4")
    and os.path.getsize(f"{OUTPUT}/broll_{i:03d}.mp4") > 100000
])
audio = f"{OUTPUT}/pro_voiceover.mp3"

print(f"B-Roll : {len(broll)} clips")
print(f"Audio  : {'OK' if os.path.exists(audio) else 'TIDAK ADA'}")
print(f"Font   : {find_font()}")

if not broll:
    print("Tidak ada B-Roll! Jalankan pipeline dulu.")
    sys.exit(1)
if not os.path.exists(audio):
    print("Tidak ada audio!")
    sys.exit(1)

# Durasi audio
dur = int(get_duration(audio))
print(f"Durasi : {dur}s ({dur//60}:{dur%60:02d})\n")

# Ambil judul dari script
title = "Cara Menghasilkan Uang dari AI di Indonesia 2026"
scripts = glob.glob(f"{OUTPUT}/script_*.txt")
if scripts:
    with open(scripts[-1], "r", encoding="utf-8") as f:
        for line in f.read().split("\n"):
            line = re.sub(
                r'^(Topic|TOPIC|Topik|TITLE|Title|topic)[\s:*]+',
                '', line.strip()
            ).lstrip("0123456789. *\"'#-").strip()
            if 20 < len(line) < 90:
                title = line
                break
print(f"Judul: {title}\n")

# Tanya mode video
print("Pilih mode video:")
print("  [1] B-Roll saja (tanpa presenter)")
print("  [2] B-Roll + D-ID Avatar presenter")
mode    = input("Pilih (1/2, default=1): ").strip() or "1"
use_did = mode == "2"
print(f"Mode: {'B-Roll + Avatar' if use_did else 'B-Roll only'}\n")

# Info video dari B-Roll pertama
w, h, fps = get_video_info(broll[0])

# ── STEP 1: TITLE CARD ────────────────────────────────────
print("[1] Buat title card...")
title_vid = make_title_card(
    title       = title,
    subtitle    = "PETER AI — Konten Otomatis",
    duration    = 4,
    output_path = f"{OUTPUT}/_title.mp4",
    w=w, h=h
)
title_dur = 4 if title_vid else 0
print(f"    {'OK' if title_vid else 'GAGAL'}: {title_dur}s")

# ── STEP 2: CONCAT BROLL ──────────────────────────────────
print("\n[2] Concat B-Roll...")
list_f = f"{OUTPUT}/_list.txt"
concat = f"{OUTPUT}/_concat.mp4"
with open(list_f, "w") as f:
    for v in broll:
        f.write(f"file '{v}'\n")
run_ff(f'ffmpeg -y -f concat -safe 0 -i "{list_f}" -c copy "{concat}"')
broll_dur = int(get_duration(concat))
print(f"    {os.path.getsize(concat):,} bytes | {broll_dur}s")

# ── STEP 3: OUTRO CARD ────────────────────────────────────
print("\n[3] Buat outro card...")
outro_vid = make_outro_card(
    channel     = "PETER AI",
    cta         = "Subscribe & Like untuk konten AI terbaik!",
    duration    = 3,
    output_path = f"{OUTPUT}/_outro.mp4",
    w=w, h=h
)
outro_dur = 3 if outro_vid else 0
print(f"    {'OK' if outro_vid else 'GAGAL'}: {outro_dur}s")

# ── STEP 4: LOOP BROLL SESUAI DURASI AUDIO ────────────────
print("\n[4] Loop B-Roll sesuai durasi audio...")
need_dur = max(1, dur - title_dur - outro_dur)
loops    = max(1, -(-need_dur // max(broll_dur, 1)))
print(f"    B-Roll  : {broll_dur}s")
print(f"    Perlu   : {need_dur}s")
print(f"    Loop    : {loops}x")

full_list = f"{OUTPUT}/_full_list.txt"
full_raw  = f"{OUTPUT}/_full_raw.mp4"
with open(full_list, "w") as f:
    if title_vid and os.path.exists(title_vid):
        f.write(f"file '{title_vid}'\n")
    for _ in range(loops):
        f.write(f"file '{concat}'\n")
    if outro_vid and os.path.exists(outro_vid):
        f.write(f"file '{outro_vid}'\n")

run_ff(
    f'ffmpeg -y -f concat -safe 0 '
    f'-i "{full_list}" -c copy "{full_raw}"'
)
full_dur = int(get_duration(full_raw))
print(f"    OK: {os.path.getsize(full_raw):,} bytes | {full_dur}s")

# ── STEP 5: GABUNG AUDIO ──────────────────────────────────
print("\n[5] Gabung audio...")
with_audio  = f"{OUTPUT}/_with_audio.mp4"
audio_delay = title_dur * 1000

# Hitung durasi total video
video_total = int(get_duration(full_raw))
# Audio butuh delay karena ada title card
# Video total = title + broll_loop + outro
# Audio mulai setelah title card selesai

if audio_delay > 0:
    # Pad audio dengan silence di awal = durasi title card
    padded_audio = f"{OUTPUT}/_audio_padded.mp3"
    run_ff(
        f'ffmpeg -y '
        f'-i "{audio}" '
        f'-af "adelay={audio_delay}|{audio_delay},'
        f'apad=pad_dur={outro_dur}" '
        f'-t {video_total} '
        f'"{padded_audio}"'
    )

    if os.path.exists(padded_audio):
        run_ff(
            f'ffmpeg -y '
            f'-i "{full_raw}" '
            f'-i "{padded_audio}" '
            f'-c:v copy '
            f'-c:a aac -b:a 192k '
            f'-t {video_total} '
            f'"{with_audio}"'
        )
    else:
        # Fallback
        run_ff(
            f'ffmpeg -y '
            f'-i "{full_raw}" '
            f'-i "{audio}" '
            f'-filter_complex '
            f'"[1:a]adelay={audio_delay}|{audio_delay}[da]" '
            f'-map 0:v -map "[da]" '
            f'-c:v copy -c:a aac -b:a 192k '
            f'-t {video_total} '
            f'"{with_audio}"'
        )
else:
    run_ff(
        f'ffmpeg -y -i "{full_raw}" -i "{audio}" '
        f'-c:v copy -c:a aac -b:a 192k '
        f'-t {video_total} '
        f'"{with_audio}"'
    )

actual_dur = int(get_duration(with_audio))
print(f"    OK: {os.path.getsize(with_audio):,} bytes")
print(f"    Durasi: {actual_dur}s ({actual_dur//60}:{actual_dur%60:02d})")
current = with_audio

# ── STEP 6: D-ID AVATAR (opsional) ───────────────────────
if use_did:
    print("\n[6] D-ID Avatar presenter...")
    try:
        from content.pro_video_engine import DIDPresenter
        did    = DIDPresenter()
        avatar = did.create_talking_avatar(
            audio_path  = audio,
            output_name = "avatar_presenter.mp4"
        )
        if avatar and os.path.exists(avatar):
            pip_out = f"{OUTPUT}/_with_pip.mp4"
            ok      = add_avatar_pip(current, avatar, pip_out)
            if ok:
                current = pip_out
                print("    Avatar PiP OK!")
            else:
                print("    PiP gagal — lanjut tanpa avatar")
        else:
            print("    Avatar gagal — lanjut tanpa avatar")
    except Exception as e:
        print(f"    D-ID error: {e}")
else:
    print("\n[6] Avatar: skip (mode B-Roll only)")

# ── STEP 7: BRANDING ──────────────────────────────────────
print("\n[7] Branding PETER AI...")
branded     = f"{OUTPUT}/_branded.mp4"
branding_ok = add_branding(current, branded)
if branding_ok:
    current = branded
    print(f"    OK: {os.path.getsize(branded):,} bytes")
else:
    print("    Gagal — skip")

# ── STEP 8: SUBTITLE WHISPER ──────────────────────────────
print("\n[8] Subtitle akurat Whisper...")
segments    = transcribe_audio_whisper(audio)
subtitle_ok = False

if segments:
    sub_out     = f"{OUTPUT}/_sub.mp4"
    subtitle_ok = render_subtitle_whisper(
        current, segments,
        float(title_dur),
        sub_out
    )
    if subtitle_ok:
        current = sub_out
    else:
        print("    Gagal — skip subtitle")
else:
    print("    Whisper gagal — skip subtitle")

# ── STEP 9: SIMPAN FINAL ──────────────────────────────────
print("\n[9] Simpan final...")
final = f"{OUTPUT}/pro_final_new.mp4"
shutil.copy(current, final)
final_dur = int(get_duration(final))
print(f"    OK: {os.path.getsize(final):,} bytes")
print(f"    Durasi    : {final_dur}s ({final_dur//60}:{final_dur%60:02d})")
print(f"    Title Card: {'YES' if title_vid else 'NO'}")
print(f"    Outro     : {'YES' if outro_vid else 'NO'}")
print(f"    Subtitle  : {'YES — Whisper' if subtitle_ok else 'NO'}")
print(f"    Branding  : {'YES' if branding_ok else 'NO'}")
print(f"    Avatar    : {'YES' if use_did else 'NO'}")

# ── STEP 10: PORTRAIT ─────────────────────────────────────
print("\n[10] Portrait 9:16...")
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

# ── RINGKASAN ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("  HASIL AKHIR")
print("=" * 60)
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
print("=" * 60)

os.startfile(final.replace("/", "\\"))

upload = input("\nUpload ke YouTube? (y/n): ").strip().lower()
if upload == 'y':
    try:
        from publishers.youtube_pub import upload_youtube
        yt = upload_youtube(
            video_path  = final.replace("/", "\\"),
            title       = title,
            description = (
                f"{title}\n\n"
                f"Dibuat otomatis oleh PETER AI.\n\n"
                f"00:00 Intro\n"
                f"00:04 Pembahasan\n"
                f"{(dur+title_dur)//60}:{(dur+title_dur)%60:02d} Outro\n\n"
                f"Subscribe untuk konten AI terbaik setiap hari!\n\n"
                f"#AI #Indonesia #teknologi #2026 #PETERAI"
            ),
            tags        = [
                "AI Indonesia", "teknologi AI 2026",
                "cara menghasilkan uang AI",
                "passive income Indonesia",
                "tutorial AI pemula", "PETER AI",
                "ChatGPT Indonesia", "bisnis online AI"
            ],
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