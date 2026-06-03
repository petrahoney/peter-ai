import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)
import os, sys, subprocess
sys.path.append("C:\\peter-ai")
from dotenv import load_dotenv
load_dotenv()

OUTPUT = "C:\\peter-ai\\data\\outputs"

print("=" * 55)
print("  Debug Compositor")
print("=" * 55)

# Cek semua file yang ada
files = {
    "avatar"  : "avatar_presenter.mp4",
    "broll_0" : "broll_000.mp4",
    "broll_1" : "broll_001.mp4",
    "broll_2" : "broll_002.mp4",
    "broll_3" : "broll_003.mp4",
    "audio"   : "pro_voiceover.mp3",
}

print("\nFile tersedia:")
for name, fname in files.items():
    path = os.path.join(OUTPUT, fname)
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"  ✅ {name:10}: {fname} ({size:,} bytes)")
    else:
        print(f"  ❌ {name:10}: tidak ada")

# Kumpulkan broll yang ada
broll = [
    os.path.join(OUTPUT, f"broll_{i:03d}.mp4")
    for i in range(4)
    if os.path.exists(os.path.join(OUTPUT, f"broll_{i:03d}.mp4"))
]
avatar = os.path.join(OUTPUT, "avatar_presenter.mp4")
audio  = os.path.join(OUTPUT, "pro_voiceover.mp3")

print(f"\nB-Roll clips: {len(broll)}")
print(f"Avatar      : {'✅' if os.path.exists(avatar) else '❌'}")
print(f"Audio       : {'✅' if os.path.exists(audio) else '❌'}")

if not broll and not os.path.exists(avatar):
    print("\nTidak ada video! Jalankan pipeline dulu.")
    sys.exit(1)

# Test 1 — Concat B-Roll
if broll:
    print(f"\n[TEST 1] Concat {len(broll)} B-Roll clips...")
    list_f = os.path.join(OUTPUT, "_test_list.txt")
    concat = os.path.join(OUTPUT, "_test_concat.mp4")
    with open(list_f, "w") as f:
        for v in broll:
            f.write(f"file '{v.replace(chr(92), '/')}'\n")
    r = subprocess.run(
        f'ffmpeg -y -f concat -safe 0 -i "{list_f}" -c copy "{concat}"',
        shell=True, capture_output=True, text=True
    )
    if os.path.exists(concat):
        print(f"  ✅ Concat OK: {os.path.getsize(concat):,} bytes")
    else:
        print(f"  ❌ Concat gagal!")
        print(f"  stderr: {r.stderr[-200:]}")

# Test 2 — PiP
if broll and os.path.exists(avatar):
    print("\n[TEST 2] Test Avatar PiP...")
    pip_out = os.path.join(OUTPUT, "_test_pip.mp4")
    base    = concat if os.path.exists(concat) else broll[0]
    cmd = (
        f'ffmpeg -y -i "{base}" -i "{avatar}" '
        f'-filter_complex "[1:v]scale=320:400[av];'
        f'[0:v][av]overlay=x=W-340:y=H-420" '
        f'-c:v libx264 -preset fast -crf 20 '
        f'-pix_fmt yuv420p -c:a copy "{pip_out}"'
    )
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if os.path.exists(pip_out) and os.path.getsize(pip_out) > 10000:
        print(f"  ✅ PiP OK: {os.path.getsize(pip_out):,} bytes")
        os.startfile(pip_out)
    else:
        print(f"  ❌ PiP gagal!")
        print(f"  stderr: {r.stderr[-300:]}")

# Test 3 — Gabung audio dengan B-Roll
if broll and os.path.exists(audio):
    print("\n[TEST 3] Gabung B-Roll + Audio...")
    base      = concat if os.path.exists(concat) else broll[0]
    with_aud  = os.path.join(OUTPUT, "_test_with_audio.mp4")
    cmd_audio = (
        f'ffmpeg -y '
        f'-stream_loop -1 -i "{base}" '
        f'-i "{audio}" '
        f'-c:v copy -c:a aac '
        f'-shortest "{with_aud}"'
    )
    r = subprocess.run(cmd_audio, shell=True, capture_output=True, text=True)
    if os.path.exists(with_aud):
        print(f"  ✅ Audio OK: {os.path.getsize(with_aud):,} bytes")
    else:
        print(f"  ❌ Audio gagal!")
        print(f"  stderr: {r.stderr[-200:]}")

print("\nDebug selesai!")
print("Cek file _test_*.mp4 di outputs untuk lihat hasilnya")