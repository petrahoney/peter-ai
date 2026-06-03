import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

import os
import sys
import requests
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

import runwayml
import time

RUNWAY_KEY = os.getenv("RUNWAY_API_KEY", "")
OUTPUT     = "C:\\peter-ai\\data\\outputs"
client     = runwayml.RunwayML(api_key=RUNWAY_KEY)

print("Generate video Runway Gen4 Turbo...")

task = client.image_to_video.create(
    model        = "gen4_turbo",
    prompt_image = "https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_(cropped).jpg",
    prompt_text  = "Cinematic aerial view modern Indonesia city at night, neon lights, slow pan, dramatic lighting, 4K",
    duration     = 5,
    ratio        = "1280:720"
)

print(f"Task ID: {task.id}")

for i in range(60):
    time.sleep(5)
    task = client.tasks.retrieve(task.id)
    print(f"  Status: {task.status} ({(i+1)*5}s)")

    if task.status == "SUCCEEDED":
        url = task.output[0]
        print(f"\n✅ URL: {url[:80]}...")

        # Download
        output_path = os.path.join(OUTPUT, "test_runway_final.mp4")
        r = requests.get(url, stream=True)
        with open(output_path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)

        size = os.path.getsize(output_path)
        print(f"✅ Downloaded: {output_path}")
        print(f"   Size: {size:,} bytes")
        os.startfile(output_path)
        break

    elif task.status == "FAILED":
        print(f"❌ Failed: {task.failure}")
        break

print("\nSelesai!")