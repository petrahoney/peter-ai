import re

path = "C:\\peter-ai\\core\\oi_engine.py"

with open(path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Fix subprocess tanpa encoding
old = 'capture_output=True, text=True'
new = 'capture_output=True, text=True, encoding="utf-8", errors="replace"'
content = content.replace(old, new)

# Fix subprocess.run tanpa encoding
old2 = 'stdout=subprocess.PIPE, stderr=subprocess.PIPE'
new2 = 'stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", errors="replace"'
content = content.replace(old2, new2)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fix selesai!")