 
import os
import json
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
    "contents": [
        {
            "parts": [
                {"text": prompt}
            ]
        }
    ]
}

request = urllib.request.Request(
    url,
    data=json.dumps(data).encode("utf-8"),
    headers={
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    },
    method="POST"
)

try:
    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    generated_text = result["candidates"][0]["content"]["parts"][0]["text"]

    with open("generated_script.txt", "w", encoding="utf-8") as file:
        file.write(generated_text)

    print("SUCCESS: Gemini generated your YouTube script!")

except urllib.error.HTTPError as error:
    print("Gemini API Error:", error.code)
    print(error.read().decode("utf-8"))
    raise

except Exception as error:
    print("Error:", str(error))
    raise
