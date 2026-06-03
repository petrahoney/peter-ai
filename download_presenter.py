import requests
import os

OUTPUT = "C:\\peter-ai\\data"
os.makedirs(OUTPUT, exist_ok=True)

# Foto pria profesional Indonesia dari Unsplash
photos = {
    "presenter_male.jpg": "https://images.unsplash.com/photo-1633332755192-727a05c4013d?w=400&h=500&fit=crop&crop=face",
    "presenter_female.jpg": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&h=500&fit=crop&crop=face",
}

headers = {"User-Agent": "Mozilla/5.0"}

for name, url in photos.items():
    path = os.path.join(OUTPUT, name)
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            size = os.path.getsize(path)
            print(f"✅ {name}: {size:,} bytes")
        else:
            print(f"❌ {name}: HTTP {r.status_code}")
    except Exception as e:
        print(f"❌ {name}: {e}")

print("\nUpdate .env dengan:")
print(f"PRESENTER_IMAGE=C:\\peter-ai\\data\\presenter_male.jpg")
print(f"PRESENTER_GENDER=male")