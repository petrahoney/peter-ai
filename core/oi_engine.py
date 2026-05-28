"""
core/oi_engine.py
PETER Code Engine — Level 2
Auto-generate + Auto-fix + Auto-run
PETER bisa coding sendiri sampai berhasil!
"""

import os
import sys
import ast
import subprocess
import tempfile
import time
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
USER_NAME     = os.getenv("USER_NAME", "Sir")
OUTPUT_DIR    = "C:\\peter-ai\\data\\outputs"
MAX_RETRIES   = 3


def _strip_docstrings(code: str) -> str:
    """
    Hapus semua triple-quoted strings dari kode
    Ganti dengan komentar # biasa
    """
    import re

    # Hapus triple double quotes
    code = re.sub(
        r'"""[\s\S]*?"""',
        '',
        code
    )

    # Hapus triple single quotes
    code = re.sub(
        r"'''[\s\S]*?'''",
        '',
        code
    )

    # Jika masih ada triple quote yang tidak tertutup
    # hapus dari titik itu sampai akhir baris
    lines     = code.split("\n")
    new_lines = []
    skip      = False

    for line in lines:
        # Cek triple double quote
        if '"""' in line:
            count = line.count('"""')
            if count % 2 != 0:
                # Tidak tertutup di baris ini
                # Hapus bagian setelah triple quote
                idx  = line.index('"""')
                line = line[:idx]
                skip = not skip
            if not line.strip():
                continue

        # Cek triple single quote
        if "'''" in line:
            count = line.count("'''")
            if count % 2 != 0:
                idx  = line.index("'''")
                line = line[:idx]
                skip = not skip
            if not line.strip():
                continue

        if not skip:
            new_lines.append(line)

    # Hapus baris kosong berlebihan
    result = "\n".join(new_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()


def generate_code(task: str,
                  context: str = "",
                  previous_error: str = "") -> str:
    """Generate kode Python dengan Claude"""
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    if previous_error:
        prompt = f"""Kode sebelumnya gagal dengan error:
{previous_error}

Task: {task}
{f'Konteks: {context}' if context else ''}

Tulis ulang kode Python yang BENAR dan memperbaiki error tersebut."""
    else:
        prompt = f"""Task: {task}
{f'Konteks: {context}' if context else ''}

Tulis kode Python yang menyelesaikan task ini."""

    response = client.messages.create(
        model      = "claude-sonnet-4-6",
        max_tokens = 4096,
        system     = f"""Kamu adalah senior Python developer expert.

ATURAN WAJIB — IKUTI SEMUA:
1. Return HANYA kode Python murni
2. DILARANG: markdown, backtick, penjelasan, komentar panjang
3. DILARANG: triple-quoted strings (\"\"\" atau \'\'\') — gunakan # untuk komentar
4. Semua bracket dan tanda kutip HARUS tertutup dengan benar
5. Indentasi konsisten 4 spasi — JANGAN tab
6. Output/hasil ke: C:/peter-ai/data/outputs/
7. Selalu print hasil akhir
8. Gunakan try-except untuk error handling
9. Import semua library di baris pertama
10. Jika butuh install library:
    import subprocess, sys
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'nama'], capture_output=True)
11. Kode harus bisa langsung dijalankan tanpa modifikasi
12. JANGAN gunakan docstring — gunakan komentar # biasa""",
        messages   = [{"role": "user", "content": prompt}]
    )

    code = response.content[0].text.strip()

    # Bersihkan markdown
    if "```" in code:
        lines = code.split("\n")
        lines = [
            l for l in lines
            if not l.strip().startswith("```")
        ]
        code = "\n".join(lines).strip()

    # Strip semua triple-quotes dan ganti jadi komentar
    code = _strip_docstrings(code)
    # ─────────────────────────────────────────────

    return code


def _fix_triple_quotes(code: str) -> str:
    """Fix triple-quoted strings yang tidak tertutup"""
    # Hitung jumlah triple quotes
    triple_double = code.count('"""')
    triple_single = code.count("'''")

    # Jika ganjil, ada yang tidak tertutup
    if triple_double % 2 != 0:
        # Hapus semua docstring triple double quote
        import re
        code = re.sub(r'"""[\s\S]*?"""', '', code)
        # Jika masih ada yang tidak tertutup, hapus baris itu
        lines     = code.split("\n")
        new_lines = []
        in_triple = False
        for line in lines:
            if '"""' in line:
                count = line.count('"""')
                if count % 2 != 0:
                    in_triple = not in_triple
                    if in_triple:
                        continue
                else:
                    new_lines.append(line)
            elif not in_triple:
                new_lines.append(line)
        code = "\n".join(new_lines)

    if triple_single % 2 != 0:
        import re
        code = re.sub(r"'''[\s\S]*?'''", '', code)

    return code.strip()


def validate_code(code: str) -> tuple:
    """
    Validasi syntax Python
    Return: (is_valid, error_message)
    """
    if not code or not code.strip():
        return False, "Kode kosong"

    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        error_msg = f"SyntaxError baris {e.lineno}: {e.msg}"

        # Coba fix otomatis beberapa masalah umum
        fixed = _auto_fix_syntax(code, e)
        if fixed != code:
            try:
                ast.parse(fixed)
                return True, ""
            except SyntaxError:
                pass

        return False, error_msg


def _auto_fix_syntax(code: str, error: SyntaxError) -> str:
    """Coba fix syntax error otomatis"""
    lines = code.split("\n")

    # Fix unterminated string
    if "unterminated" in str(error.msg).lower():
        # Hapus baris yang bermasalah
        if error.lineno and error.lineno <= len(lines):
            bad_line = lines[error.lineno - 1]
            # Jika ada triple quote, hapus
            if '"""' in bad_line or "'''" in bad_line:
                lines[error.lineno - 1] = "# " + bad_line
                return "\n".join(lines)

    # Fix unmatched bracket
    if "unmatched" in str(error.msg).lower():
        if error.lineno and error.lineno <= len(lines):
            lines[error.lineno - 1] = "# " + lines[error.lineno - 1]
            return "\n".join(lines)

    return code


def execute_code(code: str,
                 timeout: int = 60) -> tuple:
    """
    Jalankan kode Python
    Return: (success, output, error)
    """
    with tempfile.NamedTemporaryFile(
        mode     = 'w',
        suffix   = '.py',
        delete   = False,
        prefix   = 'peter_',
        encoding = 'utf-8'
    ) as f:
        f.write(code)
        tmp = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp],
            capture_output = True,
            text           = True,
            timeout        = timeout,
            encoding       = 'utf-8'
        )
        success = result.returncode == 0
        output  = result.stdout.strip()
        error   = result.stderr.strip()
        return success, output, error

    except subprocess.TimeoutExpired:
        return False, "", f"Timeout: kode berjalan lebih dari {timeout} detik"
    except Exception as e:
        return False, "", str(e)
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass


