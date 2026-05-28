from interpreter import interpreter

# Pakai Ollama lokal - GRATIS, tanpa API key
interpreter.llm.model = "ollama/llama3.2:3b"
interpreter.llm.api_base = "http://localhost:11434"
interpreter.auto_run = True

# Persona PETER
interpreter.system_message = """
Kamu adalah PETER - Personal Enhanced Thinking & Execution Robot.
Asisten AI pribadi yang canggih dan berbicara Bahasa Indonesia.
Selesaikan semua task sampai tuntas.
"""

# Mulai chat
interpreter.chat()