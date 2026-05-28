"""
publishers/tiktok_pub.py
Auto upload ke TikTok via API
"""

import os
import sys
import requests
sys.path.append("C:\\peter-ai")

from config import TIKTOK_TOKEN


def upload_tiktok(video_path: str,
                  caption: str,
                  privacy: str = "PUBLIC_TO_EVERYONE") -> dict:
    """Upload video ke TikTok"""
    try:
        if not TIKTOK_TOKEN:
            return {
                "error": "TIKTOK_ACCESS_TOKEN belum diset di .env",
                "info" : "Daftar di developers.tiktok.com untuk mendapatkan token"
            }

        # TikTok Content Posting API
        url     = "https://open.tiktokapis.com/v2/post/publish/video/init/"
        headers = {
            "Authorization": f"Bearer {TIKTOK_TOKEN}",
            "Content-Type" : "application/json"
        }
        file_size = os.path.getsize(video_path)
        data      = {
            "post_info": {
                "title"          : caption[:150],
                "privacy_level"  : privacy,
                "disable_duet"   : False,
                "disable_comment": False,
                "disable_stitch" : False
            },
            "source_info": {
                "source"           : "FILE_UPLOAD",
                "video_size"       : file_size,
                "chunk_size"       : file_size,
                "total_chunk_count": 1
            }
        }

        response = requests.post(url, headers=headers, json=data)
        result   = response.json()

        if result.get("error", {}).get("code") == "ok":
            upload_url = result["data"]["upload_url"]
            publish_id = result["data"]["publish_id"]

            # Upload video file
            with open(video_path, "rb") as f:
                video_data = f.read()

            upload_headers = {
                "Content-Type"  : "video/mp4",
                "Content-Length": str(file_size),
                "Content-Range" : f"bytes 0-{file_size-1}/{file_size}"
            }
            upload_response = requests.put(
                upload_url,
                data    = video_data,
                headers = upload_headers
            )

            if upload_response.status_code == 201:
                print(f"[TIKTOK] Upload berhasil! ID: {publish_id}")
                return {
                    "success"   : True,
                    "publish_id": publish_id,
                    "caption"   : caption[:50]
                }

        return {"error": result}

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("TikTok Publisher PETER siap!")
    print("Setup TIKTOK_ACCESS_TOKEN di .env dulu")
    print("Daftar di: developers.tiktok.com")