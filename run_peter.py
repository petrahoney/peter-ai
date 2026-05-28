from dotenv import load_dotenv
import os

# Load environment variables dari .env
load_dotenv()

# Hapus OPENAI_API_KEY agar tidak konflik
os.environ.pop("OPENAI_API_KEY", None)

# Ambil API key dari .env
api_key = os.getenv("ANTHROPIC_API_KEY")

# Validasi API key
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY tidak ditemukan di file .env!")
    exit(1)

print(f"API Key ditemukan: {api_key[:20]}...")

# Import interpreter
from interpreter import interpreter

# Setup Claude
interpreter.llm.model = "claude-sonnet-4-5"
interpreter.llm.api_key = api_key
interpreter.auto_run = False
interpreter.loop = True

# Persona PETER
interpreter.system_message = """
Kamu adalah PETER - Personal Enhanced Thinking & Execution Robot.
Asisten AI pribadi yang sangat cerdas dan berbicara Bahasa Indonesia.
Kamu bisa menulis kode, browsing internet, membuat file, dan menganalisis data.
Selalu selesaikan task sampai tuntas dengan hasil terbaik.
Setelah selesai 1 task, tunggu perintah berikutnya.
Jangan pernah keluar kecuali user ketik exit.
"""

print("=" * 50)
print("  PETER AI - Powered by Claude Sonnet")
print("  Ketik \'exit\' untuk keluar")
print("=" * 50)

interpreter.chat()
