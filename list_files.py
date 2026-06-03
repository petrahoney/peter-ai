import os

BASE    = "C:\\peter-ai"
EXCLUDE = {
    "venv", "venv-new", "__pycache__", ".git",
    "node_modules", "data", "models", ".idea",
    "dist", "build", "eggs", ".eggs"
}
EXT = {".py", ".html", ".md", ".txt", ".yml",
       ".yaml", ".json", ".sh", ".bat", ".env"}

print("=" * 60)
print("  PETER AI v2.0 — Source Files")
print("=" * 60)

total = 0
for root, dirs, files in os.walk(BASE):
    # Hapus folder yang dikecualikan
    dirs[:] = [
        d for d in dirs
        if d not in EXCLUDE and not d.startswith(".")
    ]

    level   = root.replace(BASE, "").count(os.sep)
    indent  = "  " * level
    rel     = root.replace(BASE, "").lstrip("\\")

    if level > 0:
        print(f"\n{indent}📁 {os.path.basename(root)}/")

    for f in sorted(files):
        ext  = os.path.splitext(f)[1].lower()
        if ext in EXT and not f.startswith("."):
            fpath = os.path.join(root, f)
            size  = os.path.getsize(fpath)
            print(f"{indent}  📄 {f} ({size:,} bytes)")
            total += 1

print(f"\n{'='*60}")
print(f"Total: {total} source files")
print(f"{'='*60}")
