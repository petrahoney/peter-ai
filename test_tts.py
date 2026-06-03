import sys
sys.path.append("C:\\peter-ai")
from peter_tts import peter_speak, clean_text_for_tts

# Test 1: Bersihkan teks kotor
dirty = """
## Cara Menghasilkan Uang dari AI! 🚀

**Langkah 1:** Install Python ✅
- Buka terminal
- Ketik `pip install anthropic`
- Jalankan! 

### Hasil:
> Output: Hello World!!!
> Status: [BERHASIL]
https://example.com/tutorial
"""

clean = clean_text_for_tts(dirty)
print("TEKS BERSIH:")
print(clean)
print()

# Test 2: Speak teks pendek
print("Test speak pendek...")
peter_speak("Halo Tjerlang! Saya PETER, asisten AI kamu. Semua sistem berjalan dengan baik hari ini.")

input("\nTekan Enter untuk test teks panjang...")

# Test 3: Speak teks panjang
long_text = """
Halo semuanya dan selamat datang kembali di channel ini.
Di video kali ini kita akan membahas cara menghasilkan uang dari kecerdasan buatan.
Ada tiga cara utama yang bisa kamu coba mulai hari ini.
Pertama adalah membuat konten YouTube menggunakan AI untuk otomasi.
Kedua adalah menjual jasa menggunakan tool AI kepada klien.
Ketiga adalah membangun produk digital berbasis AI.
Masing-masing cara ini memiliki potensi penghasilan yang berbeda.
Cara pertama bisa menghasilkan antara satu hingga sepuluh juta rupiah per bulan.
Cara kedua bisa menghasilkan antara lima hingga lima puluh juta rupiah per bulan.
Cara ketiga memiliki potensi tidak terbatas tergantung seberapa besar produk yang kamu buat.
Jadi tonton video ini sampai habis karena di akhir ada tips yang paling penting.
"""

print("Test speak panjang (akan di-chunk otomatis)...")
peter_speak(long_text)
print("Selesai!")