def run_with_auto_fix(task: str,
                      context: str = "",
                      max_retries: int = MAX_RETRIES,
                      auto_run: bool = False) -> dict:
    """
    PETER coding sendiri dengan auto-fix!

    Flow:
    1. Generate kode
    2. Validasi syntax
    3. Jalankan
    4. Jika error → analisis → fix → coba lagi
    5. Maksimal max_retries percobaan
    """
    print(f"\n[CODE ENGINE] Task: {task}")
    print(f"[CODE ENGINE] Max retries: {max_retries}")

    result = {
        "task"     : task,
        "success"  : False,
        "code"     : "",
        "output"   : "",
        "error"    : "",
        "attempts" : 0,
        "files"    : []
    }

    previous_error = ""
    previous_code  = ""

    for attempt in range(1, max_retries + 1):
        print(f"\n[CODE ENGINE] Percobaan {attempt}/{max_retries}...")

        # Generate kode
        print("[CODE ENGINE] Menulis kode...")
        code = generate_code(
            task           = task,
            context        = context,
            previous_error = previous_error
        )
        result["code"] = code

        # Tampilkan kode
        print("\n" + "─" * 50)
        print(f"[PETER] Kode (attempt {attempt}):")
        print("─" * 50)
        print(code)
        print("─" * 50)

        # Validasi syntax
        valid, syntax_error = validate_code(code)
        if not valid:
            print(f"[CODE ENGINE] Syntax error: {syntax_error}")
            previous_error = syntax_error
            previous_code  = code
            continue

        print("[CODE ENGINE] ✅ Syntax valid!")

        # Konfirmasi atau auto run
        if not auto_run:
            konfirmasi = input(
                f"\n[{USER_NAME}] Jalankan kode? (y/n/auto): "
            ).strip().lower()
            if konfirmasi == 'n':
                print("[CODE ENGINE] Dibatalkan.")
                return result
            if konfirmasi == 'auto':
                auto_run = True

        # Jalankan kode
        print("\n[CODE ENGINE] Menjalankan...")
        start_time        = time.time()
        success, output, error = execute_code(code)
        elapsed           = time.time() - start_time

        result["attempts"] = attempt

        if success:
            print(f"\n[CODE ENGINE] ✅ BERHASIL! ({elapsed:.1f}s)")
            if output:
                print(f"\n[OUTPUT]\n{output}")
            result["success"] = True
            result["output"]  = output

            # Cek file yang dibuat
            import glob
            new_files = glob.glob(f"{OUTPUT_DIR}\\*")
            result["files"] = [
                f for f in new_files
                if os.path.getmtime(f) > start_time - 1
            ]
            if result["files"]:
                print(f"\n[CODE ENGINE] File dibuat:")
                for f in result["files"]:
                    print(f"  → {os.path.basename(f)}")
            return result

        else:
            print(f"\n[CODE ENGINE] ❌ Error:")
            print(f"  {error[:300]}")
            previous_error = error
            previous_code  = code

            if attempt < max_retries:
                print(f"[CODE ENGINE] Auto-fixing... (attempt {attempt+1})")
                time.sleep(1)

    # Semua percobaan gagal
    print(f"\n[CODE ENGINE] ❌ Gagal setelah {max_retries} percobaan")
    result["error"] = previous_error
    return result


