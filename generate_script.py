
import os
import json
import time
import urllib.request
import urllib.error

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY secret is missing!")

MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite"
]

PROMPT = """
Create an original English YouTube Shorts script.

Channel: Jungle Construction
Topic: Building a luxury underground swimming pool in a jungle.

Include:
1. Catchy YouTube title
2. 45-second narration
3. 8 detailed video scenes
4. Realistic visual prompts for every scene
5. YouTube description
6. Relevant hashtags

Make it cinematic, engaging and realistic.
Each scene should connect naturally to the next.
"""

def generate_script(model):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{model}:generateContent"
    )

    data = {
        "contents": [
            {"parts": [{"text": PROMPT}]}
        ]
    }

    for attempt in range(1, 4):
        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": API_KEY
            },
            method="POST"
        )

        try:
            print(f"{model}: attempt {attempt}/3")

            with urllib.request.urlopen(request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))

            return result["candidates"][0]["content"]["parts"][0]["text"]

        except urllib.error.HTTPError as error:
            details = error.read().decode("utf-8")
            print(f"API error {error.code}: {details}")

            if error.code not in (429, 500, 502, 503, 504):
                raise

            if attempt < 3:
                delay = 15 * (2 ** (attempt - 1))
                print(f"Waiting {delay} seconds before retry...")
                time.sleep(delay)

    return None


generated_text = None

for model in MODELS:
    print(f"\nTrying model: {model}")

    generated_text = generate_script(model)

    if generated_text:
        print(f"SUCCESS: Generated using {model}")
        break

if not generated_text:
    raise RuntimeError("Both Gemini models failed. Please try again later.")

with open("generated_script.txt", "w", encoding="utf-8") as file:
    file.write(generated_text)

print("YouTube script saved successfully!")





     
