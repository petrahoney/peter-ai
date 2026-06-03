path = "C:\\peter-ai\\main_peter.py"

with open(path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# Tambahkan global USER_NAME di awal setiap fungsi yang butuhkan
old1 = "def run_peter_executor():"
new1 = """def run_peter_executor():
    global USER_NAME, MEMORY_OK, HEAL_OK, VISION_OK
    global memory, healer, vision"""

old2 = "def run_crewai(task_description: str = None):"
new2 = """def run_crewai(task_description: str = None):
    global USER_NAME, MEMORY_OK, memory"""

old3 = "def run_peter_executor_voice():"
new3 = """def run_peter_executor_voice():
    global USER_NAME, MEMORY_OK, memory"""

old4 = "def run_combined():"
new4 = """def run_combined():
    global USER_NAME"""

old5 = "def run_vision_mode():"
new5 = """def run_vision_mode():
    global USER_NAME, VISION_OK, vision, MEMORY_OK, memory"""

for old, new in [(old1,new1),(old2,new2),(old3,new3),(old4,new4),(old5,new5)]:
    if old in content:
        content = content.replace(old, new, 1)
        print(f"Fixed: {old[:40]}")
    else:
        print(f"Not found: {old[:40]}")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("\nSelesai!")