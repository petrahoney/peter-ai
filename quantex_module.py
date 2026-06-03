# ============================================================
#   QUANTEX MODULE untuk PETER AI
# ============================================================

import os
import re
import httpx
from dotenv import load_dotenv

load_dotenv()

QUANTEX_URL      = os.getenv("QUANTEX_URL", "https://quantex-backend.onrender.com")
QUANTEX_USERNAME = os.getenv("QUANTEX_USERNAME", "admin")
QUANTEX_PASSWORD = os.getenv("QUANTEX_PASSWORD", "")
USER_NAME        = os.getenv("USER_NAME", "Sir")

_token = None


def quantex_login() -> str:
    global _token
    try:
        res = httpx.post(
            f"{QUANTEX_URL}/api/auth/login",
            json={"username": QUANTEX_USERNAME, "password": QUANTEX_PASSWORD},
            timeout=30
        )
        if res.status_code == 200:
            data   = res.json()
            _token = data.get("access_token") or data.get("token", "")
            print("[QUANTEX] Login berhasil!")
            return _token
        print(f"[QUANTEX] Login gagal: {res.status_code}")
        return ""
    except Exception as e:
        print(f"[QUANTEX] Login error: {e}")
        return ""


def get_token() -> str:
    global _token
    if not _token:
        _token = quantex_login()
    return _token


def get_headers() -> dict:
    return {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json"
    }


def get_scan_results(market: str = "idx") -> list:
    try:
        res = httpx.get(
            f"{QUANTEX_URL}/api/watchlist/{market}",
            headers=get_headers(),
            timeout=30
        )
        if res.status_code != 200:
            return []
        tickers = res.json().get("tickers", [])
        if not tickers:
            return []
        res2 = httpx.post(
            f"{QUANTEX_URL}/api/scan",
            headers=get_headers(),
            json={"tickers": tickers, "isIDX": market == "idx"},
            timeout=60
        )
        if res2.status_code == 200:
            return res2.json().get("results", [])
        return []
    except Exception as e:
        print(f"[QUANTEX] Scan error: {e}")
        return []


