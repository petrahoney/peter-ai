# ============================================================
#   PETER AI v2.0 — Complete System Final
#   Self-Heal + Code Engine + CrewAI + Voice + Vision + Memory
# ============================================================

from dotenv import load_dotenv
import os
import sys
import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

load_dotenv()

ANTHROPIC_KEY    = os.getenv("ANTHROPIC_API_KEY", "")
ELEVENLABS_KEY   = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE_ID", "TIXYCOMzK2Vw9OZovSLs")
OLLAMA_URL       = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LOCAL_MODE       = os.getenv("LOCAL_MODE", "false").lower() == "true"
USER_NAME        = os.getenv("USER_NAME", "Sir")

if not LOCAL_MODE and not ANTHROPIC_KEY:
    print("ERROR: ANTHROPIC_API_KEY tidak ditemukan!")
    sys.exit(1)

os.makedirs("C:\\peter-ai\\data\\outputs", exist_ok=True)
os.makedirs("C:\\peter-ai\\data\\memory",  exist_ok=True)
os.makedirs("C:\\peter-ai\\data\\faces",   exist_ok=True)
os.makedirs("C:\\peter-ai\\data\\logs",    exist_ok=True)

# ── Self-Heal ─────────────────────────────────────────────
try:
    from peter_self_heal import PeterSelfHeal
    healer  = PeterSelfHeal()
    HEAL_OK = True
    print("[PETER] Self-Heal OK!")
except Exception as e:
    HEAL_OK = False
    healer  = None
    print(f"[PETER] Self-Heal tidak aktif: {e}")

# ── Vision ────────────────────────────────────────────────
try:
    from peter_vision import PeterVision
    vision    = PeterVision()
    VISION_OK = True
    print("[PETER] Vision OK!")
except Exception as e:
    VISION_OK = False
    vision    = None
    print(f"[PETER] Vision tidak aktif: {e}")

# ── Memory ────────────────────────────────────────────────
try:
    from peter_memory import PeterMemory
    memory    = PeterMemory()
    MEMORY_OK = True
    print("[PETER] Memory OK!")
except Exception as e:
    MEMORY_OK = False
    memory    = None
    print(f"[PETER] Memory tidak aktif: {e}")


# ============================================================
# VOICE OUTPUT
# ============================================================
def peter_speak(text: str):
    if not text or not text.strip():
        return
    try:
        from elevenlabs import ElevenLabs, VoiceSettings
        client = ElevenLabs(api_key=ELEVENLABS_KEY)
        audio  = client.text_to_speech.convert(
            voice_id       = ELEVENLABS_VOICE,
            text           = text[:500],
            model_id       = "eleven_multilingual_v2",
            voice_settings = VoiceSettings(
                stability        = 0.45,
                similarity_boost = 0.82,
                style            = 0.5,
                use_speaker_boost= True
            )
        )
        audio_file = "C:\\peter-ai\\data\\outputs\\peter_voice.mp3"
        with open(audio_file, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)
        os.startfile(audio_file)
    except Exception as e:
        print(f"[PETER Voice] Error: {e}")
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(text[:300])
            engine.runAndWait()
        except Exception:
            pass


# ============================================================
# VOICE INPUT
# ============================================================
def peter_listen(duration: int = 7):
    try:
        import sounddevice as sd
        import scipy.io.wavfile as wavfile
        import tempfile
        import whisper

        if not hasattr(peter_listen, '_model'):
            print("[PETER] Loading Whisper large-v3...")
            peter_listen._model = whisper.load_model("large-v3")
            print("[PETER] Whisper siap!")

        model       = peter_listen._model
        sample_rate = 16000

        print(f"\n[PETER] Mendengarkan {duration} detik...")
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate = sample_rate,
            channels   = 1,
            dtype      = 'float32'
        )
        sd.wait()
        print("[PETER] Memproses suara...")

        with tempfile.NamedTemporaryFile(
            suffix='.wav', delete=False
        ) as f:
            tmp = f.name
        wavfile.write(tmp, sample_rate, audio.flatten())

        result = model.transcribe(
            tmp,
            language                   = "id",
            fp16                       = True,
            beam_size                  = 5,
            best_of                    = 5,
            temperature                = 0.0,
            condition_on_previous_text = True,
            initial_prompt             = "Perintah Bahasa Indonesia untuk PETER."
        )
        os.unlink(tmp)

        text = result["text"].strip()
        if text:
            print(f"[{USER_NAME}] (suara) -> {text}")
            return text
        return None

    except Exception as e:
        print(f"[PETER] Voice error: {e}")
        return None


