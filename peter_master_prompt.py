"""
peter_master_prompt.py
PETER Master Prompt Intelligence Engine
Framework: OODA + SWOT + VUCA + E2E
Kemampuan: Semua domain prompt generation
"""

import os
import sys
import json
import time
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
USER_NAME     = os.getenv("USER_NAME", "Sir")
OUTPUT_DIR    = "C:\\peter-ai\\data\\outputs\\master_prompts"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# CORE INTELLIGENCE — 4 FRAMEWORK ANALYSIS
# ============================================================

def analyze_problem(problem: str,
                    context: str = "",
                    domain: str = "general") -> dict:
    """
    Analisis problem dengan 4 framework
    Dibagi 2 request agar tidak terpotong
    """
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    print(f"\n[MASTER] Analisis Part 1: OODA + SWOT...")

    # ── PART 1: OODA + SWOT ──────────────────────────────
    r1 = client.messages.create(
        model      = "claude-sonnet-4-6",
        max_tokens = 3000,
        system     = """Analisis dengan OODA dan SWOT framework.
Return ONLY valid JSON, no explanation, no trailing commas.
Semua string value harus dalam double quotes.
Tidak boleh ada newline dalam string value.""",
        messages   = [{
            "role"   : "user",
            "content": f"""Analisis ini dengan OODA + SWOT:
Problem: {problem}
Context: {context}
Domain: {domain}

Return JSON:
{{
  "problem_essence": "inti masalah 1 kalimat",
  "domain": "{domain}",
  "complexity": "sedang",
  "ooda": {{
    "observe": {{
      "facts": ["fakta1", "fakta2"],
      "stakeholders": ["pihak1", "pihak2"]
    }},
    "orient": {{
      "mental_models": ["model1", "model2"],
      "context_factors": ["faktor1", "faktor2"]
    }},
    "decide": {{
      "options": ["opsi1", "opsi2"],
      "recommended": "opsi terbaik"
    }},
    "act": {{
      "immediate": ["aksi segera 1", "aksi segera 2"],
      "short_term": ["aksi minggu 1", "aksi minggu 2"],
      "long_term": ["aksi bulan 1", "aksi bulan 2"]
    }}
  }},
  "swot": {{
    "strengths": ["kekuatan1", "kekuatan2"],
    "weaknesses": ["kelemahan1", "kelemahan2"],
    "opportunities": ["peluang1", "peluang2"],
    "threats": ["ancaman1", "ancaman2"],
    "so_strategy": "gunakan strength untuk opportunity",
    "st_strategy": "gunakan strength hadapi threat",
    "wo_strategy": "atasi weakness dengan opportunity",
    "wt_strategy": "minimalkan weakness dan threat"
  }}
}}"""
        }]
    )

    print(f"[MASTER] Analisis Part 2: VUCA + E2E + Synthesis...")

    # ── PART 2: VUCA + E2E + SYNTHESIS ───────────────────
    r2 = client.messages.create(
        model      = "claude-sonnet-4-6",
        max_tokens = 3000,
        system     = """Analisis dengan VUCA dan E2E framework.
Return ONLY valid JSON, no explanation, no trailing commas.
Semua string value dalam double quotes.
Tidak boleh ada newline dalam string value.""",
        messages   = [{
            "role"   : "user",
            "content": f"""Analisis dengan VUCA + E2E + Synthesis:
Problem: {problem}
Context: {context}

Return JSON:
{{
  "vuca": {{
    "volatility": {{
      "level": "sedang",
      "factors": ["faktor1"],
      "response": "strategi volatilitas"
    }},
    "uncertainty": {{
      "level": "tinggi",
      "unknowns": ["ketidakpastian1"],
      "response": "strategi uncertainty"
    }},
    "complexity": {{
      "level": "sedang",
      "variables": ["variabel1"],
      "response": "strategi kompleksitas"
    }},
    "ambiguity": {{
      "level": "rendah",
      "unclear_aspects": ["aspek1"],
      "response": "strategi ambiguitas"
    }},
    "vuca_prime": {{
      "vision": "visi counter volatility",
      "understanding": "pemahaman counter uncertainty",
      "clarity": "kejelasan counter complexity",
      "agility": "kelincahan counter ambiguity"
    }}
  }},
  "e2e": {{
    "start_state": "kondisi awal sekarang",
    "end_state": "kondisi akhir yang diinginkan",
    "gap_analysis": "gap antara now dan goal",
    "phases": [
      {{
        "phase": "Phase 1",
        "name": "Foundation",
        "duration": "1-2 minggu",
        "actions": ["aksi1", "aksi2"],
        "deliverables": ["output1"],
        "success_metrics": ["metrik1"]
      }},
      {{
        "phase": "Phase 2",
        "name": "Execution",
        "duration": "1-2 bulan",
        "actions": ["aksi1", "aksi2"],
        "deliverables": ["output1"],
        "success_metrics": ["metrik1"]
      }},
      {{
        "phase": "Phase 3",
        "name": "Optimization",
        "duration": "3-6 bulan",
        "actions": ["aksi1"],
        "deliverables": ["output1"],
        "success_metrics": ["metrik1"]
      }}
    ],
    "risks": ["risiko1", "risiko2"],
    "mitigation": ["mitigasi1", "mitigasi2"]
  }},
  "synthesis": {{
    "key_insight": "insight paling penting",
    "root_cause": "akar masalah utama",
    "leverage_point": "titik leverage terbaik",
    "quick_win": "kemenangan cepat yang bisa dilakukan",
    "north_star": "tujuan akhir yang menginspirasi"
  }}
}}"""
        }]
    )

    # ── PARSE KEDUA RESPONSE ──────────────────────────────
    import re

    def safe_parse(text: str) -> dict:
        text = re.sub(r'```json|```', '', text).strip()

        # Fix common JSON issues
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        text = re.sub(r'\n', ' ', text)
        text = re.sub(r'\t', ' ', text)
        text = re.sub(r' {2,}', ' ', text)

        try:
            return json.loads(text)
        except Exception as e:
            # Coba extract JSON dari teks
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
            print(f"[MASTER] JSON parse warning: {e}")
            return {}

    part1 = safe_parse(r1.content[0].text)
    part2 = safe_parse(r2.content[0].text)

    # Gabungkan kedua hasil
    result = {
        "problem_essence": part1.get("problem_essence", problem[:80]),
        "domain"         : part1.get("domain", domain),
        "complexity"     : part1.get("complexity", "sedang"),
        "ooda"           : part1.get("ooda", {}),
        "swot"           : part1.get("swot", {}),
        "vuca"           : part2.get("vuca", {}),
        "e2e"            : part2.get("e2e", {}),
        "synthesis"      : part2.get("synthesis", {})
    }

    # Fallback jika parse gagal
    if not result["ooda"]:
        result["ooda"] = {
            "observe" : {"facts": [problem], "stakeholders": []},
            "orient"  : {"mental_models": [], "context_factors": []},
            "decide"  : {"options": [], "recommended": "Analisis lebih lanjut"},
            "act"     : {
                "immediate" : ["Definisikan scope"],
                "short_term": ["Buat rencana aksi"],
                "long_term" : ["Evaluasi hasil"]
            }
        }

    if not result["synthesis"]:
        result["synthesis"] = {
            "key_insight"   : f"Problem utama: {problem[:50]}",
            "root_cause"    : "Perlu analisis lebih dalam",
            "leverage_point": "Fokus pada quick win dulu",
            "quick_win"     : "Mulai dengan langkah terkecil",
            "north_star"    : f"Solusi optimal untuk {domain}"
        }

    print(f"[MASTER] Analisis selesai: {result['domain']}")
    return result


