# Datenschutz
## Welche Kategorien von Daten gibt es hier?
Hierbei geht es um **personenbezogene Daten**. <br>
Es gibt **allgemeine Daten** wie Name, Adresse, Telefonnummer, E-Mail-Adresse und Geschlecht.

Bei den vorliegenden Daten lässt sich nur die sexuelle Orientierung (Interessiert an) zu den **sensiblen Daten** zählen.

**Online Daten** wie IP-Adresse oder Standort werden nicht in der Datenbank erfasst. Ebenso auch keine **finanzilellen Daten**.

## Wie müssen die Daten geschützt werden?
Die personenbezogenen Daten müssen gemäß der DSGVO, die seit 2018 in der EU gilt, verarbeitet werden. <br>Das bedeutet, dass die folgenden Kernprinzipien eingehalten werden müssen
- Transparenz: Die Datenverarbeitung muss nachvollziehbar sein
- Zweckbindung: Die Daten dürfen nur für den vereinbarten Zweck verarbeitet werden
- Datenminimierung: Es dürfen nur so viele Daten gesammelt werden wie nötig
- Richtigkeit: Die Daten müssen Richtig und aktuell sein
- Löschfrist: Die Daten dürfen nur so lange gespeichert werden, wie vereinbart
- Integrität und Vertraulichkeit: Die Daten müssen vor Missbrauch, unbefugtem Zugriff, unbefugter Verarbeitung und Weitergabe geschützt sein

## Erforderliche Maßnahmen
- **Technische und organisatorische Maßnahmen** wie Verschlüsselung und die Sicherstellung der Vertraulichkeit, Integrität und Verfügbarkeit der bereitstellenden Systeme und Dienste
- **Mitarbeiterschulungen** damit ein Verständnis für Datenschutz und Datensicherheit geschaffen oder gefestigt werden kann
- **Sicherheitsmaßnahmen** wie Zugangskontrollen, Firewalls und Anti-Shcadsoftware Programme

## Vorraussetzungen für Datenspeicherung
Der Verantwortliche muss in der Lage sein nachzuweisen, dass die betroffenen Person zur Verarbeitung ihrer personenbezogenen Daten zugestimmt hat. <br>Diese Einwilligung muss in verständlicher und leicht zugänglicher Form in einer klaren und einfachen Sprache erfolgen. <br>
Eine Einwilligung kann jederzeit wiederrufen werden. Dies muss ebenfalls so einfach sein, wie die Erteilung der Einwilligung.

<br><br>

# SQL
## Tabellen erstellen

DROP TABLE IF EXISTS
    user_hobby_preferences,
    user_hobbies,
    friendships,
    messages,
    likes,
    conversations,
    user_photos,
    hobbies,
    users,
    addresses,
    user_images
CASCADE;

CREATE TABLE User (
    ID int NOT NULL PRIMARY KEY,
    Nachname varchar(1000),
    Vorname varchar(1000),
    Straße varchar(1000),
    Nr varchar(100),
    PLZ varchar(100),
    Ort varchar(1000),
    Hobby1 varchar(1000),
    Prio1 int,
    Hobby2 varchar(1000),
    Prio2 int,
    Hobby3 varchar(1000),
    Prio3 int,
    Hobby4 varchar(1000),
    Prio4 int,
    Hobby5 varchar(1000),
    Prio5 int,
    E-Mail varchar(1000),
    Geschlecht varchar(10),
    Interessiert_an varchar(10),
    Geburtsdatum DATE,
    createdAt DATETIME,
    updatedAt DATETIME,
    phone varchar(100),
    Image_ID int REFERENCES Image(ID)
)

CREATE TABLE Like (
    ID int NOT NULL PRIMARY KEY,
    User_ID int REFERENCES User(ID),
    liked_email varchar(1000),
    like_status varchar(100),
    like_timestamp DATETIME
)

CREATE TABLE Friendship (
    User_ID int REFERENCES User(ID),
    Friend_ID int REFERENCES User(ID)
)

CREATE TABLE Conversation (
    ID int NOT NULL PRIMARY KEY,
    receiver_email varchar(1000) REFERENCES User(E-Mail),
    user_email varchar(1000) REFERENCES User(E-Mail)
)

CREATE TABLE Message (
    ID int NOT NULL PRIMARY KEY,
    Content TEXT,
    timestamp DATETIME,
    Conversation_ID int
)

CREATE TABLE Hobby (
    ID int NOT NULL PRIMARY KEY,
    Content TEXT
)

CREATE TABLE User_Hobby (
    ID int NOT NULL PRIMARY KEY,
    User_ID int REFERENCES User(ID),
    Hobby_ID int REFERENCES Hobby(ID),
    priority int
)

CREATE TABLE Image (
    ID int NOT NULL PRIMARY KEY,
    data BLOB,
    link varchar(10000)
)

CREATE TABLE User_Image (
    Image_ID int REFERENCES Image(ID),
    User_ID int REFERENCES User(ID)
)