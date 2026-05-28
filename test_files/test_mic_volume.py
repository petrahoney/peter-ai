import sounddevice as sd
import numpy as np

print("Test volume microphone — bicara sekarang!")
print("Volume bar akan muncul. Ctrl+C untuk berhenti.\n")

def callback(indata, frames, time, status):
    volume = np.abs(indata).mean()
    bars   = int(volume * 200)
    level  = "█" * min(bars, 50)
    color  = "OK" if bars > 5 else "TERLALU PELAN"
    print(f"\r[{level:<50}] {volume:.4f} {color}    ", end="")

with sd.InputStream(callback=callback, channels=1, samplerate=16000):
    print("Berbicara ke microphone...")
    try:
        while True:
            sd.sleep(100)
    except KeyboardInterrupt:
        print("\n\nSelesai!")
        print("Volume ideal: bar harus mencapai minimal 10-20 blok saat bicara")