import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

import os, sys, time, random
sys.path.append("C:\\peter-ai")
from dotenv import load_dotenv
load_dotenv()

import runwayml
RUNWAY_KEY = os.getenv("RUNWAY_API_KEY", "")
OUTPUT     = "C:\\peter-ai\\data\\outputs"
client     = runwayml.RunwayML(api_key=RUNWAY_KEY)

# Image Unsplash yang reliable
images = [
    "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1280&q=80",
    "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=1280&q=80",
    "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1280&q=80",
]

print("Test Runway Gen4 Turbo...")
print(f"Image: {images[0][:50]}...")

try:
    task = client.image_to_video.create(
        model        = "gen4_turbo",
        prompt_image = images[0],
        prompt_text  = "Cinematic aerial Jakarta city night neon lights slow pan dramatic",
        duration     = 5,
        ratio        = "1280:720"
    )
    print(f"✅ Task: {task.id}")

    for i in range(30):
        time.sleep(5)
        task = client.tasks.retrieve(task.id)
        print(f"  {task.status} ({(i+1)*5}s)")

        if task.status == "SUCCEEDED":
            url = task.output[0]
            print(f"✅ URL: {url[:60]}...")

            import requests
            out = os.path.join(OUTPUT, "debug_broll.mp4")
            r   = requests.get(url, stream=True)
            with open(out, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk: f.write(chunk)

            size = os.path.getsize(out)
            print(f"✅ Downloaded: {size:,} bytes")
            os.startfile(out)
            break

        elif task.status == "FAILED":
            print(f"❌ Failed: {task.failure}")
            break

except Exception as e:
    import traceback
    print(f"❌ Error: {e}")
    traceback.print_exc()