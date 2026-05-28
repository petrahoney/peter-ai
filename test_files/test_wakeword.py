import speech_recognition as sr
import os
from dotenv import load_dotenv

load_dotenv()

def peter_listen_once():
    """Dengarkan 1 kalimat"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            text = r.recognize_google(audio, language="id-ID")
            return text.lower()
        except Exception:
            return None

def peter_speak_simple(text):
    """Suara PETER"""
    try:
        from elevenlabs import ElevenLabs, VoiceSettings
        client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        audio = client.text_to_speech.convert(
            voice_id=os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB"),
            text=text,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.75)
        )
        audio_file = "C:\\peter-ai\\peter_voice.mp3"
        with open(audio_file, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)
        os.startfile(audio_file)
    except Exception as e:
        print(f"[Voice Error] {e}")

print("=" * 50)
print("  PETER Wake Word Test")
print("  Ucapkan 'Hey Peter' untuk aktifkan")
print("  Ctrl+C untuk keluar")
print("=" * 50)

r = sr.Recognizer()
wake_words = ["hey peter", "hi peter", "hei peter",
              "peter", "hai peter", "hey piter"]

print("\n[PETER] Menunggu wake word...")

while True:
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.3)
            print(".", end="", flush=True)
            try:
                audio = r.listen(
                    source,
                    timeout=3,
                    phrase_time_limit=4
                )
                text = r.recognize_google(
                    audio, language="id-ID"
                ).lower()
                print(f"\n[Terdengar] {text}")

                # Cek wake word
                if any(w in text for w in wake_words):
                    print("\n[PETER] Wake word terdeteksi!")
                    peter_speak_simple(
                        f"Ya, saya siap. Apa yang bisa saya bantu?"
                    )

                    # Dengarkan perintah
                    print("[PETER] Mendengarkan perintah...")
                    perintah = peter_listen_once()

                    if perintah:
                        print(f"[Perintah] {perintah}")
                        peter_speak_simple(
                            f"Baik, kamu berkata: {perintah}. Saya akan proses."
                        )
                    else:
                        peter_speak_simple("Maaf, saya tidak mendengar perintah.")

                    print("\n[PETER] Kembali menunggu wake word...")

            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass

    except KeyboardInterrupt:
        print("\n\n[PETER] Wake word listener berhenti.")
        break