def get_portfolio() -> dict:
    try:
        res = httpx.get(
            f"{QUANTEX_URL}/api/portfolio/summary",
            headers=get_headers(),
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        return {}
    except Exception as e:
        print(f"[QUANTEX] Portfolio error: {e}")
        return {}


def analyze_ticker(ticker: str, is_idx: bool = True) -> dict:
    try:
        res = httpx.post(
            f"{QUANTEX_URL}/api/analyze",
            headers=get_headers(),
            json={"ticker": ticker.upper(), "isIDX": is_idx},
            timeout=60
        )
        if res.status_code == 200:
            return res.json()
        return {}
    except Exception as e:
        print(f"[QUANTEX] Analyze error: {e}")
        return {}


def get_journal_stats(month: str = None) -> dict:
    try:
        import datetime
        if not month:
            month = datetime.datetime.now().strftime("%Y-%m")
        res = httpx.get(
            f"{QUANTEX_URL}/api/journal/stats?month={month}",
            headers=get_headers(),
            timeout=30
        )
        if res.status_code == 200:
            return res.json()
        return {}
    except Exception as e:
        print(f"[QUANTEX] Journal error: {e}")
        return {}


def chat_quantex(message: str, context_data: dict = None) -> str:
    import anthropic
    import json
    ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    client        = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    context_str   = ""
    if context_data:
        context_str = f"\nDATA QUANTEX:\n{json.dumps(context_data, ensure_ascii=False, indent=2)}\n"
    system = f"""Kamu adalah PETER — asisten trading pribadi milik {USER_NAME}.
Kamu memiliki akses ke sistem Quantex EOD — platform swing trading saham IDX dan US.
Gunakan Bahasa Indonesia. Berikan rekomendasi tegas dan actionable berdasarkan data teknikal.
Selalu ingatkan bahwa ini bukan saran finansial resmi.
{context_str}"""
    response = client.messages.create(
        model      = "claude-sonnet-4-6",
        max_tokens = 2048,
        system     = system,
        messages   = [{"role": "user", "content": message}]
    )
    return response.content[0].text


def run_quantex_menu():
    print("\n" + "=" * 52)
    print("  QUANTEX TRADING — PETER AI")
    print("=" * 52)
    print("  [1] Scan Sinyal Hari Ini     (IDX)")
    print("  [2] Scan Sinyal Hari Ini     (US)")
    print("  [3] Analisa Saham Spesifik")
    print("  [4] Cek Portfolio")
    print("  [5] Statistik Journal")
    print("  [6] Chat Trading dengan Peter")
    print("  [7] Kembali ke Menu Utama")
    print("=" * 52)

    while True:
        pilihan = input(f"\n[{USER_NAME}] Pilih (1-7): ").strip()

        if pilihan == "1":
            print("\n[QUANTEX] Scanning IDX watchlist...")
            results      = get_scan_results("idx")
            if not results:
                print("[QUANTEX] Tidak ada data.")
                continue
            buy_signals  = [r for r in results if r.get("signal") == "BUY"]
            sell_signals = [r for r in results if r.get("signal") == "SELL"]
            wait_signals = [r for r in results if r.get("signal") == "WAIT"]
            print(f"\n[QUANTEX] Hasil Scan IDX — {len(results)} ticker")
            print(f"  🟢 BUY  : {len(buy_signals)}")
            print(f"  🔴 SELL : {len(sell_signals)}")
            print(f"  🟡 WAIT : {len(wait_signals)}")
            if buy_signals:
                print("\n  🟢 SINYAL BUY:")
                for s in buy_signals:
                    order = s.get("order", {})
                    print(f"  {s['ticker']:12} Score:{s.get('score',0):3} | Entry:{order.get('entry','—')} | TP1:{order.get('tp1','—')} | SL:{order.get('sl','—')}")
            if sell_signals:
                print("\n  🔴 SINYAL SELL:")
                for s in sell_signals:
                    order = s.get("order", {})
                    print(f"  {s['ticker']:12} Score:{s.get('score',0):3} | Entry:{order.get('entry','—')} | TP1:{order.get('tp1','—')} | SL:{order.get('sl','—')}")
            if buy_signals or sell_signals:
                print("\n[PETER] Menganalisa sinyal...")
                context = {
                    "market"       : "IDX",
                    "buy_signals"  : [{"ticker": s["ticker"], "score": s.get("score", 0)} for s in buy_signals],
                    "sell_signals" : [{"ticker": s["ticker"], "score": s.get("score", 0)} for s in sell_signals],
                    "total_scanned": len(results)
                }
                analisa = chat_quantex("Berdasarkan data scan hari ini, saham mana yang paling menarik dan mengapa?", context)
                print(f"\n[PETER] {analisa}")
            else:
                print("\n[PETER] Tidak ada sinyal BUY/SELL hari ini. Market sedang konsolidasi.")

        elif pilihan == "2":
            print("\n[QUANTEX] Scanning US watchlist...")
            results     = get_scan_results("us")
            if not results:
                print("[QUANTEX] Tidak ada data US.")
                continue
            buy_signals = [r for r in results if r.get("signal") == "BUY"]
            print(f"\n[QUANTEX] Hasil Scan US — {len(results)} ticker")
            print(f"  🟢 BUY  : {len(buy_signals)}")
            if buy_signals:
                print("\n  🟢 SINYAL BUY:")
                for s in buy_signals:
                    order = s.get("order", {})
                    print(f"  {s['ticker']:12} Score:{s.get('score',0):3} | Entry:{order.get('entry','—')}")

        elif pilihan == "3":
            ticker = input("\n[QUANTEX] Masukkan ticker (contoh: BBCA.JK): ").strip().upper()
            if not ticker:
                continue
            is_idx = ticker.endswith(".JK")
            print(f"\n[QUANTEX] Menganalisa {ticker}...")
            data = analyze_ticker(ticker, is_idx)
            if not data:
                print(f"[QUANTEX] Data tidak ditemukan untuk {ticker}")
                continue
            signal     = data.get("signal", "WAIT")
            score      = data.get("score", 0)
            order      = data.get("order", {})
            indicators = data.get("indicators", {})
            emoji      = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
            print(f"\n{emoji} {ticker} — {signal} (Score: {score})")
            print(f"  RSI   : {indicators.get('rsi14', '—')}")
            print(f"  SMA20 : {indicators.get('sma20', '—')}")
            print(f"  Close : {indicators.get('close', '—')}")
            if order:
                print(f"\n  ORDER:")
                print(f"  Entry : {order.get('entry', '—')}")
                print(f"  SL    : {order.get('sl', '—')}")
                print(f"  TP1   : {order.get('tp1', '—')}")
                print(f"  TP2   : {order.get('tp2', '—')}")
                print(f"  R:R   : 1:{order.get('rr_tp1', '—')}")
            print("\n[PETER] Menganalisa...")
            context = {"ticker": ticker, "signal": signal, "score": score, "indicators": indicators, "order": order}
            analisa = chat_quantex(f"Analisa sinyal {ticker} ini. Apakah layak untuk entry?", context)
            print(f"\n[PETER] {analisa}")

        elif pilihan == "4":
            print("\n[QUANTEX] Mengambil data portfolio...")
            portfolio = get_portfolio()
            if not portfolio:
                print("[QUANTEX] Portfolio kosong atau error.")
                continue
            print(f"\n[QUANTEX] PORTFOLIO:")
            print(f"  Total Value : {portfolio.get('totalValue', 0):,.0f}")
            print(f"  Unrealized  : {portfolio.get('unrealizedPnl', 0):,.0f}")
            print(f"  Positions   : {portfolio.get('positionCount', 0)}")
            analisa = chat_quantex("Analisa kondisi portfolio saya saat ini.", portfolio)
            print(f"\n[PETER] {analisa}")

        elif pilihan == "5":
            print("\n[QUANTEX] Mengambil statistik journal...")
            stats = get_journal_stats()
            if not stats:
                print("[QUANTEX] Belum ada data journal.")
                continue
            print(f"\n[QUANTEX] JOURNAL BULAN INI:")
            print(f"  Win Rate  : {stats.get('winRate', 0):.1f}%")
            print(f"  Trades    : {stats.get('totalTrades', 0)}")
            analisa = chat_quantex("Evaluasi performa trading saya bulan ini.", stats)
            print(f"\n[PETER] {analisa}")

        elif pilihan == "6":
            print("\n[PETER] Chat Trading aktif!")
            print("[PETER] Tanya apapun tentang trading. Ketik 'exit' untuk kembali.")
            print("[PETER] Tips: sebut nama saham (contoh: BBCA.JK) untuk analisa otomatis\n")
            while True:
                tanya = input(f"[{USER_NAME}] -> ").strip()
                if tanya.lower() in ["exit", "keluar"]:
                    break
                if not tanya:
                    continue
                ticker_match = re.findall(r'\b([A-Z]{2,6}\.JK)\b', tanya.upper())
                context = {}
                for t in ticker_match:
                    print(f"\n[QUANTEX] Mengambil data {t}...")
                    data = analyze_ticker(t, True)
                    if data and data.get("signal"):
                        context[t] = {
                            "signal"    : data.get("signal"),
                            "score"     : data.get("score"),
                            "indicators": data.get("indicators", {}),
                            "order"     : data.get("order", {}),
                        }
                        print(f"[QUANTEX] {t}: {data.get('signal')} (Score: {data.get('score')})")
                        break
                print("\n[PETER] Berpikir...\n")
                jawab = chat_quantex(tanya, context if context else None)
                print(f"[PETER] {jawab}\n")

        elif pilihan == "7":
            print("[QUANTEX] Kembali ke menu utama.")
            break

        else:
            print("[PETER] Pilihan tidak valid. Ketik 1-7.")