import os

import pandas as pd
from recombee_api_client.api_client import RecombeeClient, Region
from recombee_api_client.api_requests import AddItemProperty, ListItemProperties
from recombee_api_client.exceptions import APIException

DB_NAME = os.getenv('RECOMBEE_DB', 'numele_bazei_tale_de_date')
PRIVATE_TOKEN = os.getenv('RECOMBEE_TOKEN', 'tokenul_tau_privat')
REGION = os.getenv('RECOMBEE_REGION', 'eu-west')

# Initializarea clientului Recombee
client = RecombeeClient(DB_NAME, PRIVATE_TOKEN, region=Region[REGION.upper().replace('-', '_')])

PATH_DATASET = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'books.csv')

PROPRIETATI_CATALOG = [
    {"name": "title",            "type": "string"},
    {"name": "authors",          "type": "string"},
    {"name": "publication_year", "type": "int"},
    {"name": "language_code",    "type": "string"},
    {"name": "average_rating",   "type": "double"},
    {"name": "ratings_count",    "type": "int"},
    {"name": "image_url",        "type": "image"},
]


def load_dataset():
    """Functie helper care citeste si verifica dataset-ul"""
    try:
        df = pd.read_csv(PATH_DATASET)
        total_randuri = len(df)
        print(f"Dataset incarcat cu succes! Total randuri: {total_randuri}")

        # Verificare numar de randuri (100 - 10K)
        if total_randuri < 100:
            print("ATENTIE: Dataset-ul are sub 100 de produse!")
        elif total_randuri > 10 * 1000:
            print("ATENTIE: Dataset-ul este prea mare! Limitati-l la primele 10K randuri.")

        lipsa = [p["name"] for p in PROPRIETATI_CATALOG if p["name"] not in df.columns]
        if lipsa:
            print(f"ATENTIE: Coloane lipsa din CSV: {lipsa}")

        print("\nPreview primele 3 randuri:")
        print(df.head(3))
        print("-" * 50)
        return df
    except FileNotFoundError:
        print(f"Eroare: Fisierul '{PATH_DATASET}' nu a fost gasit!")
        return None


def set_properties():
    """Functie care trimite structura coloanelor catre Recombee"""
    print(f"\nIncepe definirea proprietatilor pentru baza de date: '{DB_NAME}'...")

    for prop in PROPRIETATI_CATALOG:
        try:
            # Request API Recombee pentru adaugarea proprietatii (echivalentul adaugarii unei coloane intr-un tabel)
            client.send(AddItemProperty(prop["name"], prop["type"]))
            print(f"Proprietatea '{prop['name']}' ({prop['type']}) a fost adaugata cu succes.")
        except APIException as e:
            # Recombee returnează eroare daca proprietatea a fost deja definita la o rulare anterioara
            if "409" in str(e) or "already exists" in str(e).lower():
                print(f"Proprietatea '{prop['name']}' exista deja in Recombee.")
            else:
                print(f"Eroare API la proprietatea '{prop['name']}': {e}")


def verify():
    """Interogheaza API-ul pentru a lista toate proprietatile active din cont"""
    print("\nSe verifica structura finala din Recombee...")
    try:
        atribute_active = client.send(ListItemProperties())
        print("Proprietatile configurate in acest moment in baza ta de date:")
        for atribut in atribute_active:
            print(f"- {atribut['name']} => tip de date: {atribut['type']}")
    except APIException as e:
        print(f"Nu s-a putut efectua verificarea. Detalii eroare: {e}")


if __name__ == "__main__":
    # Verificam daca fisierul CSV local se citeste corect
    dataset_ok = load_dataset()

    if dataset_ok is not None:
        # Trimitem proprietatile catre Recombee prin API
        set_properties()

        # Listam ce s-a salvat in baza de date pentru confirmare
        verify()