def generate_master_prompt(problem: str,
                            analysis: dict,
                            prompt_type: str,
                            specifications: dict = None) -> str:
    """
    Generate prompt terbaik berdasarkan analisis 4 framework
    """
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    print(f"\n[MASTER] Generating {prompt_type} prompt...")

    synthesis  = analysis.get("synthesis", {})
    ooda_act   = analysis.get("ooda", {}).get("act", {})
    swot       = analysis.get("swot", {})
    e2e_phases = analysis.get("e2e", {}).get("phases", [])
    vuca_prime = analysis.get("vuca", {}).get("vuca_prime", {})

    specs_str = json.dumps(
        specifications or {}, ensure_ascii=False
    )

    response = client.messages.create(
        model      = "claude-sonnet-4-6",
        max_tokens = 8096,
        system     = f"""Kamu adalah master prompt engineer kelas dunia.
Tugasmu: transform analisis strategic menjadi prompt yang sempurna.

Kamu menguasai semua domain prompt:
- AI Image Generation (Midjourney, DALL-E, Stable Diffusion)
- AI Video Generation (Runway, Kling, Pika, Sora)
- AI Coding (GitHub Copilot, Claude, GPT-4)
- AI Writing (artikel, copywriting, script)
- AI Business Strategy
- AI Research & Analysis
- AI Education & Training
- AI Healthcare (non-medical advice)
- AI Legal (non-legal advice)
- AI Finance (non-financial advice)
- AI Creative Arts
- AI Music & Audio
- AI Architecture & Design
- AI Marketing & Sales
- AI HR & Recruitment
- AI Data Science & Analytics
- AI Product Management
- AI Customer Service
- AI Supply Chain
- AI Real Estate
- AI Agriculture

PRINSIP PROMPT ENGINEERING MASTER:
1. Specificity — Sangat spesifik, tidak ambigu
2. Context-Rich — Berikan konteks yang cukup
3. Role Assignment — Tetapkan peran yang jelas
4. Constraint Clarity — Batasan yang jelas
5. Output Format — Format output yang diinginkan
6. Quality Markers — Indikator kualitas yang diinginkan
7. Negative Prompting — Apa yang tidak diinginkan
8. Chain of Thought — Mendorong reasoning bertahap
9. Few-Shot Examples — Contoh jika diperlukan
10. Iterative Refinement — Prompt yang bisa diiterasi

Synthesis dari analisis:
- Key Insight: {synthesis.get('key_insight', '')}
- Root Cause: {synthesis.get('root_cause', '')}
- Leverage Point: {synthesis.get('leverage_point', '')}
- North Star: {synthesis.get('north_star', '')}

VUCA Prime Response:
- Vision: {vuca_prime.get('vision', '')}
- Understanding: {vuca_prime.get('understanding', '')}
- Clarity: {vuca_prime.get('clarity', '')}
- Agility: {vuca_prime.get('agility', '')}

SWOT Strategy:
- SO: {swot.get('so_strategy', '')}
- ST: {swot.get('st_strategy', '')}""",

        messages = [{
            "role"   : "user",
            "content": f"""Generate master prompt untuk:

PROBLEM   : {problem}
TYPE      : {prompt_type}
SPECS     : {specs_str}

OODA Actions:
- Immediate: {ooda_act.get('immediate', [])}
- Short-term: {ooda_act.get('short_term', [])}

E2E Phases: {json.dumps(e2e_phases[:2], ensure_ascii=False)}

Buat prompt yang:
1. SANGAT SPESIFIK dan detail
2. Mencakup semua aspek E2E
3. Berdasarkan insight dari OODA + SWOT + VUCA
4. Actionable dan bisa langsung dieksekusi
5. Berkualitas tinggi dan profesional
6. Dalam Bahasa Indonesia (kecuali untuk AI tools yang butuh English)

Format output:
## MASTER PROMPT

### ROLE & CONTEXT
[definisi peran dan konteks]

### OBJECTIVE
[tujuan yang ingin dicapai]

### SPECIFICATIONS
[spesifikasi detail]

### CONSTRAINTS
[batasan dan rules]

### OUTPUT FORMAT
[format output yang diinginkan]

### QUALITY CRITERIA
[kriteria kualitas]

### EXAMPLES (jika relevan)
[contoh output yang diinginkan]

### NEGATIVE PROMPTS
[hal yang harus dihindari]

### CHAIN OF THOUGHT
[langkah berpikir yang harus diikuti]

---
## VARIASI PROMPT

### VARIASI 1 (Lebih Detail):
[versi lebih detail]

### VARIASI 2 (Lebih Singkat):
[versi lebih singkat]

### VARIASI 3 (Bahasa Inggris untuk AI Tools):
[versi English untuk Midjourney/Runway/dll]"""
        }]
    )

    return response.content[0].text