def create_app(app_description: str,
               app_type: str = "script") -> dict:
    """
    PETER buat aplikasi lengkap!

    app_type: script, web_app, api, dashboard, tool
    """
    print(f"\n[APP BUILDER] Membuat: {app_description}")
    print(f"[APP BUILDER] Type: {app_type}")

    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    # Plan aplikasi dulu
    print("[APP BUILDER] Merencanakan aplikasi...")
    plan_response = client.messages.create(
        model      = "claude-sonnet-4-6",
        max_tokens = 2048,
        system     = """Kamu adalah software architect.
Buat rencana aplikasi Python yang detail.
Format output:
APP_NAME: [nama app]
DESCRIPTION: [deskripsi singkat]
FILES:
- filename.py: [deskripsi file]
DEPENDENCIES: [list library yang dibutuhkan]
MAIN_FEATURES:
- [fitur 1]
- [fitur 2]""",
        messages   = [{
            "role"   : "user",
            "content": f"Rancang aplikasi Python: {app_description}\nType: {app_type}"
        }]
    )
    plan = plan_response.content[0].text

    print(f"\n[APP BUILDER] Rencana:\n{plan}\n")

    # Generate kode lengkap
    print("[APP BUILDER] Menulis kode aplikasi...")
    result = run_with_auto_fix(
        task    = f"""Buat aplikasi Python lengkap untuk: {app_description}

Rencana aplikasi:
{plan}

Buat sebagai single-file Python app yang bisa langsung dijalankan.
Simpan file output ke C:/peter-ai/data/outputs/
Berikan nama file yang deskriptif.""",
        context  = f"App type: {app_type}",
        max_retries = 3,
        auto_run    = False
    )

    return {
        "plan"   : plan,
        "result" : result,
        "success": result["success"]
    }


def run_executor():
    """Mode interaktif Peter Code Engine"""
    print("\n[CODE ENGINE] Peter Code Engine aktif!")
    print("[CODE ENGINE] PETER bisa coding dan fix error sendiri!")
    print(f"[CODE ENGINE] Ketik 'exit' untuk kembali\n")

    print("Perintah khusus:")
    print("  'buat app [deskripsi]' — buat aplikasi lengkap")
    print("  'auto: [task]'         — jalankan tanpa konfirmasi")
    print("  'exit'                 — keluar\n")

    kata_kode = [
        "buat", "buat file", "buat grafik", "buat chart",
        "buat app", "buat program", "buat script", "buat api",
        "buat web", "buat dashboard", "buat tool",
        "tulis kode", "jalankan", "hitung", "kalkulasi",
        "generate", "create", "plot", "analisis",
        "download", "scrape", "automasi", "buat aplikasi"
    ]

    while True:
        try:
            user_input = input(
                f"\n[{USER_NAME}] -> "
            ).strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "keluar", "quit"]:
                print("[CODE ENGINE] Kembali ke menu.")
                break

            # Mode auto (tanpa konfirmasi)
            auto_mode = False
            if user_input.lower().startswith("auto:"):
                auto_mode  = True
                user_input = user_input[5:].strip()
                print("[CODE ENGINE] Mode auto aktif — langsung jalankan!")

            # Buat app lengkap
            if "buat app" in user_input.lower() or "buat aplikasi" in user_input.lower():
                app_desc = user_input.replace("buat app", "").replace("buat aplikasi", "").strip()
                result   = create_app(app_desc)
                if result["success"]:
                    print("\n[CODE ENGINE] ✅ Aplikasi berhasil dibuat!")
                else:
                    print("\n[CODE ENGINE] ❌ Gagal membuat aplikasi")
                continue

            # Cek apakah butuh kode
            butuh_kode = any(
                k in user_input.lower() for k in kata_kode
            )

            if butuh_kode:
                result = run_with_auto_fix(
                    task        = user_input,
                    auto_run    = auto_mode,
                    max_retries = 3
                )

                if result["success"]:
                    print(f"\n✅ Task selesai dalam {result['attempts']} percobaan!")
                else:
                    print(f"\n❌ Task gagal setelah {result['attempts']} percobaan")

            else:
                # Chat biasa
                import anthropic
                client   = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
                response = client.messages.create(
                    model      = "claude-sonnet-4-6",
                    max_tokens = 2048,
                    system     = f"""Kamu adalah PETER, AI assistant canggih milik {USER_NAME}.
Berbicara Bahasa Indonesia. Jawab dengan detail dan helpful.""",
                    messages   = [{"role": "user", "content": user_input}]
                )
                print(f"\n[PETER] {response.content[0].text}\n")

        except KeyboardInterrupt:
            print("\n[CODE ENGINE] Kembali ke menu.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")


if __name__ == "__main__":
    run_executor()