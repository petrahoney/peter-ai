import sys
sys.path.append("C:\\peter-ai")
from publishers.youtube_pub import upload_youtube, get_channel_stats

print("Test YouTube PETER")
print("=" * 40)

# Cek stats channel dulu
print("Mengambil stats channel...")
stats = get_channel_stats()
print(f"Subscriber : {stats.get('subscribers', 0)}")
print(f"Views      : {stats.get('views', 0)}")
print(f"Videos     : {stats.get('videos', 0)}")
print("\nYouTube connection OK!")