import sqlite3
import random
import re
from faker import Faker
from faker.providers import BaseProvider
from datetime import datetime, timedelta

# Provider personalizzato per ospedali
class HospitalProvider(BaseProvider):
    def hospital_name(self):
        prefixes = ['Ospedale', 'Clinica', 'Casa di Cura', 'Istituto', 'Policlinico']
        names = ['San Marco', 'Santa Lucia', 'Sant\'Andrea', 'San Giovanni', 'Sant\'Anna', 'Madonna della Salute', 'Cardinale Massaia']
        suffixes = ['di Milano', 'di Roma', 'di Napoli', 'di Torino', 'di Genova', 'Centrale', 'Generale', 'Universitario']
        return f"{random.choice(prefixes)} {random.choice(names)} {random.choice(suffixes)}"
    
    def city(self):
        cities = ['Milano', 'Roma', 'Napoli', 'Torino', 'Genova', 'Firenze', 'Bologna', 'Palermo', 'Catania', 'Venezia']
        return random.choice(cities)
    
    def region(self):
        regions = ['Lazio', 'Lombardia', 'Campania', 'Piemonte', 'Sicilia', 'Liguria', 'Emilia-Romagna', 'Toscana', 'Veneto', 'Sardegna']
        return random.choice(regions)

# Faker
fake = Faker("it_IT")
fake.add_provider(HospitalProvider)

# Parametri
marca_fissa = "quanta system"
modelli = [
    "cyber tm", "cyber ho 60", "cyber ho 100", "cyber ho 150",
    "fiber dust", "fiber dust pro",
    "cyber ho 100 Magneto", "cyber ho 150 Magneto",
    "litho", "litho evo", "opera evo"
]

sigle_modello = {
    "cyber tm": "CYT",
    "cyber ho 60": "CYH",
    "cyber ho 100": "CYH",
    "cyber ho 150": "CYH",
    "fiber dust": "TFL",
    "fiber dust pro": "TFN",
    "cyber ho 100 Magneto": "CYM",
    "cyber ho 150 Magneto": "CYM",
    "litho": "LHT",
    "litho evo": "LHV",
    "opera evo": "DNL"
}

# Connessione e creazione DB
conn = sqlite3.connect("laser.db")
cursor = conn.cursor()

# Elimina tutti i dati esistenti e resetta l'autoincremento
cursor.execute("DROP TABLE IF EXISTS laser")
conn.commit()

# Creazione nuova tabella con campo accessori incluso
cursor.execute("""
CREATE TABLE laser (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    marca TEXT,
    modello TEXT,
    codice_seriale TEXT UNIQUE,
    data_collaudo TEXT,
    data_manutenzione TEXT,
    locazione TEXT,
    stato TEXT,
    accessori TEXT
)
""")

def genera_seriale(sigla):
    numero1 = random.randint(1000, 9999)
    numero2 = random.randint(1000, 9999)
    return f"{sigla}{numero1}-{numero2}"

# Inserimento dati
for _ in range(200):
    modello = random.choice(modelli)
    sigla = sigle_modello[modello]
    seriale = genera_seriale(sigla)
    while not re.match(r"^(CYT|CYH|CYM|TFL|TFN|LHT|LHV|DNL)\d{4}-\d{4}$", seriale):
        seriale = genera_seriale(sigla)

    data_collaudo = fake.date_between(start_date="-5y", end_date="today")
    data_manutenzione = data_collaudo + timedelta(days=random.randint(100, 800))
    
    nome_clinica = fake.hospital_name()
    citta = fake.city()
    regione = fake.region()
    locazione = f"{nome_clinica} - {citta} ({regione})"

    stato = random.choice(["attivo", "in manutenzione", "fuori uso"])
    accessorio = f"00{random.randint(1000, 9999)}"

    cursor.execute("""
    INSERT INTO laser (marca, modello, codice_seriale, data_collaudo, data_manutenzione, locazione, stato, accessori)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        marca_fissa,
        modello,
        seriale,
        data_collaudo.strftime("%Y-%m-%d"),
        data_manutenzione.strftime("%Y-%m-%d"),
        locazione,
        stato,
        accessorio
    ))

conn.commit()
conn.close()
print("Database generato con successo: laser.db")
