path = "C:\\peter-ai\\main_peter.py"

with open(path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# Ganti blok rusak
old = """# Cek pengecualian dulu
    butuh_kode = any(k in user_input.lower() for k in kata_kode)
    if any(b in user_input.lower() for b in bukan_kode):
    butuh_kode = False

    while True:"""

new = """    while True:"""

if old in content:
    content = content.replace(old, new)
    print("Fix berhasil!")
else:
    print("Pattern tidak ditemukan!")
    # Cari manual
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if 'Cek pengecualian' in line or 'butuh_kode = any' in line:
            print(f"  {i}: {line[:80]}")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)