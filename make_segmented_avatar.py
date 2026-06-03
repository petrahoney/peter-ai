import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)
import os, sys, subprocess, shutil
sys.path.append("C:\\peter-ai")
from dotenv import load_dotenv
load_dotenv()

OUTPUT = "C:\\peter-ai\\data\\outputs"


def get_duration(path):
    r = subprocess.run(
        ['ffprobe', '-v', 'error',
         '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', path],
        capture_output=True, text=True
    )
    try: return float(r.stdout.strip())
    except: return 0.0


def split_audio(audio_path, segment_dur=45):
    """Bagi audio jadi segmen 45 detik"""
    total = get_duration(audio_path)
    segs  = []
    i     = 0
    start = 0.0

    while start < total:
        end      = min(start + segment_dur, total)
        seg_path = f"{OUTPUT}/_seg_{i:03d}.wav"

        subprocess.run(
            f'ffmpeg -y -i "{audio_path}" '
            f'-ss {start:.2f} -t {segment_dur} '
            f'-ar 44100 -ac 1 -acodec pcm_s16le '
            f'"{seg_path}"',
            shell=True, capture_output=True
        )

        if os.path.exists(seg_path):
            segs.append({
                "path" : seg_path,
                "start": start,
                "end"  : end,
                "index": i
            })
            dur = get_duration(seg_path)
            print(f"  Segmen {i+1}: {start:.0f}s-{end:.0f}s ({dur:.1f}s)")

        start += segment_dur
        i     += 1

    return segs


def make_segmented_video():
    audio_mp3 = f"{OUTPUT}\\pro_voiceover.mp3"

    if not os.path.exists(audio_mp3):
        print("Audio tidak ada!")
        return

    total_dur = get_duration(audio_mp3)
    print(f"Audio total: {total_dur:.0f}s")

    # Untuk video pendek — langsung 1 segmen
    if total_dur <= 90:
        seg_dur = int(total_dur)
        print(f"Video pendek — 1 segmen {seg_dur}s")
        n_segs  = 1
    else:
        seg_dur = 45
        n_segs  = int(total_dur / seg_dur) + 1
        print(f"Video panjang — {n_segs} segmen @ {seg_dur}s")

    confirm = input(f"\nBuat {n_segs} avatar segmen? (y/n): ").strip().lower()
    if confirm != 'y':
        return

    # Split audio
    print("\nSplit audio...")
    segments = split_audio(audio_mp3, seg_dur)
    print(f"Total segmen: {len(segments)}")

    # Generate avatar per segmen
    from content.pro_video_engine import DIDPresenter
    did          = DIDPresenter()
    avatar_clips = []

    for seg in segments:
        print(f"\n[D-ID] Segmen {seg['index']+1}/{len(segments)}...")
        avatar = did.create_talking_avatar(
            audio_path  = seg["path"],
            output_name = f"avatar_seg_{seg['index']:03d}.mp4"
        )
        if avatar and os.path.exists(avatar):
            avatar_clips.append(avatar)
            print(f"  OK: {os.path.getsize(avatar):,} bytes")
        else:
            print(f"  GAGAL — skip segmen ini")

    if not avatar_clips:
        print("Semua segmen gagal!")
        return

    # Gabungkan semua avatar clips
    print(f"\nGabungkan {len(avatar_clips)} avatar clips...")
    list_f = f"{OUTPUT}/_avatar_list.txt"
    with open(list_f, "w") as f:
        for clip in avatar_clips:
            f.write(f"file '{clip.replace(chr(92), '/')}'\n")

    final_avatar = f"{OUTPUT}/avatar_final_synced.mp4"
    subprocess.run(
        f'ffmpeg -y -f concat -safe 0 '
        f'-i "{list_f}" -c copy "{final_avatar}"',
        shell=True, capture_output=True
    )

    if os.path.exists(final_avatar):
        size = os.path.getsize(final_avatar)
        dur  = get_duration(final_avatar)
        print(f"\nAvatar final: {size:,} bytes | {dur:.0f}s")
        os.startfile(final_avatar)

        # Gabungkan dengan B-Roll sebagai background
        combine = input("\nGabungkan dengan B-Roll? (y/n): ").strip().lower()
        if combine == 'y':
            _combine_with_broll(final_avatar, audio_mp3)
    else:
        print("Gagal gabungkan clips!")


def _combine_with_broll(avatar_path, audio_path):
    """Gabungkan avatar synced dengan B-Roll background"""
    import glob

    broll = sorted([
        f"{OUTPUT}/broll_{i:03d}.mp4"
        for i in range(10)
        if os.path.exists(f"{OUTPUT}/broll_{i:03d}.mp4")
    ])

    if not broll:
        print("Tidak ada B-Roll!")
        return

    # Concat dan loop B-Roll
    dur     = get_duration(audio_path)
    list_f  = f"{OUTPUT}/_broll_list.txt"
    concat  = f"{OUTPUT}/_broll_bg.mp4"
    broll_d = get_duration(broll[0]) * len(broll)
    loops   = max(1, int(dur / broll_d) + 1)

    with open(list_f, "w") as f:
        for _ in range(loops):
            for v in broll:
                f.write(f"file '{v.replace(chr(92), '/')}'\n")

    subprocess.run(
        f'ffmpeg -y -f concat -safe 0 '
        f'-i "{list_f}" -c copy "{concat}"',
        shell=True, capture_output=True
    )

    # Overlay avatar di pojok kanan bawah
    output = f"{OUTPUT}/pro_final_synced.mp4"
    av_w, av_h = 300, 380

    subprocess.run(
        f'ffmpeg -y '
        f'-i "{concat}" '
        f'-i "{avatar_path}" '
        f'-i "{audio_path}" '
        f'-filter_complex '
        f'"[1:v]scale={av_w}:{av_h}[av];'
        f'[0:v][av]overlay=x=W-{av_w+20}:y=H-{av_h+80}[vid]" '
        f'-map "[vid]" -map 2:a '
        f'-c:v libx264 -preset fast -crf 20 '
        f'-pix_fmt yuv420p '
        f'-c:a aac -b:a 192k '
        f'-t {dur + 2} '
        f'"{output}"',
        shell=True, capture_output=True
    )

    if os.path.exists(output):
        size = os.path.getsize(output)
        print(f"\nFinal synced: {output}")
        print(f"Size: {size:,} bytes")
        os.startfile(output)

        upload = input("\nUpload ke YouTube? (y/n): ").strip().lower()
        if upload == 'y':
            from publishers.youtube_pub import upload_youtube
            yt = upload_youtube(
                video_path  = output,
                title       = "Cara Menghasilkan Uang dari AI 2026",
                description = "Dibuat otomatis oleh PETER AI",
                tags        = ["AI", "Indonesia", "2026"],
                privacy     = "unlisted"
            )
            if yt.get("success"):
                print(f"YouTube: {yt['url']}")


if __name__ == "__main__":
    make_segmented_video()