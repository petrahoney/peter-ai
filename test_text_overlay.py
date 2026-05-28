import os
import sys
sys.path.append("C:\\peter-ai")

OUTPUT = "C:\\peter-ai\\data\\outputs"
video  = os.path.join(OUTPUT, "test_slideshow.mp4")
out    = os.path.join(OUTPUT, "test_with_text.mp4")

title = "Cara Menghasilkan Uang dari AI 2026"

# Test langsung dengan FFmpeg tanpa fungsi wrapper
import re
safe = re.sub(r"['\"\\\[\]{}|<>]", "", title)
safe = safe.replace(":", " -").replace("&", "dan")[:55]

words = safe.split()
if len(words) > 5:
    mid   = len(words) // 2
    line1 = " ".join(words[:mid])
    line2 = " ".join(words[mid:])
    teks  = f"{line1}\\n{line2}"
else:
    teks = safe

print(f"Teks: {teks}")

# Jalankan FFmpeg langsung dengan output error
cmd = (
    f'ffmpeg -y '
    f'-i "{video}" '
    f'-vf "drawtext='
    f'text=\'{teks}\':'
    f'fontsize=48:'
    f'fontcolor=white:'
    f'x=(w-text_w)/2:'
    f'y=h-text_h-60:'
    f'box=1:'
    f'boxcolor=black@0.7:'
    f'boxborderw=15" '
    f'-c:v libx264 '
    f'-preset fast '
    f'-crf 23 '
    f'-pix_fmt yuv420p '
    f'-c:a copy '
    f'"{out}"'
)

print(f"\nCommand:\n{cmd}\n")
ret = os.system(cmd)
print(f"\nReturn code: {ret}")

if os.path.exists(out):
    size = os.path.getsize(out)
    print(f"Output size: {size:,} bytes")
    if size > 10000:
        print("TEXT OVERLAY BERHASIL!")
        os.startfile(out)
    else:
        print("File terlalu kecil!")
else:
    print("File tidak terbuat!")