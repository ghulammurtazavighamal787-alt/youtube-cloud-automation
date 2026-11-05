import os, sys, json, time
import urllib.request, urllib.error

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    sys.exit("GEMINI_API_KEY secret missing hai")

# Primary pehle, backup baad mein. Model names Google ki current list se check kar lena.
MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]

PROMPT = """Write a 5-minute cinematic documentary YouTube script about a jungle.
Use a strong cold-open hook, short spoken sentences, a midpoint twist,
and an ending line that ties it to today. Add [visual cue] notes."""

def call(model):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = json.dumps({"contents": [{"parts": [{"text": PROMPT}]}]}).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json", "x-goog-api-key": API_KEY},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    return data["candidates"][0]["content"]["parts"][0]["text"]

for model in MODELS:
    for attempt in range(3):
        try:
            text = call(model)
            with open("generated_script.txt", "w", encoding="utf-8") as f:
                f.write(text)
            print(f"OK: {model}, {len(text)} characters")
            sys.exit(0)
        except urllib.error.HTTPError as e:
            print(f"{model} attempt {attempt+1}: HTTP {e.code}")
            if e.code not in (429, 500, 503):
                break
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            print(f"{model} attempt {attempt+1}: {e}")
            time.sleep(5)

sys.exit("Dono models fail ho gaye")
