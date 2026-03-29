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

COLUMN_MAP = {"id": "ID",
            "tipo de registro": "Tipo de Registro",
            "especie_comum": "Nome Popular", 
            "nome_cientifico": "Nome Cientifico",
            "assunto(s)": "Assunto",
            "ação principal": "Ação Principal",
            "sexo": "Sexo",
            "idade": "Idade",
            "autor": "Autor",
            "município": "Município",
            "feita em": "Data do Registro",
            "publicada em": "Data de Publicação",
            "câmera": "Câmera",
            "observações do autor": "Observações do Autor",
            "guiado(a) por": "Guia",
            "tipo de som": "Tipo de Som",
            "emissor do som": "Emissor do Som",
            "emissor foi avistado?": "Emissor Avistado",
            "contexto": "Contexto",
            "após playback?": "Após Playback",
            "gravado em": "Data de Gravação",
            "tamanho do arquivo": "Tamanho do Arquivo",
            "duração": "Duração",
            "gravador": "Gravador",
            "microfone": "Microfone",}


def request_card(registro_id):
    try:

        # Extracts the HTML code of each card
        response = requests.get(f"{BASE_URL}{registro_id}", 
                                headers=HEADERS,
                                timeout=(5,10))
        
        response.raise_for_status()
        
        return response.text

    except requests.exceptions.Timeout:
        logging.error(f"Timeout for ID {registro_id}")
        return None
    
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error for ID {registro_id}: {e}")
        return None
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for ID {registro_id}: {e}")
        return None

def extract_card_data(soup, registro_id, tipo):

    # HTML portion containing the desired data
    div_data = soup.find("div", class_="wa-lista-detalhes")
    
    if not div_data:
        return None
    
    # Extracts the value from 'Nome Popular'
    nome_popular_tag = div_data.find("a", class_="wa-id")
    if nome_popular_tag:
        nome_popular = nome_popular_tag.text.strip()
    else:
        nome_popular = ""

    # Extracts the value from 'Nome Cientifico'
    nome_cientifico_tag = div_data.find("i")
    if nome_cientifico_tag:
        nome_cientifico = nome_cientifico_tag.text.strip()
    else:
        nome_cientifico = ""
        
    # Dictionary containing the data from each card
    record_dict = {
        "id": registro_id,
        "tipo de registro": tipo,
        "especie_comum": nome_popular,
        "nome_cientifico": nome_cientifico,
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

def save_cards(record_data, file_input, extraction_date):
    """
    Saves the extracted data from the cards into a new .csv file.
    """

    # Extracts the file name to be used in the new file 
    file_name = file_input.split("_(")[0]

    # Converts the list of dictionaries to a dataframe
    df = pd.DataFrame(record_data)

    df = df.rename(columns=COLUMN_MAP)

    # Creates a csv file inside the wikiaves_data folder
    df.to_csv(os.path.join("wikiaves_data", f"{file_name}_({extraction_date})_cards.csv"), index=False)
    logging.info(f"Data from cards saved to '{file_name}_({extraction_date})_cards.csv' with {len(df)} records")


def extract_cards(file_input):

    extraction_date = dt.datetime.now().strftime('%d-%m-%Y')

    # List containing the data from all cards
    record_data = []

    # Extracts the record's ID from the cards 
    with open(file_input, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:

            # Extracts basic data to be included in the new .csv file
            registro_id = row["id"]
            tipo = row["media_type"]
            
            response_html = request_card(registro_id)

            if response_html is None:
                continue

            soup = BeautifulSoup(response_html, "html.parser")

            # Extracts the data from each card
            record_dict = extract_card_data(soup, registro_id, tipo)

            # Adds the data from each card to the list
            if record_dict is not None:
                record_data.append(record_dict)
            
            wait = random.uniform(5, 20)
            time.sleep(wait)

    save_cards(record_data, file_input, extraction_date)
