import os
import redis
from google import genai
from google.genai import types, errors
from dotenv import load_dotenv
from .caching import Cache


def generate_summary(data: dict) -> dict:

    # set the program's .env path string from this file (in the root directory)
    env_path = os.path.join(os.path.dirname(__file__), '../../.env')
    
    # set the programm's .env using the path created
    load_dotenv(dotenv_path=env_path)

    # get the gemini api key
    api_key = os.getenv("GEMINI_API_KEY")

    # connect to gemini client using api key
    client = genai.Client(api_key=api_key)

    # set magnitude condition prompt for ai
    magnitude_condition = (
        "Only if the magnitude is 4.0 or higher, "
        "Include 2 short, simple, and relevant safety tips for the affected areas."
        "Also report the additional details included in the official bulletin report "
        f"{data['detail_link']}."
        "Additional reports:" \
        "1. Reported Intensities" \
        "2. Expected Damages?" \
        "3. Expected Aftershocks?"
    )

    # set the ai's general role and instruction
    # this context will be used by the ai for all messages
    system_instruction = (
        "You are an AI assistant that summarizes PHIVOLCS earthquake reports. "
        "Your tone should be calm, and formal but still easy-to-digest — as if you’re explaining the situation to everyday Filipinos. "
        "Avoid technical jargon, but keep the facts accurate. Avoid greetings as well -- just straight to the report."
        "Never use decorations (like bold, italics, headers, or bullets). "
        "Respond in plain text only."
    )

    # set the actual text to be fed into the ai
    contents = (
        "TASK:\n"
        "Summarize the following earthquake information in exactly 5 sentences. "
        "Make it easy to understand and reassuring in tone. "
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
        # send the instruction and content to gemini, and retrieve the response
        response = client.models.generate_content(
            model="gemini-2.0-flash", # best least busy model 
            config=types.GenerateContentConfig(system_instruction=system_instruction),
            contents=contents
        )

        # if request is successful, return success and data
        return {
            "success": True,
            "data": response.text
        }
    
    # handle error for when request fails
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

    
# function for caching and fetching ai summary
def fetch_summary(earthquake):
    # cache key is the detail link of the bulletin
    # such that, the same summary for an earthquake is consistent among all users
    cache = Cache(f"{earthquake['detail_link']}-summary")
    data = cache.get()

    # if cached data exists, return it
    if data is not None:
        return data
    
    # else, generate data 
    data = generate_summary(earthquake)

    # check if data returns true or false in success

    # return the actual data if successful
    if data["success"]:
        cache.set(data["data"])
        return data["data"]

    # else, return an error string
    return f"Error generating earthquake summary. Please refer to the original bulletin for details. error: {data['error']}"