# ============================================================
# DOMAIN-SPECIFIC PROMPT GENERATORS
# ============================================================

DOMAINS = {
    "1" : ("Video & Film",          "video"),
    "2" : ("Iklan & Marketing",     "marketing"),
    "3" : ("Aplikasi & Software",   "software"),
    "4" : ("Bisnis & Strategi",     "business"),
    "5" : ("Riset & Analisis",      "research"),
    "6" : ("Pendidikan & Training", "education"),
    "7" : ("Desain & Kreatif",      "design"),
    "8" : ("AI Image Generation",   "image_gen"),
    "9" : ("Penulisan & Konten",    "writing"),
    "10": ("Data Science & AI",     "data_science"),
    "11": ("Produk & Inovasi",      "product"),
    "12": ("HR & Organisasi",       "hr"),
    "13": ("Keuangan & Investasi",  "finance"),
    "14": ("Kesehatan & Wellness",  "health"),
    "15": ("Hukum & Compliance",    "legal"),
    "16": ("Real Estate & Properti","realestate"),
    "17": ("Pertanian & Agritech",  "agritech"),
    "18": ("E-Commerce & Retail",   "ecommerce"),
    "19": ("Customer Experience",   "cx"),
    "20": ("Supply Chain & Ops",    "ops"),
    "21": ("Personal Development",  "personal"),
    "22": ("Game Development",      "gamedev"),
    "23": ("Musik & Audio",         "music"),
    "24": ("Arsitektur & Interior", "architecture"),
    "25": ("Lingkungan & Energi",   "environment"),
    "0" : ("Custom Domain",         "custom"),
}