def peter_wait_wakeword():
    try:
        import sounddevice as sd
        import scipy.io.wavfile as wavfile
        import tempfile
        import numpy as np
        import whisper

        if not hasattr(peter_wait_wakeword, '_model'):
            print("[PETER] Loading wake word model...")
            peter_wait_wakeword._model = whisper.load_model("small")

        model       = peter_wait_wakeword._model
        sample_rate = 16000
        wake_words  = [
            "hey peter", "hi peter", "hei peter",
            "peter", "hai peter", "hey piter"
        ]

        print("\n[PETER] Menunggu 'Hey Peter'... (Ctrl+C untuk skip)\n")

        while True:
            try:
                print(".", end="", flush=True)
                audio = sd.rec(
                    int(3 * sample_rate),
                    samplerate = sample_rate,
                    channels   = 1,
                    dtype      = 'float32'
                )
                sd.wait()

                if np.abs(audio).mean() < 0.005:
                    continue

                with tempfile.NamedTemporaryFile(
                    suffix='.wav', delete=False
                ) as f:
                    tmp = f.name
                wavfile.write(tmp, sample_rate, audio.flatten())

                result = model.transcribe(
                    tmp,
                    language    = "id",
                    fp16        = True,
                    beam_size   = 3,
                    temperature = 0.0
                )
                os.unlink(tmp)

                text = result["text"].strip().lower()
                if text:
                    print(f"\n[Terdengar] {text}")

                if any(w in text for w in wake_words):
                    print("\n[PETER] Wake word!")
                    peter_speak(f"Ya {USER_NAME}, saya siap!")
                    return True

            except Exception:
                pass

    except KeyboardInterrupt:
        print("\n[PETER] Skip — mode ketik aktif.")
        return False


# ============================================================
# CHAT
# ============================================================
def chat_peter(message: str, use_memory: bool = True) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    context_str = ""
    history     = []

    if use_memory and MEMORY_OK and memory:
        ctx         = memory.build_context(message)
        context_str = ctx["context_string"]
        history     = ctx["history"]

    system = f"""Kamu adalah PETER — Personal Enhanced Thinking & Execution Robot.
Asisten AI pribadi milik {USER_NAME}.

IDENTITAS:
- Kepribadian: Cerdas, analitis, proaktif seperti JARVIS
- Bahasa: Indonesia (default)
- Gaya: Profesional dan friendly

KEMAMPUAN:
1. Analisis mendalam dengan data dan fakta
2. Content creation — script, caption, artikel viral
3. Strategi monetisasi konten digital
4. Python coding dan otomasi apps
5. YouTube, Instagram, TikTok growth strategy
6. Riset topik viral dan SEO optimization

CARA MENJAWAB:
- SELALU detail, lengkap, dan actionable
- Gunakan angka dan contoh konkret
- Berikan langkah yang bisa langsung dilakukan
- Akhiri dengan next step

KONTEKS {USER_NAME}:
- Membangun bisnis konten digital
- Target: passive income dari YouTube + IG + TikTok
- Tools: PETER AI, Python, CrewAI, Claude

{f'MEMORY:{chr(10)}{context_str}' if context_str else ''}"""

    messages = []
    for h in history[-10:]:
        messages.append({
            "role"   : h["role"],
            "content": h["content"]
        })
    messages.append({"role": "user", "content": message})

    response = client.messages.create(
        model      = "claude-sonnet-4-6",
        max_tokens = 8096,
        system     = system,
        messages   = messages
    )
    answer = response.content[0].text

    if use_memory and MEMORY_OK and memory:
        memory.add_short_term("user", message)
        memory.add_short_term("assistant", answer)
        memory.auto_learn(message, answer)

    return answer


