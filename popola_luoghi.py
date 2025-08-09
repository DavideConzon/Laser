import json
import sqlite3

# Parole chiave da includere nel nome
parole_chiave_valide = [
    "ospedale", "clinica", "istituto", "irccs", "casa di cura", 
    "san donato", "centro medico", "poliambulatorio", "universitario"
]

# Carica il file GeoJSON
with open(r'C:\Users\david\OneDrive\Desktop\progetto finale ITS\hotosm_ita_health_facilities_points_geojson\hotosm_ita_health_facilities_points_geojson.geojson', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Connessione al database
conn = sqlite3.connect('luoghi.db')
cur = conn.cursor()

# Opzionale: elimina i dati esistenti
cur.execute('DELETE FROM places')

count = 0
for feature in data['features']:
    props = feature['properties']
    geometry = feature['geometry']

    nome = props.get('name')
    luogo = props.get('addr:city') or props.get('addr:municipality') or props.get('addr:province') or "Sconosciuto"

    # Salta se mancano nome o coordinate
    if not nome or geometry is None or geometry['type'] != 'Point':
        continue

    # Confronto case-insensitive sul nome
    nome_lower = nome.lower()

    # Verifica se il nome contiene una parola chiave valida
    if not any(parola in nome_lower for parola in parole_chiave_valide):
        continue

    lon, lat = geometry['coordinates']

    try:
        cur.execute('''
            INSERT OR IGNORE INTO places (nome_clinica, luogo, latitudine, longitudine)
            VALUES (?, ?, ?, ?)
        ''', (nome, luogo, lat, lon))
        count += 1
    except Exception as e:
        print(f"Errore con {nome}: {e}")

# Salva e chiudi
conn.commit()
conn.close()

print(f"✅ Inseriti {count} luoghi sanitari filtrati nel database.")
