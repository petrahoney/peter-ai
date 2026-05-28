from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings
import os

load_dotenv()

client   = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
voice_id = "TIXYCOMzK2Vw9OZovSLs"

# Test dengan teks natural Indonesia
teks = """Halo semuanya! Selamat datang di channel ini.
Di video kali ini kita akan belajar bersama tentang 
cara menggunakan kecerdasan buatan untuk kehidupan sehari-hari.
Yuk kita mulai!"""

# Test 3 model berbeda
models = [
    "eleven_turbo_v2_5",
    "eleven_multilingual_v2",
    "eleven_flash_v2_5"
]

for model in models:
    print(f"\nTest model: {model}")
    try:
        audio = client.text_to_speech.convert(
            voice_id       = voice_id,
            text           = teks,
            model_id       = model,
            voice_settings = VoiceSettings(
                stability         = 0.35,
                similarity_boost  = 0.85,
                style             = 0.6,
                use_speaker_boost = True
            )
        )
        out = f"C:\\peter-ai\\data\\outputs\\test_{model}.mp3"
        with open(out, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)

        os.startfile(out)
        input(f"Dengar {model} → Enter untuk lanjut ke model berikutnya...")

    except Exception as e:
        print(f"Error {model}: {e}")

print("\nPilih model yang paling natural!")