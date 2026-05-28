from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import pickle
import os

SCOPES     = ["https://www.googleapis.com/auth/youtube.upload",
               "https://www.googleapis.com/auth/youtube.readonly"]
TOKEN_FILE = "C:\\peter-ai\\data\\youtube_token.pkl"

print("=" * 50)
print("  PETER — YouTube Authentication")
print("=" * 50)

if os.path.exists(TOKEN_FILE):
    print("Token sudah ada! Cek apakah masih valid...")
    with open(TOKEN_FILE, "rb") as f:
        creds = pickle.load(f)
    if creds.valid:
        print("Token masih valid!")
    else:
        print("Token expired — perlu login ulang")
        os.remove(TOKEN_FILE)

if not os.path.exists(TOKEN_FILE):
    print("\nMembuka browser untuk login YouTube...")
    print("Login dengan akun YouTube channel kamu\n")

    flow = InstalledAppFlow.from_client_secrets_file(
        "C:\\peter-ai\\client_secrets.json",
        SCOPES
    )
    creds = flow.run_local_server(port=0)

    with open(TOKEN_FILE, "wb") as f:
        pickle.dump(creds, f)
    print("\nYouTube auth berhasil!")
    print(f"Token disimpan: {TOKEN_FILE}")

# Test koneksi
print("\nTest koneksi YouTube...")
from googleapiclient.discovery import build
youtube  = build("youtube", "v3", credentials=creds)
response = youtube.channels().list(
    part = "snippet,statistics",
    mine = True
).execute()

if response["items"]:
    channel = response["items"][0]
    name    = channel["snippet"]["title"]
    stats   = channel["statistics"]
    print(f"\nChannel ditemukan!")
    print(f"  Nama       : {name}")
    print(f"  Subscriber : {stats.get('subscriberCount', 0)}")
    print(f"  Total Views: {stats.get('viewCount', 0)}")
    print(f"  Total Video: {stats.get('videoCount', 0)}")
    print("\nYouTube siap untuk PETER!")
else:
    print("Channel tidak ditemukan")