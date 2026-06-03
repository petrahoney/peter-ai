import warnings
warnings.filterwarnings("ignore", category=ResourceWarning)

import os, sys
sys.path.append("C:\\peter-ai")
from dotenv import load_dotenv
load_dotenv()

print("Test Script Writer...")

try:
    from content.script_writer import write_script
    result = write_script(
        topic           = "Cara menghasilkan uang dari AI di Indonesia 2026",
        duration        = "5 menit",
        style           = "informatif engaging",
        target_audience = "pemula Indonesia"
    )

    print(f"\nScript length : {len(result.get('script', ''))}")
    print(f"Raw length    : {len(result.get('raw', ''))}")
    print(f"Titles        : {result.get('title_options', [])}")
    print(f"Tags count    : {len(result.get('tags', []))}")

    script = result.get('script', '')
    raw    = result.get('raw', '')

    if not script and raw:
        print("\nScript kosong tapi raw ada!")
        print(f"Raw preview: {raw[:300]}")
    elif script:
        print(f"\nScript preview: {script[:300]}")
    else:
        print("\nKeduanya kosong!")

except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()