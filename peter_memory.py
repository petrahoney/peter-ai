"""
peter_memory.py
Advanced Memory System untuk PETER
"""

import os
import json
import time
import hashlib
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
USER_NAME     = os.getenv("USER_NAME", "Sir")
MEMORY_DIR    = "C:\\peter-ai\\data\\memory"
PROFILE_FILE  = f"{MEMORY_DIR}\\user_profile.json"
EPISODES_FILE = f"{MEMORY_DIR}\\episodes.json"

os.makedirs(MEMORY_DIR, exist_ok=True)


class PeterMemory:
    def __init__(self):
        self.short_term = []
        self.max_short  = 20
        self.collection = None
        self._init_chromadb()
        self.profile  = self._load_profile()
        self.episodes = self._load_episodes()
        print("[MEMORY] Peter Memory System aktif!")
        print(f"[MEMORY] Long term: {self._count_memories()} memori")
        print(f"[MEMORY] Profile: {len(self.profile)} atribut")

    def _init_chromadb(self):
        try:
            import chromadb
            client = chromadb.PersistentClient(path=MEMORY_DIR)
            self.collection = client.get_or_create_collection(
                name     = "peter_memories",
                metadata = {"hnsw:space": "cosine"}
            )
            print("[MEMORY] ChromaDB OK!")
        except Exception as e:
            print(f"[MEMORY] ChromaDB error: {e}")
            self.collection = None

    def _load_profile(self) -> dict:
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "name"        : USER_NAME,
            "interests"   : [],
            "work_style"  : "professional",
            "language"    : "Indonesian",
            "topics"      : [],
            "preferences" : {},
            "goals"       : [],
            "created_at"  : datetime.now().isoformat()
        }

    def _save_profile(self):
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                self.profile, f,
                indent=2, ensure_ascii=False
            )

    def _load_episodes(self) -> list:
        if os.path.exists(EPISODES_FILE):
            with open(EPISODES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_episodes(self):
        with open(EPISODES_FILE, "w", encoding="utf-8") as f:
            json.dump(
                self.episodes[-100:], f,
                indent=2, ensure_ascii=False
            )

    def _count_memories(self) -> int:
        if self.collection:
            return self.collection.count()
        return 0

    def _generate_id(self, text: str) -> str:
        return hashlib.md5(
            f"{text}{time.time()}".encode()
        ).hexdigest()

    def add_short_term(self, role: str, content: str):
        self.short_term.append({
            "role"      : role,
            "content"   : content,
            "timestamp" : datetime.now().isoformat()
        })
        if len(self.short_term) > self.max_short:
            old = self.short_term.pop(0)
            if old["role"] == "user":
                self.add_long_term(
                    old["content"],
                    category = "conversation"
                )

    def get_short_term(self) -> list:
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self.short_term
        ]

    def clear_short_term(self):
        self.short_term = []

    def add_long_term(self, text: str,
                      category: str = "general",
                      metadata: dict = None):
        if not self.collection or not text.strip():
            return
        try:
            doc_id = self._generate_id(text)
            meta   = {
                "category"  : category,
                "user"      : USER_NAME,
                "timestamp" : datetime.now().isoformat(),
                "date"      : datetime.now().strftime("%Y-%m-%d")
            }
            if metadata:
                meta.update(metadata)
            self.collection.add(
                documents = [text],
                metadatas = [meta],
                ids       = [doc_id]
            )
        except Exception:
            pass

    def search_memory(self, query: str,
                      n_results: int = 5,
                      category: str = None) -> list:
        if not self.collection:
            return []
        try:
            count = self._count_memories()
            if count == 0:
                return []
            results = self.collection.query(
                query_texts = [query],
                n_results   = min(n_results, count)
            )
            memories = []
            if results["documents"]:
                for doc, meta in zip(
                    results["documents"][0],
                    results["metadatas"][0]
                ):
                    memories.append({
                        "content"  : doc,
                        "category" : meta.get("category"),
                        "date"     : meta.get("date"),
                        "timestamp": meta.get("timestamp")
                    })
            return memories
        except Exception:
            return []

    def add_episode(self, title: str,
                    summary: str,
                    importance: int = 1):
        episode = {
            "title"      : title,
            "summary"    : summary,
            "importance" : importance,
            "timestamp"  : datetime.now().isoformat(),
            "date"       : datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        self.episodes.append(episode)
        self._save_episodes()
        self.add_long_term(
            f"{title}: {summary}",
            category = "episode",
            metadata = {"importance": str(importance)}
        )

    def get_recent_episodes(self, n: int = 5) -> list:
        return sorted(
            self.episodes,
            key     = lambda x: x["timestamp"],
            reverse = True
        )[:n]

    def update_profile(self, key: str, value):
        self.profile[key] = value
        self.profile["updated_at"] = datetime.now().isoformat()
        self._save_profile()

    def add_interest(self, interest: str):
        if interest not in self.profile["interests"]:
            self.profile["interests"].append(interest)
            self._save_profile()

    def add_goal(self, goal: str):
        if goal not in self.profile["goals"]:
            self.profile["goals"].append(goal)
            self._save_profile()

    def get_profile_summary(self) -> str:
        p     = self.profile
        lines = [f"Nama: {p.get('name', USER_NAME)}"]
        if p.get("interests"):
            lines.append(
                f"Minat: {', '.join(p['interests'][:5])}"
            )
        if p.get("goals"):
            lines.append(
                f"Tujuan: {', '.join(p['goals'][:3])}"
            )
        if p.get("topics"):
            lines.append(
                f"Topik: {', '.join(p['topics'][:5])}"
            )
        return "\n".join(lines)

    def build_context(self, current_message: str) -> dict:
        relevant = self.search_memory(
            current_message, n_results=3
        )
        episodes = self.get_recent_episodes(3)
        parts    = []

        if relevant:
            parts.append("MEMORI RELEVAN:")
            for m in relevant:
                parts.append(
                    f"  [{m['date']}] {m['content'][:200]}"
                )

        if episodes:
            parts.append("\nKEJADIAN TERBARU:")
            for e in episodes:
                parts.append(
                    f"  [{e['date']}] {e['title']}: {e['summary'][:100]}"
                )

        profile = self.get_profile_summary()
        if profile:
            parts.append(f"\nPROFIL:\n{profile}")

        return {
            "context_string"    : "\n".join(parts),
            "relevant_memories" : relevant,
            "episodes"          : episodes,
            "profile"           : self.profile,
            "history"           : self.get_short_term()
        }

    def auto_learn(self, user_message: str,
                   assistant_response: str):
        self.add_long_term(
            f"User: {user_message}\nPETER: {assistant_response[:300]}",
            category = "conversation"
        )
        topics_keywords = {
            "youtube"   : ["youtube", "channel", "video", "subscriber"],
            "instagram" : ["instagram", "reels", "story", "followers"],
            "tiktok"    : ["tiktok", "fyp", "viral", "trending"],
            "konten"    : ["konten", "content", "script"],
            "bisnis"    : ["bisnis", "monetisasi", "income", "revenue"],
            "coding"    : ["python", "kode", "code", "programming"],
            "ai"        : ["ai", "artificial intelligence", "llm"],
            "marketing" : ["marketing", "ads", "iklan", "promosi"]
        }
        msg_lower = user_message.lower()
        for topic, keywords in topics_keywords.items():
            if any(kw in msg_lower for kw in keywords):
                if "topics" not in self.profile:
                    self.profile["topics"] = []
                if topic not in self.profile["topics"]:
                    self.profile["topics"].append(topic)
                    self._save_profile()

    def get_stats(self) -> dict:
        return {
            "short_term_count"  : len(self.short_term),
            "long_term_count"   : self._count_memories(),
            "episodes_count"    : len(self.episodes),
            "profile_interests" : len(self.profile.get("interests", [])),
            "profile_goals"     : len(self.profile.get("goals", [])),
            "profile_topics"    : len(self.profile.get("topics", []))
        }