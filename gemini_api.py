import requests

AZURE_GATEWAY_URL = "http://48.220.33.102:5000/generate"

def call_gemini(prompt: str, temp: float = 0.0) -> str:
    payload = {
        "prompt": prompt,
        "temp": temp
    }

    try:
        r = requests.post(AZURE_GATEWAY_URL, json=payload, timeout=60)

        if r.status_code != 200:
            print(f"Server Error {r.status_code}: {r.text}")
            return ""

        data = r.json()
        return data.get("text", "").strip()

    except Exception as e:
        print(f"Connection error: {e}")
        return ""