def get_domain_context(domain: str) -> str:
    """Context spesifik per domain"""
    contexts = {
        "video"       : "Fokus pada storytelling visual, cinematography, pacing, dan emotional impact",
        "marketing"   : "Fokus pada conversion, persuasion, target audience psychology, dan ROI",
        "software"    : "Fokus pada user experience, scalability, security, dan maintainability",
        "business"    : "Fokus pada profitability, market fit, competitive advantage, dan sustainability",
        "research"    : "Fokus pada methodology, objectivity, validity, dan actionable insights",
        "education"   : "Fokus pada learning outcomes, engagement, retention, dan practical application",
        "design"      : "Fokus pada aesthetics, functionality, user psychology, dan brand consistency",
        "image_gen"   : "Fokus pada visual elements, style references, technical parameters, dan artistic direction",
        "writing"     : "Fokus pada clarity, engagement, SEO, dan reader value",
        "data_science": "Fokus pada accuracy, interpretability, bias mitigation, dan business impact",
        "product"     : "Fokus pada user needs, market timing, differentiation, dan go-to-market",
        "hr"          : "Fokus pada culture fit, skill assessment, diversity, dan retention",
        "finance"     : "Fokus pada risk management, return optimization, dan regulatory compliance",
        "health"      : "Fokus pada evidence-based, safety, accessibility, dan behavior change",
        "legal"       : "Fokus pada compliance, risk mitigation, clarity, dan jurisdictional relevance",
        "realestate"  : "Fokus pada location value, market trends, ROI, dan regulatory compliance",
        "agritech"    : "Fokus pada sustainability, yield optimization, dan farmer adoption",
        "ecommerce"   : "Fokus pada conversion funnel, customer lifetime value, dan logistics",
        "cx"          : "Fokus pada customer journey, touchpoints, NPS, dan resolution speed",
        "ops"         : "Fokus pada efficiency, cost reduction, resilience, dan visibility",
        "personal"    : "Fokus pada habit formation, motivation, accountability, dan measurable growth",
        "gamedev"     : "Fokus pada game mechanics, player psychology, monetization, dan performance",
        "music"       : "Fokus pada composition, production quality, emotional resonance, dan distribution",
        "architecture": "Fokus pada functionality, aesthetics, sustainability, dan code compliance",
        "environment" : "Fokus pada impact measurement, scalability, adoption, dan policy alignment",
        "custom"      : "Analisis mendalam untuk solusi yang paling optimal"
    }
    return contexts.get(domain, contexts["custom"])


