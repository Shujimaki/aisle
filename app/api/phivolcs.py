from bs4 import BeautifulSoup
from flask import Blueprint, jsonify
from flask_cors import CORS, cross_origin
import requests
from datetime import datetime

bp = Blueprint("phivolcs_api", __name__, url_prefix="/api/phivolcs")
CORS(bp)

cached_data = None
last_fetch_time = None
CACHE_DURATION = 10 * 60 # seconds
BASE_URL = 'https://earthquake.phivolcs.dost.gov.ph/'

@bp.route("/earthquakes")
def get_earthquakes():
    # get global variables for cached_data and last fetched time
    global cached_data, last_fetch_time

    # get current time
    now = datetime.now()
    print(f"time {now}")

    # check if cached_data and last_fetch_time has content
    # check if time elapsed between current time and last fetched time is less than cache duration
    if cached_data and last_fetch_time and (now.second - last_fetch_time.second) < CACHE_DURATION:
        # if true, return cached data with last updated time
        return jsonify({
            "success": True,
            "data": cached_data,
            "cached": True,
            "last_updated": last_fetch_time
        })

    print(f"condition done")
    # fetch the text data from the phivolcs earthquake database
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': "keep-alive",
    }

    res = requests.get("https://earthquake.phivolcs.dost.gov.ph/", headers=headers, verify=False, timeout=5)
    print("requests done")
    # parse the text data into a data structure using beautiful soup
    soup = BeautifulSoup(res.text, 'html.parser')
    print("parsing done")
    
    tables = soup.select('table.MsoNormalTable')
    print(tables)
    earthquakes = []
    for table in tables:
        for row in table.select('tr')[1:]:
            cells = [td.get_text(strip=True) for td in row.select('td')]
            if len(cells) == 6:
                earthquakes.append({
                    "dateTime": cells[0],
                    "latitude": cells[1],
                    "longitude": cells[2],
                    "depth": cells[3],
                    "magnitude": cells[4],
                    "location": cells[5]
                })

    cached_data = earthquakes
    last_fetch_time = now

    return jsonify({
        "success": True,
        "data": earthquakes,
        "cached": False,
        "last_updated": last_fetch_time
    })
