"""
tools/file_manager.py
File operations untuk PETER — Fixed untuk CrewAI
"""

from crewai.tools import tool
import os
import sys
sys.path.append("C:\\peter-ai")

OUTPUT_DIR = "C:\\peter-ai\\data\\outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


@tool("save_text_file")
def save_text_file(filename: str, content: str) -> str:
    """
    Simpan teks ke file.
    WAJIB berikan KEDUA argument: filename DAN content.
    Contoh: filename='script.txt', content='isi konten di sini'
    """
    try:
        if not filename:
            return "Error: filename tidak boleh kosong"
        if not content:
            return "Error: content tidak boleh kosong"
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File berhasil disimpan: {path}"
    except Exception as e:
        return f"Error: {e}"


@tool("read_text_file")
def read_text_file(filename: str) -> str:
    """
    Baca isi file dari folder outputs.
    Berikan filename yang ingin dibaca.
    """
    try:
        path = os.path.join(OUTPUT_DIR, filename)
        if not os.path.exists(path):
            return f"File tidak ditemukan: {filename}"
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"


@tool("list_output_files")
def list_output_files() -> str:
    """Tampilkan semua file di folder outputs"""
    try:
        files = os.listdir(OUTPUT_DIR)
        if not files:
            return "Folder outputs kosong"
        output = "File di outputs:\n"
        for f in files:
            path = os.path.join(OUTPUT_DIR, f)
            size = os.path.getsize(path)
            output += f"  - {f} ({size:,} bytes)\n"
        return output
    except Exception as e:
        return f"Error: {e}"