import os
import redis
from google import genai
from google.genai import types
from dotenv import load_dotenv
from .caching import Cache


def generate_summary(data: dict) -> str:

    env_path = os.path.join(os.path.dirname(__file__), '../../.env')
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="You are a super AI agent that analyzes and translates PHIVOLCS' earthquake details " \
            "into simple, friendly, consumable and easy-to-digest information for Filipinos. You are able to give the" \
            "reports primarily in English, but also in distinct Filipino native languages, per their preferences"
        ),
        contents=
        "In a 4-sentence paragraph, summarize of the earthquake detail reports, along with" \
        "2 simple tips on earthquake safety for affected regions (include in the paragraph)." \
        "Make sure the tips are appropriate for the situation and severity." \
        "Earthquake Information:" \
        f"Date and Time: {data["date_time"]}"
        f"Latitude: {data['latitude']}"
        f"Longitude: {data['longitude']}"
        f"Depth: {data['depth']}"
        f"Magnitude: {data['magnitude']}"
        f"Location: {data['location']}"
    )

    return response.text

    
def fetch_summary(earthquake):
    cache = Cache(f"{earthquake['detail_link']}-summary")
    data = cache.get()
    if data is not None:
        return data
    else:
        data = generate_summary(earthquake)
        cache.set(data)
        return data