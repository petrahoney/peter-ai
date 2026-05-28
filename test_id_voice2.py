from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings
import os
import time

load_dotenv()

client   = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
voice_id = "TIXYCOMzK2Vw9OZovSLs"

test_text = """
Halo semuanya dan selamat datang kembali di channel PETER AI!
Di video kali ini, kita akan membahas cara menggunakan kecerdasan buatan 
untuk menghasilkan uang secara online di Indonesia tahun 2026.

Kita akan bahas mulai dari tool AI gratis yang bisa kamu pakai sekarang,
sampai strategi monetisasi yang sudah terbukti menghasilkan jutaan rupiah
setiap bulannya.

Jadi pastikan kamu tonton video ini sampai habis ya,
karena di akhir video ada tips spesial yang tidak ada di video lain!
"""

print("Generating suara Indonesia...")
audio = client.text_to_speech.convert(
    voice_id       = voice_id,
    text           = test_text,
    model_id       = "eleven_multilingual_v2",
    voice_settings = VoiceSettings(
        stability        = 0.4,
        similarity_boost = 0.8,
        style            = 0.5,
        use_speaker_boost= True
    )
)

out = "C:\\peter-ai\\data\\outputs\\test_id_voice2.mp3"
with open(out, "wb") as f:
    for chunk in audio:
        if chunk:
            f.write(chunk)

os.startfile(out)
print("Suara sedang diputar!")
print("Dengarkan apakah sudah natural seperti orang Indonesia bicara")
time.sleep(15)
print("Selesai!")