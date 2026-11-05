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

PROMPT = """
You are a professional YouTube video production planner.

CHANNEL: Realistic AI Jungle Construction
LANGUAGE: English
TOPIC: Building a Luxury Underground Swimming Pool in a Dense Jungle.

VIDEO DURATION: EXACTLY 60 SECONDS.

Create a complete production plan for ONE 60-second video.

STRICT REQUIREMENTS:

1. Catchy YouTube title.
2. Opening hook: maximum 3 seconds.
3. Narration: approximately 100-120 words.
4. EXACTLY 8 chronological scenes.
5. Each scene: approximately 7-8 seconds.
6. Detailed AI video generation prompt for every scene.
7. Camera angle and camera movement for every scene.
8. Background music and sound effects.
9. YouTube description and hashtags.

CONSTRUCTION STORY:
- Scene 1: Show the jungle construction location.
- Scene 2: Clear the jungle area.
- Scene 3: Mark the pool and excavate the ground.
- Scene 4: Prepare the foundation and reinforcement.
- Scene 5: Build the underground pool structure.
- Scene 6: Apply waterproofing and install tiles.
- Scene 7: Fill the pool with clean water and finish the deck.
- Scene 8: Reveal the completed luxury underground pool.

CREATE TWO FORMATS:
A. YouTube Shorts: Vertical 9:16.
B. Regular YouTube video: Horizontal 16:9.

Both formats must use the SAME 60-second story and 8 scenes.
Adapt the camera framing for each format.

CONTINUITY RULES:
- Keep the same jungle location throughout.
- Keep workers, clothing and pool design consistent.
- Show realistic construction progress.
- Every scene must continue from the previous scene.
- Use photorealistic cinematic visuals.
- No unrelated wildlife or documentary footage.

FINAL VALIDATION:
- Total duration must be exactly 60 seconds.
- Exactly 8 scenes.
- No 5-minute narration.
- No 30-scene production plan.
- Do not add extra scenes.
- If requirements conflict, ALWAYS follow the 60-second limit.

Return the complete production plan in clearly labeled sections.
"""
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
