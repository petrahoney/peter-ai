import os

folders = [
    "C:\\peter-ai",
    "C:\\peter-ai\\core",
    "C:\\peter-ai\\content",
    "C:\\peter-ai\\publishers",
]

for folder in folders:
    if not os.path.exists(folder):
        continue
    for f in os.listdir(folder):
        if not f.endswith(".py"):
            continue
        fpath = os.path.join(folder, f)
        try:
            lines = open(
                fpath, encoding="utf-8", errors="replace"
            ).readlines()
            for i, l in enumerate(lines, 1):
                # Cari user_name yang bukan parameter fungsi
                if ("user_name" in l.lower() and
                    "USER_NAME" not in l and
                    "def " not in l and
                    "f\"" not in l and
                    "f'" not in l and
                    "#" not in l):
                    print(f"{f}:{i}: {l.rstrip()[:80]}")
        except Exception:
            pass

print("\nSelesai!")