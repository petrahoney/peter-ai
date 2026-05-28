from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings
import os

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Daftar suara pria untuk dicoba
voices = {
    "Adam"    : "pNInz6obpgDQGcFmaJgB",
    "Antoni"  : "ErXwobaYiN019PkySvjV",
    "Arnold"  : "VR6AewLTigWG4xSOukaG",
    "Josh"    : "TxGEqnHWrfWFTfGW9XjX",
    "Daniel"  : "onwK4e9ZLuTAKqWW03F9",
    "Marcus"  : "iP95p4xoKVk53GoZ742B",
}

print("Test suara pria ElevenLabs untuk PETER")
print("=" * 45)

for nama, vid in voices.items():
    pilihan = input(f"\nTest suara '{nama}'? (y/n): ").strip().lower()
    if pilihan != 'y':
        continue

    try:
        print(f"Generating suara {nama}...")
        audio = client.text_to_speech.convert(
            voice_id=vid,
            text=f"Halo, saya PETER. Nama suara saya adalah {nama}. Apakah suara ini cocok untuk asisten AI kamu?",
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75
            )
        )

        audio_file = f"C:\\peter-ai\\voice_{nama}.mp3"
        with open(audio_file, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)

        os.startfile(audio_file)
        print(f"Suara {nama} sedang diputar!")

        cocok = input(f"Apakah suara {nama} cocok untuk PETER? (y/n): ").strip().lower()
        if cocok == 'y':
            print(f"\nVoice ID untuk {nama}: {vid}")
            print(f"Tambahkan ke .env: ELEVENLABS_VOICE_ID={vid}")
            break

    except Exception as e:
        print(f"Error: {e}")

print("\nSelesai test suara!")