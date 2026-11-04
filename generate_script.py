import os
import json
import urllib.request

api_key = os.environ["GEMINI_API_KEY"]

prompt = """
Create an original YouTube Shorts script for a realistic AI jungle
construction video.

Topic: Building a luxury underground swimming pool in a jungle.

Write:
1. Catchy title
2. 45-second video script
3. Scene-by-scene visual prompts
4. YouTube description
5. Relevant hashtags

Make it engaging and realistic.
"""

url = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.5-flash:generateContent"
    f"?key={api_key}"
)

data = {
    "contents": [{"parts": [{"text": prompt}]}]
}

request = urllib.request.Request(
    url,
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode("utf-8"))

text = result["candidates"][0]["content"]["parts"][0]["text"]

with open("generated_script.txt", "w", encoding="utf-8") as file:
    file.write(text)

print("Gemini script generated successfully!")
