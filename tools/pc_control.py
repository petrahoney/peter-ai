"""
tools/pc_control.py
PC Control dengan PyAutoGUI
"""

from crewai.tools import tool
import os
import sys
sys.path.append("C:\\peter-ai")


@tool
def take_screenshot(filename: str = "screenshot.png") -> str:
    """Ambil screenshot layar"""
    try:
        import pyautogui
        path = f"C:\\peter-ai\\data\\outputs\\{filename}"
        pyautogui.screenshot(path)
        return f"Screenshot disimpan: {path}"
    except Exception as e:
        return f"Error: {e}"


@tool
def open_application(app_name: str) -> str:
    """Buka aplikasi di Windows"""
    try:
        os.startfile(app_name)
        return f"Aplikasi '{app_name}' dibuka"
    except Exception as e:
        return f"Error: {e}"


@tool
def get_system_info() -> str:
    """Dapatkan info sistem PC"""
    try:
        import psutil
        cpu    = psutil.cpu_percent(interval=1)
        ram    = psutil.virtual_memory()
        disk   = psutil.disk_usage('C:\\')
        output = f"""Info Sistem PETER:
CPU Usage  : {cpu}%
RAM Used   : {ram.percent}% ({ram.used//1024//1024//1024}GB / {ram.total//1024//1024//1024}GB)
Disk C:    : {disk.percent}% used ({disk.free//1024//1024//1024}GB free)"""
        return output
    except Exception as e:
        return f"Error: {e}"


@tool
def type_text(text: str) -> str:
    """Ketik teks menggunakan PyAutoGUI"""
    try:
        import pyautogui
        import time
        time.sleep(1)
        pyautogui.typewrite(text, interval=0.05)
        return f"Teks diketik: {text[:50]}..."
    except Exception as e:
        return f"Error: {e}"