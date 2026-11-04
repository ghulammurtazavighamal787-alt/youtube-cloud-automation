
import os
import json
import time
import urllib.request
import urllib.error

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY secret is missing!")

prompt = """
Create an original English YouTube Shorts script.

Channel: Jungle Construction
Topic: Building a luxury underground swimming pool in a jungle.

Include:
1. Catchy title
2. 45-second narration
3. 8 detailed video scenes
4. Visual prompts for each scene
5. YouTube description
6. Relevant hashtags

Make it realistic, engaging and cinematic.
"""

url = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-3.8-flash:generateContent"
)

data = {
    "contents": [{"parts": [{"text": prompt}]}]
}

request_data = json.dumps(data).encode("utf-8")

for attempt in range(1, 5):
    request = urllib.request.Request(
        url,
        data=request_data,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        },
        method="POST"
    )

    try:
        print(f"Gemini request attempt {attempt}/4")

        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))

        generated_text = (
            result["candidates"][0]["content"]["parts"][0]["text"]
        )

        with open("generated_script.txt", "w", encoding="utf-8") as file:
            file.write(generated_text)

        print("SUCCESS: Gemini script generated!")
        break

    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8")
        print(f"API error {error.code}: {details}")

        if error.code not in (429, 500, 502, 503, 504):
            raise

        if attempt == 4:
            raise RuntimeError("Gemini is still unavailable after 4 attempts.")

        wait_time = attempt * 15
        print(f"Retrying after {wait_time} seconds...")
        time.sleep(wait_time)

    except Exception as error:
        print("Unexpected error:", error)
        raise
