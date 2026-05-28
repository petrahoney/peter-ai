"""
publishers/youtube_pub.py
Auto upload video ke YouTube
"""

import os
import sys
sys.path.append("C:\\peter-ai")

from config import (
    YOUTUBE_CLIENT_ID,
    YOUTUBE_CLIENT_SECRET,
    OUTPUT_DIR
)


def upload_youtube(video_path: str,
                   title: str,
                   description: str,
                   tags: list = None,
                   category_id: str = "28",
                   privacy: str = "public") -> dict:
    """Upload video ke YouTube"""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        import pickle

        SCOPES      = ["https://www.googleapis.com/auth/youtube.upload"]
        TOKEN_FILE  = "C:\\peter-ai\\data\\youtube_token.pkl"
        SECRET_FILE = "C:\\peter-ai\\client_secrets.json"

        creds = None
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "rb") as f:
                creds = pickle.load(f)

        if not creds or not creds.valid:
            flow  = InstalledAppFlow.from_client_secrets_file(
                SECRET_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "wb") as f:
                pickle.dump(creds, f)

        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title"      : title[:100],
                "description": description[:5000],
                "tags"       : tags or [],
                "categoryId" : category_id
            },
            "status": {
                "privacyStatus": privacy
            }
        }

        media  = MediaFileUpload(video_path, resumable=True)
        request = youtube.videos().insert(
            part  = "snippet,status",
            body  = body,
            media_body = media
        )

        print(f"[YOUTUBE] Uploading: {title}")
        response = request.execute()
        video_id = response.get("id")
        url      = f"https://youtube.com/watch?v={video_id}"

        # Set thumbnail jika ada
        thumb_path = "C:\\peter-ai\\data\\outputs\\thumbnail_blue.png"
        if os.path.exists(thumb_path):
            try:
                from googleapiclient.http import MediaFileUpload
                youtube.thumbnails().set(
                    videoId    = video_id,
                    media_body = MediaFileUpload(thumb_path)
                ).execute()
                print(f"[YOUTUBE] Thumbnail set!")
            except Exception as e:
                print(f"[YOUTUBE] Thumbnail error: {e}")

        print(f"[YOUTUBE] Upload berhasil!")
        print(f"[YOUTUBE] URL: {url}")

        return {
            "success"  : True,
            "video_id" : video_id,
            "url"      : url,
            "title"    : title
        }

    except ImportError:
        return {
            "success": False,
            "error"  : "Install: pip install google-auth google-auth-oauthlib google-api-python-client"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_channel_stats() -> dict:
    """Dapatkan statistik channel YouTube"""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        import pickle

        TOKEN_FILE = "C:\\peter-ai\\data\\youtube_token.pkl"
        if not os.path.exists(TOKEN_FILE):
            return {"error": "Belum login YouTube. Jalankan upload_youtube dulu."}

        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

        youtube = build("youtube", "v3", credentials=creds)

        response = youtube.channels().list(
            part = "statistics",
            mine = True
        ).execute()

        stats = response["items"][0]["statistics"]
        return {
            "subscribers": stats.get("subscriberCount", 0),
            "views"      : stats.get("viewCount", 0),
            "videos"     : stats.get("videoCount", 0)
        }

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("YouTube Publisher PETER siap!")
    print("Setup client_secrets.json dulu dari Google Console")