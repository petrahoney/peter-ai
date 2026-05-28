from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 55)
print("  Test CrewAI PETER")
print("=" * 55)

# Setup LLM
if os.getenv("LOCAL_MODE") == "true":
    llm = LLM(
        model    = "ollama/llama3.3",
        base_url = "http://localhost:11434"
    )
    llm_fast = LLM(
        model    = "ollama/llama3.2:3b",
        base_url = "http://localhost:11434"
    )
else:
    llm = LLM(
        model   = "anthropic/claude-sonnet-4-6",
        api_key = os.getenv("ANTHROPIC_API_KEY")
    )
    llm_fast = LLM(
        model   = "anthropic/claude-haiku-4-5-20251001",
        api_key = os.getenv("ANTHROPIC_API_KEY")
    )

print(f"Mode: {'LOCAL (Ollama)' if os.getenv('LOCAL_MODE')=='true' else 'CLOUD (Claude)'}")
print("Membuat agents...\n")

# ── BUAT AGENTS ──────────────────────────────────
peter = Agent(
    role      = "PETER — AI Manager",
    goal      = "Koordinasi task dan berikan respons terbaik",
    backstory  = "Kamu adalah PETER, AI personal assistant canggih milik Tjerlang.",
    llm       = llm,
    verbose   = True
)

researcher = Agent(
    role      = "Research Specialist",
    goal      = "Cari informasi akurat dan terkini",
    backstory  = "Expert researcher dengan kemampuan analisis mendalam.",
    llm       = llm,
    verbose   = True
)

# ── BUAT TASKS ───────────────────────────────────
research_task = Task(
    description     = """Riset 5 niche YouTube paling profitable
untuk konten AI di Indonesia tahun 2026.
Berikan data RPM, estimasi subscriber, dan tingkat kompetisi.""",
    agent           = researcher,
    expected_output = "Daftar 5 niche dengan estimasi RPM dan potensi subscriber"
)

summary_task = Task(
    description     = """Rangkum hasil riset dan buat rekomendasi
niche terbaik untuk channel YouTube PETER.
Sertakan rencana konten 30 hari pertama.""",
    agent           = peter,
    expected_output = "Rekomendasi 1 niche terbaik dengan rencana konten 30 hari"
)

# ── JALANKAN CREW ─────────────────────────────────
print("Menjalankan CrewAI...\n")

crew = Crew(
    agents  = [peter, researcher],
    tasks   = [research_task, summary_task],
    process = Process.sequential,
    verbose = True
)

result = crew.kickoff()

print("\n" + "=" * 55)
print("  HASIL PETER CREW:")
print("=" * 55)
print(result)
print("=" * 55)

# Simpan hasil
with open("C:\\peter-ai\\crew_output.txt", "w", encoding="utf-8") as f:
    f.write(str(result))
print("\nHasil disimpan ke: C:\\peter-ai\\crew_output.txt")