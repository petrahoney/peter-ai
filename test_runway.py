import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

import os
import sys
import time
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

RUNWAY_KEY = os.getenv("RUNWAY_API_KEY", "")
OUTPUT     = "C:\\peter-ai\\data\\outputs"

print("=" * 50)
print("  Test Runway ML SDK — Gen-4.5")
print("=" * 50)
print(f"Runway Key: {'✅ Ada' if RUNWAY_KEY else '❌ Tidak ada'}")

try:
    import runwayml

    client = runwayml.RunwayML(api_key=RUNWAY_KEY)
    print("✅ Runway SDK OK!")

    # Test generate video dari image
    print("\n[TEST] Generate video sinematik...")
    print("Prompt: Aerial view modern city Indonesia night neon lights")

    task = client.image_to_video.create(
        model        = "gen4_turbo",
        prompt_image = "https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_(cropped).jpg",
        prompt_text  = "Cinematic aerial view of modern city at night, neon lights reflecting on wet streets, slow pan, dramatic lighting, 4K quality",
        duration     = 5,
        ratio        = "1280:720"
    )

    task_id = task.id
    print(f"Task ID: {task_id}")
    print("Menunggu render...")

    # Poll sampai selesai
    for i in range(60):
        time.sleep(5)
        task = client.tasks.retrieve(task_id)
        print(f"  Status: {task.status} ({(i+1)*5}s)")

        if task.status == "SUCCEEDED":
            url = task.output[0]
            print(f"\n✅ Video siap: {url[:60]}...")

            # Download
            import requests
            output_path = os.path.join(OUTPUT, "test_runway.mp4")
            r = requests.get(url, stream=True)
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    if chunk:
                        f.write(chunk)

            size = os.path.getsize(output_path)
            print(f"✅ Downloaded: {output_path} ({size:,} bytes)")
            os.startfile(output_path)
            break

        elif task.status == "FAILED":
            print(f"❌ Failed: {task.failure}")
            break

except ImportError:
    print("❌ runwayml tidak terinstall!")
    print("   Run: pip install runwayml")
except Exception as e:
    import traceback
    print(f"❌ Error: {e}")
    traceback.print_exc()

print("\nTest selesai!")