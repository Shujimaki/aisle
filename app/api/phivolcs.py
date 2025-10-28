from bs4 import BeautifulSoup
from flask import jsonify
from urllib.parse import urljoin
import requests
from datetime import datetime

# initialize storage for cached data, last fetched time
cached_data = None
last_fetch_time = None

# set constant cache duration
CACHE_DURATION = 10 * 60 # seconds

# set the base url for api calls
BASE_URL = 'https://earthquake.phivolcs.dost.gov.ph/'

def get_earthquakes():
    # get global variables for cached_data and last fetched time
    global cached_data, last_fetch_time

    try:
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

        # apply headers (same from original server.js)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': "keep-alive",
        }

        # fetch the text data from the phivolcs earthquake database
        # set verify to false to bypass SSL
        # apply headers
        res = requests.get("https://earthquake.phivolcs.dost.gov.ph/", headers=headers, verify=False, timeout=10)
        print("requests done")

        # parse the text data into a data structure using beautiful soup
        soup = BeautifulSoup(res.text, 'html.parser')
        print("parsing done")
        
        # create list of tables with css MsoNormalTable
        tables = soup.select('table.MsoNormalTable')

        # initialize list of earthquakes
        earthquakes = []

        # iterate through tables
        for table in tables:
            
            # select tr values and iterate through them
            # the first tr is usually header, so skip
            for row in table.select('tr')[1:]:
                # find all data values stored in td

                cells = row.find_all('td')
                if not cells:
                    continue

                if len(cells) == 6:

                    date_time_cell = cells[0]
                    latitude_cell = cells[1]
                    longitude_cell = cells[2]
                    depth_cell = cells[3]
                    magnitude_cell = cells[4]
                    location_cell = cells[5]

                    # find a tag to get href
                    date_time = date_time_cell.find('a').get_text().strip()
                    a_tag = date_time_cell.find('a')
                    # check if a tag and href exists
                    if a_tag and 'href' in a_tag.attrs:
                        # get the href value
                        href = a_tag['href']
                    else:
                        href = None
                    
                    # if href variable has content, normalize and combine to base url
                    if href:
                        # replace the \ with /
                        normalized_path = href.replace('\\','/')
                        
                        # combine the base url and normalized path to make a url
                        try:
                            detail_link = urljoin(BASE_URL, normalized_path)
                        except Exception:
                            detail_link = normalized_path

                    # get_earthquake_additional_info(detail_link)

                    # format the rest of the data to string, and remove whitespaces
                    latitude = latitude_cell.get_text().strip()
                    longitude = longitude_cell.get_text().strip()
                    depth = depth_cell.get_text().strip()
                    magnitude= magnitude_cell.get_text().strip()
                    location = location_cell.get_text().strip()

                    # append all data as dictionary, to earthquake list
                    earthquakes.append({
                        "date_time": date_time,
                        "detail_link": detail_link,
                        "latitude": latitude,
                        "longitude": longitude,
                        "depth": depth,
                        "magnitude": magnitude,
                        "location": location,
                    })

        # update cached_data to recently fetched data
        cached_data = earthquakes
        # update last fetched time to current time
        last_fetch_time = now

        # return json of status indicators, along with data
        return jsonify({
            "success": True,
            "data": earthquakes,
            "cached": False,
            "last_updated": last_fetch_time
        })
    
    # catch an error
    except Exception as e:
        # return json with status indicator, along with error message for debugging
        return jsonify({
            "success": False,
            "message": "Error fetching earthquake data",
            "error": str(e)
        })



"""
TODO:
complete for viewing each earthquake 
1. Reported Intensity
2. Expected Damage?
3. Expected Aftershocks?


def get_earthquake_additional_info(detail_link):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': "keep-alive",
    }

    res = requests.get(detail_link, headers=headers, verify=False, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')

    doc = soup.find_all(text="Reported")
    print(f"doc: {doc}")

    # parent = doc
    # print(f"parent: {parent}")
"""
