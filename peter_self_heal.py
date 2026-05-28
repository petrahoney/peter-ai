"""
peter_self_heal.py
PETER Self-Healing & Self-Improvement System
Monitor + Auto-Fix + Propose Improvements
"""

import os
import sys
import subprocess
import shutil
import time
import json
from datetime import datetime
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
USER_NAME     = os.getenv("USER_NAME", "Sir")
LOG_DIR       = "C:\\peter-ai\\data\\logs"
BACKUP_DIR    = "C:\\peter-ai\\data\\backups"
OUTPUT_DIR    = "C:\\peter-ai\\data\\outputs"

os.makedirs(LOG_DIR,    exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)


class PeterSelfHeal:
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        self.proposals    = []
        print("[SELF-HEAL] System initialized!")

    # ──────────────────────────────────────────────
    # MONITORING
    # ──────────────────────────────────────────────

    def check_all(self) -> dict:
        """Cek semua sistem PETER"""
        print("\n[SELF-HEAL] Mendiagnosa semua sistem...")
        report = {
            "timestamp" : datetime.now().isoformat(),
            "healthy"   : [],
            "issues"    : [],
            "fixed"     : [],
            "warnings"  : []
        }

        # 1. Cek dependencies
        print("[SELF-HEAL] Cek dependencies...")
        dep_result = self._check_dependencies()
        if dep_result["missing"]:
            report["issues"].append({
                "type"   : "missing_packages",
                "detail" : dep_result["missing"]
            })
        else:
            report["healthy"].append("dependencies")

        # 2. Cek ChromaDB
        print("[SELF-HEAL] Cek memory system...")
        mem_result = self._check_memory()
        if mem_result["ok"]:
            report["healthy"].append(f"memory ({mem_result['count']} memories)")
        else:
            report["issues"].append({
                "type"  : "memory_corrupt",
                "detail": mem_result["error"]
            })

        # 3. Cek disk space
        print("[SELF-HEAL] Cek disk space...")
        disk_result = self._check_disk()
        if disk_result["free_gb"] < 5:
            report["warnings"].append(
                f"Disk hampir penuh: {disk_result['free_gb']:.1f}GB tersisa"
            )
        else:
            report["healthy"].append(
                f"disk ({disk_result['free_gb']:.1f}GB free)"
            )

        # 4. Cek API keys
        print("[SELF-HEAL] Cek API keys...")
        api_result = self._check_api_keys()
        for key, status in api_result.items():
            if status:
                report["healthy"].append(f"API:{key}")
            else:
                report["warnings"].append(f"API key kosong: {key}")

        # 5. Cek file-file penting
        print("[SELF-HEAL] Cek file sistem...")
        files_result = self._check_critical_files()
        for f, exists in files_result.items():
            if exists:
                report["healthy"].append(f"file:{f}")
            else:
                report["issues"].append({
                    "type"  : "missing_file",
                    "detail": f
                })

        # 6. Cek kamera
        print("[SELF-HEAL] Cek kamera...")
        cam_result = self._check_camera()
        if cam_result["ok"]:
            report["healthy"].append("camera")
        else:
            report["warnings"].append("Kamera tidak terdeteksi")

        # 7. Cek temp files
        print("[SELF-HEAL] Cek temp files...")
        temp_result = self._check_temp_files()
        if temp_result["count"] > 10:
            report["warnings"].append(
                f"{temp_result['count']} temp files ({temp_result['size_mb']:.1f}MB)"
            )

        # Simpan report
        self._save_report(report)
        return report

    def _check_dependencies(self) -> dict:
        """Cek semua package yang dibutuhkan"""
        required = {
            "anthropic"        : "anthropic",
            "crewai"           : "crewai",
            "elevenlabs"       : "elevenlabs",
            "whisper"          : "whisper",
            "cv2"              : "opencv-python",
            "chromadb"         : "chromadb",
            "fastapi"          : "fastapi",
            "face_recognition" : "face-recognition",
            "PIL"              : "pillow",
            "sounddevice"      : "sounddevice",
            "scipy"            : "scipy",
        }
        missing = []
        for import_name, pkg_name in required.items():
            try:
                __import__(import_name)
            except ImportError:
                missing.append(pkg_name)
        return {"missing": missing, "total": len(required)}

    def _check_memory(self) -> dict:
        """Cek ChromaDB memory system"""
        try:
            from peter_memory import PeterMemory
            m     = PeterMemory()
            stats = m.get_stats()
            return {
                "ok"   : True,
                "count": stats["long_term_count"]
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _check_disk(self) -> dict:
        """Cek ruang disk"""
        usage   = shutil.disk_usage("C:\\")
        free_gb = usage.free / (1024 ** 3)
        used_gb = usage.used / (1024 ** 3)
        total_gb= usage.total / (1024 ** 3)
        return {
            "free_gb" : free_gb,
            "used_gb" : used_gb,
            "total_gb": total_gb,
            "percent" : usage.used / usage.total * 100
        }

    def _check_api_keys(self) -> dict:
        """Cek API keys tersedia"""
        return {
            "ANTHROPIC"  : bool(os.getenv("ANTHROPIC_API_KEY")),
            "ELEVENLABS" : bool(os.getenv("ELEVENLABS_API_KEY")),
            "ELEVENLABS_VOICE": bool(os.getenv("ELEVENLABS_VOICE_ID")),
        }

    def _check_critical_files(self) -> dict:
        """Cek file-file penting PETER"""
        files = {
            "main_peter.py"    : "C:\\peter-ai\\main_peter.py",
            "peter_memory.py"  : "C:\\peter-ai\\peter_memory.py",
            "peter_vision.py"  : "C:\\peter-ai\\peter_vision.py",
            "config.py"        : "C:\\peter-ai\\config.py",
            ".env"             : "C:\\peter-ai\\.env",
        }
        return {
            name: os.path.exists(path)
            for name, path in files.items()
        }

    def _check_camera(self) -> dict:
        """Cek kamera tersedia"""
        try:
            import cv2
            cap = cv2.VideoCapture(
                int(os.getenv("CAMERA_INDEX", 0))
            )
            ok  = cap.isOpened()
            cap.release()
            return {"ok": ok}
        except Exception:
            return {"ok": False}

    def _check_temp_files(self) -> dict:
        """Cek temp files di outputs"""
        import glob
        patterns = [
            f"{OUTPUT_DIR}\\_*.mp4",
            f"{OUTPUT_DIR}\\_*.txt",
            f"{OUTPUT_DIR}\\_*.jpg",
        ]
        files    = []
        total_sz = 0
        for p in patterns:
            found = glob.glob(p)
            files.extend(found)
            for f in found:
                try:
                    total_sz += os.path.getsize(f)
                except Exception:
                    pass
        return {
            "count"  : len(files),
            "files"  : files,
            "size_mb": total_sz / (1024 * 1024)
        }

    # ──────────────────────────────────────────────
    # AUTO-FIX
    # ──────────────────────────────────────────────

    def auto_fix_all(self, report: dict) -> list:
        """Auto-fix semua masalah yang bisa diperbaiki"""
        fixed = []

        for issue in report.get("issues", []):
            issue_type = issue["type"]

            if issue_type == "missing_packages":
                result = self.fix_missing_packages(issue["detail"])
                if result:
                    fixed.extend(result)

            elif issue_type == "memory_corrupt":
                result = self.fix_memory()
                if result:
                    fixed.append("memory_reset")

            elif issue_type == "missing_file":
                print(f"[SELF-HEAL] ⚠️ File hilang: {issue['detail']}")
                print("[SELF-HEAL] File ini tidak bisa dibuat otomatis")

        # Fix warnings
        for warning in report.get("warnings", []):
            if "temp files" in warning:
                self.cleanup_temp_files()
                fixed.append("cleanup_temp")

        self.fixes_applied.extend(fixed)
        return fixed

    def fix_missing_packages(self, packages: list) -> list:
        """Install package yang hilang"""
        installed = []
        for pkg in packages:
            print(f"[SELF-HEAL] Installing {pkg}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg],
                capture_output = True,
                text           = True
            )
            if result.returncode == 0:
                installed.append(pkg)
                print(f"[SELF-HEAL] ✅ {pkg} terinstall")
            else:
                print(f"[SELF-HEAL] ❌ {pkg} gagal: {result.stderr[:100]}")
        return installed

    def fix_memory(self) -> bool:
        """Reset ChromaDB jika corrupt"""
        try:
            memory_dir  = "C:\\peter-ai\\data\\memory"
            backup_path = os.path.join(
                BACKUP_DIR,
                f"memory_backup_{int(time.time())}"
            )
            if os.path.exists(memory_dir):
                shutil.move(memory_dir, backup_path)
                print(f"[SELF-HEAL] Memory backup: {backup_path}")
            os.makedirs(memory_dir, exist_ok=True)
            print("[SELF-HEAL] ✅ Memory direset")
            return True
        except Exception as e:
            print(f"[SELF-HEAL] Memory fix error: {e}")
            return False

    def cleanup_temp_files(self) -> int:
        """Hapus temp files"""
        import glob
        patterns = [
            f"{OUTPUT_DIR}\\_*.mp4",
            f"{OUTPUT_DIR}\\_*.txt",
            f"{OUTPUT_DIR}\\_*.jpg",
            f"{OUTPUT_DIR}\\temp_*.mp4",
            f"{OUTPUT_DIR}\\peter_*.py",
        ]
        deleted = 0
        for p in patterns:
            for f in glob.glob(p):
                try:
                    os.unlink(f)
                    deleted += 1
                except Exception:
                    pass
        print(f"[SELF-HEAL] ✅ {deleted} temp files dihapus")
        return deleted

    # ──────────────────────────────────────────────
    # SELF-IMPROVEMENT — PROPOSE & APPLY
    # ──────────────────────────────────────────────

    def propose_improvement(self, problem: str) -> str:
        """
        Analisis masalah dan propose solusi kode
        User harus approve sebelum diterapkan
        """
        print(f"\n[SELF-HEAL] Menganalisis: {problem}")
        try:
            import anthropic
            client   = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
            response = client.messages.create(
                model      = "claude-sonnet-4-6",
                max_tokens = 2048,
                system     = f"""Kamu adalah PETER AI system engineer.
Analisis masalah sistem PETER AI dan propose solusi.

Format output HARUS persis:
MASALAH: [deskripsi jelas masalah]
PENYEBAB: [root cause analisis]
FILE: [nama file Python yang perlu diubah]
SOLUSI_KODE: [kode Python pengganti — lengkap]
RISIKO: [rendah/sedang/tinggi]
ESTIMASI: [estimasi waktu fix dalam menit]""",
                messages   = [{
                    "role"   : "user",
                    "content": f"Analisis dan propose fix untuk masalah PETER:\n{problem}"
                }]
            )
            proposal = response.content[0].text

            # Simpan proposal
            log_file = os.path.join(
                LOG_DIR, "improvement_proposals.txt"
            )
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Waktu   : {datetime.now()}\n")
                f.write(f"Masalah : {problem}\n")
                f.write(f"Proposal:\n{proposal}\n")

            self.proposals.append({
                "problem" : problem,
                "proposal": proposal,
                "time"    : datetime.now().isoformat()
            })

            print(f"[SELF-HEAL] Proposal disimpan ke: {log_file}")
            return proposal

        except Exception as e:
            return f"Error analisis: {e}"

    def apply_fix(self, file_path: str,
                  old_code: str,
                  new_code: str,
                  description: str = "") -> bool:
        """
        Terapkan fix kode — SELALU backup dulu
        Harus ada approval user sebelum dipanggil
        """
        if not os.path.exists(file_path):
            print(f"[SELF-HEAL] File tidak ditemukan: {file_path}")
            return False

        # Backup
        backup_name = os.path.basename(file_path)
        backup_path = os.path.join(
            BACKUP_DIR,
            f"{backup_name}.{int(time.time())}.bak"
        )
        try:
            shutil.copy(file_path, backup_path)
            print(f"[SELF-HEAL] Backup: {backup_path}")
        except Exception as e:
            print(f"[SELF-HEAL] Backup gagal: {e}")
            return False

        # Apply fix
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if old_code not in content:
                print("[SELF-HEAL] Kode lama tidak ditemukan!")
                return False

            new_content = content.replace(old_code, new_code, 1)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            # Log fix
            log_file = os.path.join(LOG_DIR, "fixes_applied.txt")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"Waktu      : {datetime.now()}\n")
                f.write(f"File       : {file_path}\n")
                f.write(f"Deskripsi  : {description}\n")
                f.write(f"Backup     : {backup_path}\n")

            print(f"[SELF-HEAL] ✅ Fix diterapkan: {file_path}")
            return True

        except Exception as e:
            print(f"[SELF-HEAL] Apply fix error: {e}")
            # Restore backup
            try:
                shutil.copy(backup_path, file_path)
                print("[SELF-HEAL] Backup restored!")
            except Exception:
                pass
            return False

    def rollback(self, file_path: str) -> bool:
        """Rollback ke versi backup terakhir"""
        import glob
        backup_name = os.path.basename(file_path)
        backups     = sorted(
            glob.glob(f"{BACKUP_DIR}\\{backup_name}.*.bak"),
            reverse=True
        )
        if not backups:
            print("[SELF-HEAL] Tidak ada backup ditemukan!")
            return False

        latest = backups[0]
        try:
            shutil.copy(latest, file_path)
            print(f"[SELF-HEAL] ✅ Rollback dari: {latest}")
            return True
        except Exception as e:
            print(f"[SELF-HEAL] Rollback error: {e}")
            return False

    # ──────────────────────────────────────────────
    # PERFORMANCE MONITOR
    # ──────────────────────────────────────────────

    def get_performance_stats(self) -> dict:
        """Statistik performa PETER"""
        import glob

        stats = {
            "timestamp"       : datetime.now().isoformat(),
            "memory_memories" : 0,
            "output_files"    : 0,
            "output_size_mb"  : 0,
            "backup_count"    : 0,
            "log_count"       : 0,
            "youtube_uploads" : 0,
        }

        # Memory stats
        try:
            from peter_memory import PeterMemory
            m                      = PeterMemory()
            s                      = m.get_stats()
            stats["memory_memories"] = s["long_term_count"]
        except Exception:
            pass

        # Output files
        output_files = os.listdir(OUTPUT_DIR) if os.path.exists(OUTPUT_DIR) else []
        stats["output_files"] = len(output_files)
        stats["output_size_mb"] = sum(
            os.path.getsize(os.path.join(OUTPUT_DIR, f))
            for f in output_files
            if os.path.isfile(os.path.join(OUTPUT_DIR, f))
        ) / (1024 * 1024)

        # Backup count
        stats["backup_count"] = len(
            glob.glob(f"{BACKUP_DIR}\\*.bak")
        )

        # YouTube uploads dari report
        reports = glob.glob(
            f"{OUTPUT_DIR}\\pipeline_report*.txt"
        )
        stats["youtube_uploads"] = len(reports)

        return stats

    # ──────────────────────────────────────────────
    # DAILY REPORT
    # ──────────────────────────────────────────────

    def generate_daily_report(self) -> str:
        """Generate laporan harian PETER"""
        report  = self.check_all()
        stats   = self.get_performance_stats()
        disk    = self._check_disk()

        lines = [
            f"PETER AI — Laporan Harian",
            f"{'='*40}",
            f"Tanggal  : {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"",
            f"STATUS SISTEM:",
        ]

        for h in report["healthy"]:
            lines.append(f"  ✅ {h}")

        if report["issues"]:
            lines.append(f"\nMASALAH:")
            for issue in report["issues"]:
                lines.append(f"  ❌ {issue['type']}: {issue['detail']}")

        if report["warnings"]:
            lines.append(f"\nPERINGATAN:")
            for w in report["warnings"]:
                lines.append(f"  ⚠️ {w}")

        lines.extend([
            f"",
            f"STATISTIK:",
            f"  Memories     : {stats['memory_memories']}",
            f"  Output files : {stats['output_files']} ({stats['output_size_mb']:.1f}MB)",
            f"  YT Uploads   : {stats['youtube_uploads']}",
            f"  Backups      : {stats['backup_count']}",
            f"  Disk free    : {disk['free_gb']:.1f}GB ({100-disk['percent']:.0f}%)",
        ])

        text = "\n".join(lines)

        # Simpan report
        report_file = os.path.join(
            LOG_DIR,
            f"daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"[SELF-HEAL] Report: {report_file}")
        return text

    def _save_report(self, report: dict):
        """Simpan report ke log"""
        log_file = os.path.join(LOG_DIR, "health_log.json")
        logs     = []
        if os.path.exists(log_file):
            try:
                with open(log_file, "r") as f:
                    logs = json.load(f)
            except Exception:
                pass
        logs.append(report)
        logs = logs[-30:]  # Keep 30 reports terakhir
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)