# ============================================================
# MODE 1 — PETER EXECUTOR (Code Engine Level 2)
# ============================================================
def run_peter_executor():
    print("\n[PETER] Peter Executor aktif!")
    print("[PETER] Ketik 'exit' untuk kembali.")
    print("[PETER] Tips:")
    print("  'auto: [task]'   — jalankan tanpa konfirmasi")
    print("  'buat app [desc]'— buat aplikasi lengkap")
    print("  'memory stats'   — cek memory")
    print("  'ingat [teks]'   — simpan ke memory\n")

    peter_speak(f"Halo {USER_NAME}! Peter Executor siap.")

    kata_kode = [
        "buat", "buat file", "buat grafik", "buat chart",
        "buat app", "buat program", "buat script", "buat api",
        "buat web", "buat dashboard", "buat tool", "buat aplikasi",
        "tulis kode", "jalankan", "hitung", "kalkulasi",
        "generate", "create", "plot", "analisis data",
        "download", "scrape", "automasi"
    ]

    while True:
        try:
            user_input = input(f"\n[{USER_NAME}] -> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "keluar", "quit"]:
                print("[PETER] Kembali ke menu.")
                break

            # Perintah khusus memory
            if user_input.lower() == "memory stats":
                if MEMORY_OK:
                    stats = memory.get_stats()
                    print("\n[MEMORY] Statistik:")
                    for k, v in stats.items():
                        print(f"  {k}: {v}")
                continue

            if user_input.lower().startswith("ingat "):
                to_remember = user_input[6:].strip()
                if MEMORY_OK and to_remember:
                    memory.add_long_term(
                        to_remember, category="important"
                    )
                    memory.add_episode(
                        title      = "Catatan penting",
                        summary    = to_remember,
                        importance = 5
                    )
                    print(f"[PETER] Tersimpan: '{to_remember}'")
                    peter_speak("Baik, saya akan ingat itu.")
                continue

            # Mode auto
            auto_mode = False
            task      = user_input
            if user_input.lower().startswith("auto:"):
                auto_mode = True
                task      = user_input[5:].strip()
                print("[PETER] Mode auto — langsung jalankan!")

            # Buat app lengkap
            is_app = any(
                k in user_input.lower()
                for k in ["buat app", "buat aplikasi", "create app"]
            )

            if is_app:
                peter_speak("Baik, saya akan buat aplikasinya.")
                from core.oi_engine import create_app
                app_desc = (
                    task
                    .replace("buat app", "")
                    .replace("buat aplikasi", "")
                    .replace("create app", "")
                    .strip()
                )
                result = create_app(app_desc)
                if result["success"]:
                    peter_speak("Aplikasi berhasil dibuat!")
                    print("\n[PETER] ✅ Aplikasi selesai!")
                else:
                    peter_speak("Maaf, aplikasi gagal dibuat.")
                continue

            # Cek butuh kode
            butuh_kode = any(
                k in user_input.lower() for k in kata_kode
            )

            if butuh_kode:
                peter_speak("Baik, saya kerjakan sekarang.")
                from core.oi_engine import run_with_auto_fix
                result = run_with_auto_fix(
                    task        = task,
                    auto_run    = auto_mode,
                    max_retries = 3
                )
                if result["success"]:
                    msg = f"Selesai dalam {result['attempts']} percobaan!"
                    print(f"\n[PETER] ✅ {msg}")
                    peter_speak(msg)
                    if MEMORY_OK and memory:
                        memory.add_long_term(
                            f"Task: {task}\nOutput: {result['output'][:200]}",
                            category = "code_execution"
                        )
                else:
                    peter_speak("Maaf, task gagal. Coba perintah yang lebih spesifik.")

            else:
                print("\n[PETER] Berpikir...\n")
                response = chat_peter(user_input, use_memory=True)
                print(f"[PETER] {response}\n")
                peter_speak(response[:400])

        except KeyboardInterrupt:
            print("\n[PETER] Kembali ke menu.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")


# ============================================================
# MODE 2 — CREWAI
# ============================================================
def run_crewai(task_description: str = None):
    print("\n[PETER] Memulai CrewAI Multi-Agent...")

    try:
        from crewai import Agent, Task, Crew, LLM

        if LOCAL_MODE:
            llm = LLM(
                model    = "ollama/llama3.3",
                base_url = OLLAMA_URL
            )
            llm_fast = LLM(
                model    = "ollama/llama3.2:3b",
                base_url = OLLAMA_URL
            )
        else:
            llm = LLM(
                model   = "anthropic/claude-sonnet-4-6",
                api_key = ANTHROPIC_KEY
            )
            llm_fast = LLM(
                model   = "anthropic/claude-haiku-4-5-20251001",
                api_key = ANTHROPIC_KEY
            )

        manager = Agent(
            role      = "PETER Manager",
            goal      = "Koordinasi semua agent untuk hasil terbaik",
            backstory  = f"AI manager milik {USER_NAME}.",
            llm       = llm,
            verbose   = True
        )
        researcher = Agent(
            role      = "Research Specialist",
            goal      = "Cari informasi akurat dan terkini",
            backstory  = "Expert researcher.",
            llm       = llm,
            verbose   = True
        )
        writer = Agent(
            role      = "Content Writer",
            goal      = "Tulis konten viral yang engaging",
            backstory  = "Penulis konten profesional.",
            llm       = llm,
            verbose   = True
        )
        analyst = Agent(
            role      = "Data Analyst",
            goal      = "Analisis data dan berikan insight",
            backstory  = "Data analyst berpengalaman.",
            llm       = llm_fast,
            verbose   = True
        )
        strategist = Agent(
            role      = "Digital Strategist",
            goal      = "Buat strategi monetisasi terbaik",
            backstory  = "Expert digital marketing.",
            llm       = llm,
            verbose   = True
        )

        if not task_description:
            print("\n  Agents: Manager, Researcher, Writer, Analyst, Strategist\n")
            task_description = input(
                f"[{USER_NAME}] Task -> "
            ).strip()

        if not task_description:
            return

        td = task_description.lower()
        if any(w in td for w in ["riset","cari","informasi"]):
            primary = researcher
        elif any(w in td for w in ["tulis","script","konten","youtube"]):
            primary = writer
        elif any(w in td for w in ["analisis","data","statistik"]):
            primary = analyst
        elif any(w in td for w in ["strategi","marketing","monetisasi"]):
            primary = strategist
        else:
            primary = manager

        task = Task(
            description     = f"{task_description}\n\nGunakan Bahasa Indonesia. Berikan hasil LENGKAP dan ACTIONABLE.",
            agent           = primary,
            expected_output = "Hasil lengkap dalam Bahasa Indonesia"
        )
        crew = Crew(
            agents  = [manager, researcher, writer, analyst, strategist],
            tasks   = [task],
            verbose = True
        )

        print(f"\n[PETER] Tim bekerja untuk {USER_NAME}...")
        peter_speak("Tim agent sedang bekerja.")
        result = crew.kickoff()

        print("\n" + "=" * 60)
        print("  HASIL TIM PETER:")
        print("=" * 60)
        print(result)
        print("=" * 60)

        output_file = "C:\\peter-ai\\crew_output.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Task: {task_description}\n\n{str(result)}")
        print(f"\n[PETER] Disimpan: {output_file}")

        if MEMORY_OK and memory:
            memory.add_episode(
                title      = f"CrewAI: {task_description[:50]}",
                summary    = str(result)[:300],
                importance = 3
            )
        peter_speak("Tim selesai bekerja.")

    except ImportError as e:
        print(f"[ERROR] {e}")
    except Exception as e:
        print(f"[ERROR] {e}")


