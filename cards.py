from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import csv
import random
import time


def extract_cards(file):

    # Extracts the file name to be used in the new file 
    file_name = file.replace("_grid", "")

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
    with open(f"wikiaves_data/{file}", "r") as file:
        reader = csv.DictReader(file)

        for row in reader:

            # Extracts basic data to be included in the new .csv file
            id = row["ID"]
            tipo = row["Tipo de Registro"]

            # Extracts the HTML code of each card
            response = requests.get(f"https://www.wikiaves.com.br/{id}", headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            # HTML portion containing the desired data
            div_data = soup.find("div", class_="wa-lista-detalhes")

            # Extracts the desired data
            nome_popular = div_data.find("a", class_="wa-id").text.strip()

            nome_cientifico = div_data.find("i").text.strip()
            record_dict.update({
                "id": id,
                "tipo de registro": tipo,
                "especie_comum": nome_popular,
                "nome_cientifico": nome_cientifico,
            })

            for div in div_data.find_all("div"):
                label_tag = div.find("label")
                if not label_tag:
                    continue
                label = label_tag.text.strip().replace(":", "").lower()
                value = label_tag.next_sibling.strip() if label_tag.next_sibling else ""
                
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