# ──────────────────────────────────────────────────
# INTERACTIVE MODE
# ──────────────────────────────────────────────────
def run_self_heal_menu():
    healer = PeterSelfHeal()

    while True:
        print("\n" + "=" * 50)
        print("  PETER Self-Heal System")
        print("=" * 50)
        print("  [1] Diagnosa semua sistem")
        print("  [2] Auto-fix masalah")
        print("  [3] Propose improvement")
        print("  [4] Cleanup temp files")
        print("  [5] Laporan harian")
        print("  [6] Performance stats")
        print("  [7] Rollback file")
        print("  [8] Keluar")
        print("=" * 50)

        pilihan = input(f"\n[{USER_NAME}] Pilih (1-8): ").strip()

        if pilihan == "1":
            report = healer.check_all()
            print(f"\n✅ Sehat  : {len(report['healthy'])}")
            print(f"❌ Masalah: {len(report['issues'])}")
            print(f"⚠️ Warning: {len(report['warnings'])}")

            if report["issues"]:
                print("\nMasalah ditemukan:")
                for i in report["issues"]:
                    print(f"  ❌ {i['type']}: {i['detail']}")

            if report["warnings"]:
                print("\nPeringatan:")
                for w in report["warnings"]:
                    print(f"  ⚠️ {w}")

        elif pilihan == "2":
            report = healer.check_all()
            if not report["issues"]:
                print("\n✅ Tidak ada masalah!")
            else:
                print(f"\n{len(report['issues'])} masalah ditemukan.")
                fix = input("Auto-fix sekarang? (y/n): ").strip().lower()
                if fix == 'y':
                    fixed = healer.auto_fix_all(report)
                    print(f"\n✅ {len(fixed)} masalah diperbaiki: {fixed}")

        elif pilihan == "3":
            problem = input("\nDeskripsikan masalah: ").strip()
            if problem:
                proposal = healer.propose_improvement(problem)
                print(f"\nProposal:\n{proposal}")

                apply = input("\nTerapkan fix? (y/n): ").strip().lower()
                if apply == 'y':
                    file_path = input("Path file: ").strip()
                    old_code  = input("Kode lama (Enter untuk skip): ").strip()
                    new_code  = input("Kode baru: ").strip()
                    if file_path and new_code:
                        healer.apply_fix(
                            file_path   = file_path,
                            old_code    = old_code,
                            new_code    = new_code,
                            description = problem
                        )

        elif pilihan == "4":
            deleted = healer.cleanup_temp_files()
            print(f"\n✅ {deleted} file dihapus!")

        elif pilihan == "5":
            report_text = healer.generate_daily_report()
            print(f"\n{report_text}")

        elif pilihan == "6":
            stats = healer.get_performance_stats()
            print(f"\nPerforma PETER:")
            for k, v in stats.items():
                if k != "timestamp":
                    print(f"  {k}: {v}")

        elif pilihan == "7":
            file_path = input("\nPath file untuk rollback: ").strip()
            if file_path:
                healer.rollback(file_path)

        elif pilihan == "8":
            print("\n[SELF-HEAL] Keluar.")
            break


if __name__ == "__main__":
    run_self_heal_menu()