def save_master_prompt(problem: str,
                       analysis: dict,
                       prompt: str,
                       domain: str) -> str:
    """Simpan master prompt ke file"""
    timestamp = int(time.time())
    filename  = f"master_{domain}_{timestamp}.txt"
    path      = os.path.join(OUTPUT_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("  PETER MASTER PROMPT — E2E + OODA + SWOT + VUCA\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"PROBLEM : {problem}\n")
        f.write(f"DOMAIN  : {domain}\n")
        f.write(f"WAKTU   : {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        # Synthesis
        synth = analysis.get("synthesis", {})
        if synth:
            f.write("SYNTHESIS:\n")
            for k, v in synth.items():
                f.write(f"  {k}: {v}\n")
            f.write("\n")

        # SWOT Summary
        swot = analysis.get("swot", {})
        if swot:
            f.write("SWOT:\n")
            for k in ['strengths', 'weaknesses', 'opportunities', 'threats']:
                items = swot.get(k, [])
                if items:
                    f.write(f"  {k.upper()}: {', '.join(items[:2])}\n")
            f.write("\n")

        # Master Prompt
        f.write("=" * 70 + "\n")
        f.write("MASTER PROMPT:\n")
        f.write("=" * 70 + "\n\n")
        f.write(prompt)

    print(f"\n[MASTER] Disimpan: {path}")
    return path


# ============================================================
# INTERACTIVE MENU
# ============================================================

def run_master_prompt():
    """Menu utama Master Prompt Engine"""

    print("\n" + "═" * 65)
    print("  ██████╗ ███████╗████████╗███████╗██████╗ ")
    print("  ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗")
    print("  ██████╔╝█████╗     ██║   █████╗  ██████╔╝")
    print("  ██╔═══╝ ██╔══╝     ██║   ██╔══╝  ██╔══██╗")
    print("  ██║     ███████╗   ██║   ███████╗██║  ██║")
    print("  ╚═╝     ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝")
    print("\n  MASTER PROMPT INTELLIGENCE ENGINE")
    print("  Framework: OODA + SWOT + VUCA + E2E")
    print("═" * 65)

    while True:
        print("\n" + "─" * 65)
        print("  MENU UTAMA")
        print("─" * 65)
        print("  [1]  Generate Master Prompt (dari problem)")
        print("  [2]  Quick Prompt Generator (pilih domain)")
        print("  [3]  Analisis Mendalam (4 Framework)")
        print("  [4]  Prompt Battle (bandingkan 2 approach)")
        print("  [5]  Prompt Chain Builder")
        print("  [6]  Lihat prompt tersimpan")
        print("  [7]  Prompt dari Dokumen/File")
        print("  [0]  Kembali ke PETER")
        print("─" * 65)

        pilihan = input(f"\n[{USER_NAME}] Pilih: ").strip()

        if pilihan == "1":
            _menu_master_prompt()

        elif pilihan == "2":
            _menu_quick_prompt()

        elif pilihan == "3":
            _menu_deep_analysis()

        elif pilihan == "4":
            _menu_prompt_battle()

        elif pilihan == "5":
            _menu_prompt_chain()

        elif pilihan == "6":
            _menu_view_prompts()

        elif pilihan == "7":
            _menu_prompt_from_file()

        elif pilihan == "0":
            break


def _menu_master_prompt():
    """Generate master prompt dari problem"""
    print("\n" + "─" * 55)
    print("  MASTER PROMPT GENERATOR")
    print("  Input problem → Analisis 4 Framework → Prompt Terbaik")
    print("─" * 55)

    # Pilih domain
    print("\nPilih domain:")
    items = list(DOMAINS.items())
    for i in range(0, len(items), 2):
        a = items[i]
        b = items[i+1] if i+1 < len(items) else ("", ("", ""))
        print(f"  [{a[0]:2}] {a[1][0]:25}  [{b[0]:2}] {b[1][0]}")

    domain_key = input("\nDomain (default=0 custom): ").strip() or "0"
    domain_info = DOMAINS.get(domain_key, DOMAINS["0"])
    domain_name = domain_info[0]
    domain_key2 = domain_info[1]

    print(f"\nDomain: {domain_name}")
    print(f"Context: {get_domain_context(domain_key2)}\n")

    # Input problem
    print("Deskripsikan problem atau kebutuhan kamu.")
    print("Semakin detail semakin bagus!\n")
    problem = input("Problem/Kebutuhan: ").strip()
    if not problem:
        return

    context = input("Context tambahan (opsional): ").strip()

    # Spesifikasi tambahan
    print("\nSpesifikasi tambahan (opsional):")
    target   = input("  Target audience: ").strip()
    platform = input("  Platform/media : ").strip()
    budget   = input("  Budget/resource: ").strip()
    timeline = input("  Timeline       : ").strip()
    kpi      = input("  KPI/success    : ").strip()

    specs = {}
    if target  : specs["target_audience"] = target
    if platform: specs["platform"]         = platform
    if budget  : specs["budget"]            = budget
    if timeline: specs["timeline"]          = timeline
    if kpi     : specs["success_metrics"]   = kpi

    print("\n" + "═" * 55)
    print("  PETER sedang berpikir dengan 4 framework...")
    print("  OODA → SWOT → VUCA → E2E → Master Prompt")
    print("═" * 55)

    # Analisis
    full_context = f"{context}\nDomain: {domain_name}\n{get_domain_context(domain_key2)}"
    analysis     = analyze_problem(problem, full_context, domain_name)

    if "error" in analysis:
        print(f"Analisis gagal: {analysis['error']}")
        return

    # Tampilkan synthesis
    synth = analysis.get("synthesis", {})
    print(f"\n{'─'*55}")
    print("  SYNTHESIS ANALISIS:")
    print(f"{'─'*55}")
    print(f"  Inti     : {synth.get('problem_essence', problem[:50])}")
    print(f"  Insight  : {synth.get('key_insight', '')[:60]}")
    print(f"  Root     : {synth.get('root_cause', '')[:60]}")
    print(f"  Leverage : {synth.get('leverage_point', '')[:60]}")
    print(f"  Quick Win: {synth.get('quick_win', '')[:60]}")
    print(f"  North ★  : {synth.get('north_star', '')[:60]}")

    # SWOT summary
    swot = analysis.get("swot", {})
    print(f"\n  SWOT:")
    print(f"  S: {', '.join(swot.get('strengths', [])[:2])}")
    print(f"  W: {', '.join(swot.get('weaknesses', [])[:2])}")
    print(f"  O: {', '.join(swot.get('opportunities', [])[:2])}")
    print(f"  T: {', '.join(swot.get('threats', [])[:2])}")

    # VUCA
    vuca = analysis.get("vuca", {})
    vuca_prime = vuca.get("vuca_prime", {})
    print(f"\n  VUCA Prime:")
    print(f"  Vision    : {vuca_prime.get('vision', '')[:50]}")
    print(f"  Agility   : {vuca_prime.get('agility', '')[:50]}")

    lanjut = input("\n\nLanjut generate Master Prompt? (y/n): ").strip().lower()
    if lanjut != 'y':
        return

    # Generate prompt
    prompt_type = f"{domain_name} prompt"
    master      = generate_master_prompt(
        problem, analysis, prompt_type, specs
    )

    print(f"\n{'═'*65}")
    print("  MASTER PROMPT HASIL:")
    print(f"{'═'*65}")
    print(master)

    # Simpan
    save = input("\n\nSimpan prompt? (y/n): ").strip().lower()
    if save == 'y':
        path = save_master_prompt(
            problem, analysis, master, domain_key2
        )
        buka = input("Buka file? (y/n): ").strip().lower()
        if buka == 'y':
            os.startfile(path.replace("/", "\\"))

    # Langsung eksekusi?
    if domain_key2 in ["software", "data_science", "gamedev"]:
        build = input("\nLangsung build dengan PETER App Builder? (y/n): ").strip().lower()
        if build == 'y':
            from peter_app_builder import build_app
            build_app(problem)

    elif domain_key2 in ["video", "image_gen", "music"]:
        gen = input("\nLangsung generate video/image? (y/n): ").strip().lower()
        if gen == 'y':
            from content.pro_video_engine import RunwayBRoll, generate_broll_prompts
            runway  = RunwayBRoll()
            prompts = generate_broll_prompts(master, problem, 3)
            clips   = runway.generate_multiple_clips(prompts, duration_each=5)
            print(f"\n✅ Generated {len(clips)} clips!")


def _menu_quick_prompt():
    """Quick prompt generator tanpa deep analysis"""
    print("\nQuick Prompt — pilih domain dan input:")

    print("\nDomain:")
    for k, v in list(DOMAINS.items())[:15]:
        print(f"  [{k:2}] {v[0]}")

    domain_key  = input("\nDomain: ").strip() or "0"
    domain_info = DOMAINS.get(domain_key, DOMAINS["0"])
    domain_name = domain_info[0]

    request = input(f"\nRequest untuk {domain_name}: ").strip()
    if not request:
        return

    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    print("\n[PETER] Generating prompt...")
    response = client.messages.create(
        model      = "claude-sonnet-4-6",
        max_tokens = 3000,
        system     = f"""Kamu adalah master prompt engineer untuk {domain_name}.
Buat prompt yang sangat detail, spesifik, dan actionable.
Sertakan: Role, Context, Task, Format, Quality criteria.
Bahasa Indonesia kecuali untuk AI tools yang butuh English.""",
        messages = [{
            "role"   : "user",
            "content": f"Buat master prompt untuk: {request}\nDomain: {domain_name}"
        }]
    )

    result = response.content[0].text
    print(f"\n{'═'*55}")
    print(result)
    print(f"{'═'*55}")

    save = input("\nSimpan? (y/n): ").strip().lower()
    if save == 'y':
        path = os.path.join(
            OUTPUT_DIR,
            f"quick_{domain_info[1]}_{int(time.time())}.txt"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Domain : {domain_name}\n")
            f.write(f"Request: {request}\n\n")
            f.write(result)
        print(f"Disimpan: {path}")
        os.startfile(path.replace("/", "\\"))


def _menu_deep_analysis():
    """Analisis mendalam dengan 4 framework"""
    print("\nANALISIS MENDALAM — OODA + SWOT + VUCA + E2E")
    print("Masukkan situasi, masalah, atau keputusan yang ingin dianalisis.\n")

    problem = input("Problem/Situasi: ").strip()
    context = input("Context: ").strip()
    domain  = input("Domain (opsional): ").strip() or "general"

    if not problem:
        return

    analysis = analyze_problem(problem, context, domain)

    if "error" in analysis:
        print(f"Error: {analysis['error']}")
        return

    # Tampilkan analisis lengkap
    print(f"\n{'═'*65}")
    print("  ANALISIS LENGKAP 4 FRAMEWORK")
    print(f"{'═'*65}")

    # OODA
    ooda = analysis.get("ooda", {})
    print("\n📊 OODA:")
    print(f"  Observe  : {', '.join(ooda.get('observe',{}).get('facts',[])[:2])}")
    print(f"  Orient   : {', '.join(ooda.get('orient',{}).get('mental_models',[])[:2])}")
    print(f"  Decide   : {ooda.get('decide',{}).get('recommended','')}")
    print(f"  Act Now  : {', '.join(ooda.get('act',{}).get('immediate',[])[:2])}")

    # SWOT
    swot = analysis.get("swot", {})
    print("\n📈 SWOT:")
    for k in ['strengths','weaknesses','opportunities','threats']:
        items = swot.get(k, [])[:2]
        print(f"  {k[:1].upper()}: {', '.join(items)}")
    print(f"\n  Strategi SO: {swot.get('so_strategy','')[:60]}")
    print(f"  Strategi WT: {swot.get('wt_strategy','')[:60]}")

    # VUCA
    vuca = analysis.get("vuca", {})
    print("\n⚡ VUCA:")
    for aspect in ['volatility','uncertainty','complexity','ambiguity']:
        data = vuca.get(aspect, {})
        print(f"  {aspect[:1].upper()}: Level={data.get('level','')} | {data.get('response','')[:40]}")

    vuca_prime = vuca.get("vuca_prime", {})
    print(f"\n  VUCA Prime Vision : {vuca_prime.get('vision','')[:60]}")
    print(f"  VUCA Prime Agility: {vuca_prime.get('agility','')[:60]}")

    # E2E
    e2e = analysis.get("e2e", {})
    print("\n🎯 E2E:")
    print(f"  Start : {e2e.get('start_state','')[:50]}")
    print(f"  End   : {e2e.get('end_state','')[:50]}")
    print(f"  Gap   : {e2e.get('gap_analysis','')[:50]}")
    phases = e2e.get("phases", [])
    for p in phases[:3]:
        print(f"  Phase : {p.get('name','')} ({p.get('duration','')})")

    # Synthesis
    synth = analysis.get("synthesis", {})
    print(f"\n💡 SYNTHESIS:")
    print(f"  North Star  : {synth.get('north_star','')}")
    print(f"  Leverage    : {synth.get('leverage_point','')}")
    print(f"  Quick Win   : {synth.get('quick_win','')}")

    save = input("\nSimpan + Generate prompt? (y/n): ").strip().lower()
    if save == 'y':
        prompt = generate_master_prompt(problem, analysis, domain)
        path   = save_master_prompt(problem, analysis, prompt, domain)
        os.startfile(path.replace("/", "\\"))


def _menu_prompt_battle():
    """Bandingkan 2 approach prompt"""
    print("\nPROMPT BATTLE — Bandingkan 2 approach")

    problem    = input("Problem: ").strip()
    approach_a = input("Approach A: ").strip()
    approach_b = input("Approach B: ").strip()

    if not all([problem, approach_a, approach_b]):
        return

    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    print("\n[PETER] Generating dan membandingkan...")
    response = client.messages.create(
        model      = "claude-sonnet-4-6",
        max_tokens = 4000,
        system     = """Kamu adalah prompt engineer expert.
Bandingkan 2 approach dan rekomendasikan yang terbaik.
Analisis: effectiveness, clarity, completeness, practicality.""",
        messages = [{
            "role"   : "user",
            "content": f"""Problem: {problem}

Approach A: {approach_a}
Approach B: {approach_b}

1. Generate prompt terbaik untuk masing-masing approach
2. Bandingkan kelebihan dan kekurangan
3. Rekomendasikan approach terbaik dengan alasan
4. Buat hybrid prompt yang menggabungkan yang terbaik dari keduanya"""
        }]
    )

    print(f"\n{'═'*55}")
    print(response.content[0].text)


def _menu_prompt_chain():
    """Build prompt chain untuk task kompleks"""
    print("\nPROMPT CHAIN BUILDER")
    print("Untuk task kompleks yang butuh beberapa langkah\n")

    goal      = input("Goal akhir yang ingin dicapai: ").strip()
    steps_str = input("Jumlah langkah (default 5): ").strip()
    steps     = int(steps_str) if steps_str.isdigit() else 5

    if not goal:
        return

    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    print(f"\n[PETER] Building {steps}-step prompt chain...")
    response = client.messages.create(
        model      = "claude-sonnet-4-6",
        max_tokens = 5000,
        system     = """Kamu adalah prompt chain architect.
Buat chain of prompts yang saling terhubung untuk mencapai goal kompleks.
Setiap prompt harus menggunakan output prompt sebelumnya sebagai input.""",
        messages = [{
            "role"   : "user",
            "content": f"""Buat {steps}-step prompt chain untuk:
Goal: {goal}

Format setiap step:
STEP [N]: [nama step]
PROMPT: [prompt lengkap]
INPUT: [menggunakan output dari step sebelumnya]
OUTPUT: [apa yang dihasilkan]
NEXT: [bagaimana connect ke step berikutnya]"""
        }]
    )

    print(f"\n{'═'*55}")
    print(response.content[0].text)

    save = input("\nSimpan chain? (y/n): ").strip().lower()
    if save == 'y':
        path = os.path.join(
            OUTPUT_DIR,
            f"chain_{int(time.time())}.txt"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Goal: {goal}\n\n")
            f.write(response.content[0].text)
        print(f"Disimpan: {path}")


def _menu_view_prompts():
    """Lihat dan kelola prompt tersimpan"""
    files = sorted(os.listdir(OUTPUT_DIR), reverse=True)

    if not files:
        print("\nBelum ada prompt tersimpan.")
        return

    print(f"\nPrompt tersimpan ({len(files)}):")
    for i, f in enumerate(files[:20], 1):
        size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
        print(f"  {i:2}. {f} ({size:,} bytes)")

    idx = input("\nBuka nomor berapa? (Enter skip): ").strip()
    if idx.isdigit() and 1 <= int(idx) <= len(files):
        path = os.path.join(OUTPUT_DIR, files[int(idx)-1])
        os.startfile(path.replace("/", "\\"))


def _menu_prompt_from_file():
    """Generate prompt dari dokumen yang diupload"""
    print("\nPROMPT DARI FILE/DOKUMEN")
    filepath = input("Path file (txt/pdf/docx): ").strip()

    if not os.path.exists(filepath):
        print(f"File tidak ditemukan: {filepath}")
        return

    try:
        # Baca file
        if filepath.endswith('.txt'):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        elif filepath.endswith('.pdf'):
            import subprocess
            r = subprocess.run(
                [sys.executable, '-c',
                 f'import pdfminer.high_level; print(pdfminer.high_level.extract_text("{filepath}"))'],
                capture_output=True, text=True
            )
            content = r.stdout
        else:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

        content = content[:5000]  # Limit
        goal    = input("Apa yang ingin dilakukan dengan dokumen ini? ").strip()

        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

        response = client.messages.create(
            model    = "claude-sonnet-4-6",
            max_tokens = 3000,
            system   = "Buat prompt terbaik berdasarkan konten dokumen.",
            messages = [{
                "role"   : "user",
                "content": f"Dokumen:\n{content}\n\nGoal: {goal}\n\nBuat master prompt:"
            }]
        )
        print(f"\n{'═'*55}")
        print(response.content[0].text)

    except Exception as e:
        print(f"Error: {e}")


# ============================================================
# TAMBAHKAN KE MAIN PETER
# ============================================================
if __name__ == "__main__":
    run_master_prompt()