from bs4 import BeautifulSoup
import pandas as pd
import logging
import requests
import time
import random
import os

def extract_grid(t, c, s=None):
    """Extracts data from the pages containing individual records."""

    records = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/119.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    }

    # Extracts the data from photo/sound records
    for tm in ['f', 's']:

        page = 1

        # Uses pagination to obtain all desired records 
        while True:

            # Sets the URL parameters for the request
            params = {
            "tm": tm,
            "t": t,
            "c": c,
            "p": page
            }

            if s is not None:
                params["s"] = s
                    
            try:
                response = requests.get("https://www.wikiaves.com.br/getRegistrosJSON.php", 
                                        headers=headers, 
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
            
            items = data.get("registros", {}).get("itens", {})
            
            # Interrupts the loop when there are no more records
            if not items:
                break 

            # Extracts the desired data from each record
        
            for item in items.values():
                records.append({
                    "ID": item["id"],
                    "Tipo de Registro": item["tipo"],
                    "Autor": item["autor"],
                    "Município": item["local"],
                    "Data do Registro": item["data"],
                    "Nome Popular": item["sp"]["nvt"],
                    "Nome Cientifico": item["sp"]["nome"],
                })

            time.sleep(random.uniform(5, 20))
            
            page += 1

    df = pd.DataFrame(records)

    # Saves the data to a CSV file
    # File name is defined based on the presence of a specific parameter in the url
    if s is None:
        municipio = df["Município"].iloc[0]
        municipio = municipio.lower().replace(" ", "_")
        nome, _, estado = municipio.partition("/")
        df.to_csv(os.path.join("wikiaves_data", f"{nome}_({estado})_grid.csv"), index=False)
        logging.info(f"Data extracted from grid and saved to '{nome}_({estado})_grid.csv' with {len(df)} records")
    else:
        nome_cientifico = df["Nome Cientifico"].iloc[0]
        nome_cientifico = nome_cientifico.lower().replace(" ", "_")
        df.to_csv(os.path.join("wikiaves_data", f"{nome_cientifico}_grid.csv"), index=False)
        logging.info(f"Data extracted from grid and saved to '{nome_cientifico}_grid.csv' with {len(df)} records")
