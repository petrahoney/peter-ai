import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

import os
import sys
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

RUNWAY_KEY = os.getenv("RUNWAY_API_KEY", "")

import runwayml
client = runwayml.RunwayML(api_key=RUNWAY_KEY)

# Cek organization dan credits
try:
    org = client.organizations.retrieve()
    print(f"Organization: {org}")
except Exception as e:
    print(f"Org error: {e}")

# Cek dengan model lebih murah — gen4_turbo 2 detik
try:
    import time
    print("\nTest dengan durasi 2 detik (lebih murah)...")
    task = client.image_to_video.create(
        model        = "gen4_turbo",
        prompt_image = "https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_(cropped).jpg",
        prompt_text  = "Cinematic slow pan city lights",
        duration     = 2,
        ratio        = "1280:720"
    )
    print(f"✅ Task created: {task.id}")

    for i in range(30):
        time.sleep(5)
        task = client.tasks.retrieve(task.id)
        print(f"  Status: {task.status}")
        if task.status == "SUCCEEDED":
            print(f"✅ URL: {task.output[0][:60]}...")
            break
        elif task.status == "FAILED":
            print(f"❌ Failed: {task.failure}")
            break

except Exception as e:
    print(f"Error: {e}")