import os
import sys
import json
import time
import urllib.request
import urllib.error

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
    names = []
    url = BASE + "/models?pageSize=100"
    while url:
        data = get(url)
        for m in data.get("models", []):
            if "generateContent" in m.get("supportedGenerationMethods", []):
                names.append(m["name"].replace("models/", ""))
        token = data.get("nextPageToken")
        if token:
            url = BASE + "/models?pageSize=100&pageToken=" + token
        else:
            url = None
    return names


def rank(name):
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
        BASE + "/models/" + model + ":generateContent",
        data=body,
        headers=HEADERS,
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    return data["candidates"][0]["content"]["parts"][0]["text"]


try:
    models = available_models()
except urllib.error.HTTPError as e:
    sys.exit("Model list nahi mili: HTTP " + str(e.code) + " " + e.read().decode()[:300])

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
            print("OK:", model, len(text), "characters")
            sys.exit(0)
        except urllib.error.HTTPError as e:
            msg = e.read().decode()[:300]
            print(model, "attempt", attempt + 1, "HTTP", e.code, msg)
            if e.code not in (429, 500, 503):
                break
            time.sleep(8)
        except Exception as e:
            print(model, "attempt", attempt + 1, e)
            time.sleep(5)

sys.exit("Sab models fail ho gaye, upar ke errors dekho")
