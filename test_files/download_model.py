import whisper
print("Downloading Whisper large-v3...")
print("Ukuran: ~3GB — mohon tunggu...")
model = whisper.load_model("large-v3")
print("Download selesai!")
print(f"Device: {next(model.parameters()).device}")
print("Model siap dipakai PETER!")