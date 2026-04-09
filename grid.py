from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import logging
import requests
import time
import random
import os


BASE_URL = "https://www.wikiaves.com.br/getRegistrosJSON.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/119.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

def define_params(tm, t, c, page, s=None):
    """
    Defines the URL parameters used in the request.

    Parameters
    ----------
    tm : str
        Type of media ('f' for photos and 's' for sounds)
    t : str
        The value 'c' appears to be the default and does not affect the response.
    c : str
        City ID
    page : int
        Page number for pagination
    s : str, optional
        Species ID

    Returns
    ----------
    params : dict
        Dictionary containing the URL parameters used in the request.
    """

    params = {
    "tm": tm,
    "t": t,
    "c": c,
    "p": page
    }

    if s is not None:
        params["s"] = s
    
    return params

def extract_records(items, records):
    """
    Extracts the desired data from each record and appends it to the list of records.

    Parameters
    ----------
    items : dict
        Dictionary containing the records returned by the request.
    records : list
        List of extracted records.
    page : int
        The page number for the current iteration.

    Returns
    -------
    records : list
        Updated list of extracted records.
    """

    for item in items.values():
        records.append({
            "record_id": item["id"],
            "media_type": item["tipo"],
            "scientific_name": item["sp"]["nome"],
            "common_name": item["sp"]["nvt"],
            "record_date": item["data"],
            "location": item["local"],
            "author": item["autor"],
        })

    return records

def save_grid(df, s, extraction_date):  
    """ 
    Saves the data extracted to a CSV file.
    The filename will be on the location or scientific name, depending on whether parameter `s` is provided

    Parameters
    ---------- 
    df : pd.DataFrame
        Dataframe containing data from the extracted records.
    s : str
        URL parameter used to determine how the filename will be defined.
        If s is not provided, the extraction will be based on the location. 
        If s is provided, the extraction will be based on the species.
    extraction_date : str
        Date of the data extraction.
    """
    
    if s is None:
        location = df["municipality"].iloc[0].lower().replace(" ", "_")
        municipality, _, state = location.partition("/")
        filename = f"{municipality}_({state})_({extraction_date})_grid.csv"
    else:
        scientific_name = df["scientific_name"].iloc[0].lower().replace(" ", "_")
        filename = f"{scientific_name}_({extraction_date})_grid.csv"

    filepath = os.path.join("wikiaves_data", filename)
    df.to_csv(filepath, index=False)

    logging.info(f"Data from grid saved to '{filename}' ({len(df)} records)")


def extract_grid(t, c, s=None):
    """
    Extracts the individual records from each page.

    Parameters
    ----------
    t : str
    c : str
        City ID
    s : str, optional 
        Species ID
    """

    extraction_date = dt.datetime.now().strftime('%d-%m-%Y')
    records = []

    # Extracts the data from photo/sound records
    for tm in ['f', 's']:

        page = 1

        # Uses pagination to obtain all desired records 
        while True:

            params = define_params(tm, t, c, page, s)
                    
            try:
                response = requests.get(BASE_URL, 
                                        headers=HEADERS, 
                                        params=params,
                                        timeout=(5,10))
            except requests.exceptions.Timeout:
                logging.error(f"Timeout on page {page} for tm={tm}")
                break
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed on page {page} for tm={tm}: {e}")
                break
            
            if response.status_code != 200:
                break
            
            # Parses the JSON response and extract the records
            try:
                data = response.json()
                items = data.get("registros", {}).get("itens", {})
            except ValueError as e:
                logging.error(f"JSON decoding failed on page {page} for tm={tm}: {e}")
                break

            # Interrupts the loop when there are no more records
            if not items:
                break 

            extract_records(items, records)

            time.sleep(random.uniform(5, 20))

            page += 1

    df = pd.DataFrame(records)

    # Saves the extracted data to a CSV file
    save_grid(df, s, extraction_date)
