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
    Defines the URL parameters for the request.
    """

    # Sets the URL parameters for the request
    params = {
    "tm": tm,
    "t": t,
    "c": c,
    "p": page
    }

    if s is not None:
        params["s"] = s
    
    return params

def extract_records(items, records, page):
    """
    Extracts the desired data from each record and appends it to the list of records.
    """

    for item in items.values():
        records.append({
            "ID": item["id"],
            "Tipo de Registro": item["tipo"],
            "Autor": item["autor"],
            "Município": item["local"],
            "Data do Registro": item["data"],
            "Nome Popular": item["sp"]["nvt"],
            "Nome Cientifico": item["sp"]["nome"],
            "Página": page,
        })
    
    return records

def save_grid(df, s, extraction_date):    
    """ 
    Saves the data to a CSV file based on the location or scientific name
    """
    
    if s is None:
        municipio = df["Município"].iloc[0].lower().replace(" ", "_")
        nome, _, estado = municipio.partition("/")
        filename = f"{nome}_({estado})_({extraction_date})_grid.csv"
    else:
        nome_cientifico = df["Nome Cientifico"].iloc[0].lower().replace(" ", "_")
        filename = f"{nome_cientifico}_({extraction_date})_grid.csv"
    
    filepath = os.path.join("wikiaves_data", filename)
    df.to_csv(filepath, index=False)

    logging.info(f"Data from grid saved to '{filename}' ({len(df)} records)")


def extract_grid(t, c, s=None):
    """
    Extracts data from the pages containing individual records.
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
            
            try:
                data = response.json()
                items = data.get("registros", {}).get("itens", {})
            except ValueError as e:
                logging.error(f"JSON decoding failed on page {page} for tm={tm}: {e}")
                break

            # Interrupts the loop when there are no more records
            if not items:
                break 

            extract_records(items, records, page)

            time.sleep(random.uniform(5, 20))

            page += 1

    df = pd.DataFrame(records)

    save_grid(df, s, extraction_date)
