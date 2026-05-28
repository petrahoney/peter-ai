from dotenv import load_dotenv
from elevenlabs import ElevenLabs
import os
import time

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Suara Indonesia asli dari ElevenLabs
indonesian_voices = {
    "Zephlyn"  : "young Indonesian male — narasi & berita",
    "Blasto"   : "young Indonesian male — warm & calm",
    "Miz"      : "middle-aged baritone Indonesian male",
}

# Cari voice ID yang benar dari library
print("Mencari suara Indonesia di ElevenLabs...\n")

try:
    voices = client.voices.get_all()
    found  = []

    for v in voices.voices:
        name = v.name.lower()
        if any(idn in name for idn in [
            "indonesian", "indonesia", "zephlyn",
            "blasto", "miz", "andra", "dila"
        ]):
            found.append({
                "name"    : v.name,
                "id"      : v.voice_id,
                "category": getattr(v, 'category', 'unknown')
            })
            print(f"Ditemukan: {v.name} — ID: {v.voice_id}")

    if not found:
        print("Tidak ada suara Indonesia di library kamu.")
        print("Pergi ke elevenlabs.io → Voice Library → search 'Indonesian'")
        print("Klik 'Add to My Voices' pada suara yang kamu suka")
    else:
        print(f"\nTotal: {len(found)} suara Indonesia ditemukan!")
        print("\nTest suara pertama...")

        # Test suara pertama yang ditemukan
        v        = found[0]
        audio    = client.text_to_speech.convert(
            voice_id = v["id"],
            text     = "Halo! Selamat datang di channel PETER AI. Di video ini kita akan belajar cara menggunakan kecerdasan buatan untuk meningkatkan produktivitas kamu.",
            model_id = "eleven_multilingual_v2"
        )
        out_file = f"C:\\peter-ai\\data\\outputs\\test_id_voice.mp3"
        with open(out_file, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)
        os.startfile(out_file)
        print(f"Suara {v['name']} sedang diputar!")

except Exception as e:
    print(f"Error: {e}")