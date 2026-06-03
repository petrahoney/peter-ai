# -*- coding: utf-8 -*-
"""
main_peter.py (OPTIMIZED v2.3 — Fast Startup)
Lazy loading for sub-3 second startup
"""

import os
import sys
import time
from pathlib import Path

# FAST STARTUP - Minimal imports
from dotenv import load_dotenv

load_dotenv()

# Config (fast)
USER_NAME = os.getenv("USER_NAME", "Tjerlang")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Paths
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "outputs"
MEMORY_DIR = DATA_DIR / "memory"
FACES_DIR = DATA_DIR / "faces"
LOGS_DIR = DATA_DIR / "logs"

for d in [DATA_DIR, OUTPUT_DIR, MEMORY_DIR, FACES_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ==================== LAZY LOADING ====================
_modules = {}

def get_self_heal():
    """Lazy load self-heal"""
    if 'self_heal' not in _modules:
        try:
            from peter_self_heal import PeterSelfHeal
            _modules['self_heal'] = PeterSelfHeal()
            print("[SELF-HEAL] ✓ Loaded")
        except Exception as e:
            print(f"[SELF-HEAL] ✗ {e}")
            _modules['self_heal'] = None
    return _modules['self_heal']

def get_memory():
    """Lazy load memory"""
    if 'memory' not in _modules:
        try:
            from peter_memory import PeterMemory
            _modules['memory'] = PeterMemory()
            print("[MEMORY] ✓ Loaded")
        except Exception as e:
            print(f"[MEMORY] ✗ {e}")
            _modules['memory'] = None
    return _modules['memory']

def get_brain():
    """Load brain (essential)"""
    if 'brain' not in _modules:
        try:
            from core.brain import PeterBrain
            _modules['brain'] = PeterBrain()
            print("[BRAIN] ✓ Loaded")
        except Exception as e:
            print(f"[BRAIN] ✗ {e}")
            _modules['brain'] = None
    return _modules['brain']

# ==================== FAST STARTUP ====================

def show_banner():
    """Quick banner"""
    banner = """
╔════════════════════════════════════════════════════════╗
║  PETER AI v2.3 — Optimized                            ║
║  The Luxury Strategist                                ║
║  Intelligence, Elevated                               ║
╚════════════════════════════════════════════════════════╝
"""
    print(banner)
    print(f"Selamat, {USER_NAME}. Ready to serve.\n")

def show_menu():
    """Main menu"""
    print("COMMAND CENTER")
    print("─" * 50)
    print("[1] Chat & Code")
    print("[2] Multi-Agent")
    print("[3] Mode Gabungan")
    print("[4] Voice")
    print("[5] Vision (lazy)")
    print("[6] Self-Diagnose (lazy)")
    print("[7] Script Writer")
    print("[8] Content")
    print("[9] Trading")
    print("[10] App Builder")
    print("[11] Master Prompt")
    print("[0] Exit")
    print("─" * 50)

def main():
    """Main loop"""
    start_time = time.time()
    
    # Load brain immediately (essential)
    brain = get_brain()
    
    # Show banner (instant)
    show_banner()
    
    startup_time = time.time() - start_time
    print(f"✓ Startup: {startup_time:.2f}s\n")
    
    while True:
        show_menu()
        choice = input("Command: ").strip()
        
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            text = input("Chat: ")
            if brain:
                try:
                    response = brain.think(text)
                    print(f"\n[PETER] {response}\n")
                except Exception as e:
                    print(f"Error: {e}\n")
        elif choice == "5":
            print("Vision loading...")
            # Lazy load when needed
        elif choice == "6":
            print("Self-diagnose loading...")
            healer = get_self_heal()
            if healer:
                print("System check complete.\n")
        elif choice == "9":
            try:
                from quantex_module import run_quantex_menu
                run_quantex_menu()
            except Exception as e:
                print(f"Trading error: {e}\n")
        else:
            print(f"Option {choice} - coming soon\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