# ============================================================
# MODE 3 — COMBINED
# ============================================================
def run_combined():
    print("\n[PETER] Mode Gabungan aktif!\n")
    task = input(f"[{USER_NAME}] Task -> ").strip()
    if not task:
        return
    print("\n[PETER] Step 1: Riset CrewAI...")
    peter_speak("Memulai riset.")
    run_crewai(
        task_description = f"Riset dan buat rencana untuk: {task}"
    )
    print("\n[PETER] Step 2: Eksekusi...")
    peter_speak("Masuk mode eksekusi.")
    run_peter_executor()


# ============================================================
# MODE 4 — VOICE MODE
# ============================================================
def run_peter_executor_voice():
    print("\n[PETER] Voice Mode aktif!")
    print("[PETER] Ucapkan 'keluar' untuk berhenti.\n")

    kata_kode = [
        "buat", "buat file", "buat grafik",
        "tulis kode", "jalankan", "hitung",
        "generate", "create", "plot"
    ]

    peter_speak(f"Voice mode aktif. Halo {USER_NAME}!")

    while True:
        try:
            peter_speak("Silakan bicara.")
            user_input = peter_listen(duration=7)

            if not user_input:
                user_input = input(
                    f"[{USER_NAME}] (ketik) -> "
                ).strip()

            if not user_input:
                continue

            if any(w in user_input.lower() for w in
                   ["exit", "keluar", "quit", "stop"]):
                peter_speak("Kembali ke menu.")
                break

            butuh_kode = any(
                k in user_input.lower() for k in kata_kode
            )

            if butuh_kode:
                peter_speak("Baik, saya kerjakan.")
                from core.oi_engine import run_with_auto_fix
                result = run_with_auto_fix(
                    task        = user_input,
                    auto_run    = True,
                    max_retries = 3
                )
                if result["success"]:
                    peter_speak("Selesai!")
                else:
                    peter_speak("Maaf, gagal. Coba lagi.")
            else:
                response = chat_peter(user_input, use_memory=True)
                print(f"\n[PETER] {response}\n")
                peter_speak(response[:400])

        except KeyboardInterrupt:
            peter_speak("Sampai jumpa!")
            break
        except Exception as e:
            print(f"[ERROR] {e}")


