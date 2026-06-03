import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

import os
import sys
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

DID_KEY    = os.getenv("DID_API_KEY", "")
RUNWAY_KEY = os.getenv("RUNWAY_API_KEY", "")

print("=" * 50)
print("  Test Pro Video Engine")
print("=" * 50)
print(f"D-ID Key   : {'✅ Ada' if DID_KEY else '❌ Tidak ada'}")
print(f"Runway Key : {'✅ Ada' if RUNWAY_KEY else '❌ Tidak ada'}")

# ── TEST 1: D-ID CONNECTION ───────────────────────────────
print("\n[TEST 1] Test D-ID API...")
try:
    import requests
    import base64

    # D-ID pakai Basic Auth — encode API key
    encoded = base64.b64encode(
        f"{DID_KEY}:".encode()
    ).decode()

    response = requests.get(
        "https://api.d-id.com/credits",
        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type" : "application/json"
        },
        timeout = 10
    )

    if response.status_code == 200:
        data    = response.json()
        credits = data.get("remaining", "?")
        total   = data.get("total", "?")
        print(f"✅ D-ID OK! Credits: {credits}/{total}")
    else:
        print(f"❌ D-ID Error: {response.status_code}")
        print(f"   Response: {response.text[:200]}")

except Exception as e:
    print(f"❌ D-ID Exception: {e}")

# ── TEST 2: RUNWAY CONNECTION ─────────────────────────────
print("\n[TEST 2] Test Runway ML API...")
try:
    import requests

    response = requests.get(
        "https://api.dev.runwayml.com/v1/tasks",
        headers = {
            "Authorization"   : f"Bearer {RUNWAY_KEY}",
            "Content-Type"    : "application/json",
            "X-Runway-Version": "2024-11-06"
        },
        timeout = 10
    )

    if response.status_code in [200, 201]:
        print(f"✅ Runway OK!")
    elif response.status_code == 401:
        print(f"❌ Runway: API key salah!")
        print(f"   {response.text[:200]}")
    else:
        print(f"⚠️ Runway Status: {response.status_code}")
        print(f"   {response.text[:200]}")

except Exception as e:
    print(f"❌ Runway Exception: {e}")

# ── TEST 3: TEST D-ID GENERATE VIDEO ─────────────────────
print("\n[TEST 3] Test Generate Video D-ID...")
confirm = input("Generate test video D-ID? (y/n): ").strip().lower()

if confirm == 'y':
    try:
        import base64

        encoded = base64.b64encode(
            f"{DID_KEY}:".encode()
        ).decode()

        # Pakai text-to-speech langsung (tanpa upload audio)
        payload = {
            "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Noelle_f/thumbnail.jpeg",
            "script": {
                "type"    : "text",
                "input"   : "Halo! Saya PETER, asisten AI kamu. Video ini dibuat secara otomatis.",
                "provider": {
                    "type"  : "microsoft",
                    "voice_id": "id-ID-ArdiNeural"
                }
            },
            "config": {
                "fluent"       : True,
                "stitch"       : True,
                "result_format": "mp4"
            }
        }

        response = requests.post(
            "https://api.d-id.com/talks",
            json    = payload,
            headers = {
                "Authorization": f"Basic {encoded}",
                "Content-Type" : "application/json"
            }
        )

        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")

        if response.status_code in [200, 201]:
            talk_id = data.get("id")
            print(f"✅ Talk created! ID: {talk_id}")
            print(f"[INFO] Poll status di: https://api.d-id.com/talks/{talk_id}")

            # Poll sampai selesai
            import time
            print("\nMenunggu video selesai...")
            for i in range(30):
                time.sleep(5)
                poll = requests.get(
                    f"https://api.d-id.com/talks/{talk_id}",
                    headers = {
                        "Authorization": f"Basic {encoded}"
                    }
                )
                status = poll.json().get("status")
                print(f"  Status: {status} ({(i+1)*5}s)")

                if status == "done":
                    url = poll.json().get("result_url")
                    print(f"\n✅ Video siap: {url}")

                    # Download
                    output = "C:\\peter-ai\\data\\outputs\\test_did_video.mp4"
                    r = requests.get(url, stream=True)
                    with open(output, "wb") as f:
                        for chunk in r.iter_content(8192):
                            if chunk:
                                f.write(chunk)

                    print(f"✅ Downloaded: {output}")
                    os.startfile(output)
                    break

                elif status == "error":
                    print(f"❌ Error: {poll.json()}")
                    break

        else:
            print(f"❌ Gagal: {data}")

    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        traceback.print_exc()

print("\nTest selesai!")