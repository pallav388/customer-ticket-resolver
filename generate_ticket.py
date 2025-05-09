import os
import requests
from dotenv import load_dotenv
import json
import sys

load_dotenv()

sys.stdout.reconfigure(encoding='utf-8')

print("✅ GEMINI API KEY (partial):", os.getenv("GEMINI_API_KEY")[:20])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

def generate_reply(text: str) -> str:
    headers = {"Content-Type": "application/json"}

    prompt = f"""
You are a friendly and professional customer support agent.

Write a helpful and polite reply to the following issue:

\"\"\"{text}\"\"\"

Keep it empathetic and actionable.
"""

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        result = response.json()
        print("🔥 GEMINI Full Raw Response:", json.dumps(result, indent=2))  # Debugging line

        if 'candidates' in result and 'content' in result['candidates'][0]:
            reply = result['candidates'][0]['content']['parts'][0]['text']
            return reply.strip()
        else:
            print("❌ No candidates found in GEMINI response!")
            return "We're experiencing some technical issues. Please try again later."

    except Exception as e:
        print("❌ Reply Generation Error:", e)
        return "We're experiencing some technical issues. Please try again later."
