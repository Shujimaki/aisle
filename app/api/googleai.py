import os
import redis
from google import genai
from google.genai import types, errors
from dotenv import load_dotenv
from .caching import Cache


def generate_summary(data: dict) -> dict:

    env_path = os.path.join(os.path.dirname(__file__), '../../.env')
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    magnitude_condition = (
        "If the magnitude is 4.0 or higher, include a friendly reminder to check the full bulletin report here: "
        f"{data['detail_link']}."
    )

    system_instruction = (
        "You are an AI assistant that summarizes PHIVOLCS earthquake reports. "
        "Your tone should be calm, and formal but still easy-to-digest — as if you’re explaining the situation to everyday Filipinos. "
        "Avoid technical jargon, but keep the facts accurate. Avoid greetings as well -- just straight to the report."
        "Never use decorations (like bold, italics, headers, or bullets). "
        "Respond in plain text only."
    )

    contents = (
        "TASK:\n"
        "Summarize the following earthquake information in exactly 5 sentences. "
        "Make it easy to understand and reassuring in tone. "
        "Include 2 short, simple, and relevant safety tips for the affected areas. "
        f"{magnitude_condition}\n\n"
        "EARTHQUAKE DETAILS:\n"
        f"- Date and Time: {data['date_time']}\n"
        f"- Latitude: {data['latitude']}\n"
        f"- Longitude: {data['longitude']}\n"
        f"- Depth: {data['depth']}\n"
        f"- Magnitude: {data['magnitude']}\n"
        f"- Location: {data['location']}\n"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(system_instruction=system_instruction),
            contents=contents
        )

        return {
            "success": True,
            "data": response.text
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

    
def fetch_summary(earthquake):
    cache = Cache(f"{earthquake['detail_link']}-summary")
    data = cache.get()
    if data is not None:
        return data
    
    data = generate_summary(earthquake)

    if data["success"]:
        cache.set(data["data"])
        return data["data"]

    return f"Error generating earthquake summary. Please refer to the original bulletin for details. error: {data['error']}"