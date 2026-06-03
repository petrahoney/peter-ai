# -*- coding: utf-8 -*-
"""
peter_tts.py
PETER Text-to-Speech Engine
The Luxury Strategist — Intelligence, Elevated.
"""

import os
import re
import time
from dotenv import load_dotenv
load_dotenv()

ELEVENLABS_KEY   = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE = os.getenv("ELEVENLABS_VOICE_ID", "TIXYCOMzK2Vw9OZovSLs")
OUTPUT_DIR       = "C:\\peter-ai\\data\\outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def clean_text_for_tts(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}(.*?)_{1,3}', r'\1', text)
    text = re.sub(r'```[\s\S]*?```', 'kode', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    text = re.sub(
        r'[🎉🎊🚀💪✅❌⚠️🔥💰📊📈🎬🎙️👍👋🤖🧠👁️💻🗣️⚡💡🎯📋]',
        '', text
    )
    text = re.sub(r'^\s*[-•*→►▶]\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'[#@^~`|\\]', '', text)
    text = re.sub(r'[=\-]{2,}', '', text)
    text = re.sub(r'!{2,}', '!', text)
    text = re.sub(r'\?{2,}', '?', text)
    text = text.replace('&', 'dan')
    text = text.replace('%', 'persen')
    text = text.replace('+', 'plus')
    text = text.replace('→', ',')
    text = text.replace('|', ',')
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    text  = ' '.join(lines)
    return text.strip()


def split_into_chunks(text: str, max_chars: int = 400) -> list:
    if len(text) <= max_chars:
        return [text]
    chunks    = []
    remaining = text
    while len(remaining) > max_chars:
        chunk   = remaining[:max_chars]
        cut_pos = -1
        for sep in ['. ', '! ', '? ', ', ', ' ']:
            pos = chunk.rfind(sep)
            if pos > max_chars // 2:
                cut_pos = pos + len(sep)
                break
        if cut_pos == -1:
            cut_pos = chunk.rfind(' ')
        if cut_pos == -1:
            cut_pos = max_chars
        chunks.append(remaining[:cut_pos].strip())
        remaining = remaining[cut_pos:].strip()
    if remaining:
        chunks.append(remaining)
    return [c for c in chunks if c]


def generate_audio_chunk(text: str, filename: str) -> str:
    from elevenlabs import ElevenLabs, VoiceSettings
    client = ElevenLabs(api_key=ELEVENLABS_KEY)
    audio  = client.text_to_speech.convert(
        voice_id       = ELEVENLABS_VOICE,
        text           = text,
        model_id       = "eleven_multilingual_v2",
        voice_settings = VoiceSettings(
            stability        = 0.45,
            similarity_boost = 0.82,
            style            = 0.5,
            use_speaker_boost= True
        )
    )
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)
    return path


def merge_audio_files(audio_files: list,
                      output_name: str = "merged.mp3") -> str:
    import subprocess
    import shutil
    output_path = os.path.join(OUTPUT_DIR, output_name)
    if len(audio_files) == 1:
        shutil.copy(audio_files[0], output_path)
        return output_path
    list_file = os.path.join(OUTPUT_DIR, "_speech_list.txt")
    with open(list_file, "w") as f:
        for af in audio_files:
            f.write(f"file '{af.replace(chr(92), '/')}'\n")
    subprocess.run(
        f'ffmpeg -y -f concat -safe 0 -i "{list_file}" -c copy "{output_path}"',
        shell=True, capture_output=True
    )
    try:
        os.unlink(list_file)
    except Exception:
        pass
    return output_path if os.path.exists(output_path) else audio_files[0]


def _play_audio(audio_path: str):
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        print("[TTS] Audio selesai diputar!")
    except Exception as e:
        print(f"[TTS] pygame error: {e}")
        try:
            import subprocess
            subprocess.Popen(['start', '', audio_path], shell=True)
        except Exception:
            pass


def peter_speak(text: str,
                play: bool = True,
                max_chars_per_chunk: int = 400) -> str:
    if not text or not text.strip():
        return None

    clean = clean_text_for_tts(text)
    if not clean:
        return None

    print(f"[TTS] Teks ({len(clean)} karakter): {clean[:80]}...")

    try:
        chunks = split_into_chunks(clean, max_chars_per_chunk)
        print(f"[TTS] {len(chunks)} chunk(s)")

        if len(chunks) == 1:
            generate_audio_chunk(clean, "peter_voice.mp3")
            audio_path = os.path.join(OUTPUT_DIR, "peter_voice.mp3")
        else:
            chunk_files = []
            for i, chunk in enumerate(chunks):
                print(f"[TTS] Chunk {i+1}/{len(chunks)}: {chunk[:50]}...")
                path = generate_audio_chunk(chunk, f"_chunk_{i:03d}.mp3")
                chunk_files.append(path)
            print(f"[TTS] Menggabungkan {len(chunk_files)} chunk...")
            audio_path = merge_audio_files(chunk_files, "peter_voice.mp3")
            for cf in chunk_files:
                try:
                    os.unlink(cf)
                except Exception:
                    pass

        if play and os.path.exists(audio_path):
            _play_audio(audio_path)

        return audio_path

    except Exception as e:
        print(f"[TTS] ElevenLabs error: {e}")
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(clean[:300])
            engine.runAndWait()
        except Exception:
            pass
        return None


def generate_voiceover(script: str,
                       output_name: str = "voiceover.mp3",
                       max_words: int = 350) -> str:
    import anthropic
    ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    if not script or not script.strip():
        return None

    clean = clean_text_for_tts(script)
    if len(clean.split()) < 30:
        clean = script[:4000]

    client   = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    response = client.messages.create(
        model      = "claude-sonnet-4-6",
        max_tokens = 2000,
        system     = f"""Tulis ulang script menjadi narasi video natural untuk TTS.
Output HANYA teks narasi. Hapus semua markdown, timestamp, label.
Bahasa Indonesia conversational. Target {max_words} kata.""",
        messages   = [{
            "role"   : "user",
            "content": f"Narasi {max_words} kata:\n\n{clean[:5000]}"
        }]
    )

    narasi = clean_text_for_tts(response.content[0].text.strip())
    if len(narasi.split()) < 30:
        narasi = clean_text_for_tts(clean[:2000])

    chunks      = split_into_chunks(narasi, max_chars=450)
    chunk_files = []

    for i, chunk in enumerate(chunks):
        try:
            path = generate_audio_chunk(chunk, f"_vo_chunk_{i:03d}.mp3")
            chunk_files.append(path)
        except Exception as e:
            print(f"[VOICEOVER] Chunk {i+1} error: {e}")

    if not chunk_files:
        return None

    output_path = os.path.join(OUTPUT_DIR, output_name)
    if len(chunk_files) > 1:
        merge_audio_files(chunk_files, output_name)
    else:
        import shutil
        shutil.copy(chunk_files[0], output_path)

    for cf in chunk_files:
        try:
            os.unlink(cf)
        except Exception:
            pass

    teks_file = output_path.replace('.mp3', '_teks.txt')
    with open(teks_file, "w", encoding="utf-8") as f:
        f.write(narasi)

    if os.path.exists(output_path):
        return output_path
    return None