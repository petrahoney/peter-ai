from dotenv import load_dotenv
import os
load_dotenv()

from elevenlabs import ElevenLabs, VoiceSettings
import time

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

print("Generating suara...")
audio = client.text_to_speech.convert(
    voice_id       = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB"),
    text           = "Sampai jumpa Tjerlang. PETER offline.",
    model_id       = "eleven_multilingual_v2",
    voice_settings = VoiceSettings(
        stability        = 0.5,
        similarity_boost = 0.75
    )
)

audio_file = "C:\\peter-ai\\data\\outputs\\test_speak.mp3"
with open(audio_file, "wb") as f:
    for chunk in audio:
        if chunk:
            f.write(chunk)

print("Memainkan suara...")
os.startfile(audio_file)
time.sleep(5)
print("Selesai!")