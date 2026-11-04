import os
import json
import urllib.request
import urllib.error
import time

API_KEY = os.environ.get("GEMINI_API_KEY")
# Yahan model ka naam gemini-3.8-flash set kar diya hai
MODEL_NAME = "gemini-3.8-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={API_KEY}"

prompt_data = {
    "contents": [{
        "parts": [{"text": "Aapka jo bhi prompt ya script generate karne ka code hai wo yahan aayega"}]
    }]
}

headers = {'Content-Type': 'application/json'}
req_data = json.dumps(prompt_data).encode('utf-8')

request = urllib.request.Request(URL, data=req_data, headers=headers, method='POST')

max_attempts = 4
backoff_delays = [15, 30, 45]

success = False
response_text = ""

for attempt in range(1, max_attempts + 1):
    try:
        print(f"Gemini request attempt {attempt}/{max_attempts}")
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            response_text = result['candidates'][0]['content']['parts'][0]['text']
            success = True
            break
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"API error {e.code}: {error_body}")
        if attempt < max_attempts:
            delay = backoff_delays[attempt - 1]
            print(f"Retrying after {delay} seconds...")
            time.sleep(delay)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if attempt < max_attempts:
            time.sleep(15)

if not success:
    raise RuntimeError(f"Gemini ({MODEL_NAME}) is still unavailable after {max_attempts} attempts.")

# Output ko file ya aage process karne ke liye
print("Successfully generated script!")





     
