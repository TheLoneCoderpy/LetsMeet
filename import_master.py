import pandas as pd
import psycopg2
import re
from datetime import datetime
import xml.etree.ElementTree as ET
from pymongo import MongoClient

EXCEL_FILE = "Lets Meet DB Dump.xlsx"
XML_FILE   = "Lets_Meet_Hobbies.xml"

MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "LetsMeet"
MONGO_COLLECTION = "users"

POSTGRES_HOST = "localhost"
POSTGRES_DB   = "lf8_lets_meet_db"
POSTGRES_USER = "user"
POSTGRES_PWD  = "secret"
POSTGRES_PORT = 5433  # Falls dein Docker Compose Port 5433 ist


def main():
    """ Hauptimport-Funktion für Excel, MongoDB und XML """
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PWD,
            port=POSTGRES_PORT
        )
        conn.set_client_encoding('UTF8')
        cursor = conn.cursor()

        # Excel Import
        import_from_excel(cursor, conn)

        # MongoDB Import
        import_from_mongo(cursor, conn)

        # XML Import
        import_from_xml(cursor, conn)

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Fehler bei der Verbindung zur Datenbank: {e}")


def import_from_excel(cursor, conn):
    """ Importiert Daten aus einer Excel-Datei in PostgreSQL """
    try:
        print("Starte Excel-Import...")
        df = pd.read_excel(EXCEL_FILE, sheet_name=0)

        df.columns = [
            "nachname_vorname",
            "strasse_plz_ort",
            "telefon",
            "hobbies_raw",
            "email",
            "geschlecht",
            "interessiert_an",
            "geburtsdatum"
        ]

        for _, row in df.iterrows():
            # Namen verarbeiten
            name_str = str(row["nachname_vorname"]) if pd.notnull(row["nachname_vorname"]) else ""
            first_name, last_name = split_name_simple(name_str)

            # Adresse verarbeiten
            addr_str = str(row["strasse_plz_ort"]) if pd.notnull(row["strasse_plz_ort"]) else ""
            street, house_no, zip_code, city = parse_address(addr_str)

            # Adresse einfügen oder abrufen
            address_id = get_or_create_address(cursor, street, house_no, zip_code, city)

            # Geschlecht, Geburtstag
            gender = row["geschlecht"] if pd.notnull(row["geschlecht"]) else None
            birth_date = parse_date_ddmmYYYY(row["geburtsdatum"]) if pd.notnull(row["geburtsdatum"]) else None

            # E-Mail
            email = row["email"] if pd.notnull(row["email"]) else None
            if not email:
                continue  # Keine Benutzer ohne E-Mail

            # Benutzer anlegen
            user_id = get_or_create_user(cursor, first_name, last_name, email, address_id, gender, birth_date)
            if not user_id:
                continue

        conn.commit()

    except Exception as e:
        print(f"Fehler beim Excel-Import: {e}")
        conn.rollback()


def import_from_mongo(cursor, conn):
    """ Importiert Benutzer, Freunde, Likes und Nachrichten aus MongoDB """
    try:
        print("Starte MongoDB-Import...")

        mongo_client = MongoClient(MONGO_URI)
        mdb = mongo_client[MONGO_DB]
        user_coll = mdb[MONGO_COLLECTION]

        for doc in user_coll.find():
            email = doc.get("_id", "")
            if not email:
                continue

            # Namen aus Mongo extrahieren
            name_mongo = doc.get("name", "")
            first_name, last_name = split_name(name_mongo, email)

            user_id = get_or_create_user(cursor, first_name, last_name, email)

            if not user_id:
                continue

        conn.commit()
        mongo_client.close()

    except Exception as e:
        print(f"Fehler beim MongoDB-Import: {e}")
        conn.rollback()


def import_from_xml(cursor, conn):
    """ Importiert Hobbys aus einer XML-Datei """
    try:
        print("🔄 Starte XML-Import...")
        tree = ET.parse(XML_FILE)
        root = tree.getroot()

        for hobby in root.findall("hobby"):
            hobby_name = hobby.text.strip()
            get_or_create_hobby(cursor, hobby_name)

        conn.commit()

    except Exception as e:
        print(f"Fehler beim XML-Import: {e}")
        conn.rollback()


# 🔧 Hilfsfunktionen für den Import
def get_or_create_address(cursor, street, house_no, zip_code, city):
    """ Holt oder erstellt eine Adresse """
    if not street or not city:
        return None

    cursor.execute("SELECT id FROM addresses WHERE street = %s AND house_no = %s AND zip_code = %s AND city = %s",
                   (street, house_no, zip_code, city))
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute("INSERT INTO addresses (street, house_no, zip_code, city) VALUES (%s, %s, %s, %s) RETURNING id",
                   (street, house_no, zip_code, city))
    return cursor.fetchone()[0]


def get_or_create_user(cursor, first_name, last_name, email, address_id=None, gender=None, birth_date=None):
    """ Holt oder erstellt einen Benutzer """
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute("""
        INSERT INTO users (first_name, last_name, email, address_id, gender, birth_date)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    """, (first_name, last_name, email, address_id, gender, birth_date))

    return cursor.fetchone()[0]


def get_or_create_hobby(cursor, hobby_name):
    """ Holt oder erstellt ein Hobby """
    cursor.execute("SELECT id FROM hobbies WHERE name = %s", (hobby_name,))
    row = cursor.fetchone()
    if row:
        return row[0]

    cursor.execute("INSERT INTO hobbies (name) VALUES (%s) RETURNING id", (hobby_name,))
    return cursor.fetchone()[0]


def split_name_simple(name_str):
    """ Teilt 'Nachname, Vorname' in (Vorname, Nachname) """
    parts = name_str.split(",", 1)
    return (parts[1].strip(), parts[0].strip()) if len(parts) == 2 else ("", name_str.strip())


def split_name(name_str, email):
    """ Falls kein Name vorhanden ist, wird er aus der E-Mail-Adresse extrahiert """
    if name_str and "," in name_str:
        return split_name_simple(name_str)

    if "@" in email:
        local_part = email.split("@")[0]
        parts = local_part.split(".")
        return (parts[0].capitalize(), parts[1].capitalize()) if len(parts) > 1 else ("", local_part.capitalize())

    return ("", "")


def parse_address(addr_str):
    """ Zerlegt eine Adresse 'Straße Nr, PLZ Ort' in einzelne Felder """
    parts = [p.strip() for p in addr_str.split(",")]
    if len(parts) >= 3:
        street, house_no = parts[0].rsplit(" ", 1)
        return street, house_no, parts[1], parts[2]
    return None, None, None, None


def parse_date_ddmmYYYY(date_str):
    """ Wandelt '07.03.1959' in ein Datumsobjekt um """
    try:
        return datetime.strptime(date_str.strip(), "%d.%m.%Y").date()
    except:
        return None


if __name__ == "__main__":
    main()
