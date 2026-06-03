path = "C:\\peter-ai\\peter_tts.py"

with open(path, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

print(f"Total baris: {len(lines)}")

# Cari baris bermasalah
for i, line in enumerate(lines, 1):
    if "user_input" in line or "USER_NAME" in line:
        if "def " not in line and "#" not in line:
            print(f"MASALAH baris {i}: {line.rstrip()[:80]}")

# Hapus semua baris di luar fungsi yang tidak seharusnya ada
# Cari dimana fungsi peter_speak mulai
start_clean = 0
for i, line in enumerate(lines):
    if line.startswith("def peter_speak"):
        start_clean = i
        break

print(f"\nFungsi peter_speak mulai di baris {start_clean+1}")

# Ambil semua kode sebelum peter_speak (imports, constants)
# dan fungsi-fungsi yang valid
valid_starts = ["#", "import", "from", "def ", "class ",
                "ELEVENLABS", "OUTPUT_DIR", "os.", "\n"]

clean_lines = []
skip_mode   = False

for i, line in enumerate(lines):
    # Jika ini baris bermasalah di luar fungsi
    if i < start_clean:
        is_valid = any(line.startswith(v) for v in valid_starts)
        is_empty = line.strip() == ""
        if is_valid or is_empty:
            clean_lines.append(line)
        else:
            print(f"SKIP baris {i+1}: {line.rstrip()[:60]}")
    else:
        clean_lines.append(line)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(clean_lines)

print(f"\nSelesai! {len(clean_lines)} baris tersisa")