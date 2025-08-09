import sqlite3
import random

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Connessione al database SQLite
conn = sqlite3.connect('luoghi.db')

# Caricamento dei dati delle cliniche
df_cliniche = pd.read_sql_query("SELECT * FROM places", conn)

# Creazione della geometria dei punti
geometry = [Point(xy) for xy in zip(df_cliniche['longitudine'], df_cliniche['latitudine'])]
gdf_cliniche = gpd.GeoDataFrame(df_cliniche, geometry=geometry, crs="EPSG:4326")

# Caricamento del file GeoJSON dei comuni
gdf_comuni = gpd.read_file(r"C:\Users\david\comuni.geojson")

# Assicurarsi che entrambi i GeoDataFrame abbiano lo stesso sistema di riferimento
gdf_comuni = gdf_comuni.to_crs("EPSG:4326")

# Esecuzione del join spaziale per associare ogni clinica al comune corrispondente
gdf_joined = gpd.sjoin(gdf_cliniche, gdf_comuni, how="left", predicate="within")

# Aggiornamento della colonna 'regione' nel DataFrame originale
df_cliniche['comune'] = gdf_joined['name']  # Assicurati che 'name' sia il nome corretto del campo per il comune
df_cliniche['regione'] = gdf_joined['reg_name']  # Assicurati che 'reg_name' sia il nome corretto del campo per la regione

# Scrittura dei dati aggiornati nel database
df_cliniche.to_sql("places", conn, if_exists="replace", index=False)

conn.close()

# Connessione ai database
conn_luoghi = sqlite3.connect('luoghi.db')
cur_luoghi = conn_luoghi.cursor()

conn_laser = sqlite3.connect('laser.db')
cur_laser = conn_laser.cursor()

# Ottieni tutti i nomi delle cliniche, luoghi e regioni dal db luoghi
cur_luoghi.execute("SELECT nome_clinica, luogo, comune, regione FROM places")
cliniche = cur_luoghi.fetchall()

if not cliniche:
    print("⚠️ Nessuna clinica trovata nel database 'luoghi.db'.")
else:
    # Ottieni tutti gli ID dei laser esistenti
    cur_laser.execute("SELECT id FROM laser")
    laser_ids = [row[0] for row in cur_laser.fetchall()]

    for laser_id in laser_ids:
        nome_clinica, luogo, comune, regione = random.choice(cliniche)
        # Formattiamo la locazione come richiesto: "Clinica San Giovanni di Milano - Milano (Lombardia)"
        descrizione = f"{nome_clinica} - {comune} ({regione})"
        cur_laser.execute("UPDATE laser SET locazione = ? WHERE id = ?", (descrizione, laser_id))

    conn_laser.commit()
    print(f"✅ Popolazione completata con nome + comune + regione: {len(laser_ids)} locazioni aggiornate.")

# Chiudi le connessioni
conn_luoghi.close()
conn_laser.close()
