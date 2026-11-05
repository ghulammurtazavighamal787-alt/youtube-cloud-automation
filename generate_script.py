import os, sys, json, time
import urllib.request, urllib.error

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    sys.exit("GEMINI_API_KEY secret missing hai")

BASE = "https://generativelanguage.googleapis.com/v1beta"
HEADERS = {"Content-Type": "application/json", "x-goog-api-key": API_KEY}

PROMPT = """Write a 5-minute cinematic documentary YouTube script about a jungle.
Use a strong cold-open hook, short spoken sentences, a midpoint twist,
and an ending line that ties it to today. Add [visual cue] notes."""


def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def available_models():
    """Google se abhi ki list lo, sirf text-generation wale models."""
    names = []
    url = f"{BASE}/models?pageSize=100"
    while url:
        data = get(url)
        for m in data.get("models", []):
            if "generateContent" in m.get("supportedGenerationMethods", []):
                names.append(m["name"].replace("models/", ""))
        token = data.get("nextPageToken")
        url = f"{BASE}/models?pageSize=100&pageToken={token}" if token else None
    return names


def rank(name):
    """Chhote, sasta text models pehle. Image/audio/TTS wale skip."""
    bad = ("tts", "image", "vision", "embedding", "live", "audio", "thinking", "robotics")
    if any(b in name for b in bad):
        return None
    if "flash-lite" in name:
        return 1
    if "flash" in name:
        return 0
    if "pro" in name:
        return 2
    return 3


def generate(model):
    body = json.dumps({"contents": [{"parts": [{"text": PROMPT}]}]}).encode()
    req = urllib.request.Request(
        f"{BASE}/models/{model}:generateContent", data=body, headers=HEADERS
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    return data["candidates"][0]["content"]["parts"][0]["text"]


try:
    models = available_models()
except urllib.error.HTTPError as e:
    sys.exit(f"Model list nahi mili: HTTP {e.code} {e.read().decode()[:300]}")

print("Available models:", models)

ranked = sorted((m for m in models if rank(m) is not None), key=rank)
print("Try order:", ranked[:6])

if not ranked:
    sys.exit("Koi text model nahi mila. API key ya region check karo.")

for model in ranked[:4]:
    for attempt in range(2):
        try:
            text = generate(model)
            with open("generated_script.txt", "w", encoding="utf-8") as f:
                f.write(text)
            print(f"OK: {model}, {len(text)} characters")
            sys.exit(0)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            print(f"{model} attempt {attempt+1}: HTTP {e.code} {msg}")
            if e.code not in (429, 500, 503):
                break
            time.sleep(8)
        except Exception as e:
            print(f"{model} attempt {attempt+1}: {e}")
            time.sleep(5)

sys.exit("Sab models fail ho gaye, upar ke errors dekho")
            time.sleep(5)

sys.exit("Dono models fail ho gaye")
