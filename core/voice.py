"""
core/voice.py
Voice Input (Whisper) + Voice Output (ElevenLabs)
"""

import os
import sys
sys.path.append("C:\\peter-ai")

from config import (
    USER_NAME, ELEVENLABS_KEY, ELEVENLABS_VOICE,
    WHISPER_MODEL, LOCAL_MODE
)


def peter_speak(text: str):
    """PETER berbicara dengan ElevenLabs"""
    if not text or not text.strip():
        return
    try:
        from elevenlabs import ElevenLabs, VoiceSettings
        client = ElevenLabs(api_key=ELEVENLABS_KEY)
        audio  = client.text_to_speech.convert(
            voice_id       = ELEVENLABS_VOICE,
            text           = text[:500],
            model_id       = "eleven_multilingual_v2",
            voice_settings = VoiceSettings(
                stability        = 0.5,
                similarity_boost = 0.75
            )
        )
        audio_file = "C:\\peter-ai\\data\\outputs\\peter_voice.mp3"
        with open(audio_file, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)
        os.startfile(audio_file)
        print(f"[VOICE] Berbicara: {text[:50]}...")
    except Exception as e:
        print(f"[VOICE] ElevenLabs error: {e}")
        _speak_fallback(text)


def _speak_fallback(text: str):
    """Fallback ke pyttsx3"""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(text[:300])
        engine.runAndWait()
    except Exception:
        pass


def peter_listen(duration: int = 7) -> str:
    """Dengarkan suara dengan Whisper GPU"""
    try:
        import sounddevice as sd
        import scipy.io.wavfile as wavfile
        import tempfile
        import whisper

        if not hasattr(peter_listen, '_model'):
            print(f"[VOICE] Loading Whisper {WHISPER_MODEL}...")
            peter_listen._model = whisper.load_model(WHISPER_MODEL)
            print("[VOICE] Whisper siap!")

        model       = peter_listen._model
        sample_rate = 16000

        print(f"\n[VOICE] Mendengarkan {duration} detik...")

        audio = sd.rec(
            int(duration * sample_rate),
            samplerate = sample_rate,
            channels   = 1,
            dtype      = 'float32'
        )
        sd.wait()
        print("[VOICE] Memproses...")

        with tempfile.NamedTemporaryFile(
            suffix='.wav', delete=False
        ) as f:
            tmp = f.name

        wavfile.write(tmp, sample_rate, audio.flatten())

        result = model.transcribe(
            tmp,
            language                   = "id",
            fp16                       = True,
            beam_size                  = 5,
            best_of                    = 5,
            temperature                = 0.0,
            condition_on_previous_text = True,
            initial_prompt             = "Perintah Bahasa Indonesia untuk PETER."
        )
        os.unlink(tmp)

        text = result["text"].strip()
        if text:
            print(f"[{USER_NAME}] {text}")
            return text
        return None

    except Exception as e:
        print(f"[VOICE] Error: {e}")
        return _listen_fallback()


def _listen_fallback() -> str:
    """Fallback ke Google STT"""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("[VOICE] Google STT fallback...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        return r.recognize_google(audio, language="id-ID")
    except Exception:
        return None


def wait_wakeword() -> bool:
    """Tunggu wake word 'Hey Peter'"""
    try:
        import sounddevice as sd
        import scipy.io.wavfile as wavfile
        import tempfile
        import numpy as np
        import whisper

        if not hasattr(wait_wakeword, '_model'):
            print("[VOICE] Loading wake word model...")
            wait_wakeword._model = whisper.load_model("small")

        model       = wait_wakeword._model
        sample_rate = 16000
        wake_words  = [
            "hey peter", "hi peter", "hei peter",
            "peter", "hai peter", "hey piter"
        ]

        print("\n[VOICE] Menunggu 'Hey Peter'... (Ctrl+C untuk skip)\n")

        while True:
            try:
                print(".", end="", flush=True)
                audio = sd.rec(
                    int(3 * sample_rate),
                    samplerate = sample_rate,
                    channels   = 1,
                    dtype      = 'float32'
                )
                sd.wait()

                if np.abs(audio).mean() < 0.005:
                    continue

                with tempfile.NamedTemporaryFile(
                    suffix='.wav', delete=False
                ) as f:
                    tmp = f.name
                wavfile.write(tmp, sample_rate, audio.flatten())

                result = model.transcribe(
                    tmp,
                    language    = "id",
                    fp16        = True,
                    beam_size   = 3,
                    temperature = 0.0
                )
                os.unlink(tmp)

                text = result["text"].strip().lower()
                if text:
                    print(f"\n[Terdengar] {text}")

                if any(w in text for w in wake_words):
                    print("\n[VOICE] Wake word!")
                    peter_speak(f"Ya {USER_NAME}, saya siap!")
                    return True

            except Exception:
                pass

    except KeyboardInterrupt:
        print("\n[VOICE] Skip.")
        return False