import json

from google import genai

from schema import RESPONSE_SCHEMA
from config import GEMINI_API_KEY
from prompt import SYSTEM_PROMPT

client = genai.Client(api_key=GEMINI_API_KEY)


def analyze_report(report_text):
    full_prompt = f"""
{SYSTEM_PROMPT}

Medical Report:

{report_text}
"""

    response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=full_prompt,
    config={
        "response_mime_type": "application/json"
    }
)

    try:
        data = json.loads(response.text)
        return data

    except json.JSONDecodeError:
        return {
            "error": True,
            "message": "Gemini returned invalid JSON.",
            "raw_response": response.text
        }