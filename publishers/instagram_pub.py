"""
publishers/instagram_pub.py
Auto post ke Instagram via Graph API
"""

import os
import sys
import requests
sys.path.append("C:\\peter-ai")

from config import INSTAGRAM_TOKEN, INSTAGRAM_USER_ID


def post_reel(video_path: str,
              caption: str,
              cover_url: str = None) -> dict:
    """Upload Reels ke Instagram"""
    try:
        if not INSTAGRAM_TOKEN:
            return {"error": "INSTAGRAM_ACCESS_TOKEN belum diset di .env"}
        if not INSTAGRAM_USER_ID:
            return {"error": "INSTAGRAM_USER_ID belum diset di .env"}

        # Step 1: Upload container
        container_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_USER_ID}/media"
        container_data = {
            "media_type"  : "REELS",
            "video_url"   : video_path,
            "caption"     : caption[:2200],
            "access_token": INSTAGRAM_TOKEN
        }
        if cover_url:
            container_data["cover_url"] = cover_url

        response = requests.post(container_url, data=container_data)
        result   = response.json()

        if "id" not in result:
            return {"error": result}

        container_id = result["id"]
        print(f"[INSTAGRAM] Container ID: {container_id}")

        # Step 2: Publish
        import time
        time.sleep(30)  # Tunggu video diproses

        publish_url  = f"https://graph.facebook.com/v18.0/{INSTAGRAM_USER_ID}/media_publish"
        publish_data = {
            "creation_id" : container_id,
            "access_token": INSTAGRAM_TOKEN
        }
        pub_response = requests.post(publish_url, data=publish_data)
        pub_result   = pub_response.json()

        if "id" in pub_result:
            media_id = pub_result["id"]
            print(f"[INSTAGRAM] Post berhasil! ID: {media_id}")
            return {
                "success" : True,
                "media_id": media_id,
                "caption" : caption[:50]
            }
        return {"error": pub_result}

    except Exception as e:
        return {"error": str(e)}


def post_photo(image_path: str, caption: str) -> dict:
    """Post foto ke Instagram feed"""
    try:
        if not INSTAGRAM_TOKEN:
            return {"error": "Token belum diset"}

        # Upload gambar ke hosting dulu (butuh URL publik)
        print("[INSTAGRAM] Foto membutuhkan URL publik")
        print("[INSTAGRAM] Upload ke Imgur atau hosting dulu")
        return {
            "info": "Untuk post foto, upload ke URL publik dulu (Imgur, Cloudinary, dll)"
        }

    except Exception as e:
        return {"error": str(e)}


def get_instagram_stats() -> dict:
    """Statistik akun Instagram"""
    try:
        if not INSTAGRAM_TOKEN:
            return {"error": "Token belum diset"}

        url    = f"https://graph.facebook.com/v18.0/{INSTAGRAM_USER_ID}"
        params = {
            "fields"      : "followers_count,media_count,name",
            "access_token": INSTAGRAM_TOKEN
        }
        response = requests.get(url, params=params)
        return response.json()

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("Instagram Publisher PETER siap!")
    print("Setup INSTAGRAM_ACCESS_TOKEN di .env dulu")