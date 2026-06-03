path = "C:\\peter-ai\\core\\brain.py"

with open(path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

old = '''        if any(w in msg for w in [
            "script youtube", "konten", "caption", "thumbnail",
            "viral", "youtube", "tiktok", "instagram", "reels"
        ]):
            return "content"'''

new = '''        if any(w in msg for w in [
            "script youtube", "script video", "script tiktok",
            "script instagram", "script podcast", "script konten",
            "buat script", "tulis script", "script perdana",
            "script minggu", "konten", "caption", "thumbnail",
            "viral", "youtube", "tiktok", "instagram", "reels"
        ]):
            return "content"'''

if old in content:
    content = content.replace(old, new)
    print("Fix berhasil!")
else:
    print("Pattern tidak ditemukan — cari manual...")
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'return "content"' in line:
            print(f"  Baris {i}: {line.rstrip()[:80]}")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Selesai!")