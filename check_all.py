import os

check_dirs = [
    "C:\\peter-ai",
    "C:\\peter-ai\\core",
    "C:\\peter-ai\\content",
    "C:\\peter-ai\\publishers",
]

print("Mencari 'user_name' yang tidak valid...\n")

for folder in check_dirs:
    if not os.path.exists(folder):
        continue
    for fname in os.listdir(folder):
        if not fname.endswith(".py"):
            continue
        fpath = os.path.join(folder, fname)
        try:
            lines = open(
                fpath, encoding="utf-8", errors="replace"
            ).readlines()
            for i, line in enumerate(lines, 1):
                low = line.lower()
                if ("user_name" in low and
                    "USER_NAME" not in line and
                    "def " not in line and
                    "param" not in low and
                    "#" not in line):
                    print(f"{fname}:{i}: {line.rstrip()[:80]}")
        except Exception as e:
            print(f"Skip {fname}: {e}")

print("\nSelesai!")