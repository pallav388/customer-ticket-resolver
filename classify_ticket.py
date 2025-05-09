import os
import requests
import json
from dotenv import load_dotenv
import sys

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

# Load API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Flash 2.0 Model URL
GEMINI_FLASH_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# Pro Model URL (more accurate)
GEMINI_PRO_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"

def call_gemini_classification(text: str, model_url: str) -> dict:
    headers = {"Content-Type": "application/json"}

    prompt = f"""
You are a JSON-only classification API.

Analyze this customer ticket carefully.

Return ONLY a valid JSON like:

{{
  "sentiment": "Positive" or "Negative" or "Neutral",
  "issue_type": "Billing" or "Technical" or "Login" or "General" or "Other"
}}

Strict JSON. No explanation.

Ticket:
\"\"\"{text}\"\"\"
"""

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(model_url, headers=headers, json=payload)
    return response.json()

def parse_gemini_response(result) -> dict:
    try:
        if 'candidates' in result and 'content' in result['candidates'][0]:
            content = result['candidates'][0]['content']['parts'][0]['text']
            print("🔥 GEMINI Raw Reply:", content)

            if content.strip().startswith("{") and content.strip().endswith("}"):
                parsed = json.loads(content)
                sentiment = parsed.get("sentiment", "Unknown")
                issue_type = parsed.get("issue_type", "General")
                return {"sentiment": sentiment, "issue_type": issue_type}
            else:
                print("⚠️ Gemini returned non-JSON format.")
                return {"sentiment": "Unknown", "issue_type": "General"}
        else:
            print("⚠️ No candidates found in Gemini response.")
            return {"sentiment": "Unknown", "issue_type": "General"}
    except Exception as e:
        print("❌ Error parsing Gemini response:", e)
        return {"sentiment": "Unknown", "issue_type": "General"}

def classify_ticket(text: str) -> dict:
    try:
        # 1. Try Flash model first (fast + cheap)
        print("🚀 Trying classification with Flash model...")
        result_flash = call_gemini_classification(text, GEMINI_FLASH_URL)
        parsed = parse_gemini_response(result_flash)

        # 2. If Flash fails (Unknown), retry Flash once
        if parsed["sentiment"] == "Unknown":
            print("🔁 Retrying Flash classification...")
            result_flash_retry = call_gemini_classification(text, GEMINI_FLASH_URL)
            parsed = parse_gemini_response(result_flash_retry)

        # 3. If still fails, fallback to Pro model (more accurate)
        if parsed["sentiment"] == "Unknown":
            print("🧠 Switching to Pro model for stronger classification...")
            result_pro = call_gemini_classification(text, GEMINI_PRO_URL)
            parsed = parse_gemini_response(result_pro)

        return parsed

    except Exception as e:
        print("❌ Total Classification Error:", e)
        return {"sentiment": "Unknown", "issue_type": "General"}
