from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY", "")

if not api_key:
    print("ERROR: API key tidak ditemukan!")
    print("Cek file .env kamu")
else:
    print(f"API Key OK: {api_key[:15]}...")

try:
    from elevenlabs import ElevenLabs, VoiceSettings

    # Cara terbaru ElevenLabs SDK 2025
    client = ElevenLabs(api_key=api_key)

    print("Generating suara PETER...")

    # Generate audio sebagai bytes
    audio_generator = client.text_to_speech.convert(
        voice_id="21m00Tcm4TlvDq8ikWAM",
        text="Halo! Saya PETER, asisten AI pribadi kamu. Suara saya sudah aktif!",
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.75
        )
    )

    # Simpan ke file MP3
    audio_file = "C:\\peter-ai\\test_suara.mp3"
    with open(audio_file, "wb") as f:
        for chunk in audio_generator:
            if chunk:
                f.write(chunk)

    print(f"Audio disimpan ke: {audio_file}")

    # Play file audio
    os.startfile(audio_file)
    print("Suara sedang diputar!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()