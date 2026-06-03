import os
BASE = "C:\\peter-ai"
EXCLUDE = {"venv", "venv-new", "__pycache__", ".git", "node_modules", "data", "models", ".idea", "dist", "build"}
EXT = {".py", ".html", ".md", ".txt", ".yml", ".yaml", ".json", ".sh", ".bat", ".env"}
total = 0
for root, dirs, files in os.walk(BASE):
    dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.startswith(".")]
    for f in sorted(files):
        ext = os.path.splitext(f)[1].lower()
        if ext in EXT and not f.startswith("."):
            rel = os.path.join(root.replace(BASE, ""), f)
            print(rel)
            total += 1
print("TOTAL:", total)