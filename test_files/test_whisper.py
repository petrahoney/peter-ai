import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os
import torch

print("=" * 50)
print("  Test Whisper GPU untuk PETER")
print("=" * 50)
print(f"GPU: {torch.cuda.get_device_name(0)}")

print("\nLoading model medium...")
model = whisper.load_model("medium")
print("Model siap di:", next(model.parameters()).device)

def record_audio(duration=5, sample_rate=16000):
    print(f"\nMerekam {duration} detik... BICARA SEKARANG!")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate = sample_rate,
        channels   = 1,
        dtype      = 'float32'
    )
    sd.wait()
    print("Selesai merekam!")
    return audio.flatten(), sample_rate

def transcribe(audio, sample_rate):
    with tempfile.NamedTemporaryFile(
        suffix='.wav', delete=False
    ) as f:
        tmp = f.name
    wav.write(tmp, sample_rate, audio)
    print("Memproses dengan Whisper GPU...")
    result = model.transcribe(
        tmp,
        language = "id",
        fp16     = True
    )
    os.unlink(tmp)
    return result["text"].strip()

for i in range(3):
    input(f"\nTest {i+1}/3 — Tekan Enter lalu bicara...")
    audio, sr = record_audio(duration=5)
    text = transcribe(audio, sr)
    print(f"Hasil: '{text}'")

print("\nTest Whisper selesai!")