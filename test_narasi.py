from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings
import anthropic
import os
import re

load_dotenv()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
voice_id      = os.getenv("ELEVENLABS_VOICE_ID", "TIXYCOMzK2Vw9OZovSLs")

# Simulasi script mentah dari CrewAI
script_mentah = """
TITLE: Cara Install AI di PC Sendiri
DESCRIPTION: Di video ini kita akan belajar...
TAGS: ai, teknologi, indonesia
===========================
HOOK:
Apakah kamu tahu bahwa AI bisa menghasilkan uang?

INTRO:
Halo semuanya dan selamat datang kembali di channel kami.

KONTEN UTAMA:
1. Pertama kita akan install Python
2. Kemudian kita install Ollama
3. Setelah itu kita coba chat dengan AI

00:00 Intro
01:00 Install Python
05:00 Test AI

Subscribe sekarang!
"""

# Step 1: Minta Claude buat narasi bersih
print("Membuat narasi bersih dengan Claude...")
claude   = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
response = claude.messages.create(
    model      = "claude-sonnet-4-6",
    max_tokens = 1500,
    system     = """Kamu adalah script editor profesional Indonesia.
Ubah script mentah menjadi narasi video natural.
HAPUS semua TITLE, TAGS, timestamp, URL.
Tulis Bahasa Indonesia conversational seperti YouTuber.
Maksimal 300 kata. Output HANYA narasi saja.""",
    messages   = [{
        "role"   : "user",
        "content": f"Ubah jadi narasi natural 300 kata:\n\n{script_mentah}"
    }]
)

narasi = response.content[0].text.strip()
narasi = re.sub(r'\*+', '', narasi)
narasi = re.sub(r'#+\s*', '', narasi)
narasi = re.sub(r'\[.*?\]', '', narasi)
narasi = narasi.strip()

print(f"\nNarasi bersih ({len(narasi.split())} kata):")
print("─" * 50)
print(narasi)
print("─" * 50)

# Step 2: Generate audio
print("\nGenerating voice...")
el    = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
audio = el.text_to_speech.convert(
    voice_id       = voice_id,
    text           = narasi,
    model_id       = "eleven_multilingual_v2",
    voice_settings = VoiceSettings(
        stability         = 0.45,
        similarity_boost  = 0.82,
        style             = 0.5,
        use_speaker_boost = True
    )
)

out = "C:\\peter-ai\\data\\outputs\\test_narasi_bersih.mp3"
with open(out, "wb") as f:
    for chunk in audio:
        if chunk:
            f.write(chunk)

os.startfile(out)
print(f"\nSuara diputar!")
print("Dengarkan — seharusnya jauh lebih natural sekarang!")