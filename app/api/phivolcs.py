from bs4 import BeautifulSoup
from flask import jsonify
from urllib.parse import urljoin
import requests
import re
from datetime import datetime

# initialize storage for cached data, last fetched time
cached_data_all = None
last_fetch_time_all = None

# separate cache and fetch time for latest earthquake
cached_data_latest = None
last_fetch_time_latest = None

# set constant cache duration
CACHE_DURATION = 10 * 60 # seconds

# set the base url for api calls
BASE_URL = 'https://earthquake.phivolcs.dost.gov.ph/'

def get_latest_earthquake():
    global cached_data_latest, last_fetch_time_latest

    try:
        now = datetime.now()

        # check if cache for latest earthquake exists
        if cached_data_latest and last_fetch_time_latest and (now.second - last_fetch_time_latest.second) < CACHE_DURATION:
            # if cache exists, return cached data
            return jsonify({
                "success": True,
                "data": cached_data_latest,
                "cached": True,
                "last_updated": last_fetch_time_latest
            })
        
        # same headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': "keep-alive",
        }

        # request http connection with the phivolcs website, refuse ssl connection, timeout after 10 seconds of no connection
        res = requests.get(BASE_URL, headers=headers, verify=False, timeout=10)
        # use bs4 to parse the response (text form) into html structure
        soup = BeautifulSoup(res.text, "html.parser")

        # select all elements in the html that have css selector of MsoNormalTable
        tables = soup.select('table.MsoNormalTable')

        # iterate through tables
        for table in tables:
            print(table)
            print("before row")
            try:
                # only get second row (first row is header)
                # one row only since we're getting latest earthquake
                row = table.select('tr')[1]
            except:
                continue
            print(f"after row: {row}")

            # get all the table data elements of the row
            # the contents of the td's are the data for the earthquakes
            cells = row.find_all('td')

            # continue to next table if cells is empty
            if not cells:
                continue
        
            # continue to next table if # of cells is strictly not 6
            if len(cells) != 6:
                continue
        
            # store the cell data 
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

            additional_info = get_earthquake_additional_info(detail_link)
            
            # append all data as dictionary, to earthquake list
            earthquake ={
                "date_time": date_time,
                "detail_link": detail_link,
                "latitude": latitude,
                "longitude": longitude,
                "depth": depth,
                "magnitude": magnitude,
                "location": location,
            }

            earthquake.update(additional_info)
        
        # update cached_data_all to recently fetched data
        cached_data_latest = earthquake
        # update last fetched time to current time
        last_fetch_time_latest = now

        # return json of status indicators, along with data
        return jsonify({
            "success": True,
            "data": earthquake,
            "cached": False,
            "last_updated": last_fetch_time_latest
        })
    
    # catch an error
    except Exception as e:
        # return json with status indicator, along with error message for debugging
        return jsonify({
            "success": False,
            "message": "Error fetching latest earthquake data",
            "error": str(e)
        })





def get_all_earthquakes():
    # get global variables for cached_data_all and last fetched time
    global cached_data_all, last_fetch_time_all

    try:
        # get current time
        now = datetime.now()
        print(f"time {now}")

        # check if cached_data_all and last_fetch_time_all has content
        # check if time elapsed between current time and last fetched time is less than cache duration
        if cached_data_all and last_fetch_time_all and (now.second - last_fetch_time_all.second) < CACHE_DURATION:
            # if true, return cached data with last updated time
            return jsonify({
                "success": True,
                "data": cached_data_all,
                "cached": True,
                "last_updated": last_fetch_time_all
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

        # update cached_data_all to recently fetched data
        cached_data_all = earthquakes
        # update last fetched time to current time
        last_fetch_time_all = now

        # return json of status indicators, along with data
        return jsonify({
            "success": True,
            "data": earthquakes,
            "cached": False,
            "last_updated": last_fetch_time_all
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
"""





def get_earthquake_additional_info(detail_link):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': "keep-alive",
    }

    res = requests.get(detail_link, headers=headers, verify=False, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')

    paragraphs = soup.find_all("p")

    reported_intensities = None
    expected_damage = None
    expected_aftershocks = None

    for p in paragraphs:
        text = p.get_text(strip=True)

        if re.search(r'Reported\s+Intensities\s+:', text):
            reported_intensities = get_info_text(p)
            if reported_intensities == "":
                reported_intensities = "None"
            continue

        if re.search(r'Expecting\s+Damage\s+:', text):
            expected_damage = get_info_text(p)
            continue
    
        if re.search(r'Expecting\s+Aftershocks\s+:', text):
            expected_aftershocks = get_info_text(p)
            continue

    return ({
        "reported_intensities": reported_intensities,
        "expected_damage": expected_damage,
        "expected_aftershocks": expected_aftershocks
    })


def get_info_text(tag) -> str:
    parent = tag.find_parent("td")
    parent_sibling = parent.find_next_sibling("td")
    cousin = parent_sibling.find_all("p")
    data = cousin[0].get_text(strip=True)

    return data

# for testing of functions
# if __name__ == "__main__":
#     data = get_earthquake_additional_info("https://earthquake.phivolcs.dost.gov.ph/2025_Earthquake_Information/October/2025_1030_133142_B1F.html")
#     print(data)