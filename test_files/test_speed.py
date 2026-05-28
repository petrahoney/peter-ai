import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile
import numpy as np
import torch
import time
import os

print("=" * 50)
print("  PETER — Whisper Speed & Accuracy Test")
print("=" * 50)
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"CUDA: {torch.cuda.is_available()}")

# Test 3 model berbeda
models_to_test = ["small", "medium", "large"]

for model_name in models_to_test:
    pilih = input(f"\nTest model '{model_name}'? (y/n): ").strip().lower()
    if pilih != 'y':
        continue

    print(f"Loading {model_name}...")
    t0    = time.time()
    model = whisper.load_model(model_name)
    print(f"Load time: {time.time()-t0:.1f} detik")
    print(f"Device: {next(model.parameters()).device}")

    # Rekam dan test
    sample_rate = 16000
    input("Tekan Enter lalu ucapkan kalimat panjang dalam Bahasa Indonesia...")
    print("Merekam 7 detik... BICARA SEKARANG!")

    audio = sd.rec(
        int(7 * sample_rate),
        samplerate = sample_rate,
        channels   = 1,
        dtype      = 'float32'
    )
    sd.wait()
    print("Selesai!")

    with tempfile.NamedTemporaryFile(
        suffix='.wav', delete=False
    ) as f:
        tmp = f.name
    wav.write(tmp, sample_rate, audio.flatten())

    # Transkripsi dengan timer
    t1 = time.time()
    result = model.transcribe(
        tmp,
        language             = "id",
        fp16                 = True,
        beam_size            = 5,
        best_of              = 5,
        temperature          = 0.0,
        condition_on_previous_text = True
    )
    elapsed = time.time() - t1
    os.unlink(tmp)

    print(f"\nModel      : {model_name}")
    print(f"Waktu      : {elapsed:.2f} detik")
    print(f"Hasil      : '{result['text'].strip()}'")
    print(f"Language   : {result.get('language', 'unknown')}")