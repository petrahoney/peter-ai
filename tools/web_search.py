"""
tools/web_search.py
Web search dengan Tavily (premium) + DuckDuckGo (fallback)
"""

from crewai.tools import tool
import os
import sys
sys.path.append("C:\\peter-ai")


@tool("web_search")
def web_search(query: str) -> str:
    """
    Cari informasi akurat dari internet.
    Gunakan untuk riset topik, berita terkini, data faktual.
    """
    tavily_key = os.getenv("TAVILY_API_KEY", "")

    # Coba Tavily dulu (lebih akurat)
    if tavily_key and tavily_key != "tvly-xxxxxxxxxx":
        try:
            from tavily import TavilyClient
            client  = TavilyClient(api_key=tavily_key)
            results = client.search(
                query      = query,
                max_results = 5,
                search_depth = "advanced"
            )
            output = f"Hasil pencarian '{query}':\n\n"
            for i, r in enumerate(results.get("results", [])[:5], 1):
                output += f"{i}. {r.get('title', '')}\n"
                output += f"   {r.get('content', '')[:300]}\n"
                output += f"   URL: {r.get('url', '')}\n\n"
            return output
        except Exception as e:
            print(f"[SEARCH] Tavily error: {e} — fallback DuckDuckGo")

    # Fallback ke DuckDuckGo
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,
                max_results = 5,
                region      = "id-id"
            ))
        if not results:
            return f"Tidak ada hasil untuk: {query}"
        output = f"Hasil pencarian '{query}':\n\n"
        for i, r in enumerate(results[:5], 1):
            output += f"{i}. {r['title']}\n"
            output += f"   {r['body'][:300]}\n\n"
        return output
    except Exception as e:
        return f"Search error: {e}"


@tool("get_trending_topics")
def get_trending_topics(niche: str = "teknologi AI Indonesia") -> str:
    """
    Dapatkan topik viral dan trending untuk konten.
    Gunakan untuk research ide konten YouTube, Instagram, TikTok.
    """
    tavily_key = os.getenv("TAVILY_API_KEY", "")

    queries = [
        f"{niche} viral trending 2026",
        f"{niche} terbaru hari ini",
        f"konten YouTube {niche} paling banyak ditonton"
    ]

    all_results = []

    for query in queries:
        if tavily_key and tavily_key != "tvly-xxxxxxxxxx":
            try:
                from tavily import TavilyClient
                client  = TavilyClient(api_key=tavily_key)
                results = client.search(
                    query        = query,
                    max_results  = 3,
                    search_depth = "basic"
                )
                for r in results.get("results", []):
                    all_results.append(r.get("title", ""))
            except Exception:
                pass
        else:
            try:
                from duckduckgo_search import DDGS
                with DDGS() as ddgs:
                    results = list(ddgs.text(
                        query, max_results=3, region="id-id"
                    ))
                for r in results:
                    all_results.append(r.get("title", ""))
            except Exception:
                pass

    if not all_results:
        return f"Tidak ada trending topic untuk: {niche}"

    output = f"Trending topics untuk '{niche}':\n\n"
    for i, title in enumerate(all_results[:10], 1):
        output += f"{i}. {title}\n"
    return output


@tool("search_images")
def search_images(query: str) -> str:
    """
    Cari URL gambar yang relevan untuk konten video.
    Gunakan query dalam Bahasa Inggris untuk hasil terbaik.
    """
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.images(
                query,
                max_results = 5,
                size        = "Large"
            ))
        if not results:
            return f"Tidak ada gambar untuk: {query}"

        output = f"Gambar untuk '{query}':\n\n"
        for i, r in enumerate(results[:5], 1):
            output += f"{i}. {r.get('title', '')}\n"
            output += f"   URL: {r.get('image', '')}\n\n"
        return output
    except Exception as e:
        return f"Image search error: {e}"