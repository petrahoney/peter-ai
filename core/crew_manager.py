"""
core/crew_manager.py
CrewAI Manager — 5 Agent Specialist
"""

import sys
sys.path.append("C:\\peter-ai")

from crewai import Agent, Task, Crew, Process, LLM
from config import (
    USER_NAME, ANTHROPIC_KEY, LOCAL_MODE,
    LLM_MODEL, LLM_FAST_MODEL, LLM_BASE_URL
)
from tools.web_search import web_search, get_trending_topics
from tools.file_manager import save_text_file, read_text_file


def get_llm(fast=False):
    """Dapatkan LLM sesuai mode"""
    model = LLM_FAST_MODEL if fast else LLM_MODEL
    if LOCAL_MODE:
        return LLM(model=model, base_url=LLM_BASE_URL)
    return LLM(model=model, api_key=ANTHROPIC_KEY)


def create_agents():
    """Buat semua agent PETER"""
    llm      = get_llm(fast=False)
    llm_fast = get_llm(fast=True)

    manager = Agent(
        role      = "PETER Manager",
        goal      = "Koordinasi semua agent untuk hasil terbaik",
        backstory  = f"AI manager milik {USER_NAME}. Selalu memberikan hasil yang actionable.",
        llm       = llm,
        verbose   = True
    )

    researcher = Agent(
        role      = "Research Specialist",
        goal      = "Cari informasi akurat dan terkini dari internet",
        backstory  = "Expert researcher dengan kemampuan analisis mendalam.",
        tools     = [web_search, get_trending_topics],
        llm       = llm,
        verbose   = True
    )

    writer = Agent(
        role      = "Content Writer & Copywriter",
        goal      = "Tulis konten viral yang engaging dan convert",
        backstory  = "Penulis konten profesional YouTube, Instagram, TikTok.",
        tools     = [save_text_file],
        llm       = llm,
        verbose   = True
    )

    analyst = Agent(
        role      = "Data & Business Analyst",
        goal      = "Analisis data dan berikan insight bisnis actionable",
        backstory  = "Data analyst berpengalaman dengan keahlian bisnis digital.",
        llm       = llm_fast,
        verbose   = True
    )

    strategist = Agent(
        role      = "Digital Marketing Strategist",
        goal      = "Buat strategi digital marketing dengan ROI tertinggi",
        backstory  = "Expert monetisasi konten dan digital marketing.",
        tools     = [web_search],
        llm       = llm,
        verbose   = True
    )

    return {
        "manager"    : manager,
        "researcher" : researcher,
        "writer"     : writer,
        "analyst"    : analyst,
        "strategist" : strategist
    }


def run_crew(task_description: str,
             agent_type: str = "auto") -> str:
    """Jalankan CrewAI dengan task tertentu"""
    agents = create_agents()

    # Auto pilih agent terbaik
    if agent_type == "auto":
        td = task_description.lower()
        if any(w in td for w in ["riset","cari","search","trending"]):
            primary = agents["researcher"]
        elif any(w in td for w in ["tulis","script","konten","caption"]):
            primary = agents["writer"]
        elif any(w in td for w in ["analisis","data","revenue","angka"]):
            primary = agents["analyst"]
        elif any(w in td for w in ["strategi","marketing","monetisasi","growth"]):
            primary = agents["strategist"]
        else:
            primary = agents["manager"]
    else:
        primary = agents.get(agent_type, agents["manager"])

    task = Task(
        description     = f"{task_description}\n\nGunakan Bahasa Indonesia. Berikan hasil LENGKAP dan ACTIONABLE.",
        agent           = primary,
        expected_output = "Hasil lengkap dalam Bahasa Indonesia"
    )

    crew = Crew(
        agents  = list(agents.values()),
        tasks   = [task],
        process = Process.sequential,
        verbose = True
    )

    result = crew.kickoff()

    # Simpan hasil
    output_file = "C:\\peter-ai\\crew_output.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Task: {task_description}\n\n")
        f.write(str(result))

    return str(result)