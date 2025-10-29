import os
from google import genai
from google.genai import types
from dotenv import load_dotenv


def generate_summary(data: dict) -> str:

    env_path = os.path.join(os.path.dirname(__file__), '../../.env')
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="You are a super AI agent that analyzes and translates PHIVOLC's earthquake details " \
            "into consumable and easy-to-digest information for Filipinos. You are able to give the" \
            "reports primarily in English, but also in distinct Filipino native languages, per their preferences"
        ),
        contents=
        "Create a straight-to-the-point (no headers) summary of the specified earthquake, in 3 sentences." \
        "Afterwards, include 2 simple tips on earthquake safety for affected regions." \
        "Earthquake Information:" \
        f"Date and Time: {data["date_time"]}"
        f"Latitude: {data['latitude']}"
        f"Longitude: {data['longitude']}"
        f"Depth: {data['depth']}"
        f"Magnitude: {data['magnitude']}"
        f"Location: {data['location']}"
    )

    return response.text

if __name__ == "__main__":
    res = generate_summary(
        {'date_time': '29 October 2025 - 04:22 PM', 'depth': '030', 'detail_link': 'https://earthquake.phivolcs.dost.gov.ph/2025_Earthquake_Information/October/2025_1029_0822_B1.html', 'latitude': '09.65', 'location': '015\n\t\t  km S 15Â° E of General Luna (Surigao Del Norte)', 'longitude': '126.19', 'magnitude': '6.0'}
    )
    print(res)
    