# ============================================================
# MODE 5 — VISION MODE
# ============================================================
def run_vision_mode():
    if not VISION_OK:
        print("[PETER] Vision tidak aktif!")
        return

    print("\n[PETER] Vision Mode:")
    print("  [1] Analisis lengkap")
    print("  [2] Monitor background")
    print("  [3] Daftarkan wajah baru")
    print("  [4] Kembali\n")

    pilihan = input("[PETER] Pilih (1-4): ").strip()

    if pilihan == "1":
        print("\n[PETER] Menganalisis...")
        peter_speak("Menganalisis kamera.")
        result  = vision.capture_and_analyze()
        laporan = vision.format_result(result)
        print(f"\n[PETER] {laporan}")
        peter_speak(laporan)
        if MEMORY_OK and memory:
            memory.add_long_term(
                f"Vision: {laporan}", category="vision"
            )

    elif pilihan == "2":
        print("\n[PETER] Monitor aktif... Ctrl+C untuk berhenti\n")
        peter_speak("Monitor kamera aktif.")

        def on_face(name):
            msg = f"Saya melihat {name}"
            print(f"\n[VISION] {msg}")
            peter_speak(msg)

        def on_gesture(gesture):
            g = {
                "thumbs_up": "jempol ke atas",
                "open_hand": "tangan terbuka",
                "fist"     : "tinju",
                "pointing" : "menunjuk",
                "peace"    : "peace"
            }.get(gesture, gesture)
            print(f"\n[VISION] Gesture: {g}")

        def on_emotion(emotion):
            e = {
                "happy"  : "senang",
                "sad"    : "sedih",
                "angry"  : "marah",
                "neutral": "normal"
            }.get(emotion, emotion)
            print(f"\n[VISION] Emosi: {e}")

        vision.start_monitor(
            on_face    = on_face,
            on_gesture = on_gesture,
            on_emotion = on_emotion
        )
        try:
            while True:
                __import__('time').sleep(1)
        except KeyboardInterrupt:
            vision.stop_monitor()
            print("\n[PETER] Monitor berhenti.")

    elif pilihan == "3":
        nama = input("\n[PETER] Nama wajah baru: ").strip()
        if nama:
            vision.register_face(nama, num_photos=5)

    elif pilihan == "4":
        return


