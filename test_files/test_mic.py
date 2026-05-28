import speech_recognition as sr

print("Test Microphone PETER")
print("=" * 40)

# Cek microphone tersedia
r = sr.Recognizer()
mics = sr.Microphone.list_microphone_names()

print(f"Microphone ditemukan: {len(mics)}")
for i, mic in enumerate(mics):
    print(f"  [{i}] {mic}")

print("\nTest bicara...")
print("Silakan ucapkan sesuatu dalam 5 detik!")

with sr.Microphone() as source:
    print("Menyesuaikan noise...")
    r.adjust_for_ambient_noise(source, duration=1)
    print("Mendengarkan... BICARA SEKARANG!")
    try:
        audio = r.listen(source, timeout=5)
        print("Memproses...")
        text = r.recognize_google(audio, language="id-ID")
        print(f"Berhasil! Kamu berkata: '{text}'")
    except sr.WaitTimeoutError:
        print("Timeout — tidak ada suara")
    except sr.UnknownValueError:
        print("Suara tidak jelas")
    except Exception as e:
        print(f"Error: {e}")