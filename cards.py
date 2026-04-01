from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd
import logging
import requests
import os
import csv
import random
import time


BASE_URL = "https://www.wikiaves.com.br/"

HEADERS = {"User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36")}

COLUMN_MAP = {"id": "id",
            "tipo_registro": "media_type",
            "especie_comum": "common_name", 
            "nome_cientifico": "scientific_name",
            "assunto(s)": "subject",
            "ação principal": "main_action",
            "sexo": "sex",
            "idade": "age",
            "autor": "author",
            "município": "location",
            "feita em": "photo_date",
            "publicada em": "publication_date",
            "câmera": "camera",
            "observações do autor": "author_notes",
            "guiado(a) por": "guide",
            "tipo de som": "sound_type",
            "emissor do som": "sound_emitter",
            "emissor foi avistado?": "emitter_seen",
            "contexto": "context",
            "após playback?": "after_playback",
            "gravado em": "rec_datetime",
            "tamanho do arquivo": "file_size",
            "duração": "duration",
            "gravador": "recorder",
            "microfone": "microphone",
            "ave com anilha/pulseira?": "banded",
            "provável soltura/escape": "possible_release"}


def request_card(record_id):
    """
    Makes a request to the URL of the card and returns the HTML content.
    Parameters
    ----------
    record_id : str
        The ID of the record/card being requested.

    Returns
    -------
    response.text : str
        The HTML content of the card.
    """

    try:

        # Extracts the HTML code of each card
        response = requests.get(f"{BASE_URL}{record_id}", 
                                headers=HEADERS,
                                timeout=(5,10))
        
        response.raise_for_status()
        
        return response.text

    except requests.exceptions.Timeout:
        logging.error(f"Timeout for ID {record_id}")
        return None
    
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error for ID {record_id}: {e}")
        return None
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for ID {record_id}: {e}")
        return None

def extract_data(soup, record_id, media_type):
    """
    Extracts data from a single card.

    Parameters
    ----------
    soup : BeautifulSoup object
        Refers to the card's parsed HTML content.
    record_id : str
        The ID of the record being extracted.
    media_type : str
        The type of the media (photo or sound).
    
    Returns
    -------
    record_dict : dict
        Dictionary containing the data extracted from the card.
    """
    
    # HTML portion containing the desired data
    div_data = soup.find("div", class_="wa-lista-detalhes")
    
    if not div_data:
        return None
    
    # Extracts the value from 'Nome Popular'
    common_name_tag = div_data.find("a", class_="wa-id")
    if common_name_tag:
        common_name = common_name_tag.text.strip()
    else:
        common_name = ""

    # Extracts the value from 'Nome Cientifico'
    scientific_name_tag = div_data.find("i")
    if scientific_name_tag:
        scientific_name = scientific_name_tag.text.strip()
    else:
        scientific_name = ""
        
    # Dictionary containing the data from each card
    record_dict = {
        "id": record_id,
        "tipo_registro": media_type,
        "especie_comum": common_name,
        "nome_cientifico": scientific_name,
    }

    # Extracts the value from miscellaneous fields
    for div in div_data.find_all("div"):
        label_tag = div.find("label")
        if not label_tag:
            continue
        
        label = label_tag.text.strip().replace(":", "").lower()
        if label == "local de observação":
            continue
        
        author = div.find("a")
        if author:
            value = author.text.strip()
        else:
            sibling = label_tag.next_sibling
            value = sibling.strip() if sibling else ""

        record_dict[label] = value

    return record_dict

def save_cards(record_data, file_input):
    """
    Saves the extracted data from the cards into a new .csv file.

    Parameters
    ----------
    record_data : list
        List of dictionaries containing the data extracted from each card.
    file_input : str
        Path to the input CSV file.
    """

    extraction_date = dt.datetime.now().strftime('%d-%m-%Y')

    # Extracts the file name to be used in the new file 
    base_name = os.path.basename(file_input)
    file_name = base_name.split("_(")[0]

    # Converts the list of dictionaries to a dataframe
    df = pd.DataFrame(record_data)

    df = df.rename(columns=COLUMN_MAP)

    # Creates a csv file inside the wikiaves_data folder
    df.to_csv(os.path.join("wikiaves_data", f"{file_name}_({extraction_date})_cards.csv"), index=False)
    logging.info(f"Data from cards saved to '{file_name}_({extraction_date})_cards.csv' with {len(df)} records")


def extract_cards(file_input):
    """
    Extracts the data from the cards and saves it in a new .csv file.
    
    Parameters
    ----------
    file_input : str
        Path to the input CSV file.
    """

    # List containing the data from all cards
    record_data = []

    # Extracts the record's ID from the cards 
    with open(file_input, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:

            # Extracts basic data to be included in the new .csv file
            record_id = row["id"]
            media_type = row["media_type"]
            
            response_html = request_card(record_id)

            if response_html is None:
                continue

            soup = BeautifulSoup(response_html, "html.parser")

            # Extracts the data from each card
            record_dict = extract_data(soup, record_id, media_type)

            # Adds the data from each card to the list
            if record_dict is not None:
                record_data.append(record_dict)
            
            wait = random.uniform(5, 20)
            time.sleep(wait)

    save_cards(record_data, file_input)