# ============================================================
# BANNER
# ============================================================
def print_banner():
    print("""
╔══════════════════════════════════════════════════╗
║           P E T E R   A I   v2.0               ║
║    Personal Enhanced Thinking & Execution       ║
║  CrewAI + Claude + Whisper + Vision + Self-Heal ║
╚══════════════════════════════════════════════════╝""")
    mode = "LOCAL (Ollama)" if LOCAL_MODE else "CLOUD (Claude API)"
    print(f"  Mode    : {mode}")
    print(f"  User    : {USER_NAME}")
    print(f"  Vision  : {'OK' if VISION_OK else 'Tidak aktif'}")
    print(f"  Memory  : {'OK' if MEMORY_OK else 'Tidak aktif'}")
    print(f"  Heal    : {'OK' if HEAL_OK else 'Tidak aktif'}")
    if MEMORY_OK and memory:
        stats = memory.get_stats()
        print(f"  Memori  : {stats['long_term_count']} long term | {stats['episodes_count']} episodes")
    print(f"  STT     : Whisper large-v3 (GPU)")
    print(f"  TTS     : ElevenLabs")
    print(f"  Status  : Semua sistem online")
    print()


# ============================================================
# MAIN MENU
# ============================================================
def main():
    print_banner()

    while True:
        print("\n" + "=" * 52)
        print("  PETER AI v2.0 — Menu Utama")
        print("=" * 52)
        print("  [1] Chat & Execute Code   (Peter Executor)")
        print("  [2] Multi-Agent Team      (CrewAI)")
        print("  [3] Mode Gabungan         (Executor + CrewAI)")
        print("  [4] Voice Mode            (Hey Peter!)")
        print("  [5] Vision Mode           (Wajah & Gesture)")
        print("  [6] Self-Diagnose         (Monitor & Fix)")
        print("  [7] Script Writer         (YouTube Long-Form)")
        print("  [8] Content Automation    (Full Pipeline Auto)")
        print("  [9] Keluar")
        print("=" * 52)

        pilihan = input(
            f"\n[{USER_NAME}] Pilih menu (1-9): "
        ).strip()

        if pilihan == "1":
            run_peter_executor()

        elif pilihan == "2":
            run_crewai()

        elif pilihan == "3":
            run_combined()

        elif pilihan == "4":
            aktif = peter_wait_wakeword()
            if aktif:
                run_peter_executor_voice()

        elif pilihan == "5":
            run_vision_mode()

        elif pilihan == "6":
            if HEAL_OK:
                from peter_self_heal import run_self_heal_menu
                run_self_heal_menu()
            else:
                print("[PETER] Self-Heal tidak aktif!")

        elif pilihan == "7":
            from content.script_writer import run_script_writer_interactive
            run_script_writer_interactive()

        elif pilihan == "8":
            from content_automation import run_automation_menu
            run_automation_menu()

        elif pilihan == "9":
            print(f"\n[PETER] Sampai jumpa, {USER_NAME}!")
            peter_speak(f"Sampai jumpa {USER_NAME}. PETER offline.")
            print("[PETER] Semua sistem offline.\n")
            break

        else:
            print("[PETER] Pilihan tidak valid. Ketik 1-9.")


if __name__ == "__main__":
    main()