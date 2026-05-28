"""
core/brain.py
Otak PETER — Routing & Logic utama
"""

import sys
import os
sys.path.append("C:\\peter-ai")

from config import (
    USER_NAME, ANTHROPIC_KEY, LOCAL_MODE,
    LLM_MODEL, MEMORY_DIR
)


class PeterBrain:
    def __init__(self):
        self.memory  = None
        self.vision  = None
        self._init_memory()
        self._init_vision()
        print("[BRAIN] Peter Brain initialized!")

    def _init_memory(self):
        try:
            from peter_memory import PeterMemory
            self.memory = PeterMemory()
            print("[BRAIN] Memory OK!")
        except Exception as e:
            print(f"[BRAIN] Memory error: {e}")

    def _init_vision(self):
        try:
            from peter_vision import PeterVision
            self.vision = PeterVision()
            print("[BRAIN] Vision OK!")
        except Exception as e:
            print(f"[BRAIN] Vision error: {e}")

    def think(self, message: str) -> str:
        """Proses pesan dan routing ke module yang tepat"""
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

        # Bangun context dari memory
        context_str = ""
        history     = []
        if self.memory:
            ctx         = self.memory.build_context(message)
            context_str = ctx["context_string"]
            history     = ctx["history"]

        system = f"""Kamu adalah PETER — Personal Enhanced Thinking & Execution Robot.
Asisten AI pribadi paling canggih milik {USER_NAME}.

IDENTITAS:
- Nama: PETER
- Pemilik: {USER_NAME}
- Kepribadian: Cerdas, analitis, proaktif seperti JARVIS
- Bahasa: Indonesia
- Gaya: Profesional dan friendly

KEMAMPUAN:
1. Analisis mendalam dengan data dan fakta
2. Content creation — script, caption, artikel
3. Strategi monetisasi konten digital
4. Python coding dan otomasi
5. YouTube, Instagram, TikTok growth strategy
6. Riset topik viral dan SEO

CARA MENJAWAB:
- SELALU detail, lengkap, dan actionable
- Gunakan angka dan contoh konkret
- Berikan langkah yang bisa langsung dilakukan
- Akhiri dengan next step

KONTEKS {USER_NAME}:
- Membangun bisnis konten digital
- Target: passive income dari YouTube + IG + TikTok
- Tools: PETER AI, Python, CrewAI, Claude

{f'MEMORY:{chr(10)}{context_str}' if context_str else ''}"""

        messages = []
        for h in history[-10:]:
            messages.append({
                "role"   : h["role"],
                "content": h["content"]
            })
        messages.append({
            "role"   : "user",
            "content": message
        })

        response = client.messages.create(
            model      = "claude-sonnet-4-6",
            max_tokens = 8096,
            system     = system,
            messages   = messages
        )
        answer = response.content[0].text

        # Simpan ke memory
        if self.memory:
            self.memory.add_short_term("user", message)
            self.memory.add_short_term("assistant", answer)
            self.memory.auto_learn(message, answer)

        return answer

    def analyze_intent(self, message: str) -> str:
        """Deteksi intent dari pesan user"""
        msg = message.lower()
        if any(w in msg for w in [
            "buat", "tulis", "generate", "create",
            "buat grafik", "buat chart", "buat file",
            "jalankan kode", "plot"
        ]):
            return "code"
        elif any(w in msg for w in [
            "upload", "post", "publish",
            "youtube", "instagram", "tiktok"
        ]):
            return "publish"
        elif any(w in msg for w in [
            "riset", "cari", "search",
            "trend", "viral", "analisis"
        ]):
            return "research"
        elif any(w in msg for w in [
            "script", "konten", "caption",
            "copywriting", "artikel"
        ]):
            return "content"
        else:
            return "chat"