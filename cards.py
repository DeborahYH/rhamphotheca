from bs4 import BeautifulSoup
import pandas as pd
import logging
import requests
import os
import csv
import random
import time


def extract_cards(file_input):

    # Extracts the file name to be used in the new file 
    file_name = file_input.replace("_grid.csv", "")

    # List containing the data from all cards
    record_data = []

    # Dictionary containing the data from a single card
    record_dict = {}

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    # Extracts the record's ID from the cards 
    with open(f"wikiaves_data/{file_input}", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:

            # Extracts basic data to be included in the new .csv file
            registro_id = row["ID"]
            tipo = row["Tipo de Registro"]
            
            try:

                # Extracts the HTML code of each card
                response = requests.get(f"https://www.wikiaves.com.br/{registro_id}", 
                                        headers=headers,
                                        timeout=(5,10))
            
            except requests.exceptions.Timeout:
                logging.error(f"Timeout for ID {id}")
                continue
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed for ID {registro_id}: {e}")
                continue
            
            if response.status_code != 200:
                logging.error(f"Failed to retrieve data for ID {registro_id}: Status code {response.status_code}")
                continue

            try:
                soup = BeautifulSoup(response.text, "html.parser")

                # HTML portion containing the desired data
                div_data = soup.find("div", class_="wa-lista-detalhes")
            
            except Exception as e:
                logging.error(f"Failed to parse HTML for ID {registro_id}: {e}")
                continue
            
            if not div_data:
                continue
            
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
                
            record_dict.update({
                "id": registro_id,
                "tipo de registro": tipo,
                "especie_comum": nome_popular,
                "nome_cientifico": nome_cientifico,
            })

            # Extracts the value from miscellaneous fields
            for div in div_data.find_all("div"):
                label_tag = div.find("label")
                if not label_tag:
                    continue
                label = label_tag.text.strip().replace(":", "").lower()
                if label == "local de observação":
                    continue
                
                sibling = label_tag.next_sibling

                if sibling:
                    value = sibling.strip()
                else:
                    value = ""

                # Extracts the author and city from a link
                author = div.find("a")
                if author:
                    value = author.text.strip()
                else:
                    sibling = label_tag.next_sibling
                    if sibling:
                        value = sibling.strip()

                record_dict.update({
                    label: value
                })

            # Adds the data from each card to the list
            record_data.append(record_dict.copy())
            
            wait = random.uniform(5, 20)
            time.sleep(wait)

    # Converts the list of dictionaries to a dataframe
    df = pd.DataFrame(record_data)

    df = df.rename(columns={
                        "id": "ID",
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
                )

    # Creates a csv file inside the wikiaves_data folder
    df.to_csv(os.path.join("wikiaves_data", f"{file_name}_cards.csv"), index=False)
    logging.info(f"Data extracted from cards and saved to '{file_name}_cards.csv' with {len(df)} records")