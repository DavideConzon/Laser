
# 🏥 Laser Fleet Manager


`Laser Fleet Manager` è un'applicazione desktop completa per la gestione e il monitoraggio di laser chirurgici installati in diverse strutture sanitarie italiane. Il programma, sviluppato in **Python**, offre un'interfaccia grafica intuitiva e un'architettura robusta per la gestione dei dispositivi, delle manutenzioni e per il supporto diagnostico.

Questo progetto dimostra una profonda comprensione del ciclo di vita del software, dalla generazione dei dati di test alla creazione di un'interfaccia utente funzionale e scalabile.

-----

## ✨ Caratteristiche principali

  * **GUI Interattiva (`PyQt5`):** Un'interfaccia utente dinamica e reattiva che permette di navigare facilmente tra le diverse sezioni del programma.
  * **Database a Bordo (`sqlite3`):** Gestione della persistenza dei dati dei laser, delle manutenzioni e dei contratti di gara in un database locale.
  * **Gestione Manutenzioni:** Tracciamento dettagliato delle manutenzioni passate e calcolo automatico della prossima scadenza.
  * **Troubleshooting Intelligente (`pandas`):** Una sezione dedicata che, partendo da un database di problemi/soluzioni in formato Excel, fornisce indicazioni diagnostiche per i vari modelli di laser.
  * **Localizzazione Geografica (`folium`):** Visualizzazione su mappa interattiva delle cliniche e dei laser installati, con pin colorati che ne indicano lo stato (attivo, in manutenzione, fuori servizio).
  * **Automazione dei Dati:** Script dedicati per la generazione di dati fittizi (`Faker`), l'integrazione di dati reali da GeoJSON e l'associazione delle locazioni ai laser.

-----

## 🛠️ Tecnologie e Librerie

  * **Linguaggio di Programmazione:** Python
  * **Interfaccia Grafica:** `PyQt5`
  * **Database:** `sqlite3`
  * **Gestione Dati:** `pandas`
  * **Visualizzazione su Mappa:** `folium`
  * **Dati Fittizi:** `Faker`
  * **Altro:** `subprocess`, `re`, `datetime`

-----

## 🚀 Setup e Avvio del Programma

Per avviare il programma, segui questi semplici passaggi. È necessario un ambiente virtuale per gestire le dipendenze.

### **1. Configurazione dell'ambiente**

1.  Assicurati di avere `Python` e `Git` installati.
2.  Apri il terminale e clona il repository:
    ```bash
    git clone https://github.com/DavideConzon/[Nome-del-tuo-repo].git
    cd [Nome-del-tuo-repo]
    ```
3.  Installa le dipendenze richieste:
    ```bash
    pip install -r requirements.txt
    ```

### **2. Inizializzazione dei database**

Esegui gli script in questo ordine per generare i dati di esempio e popolare i database `luoghi.db` e `laser.db`.

1.  **Popola i dati delle cliniche:**
    ```bash
    python popola_luoghi.py
    ```
2.  **Genera i dati dei laser fittizi:**
    ```bash
    python faker_laser.py
    ```
3.  **Associa i laser alle cliniche reali:**
    ```bash
    python popola_locazioni_da_luoghi.py
    ```

### **3. Avvio dell'applicazione**

Ora che i database sono pronti, puoi avviare il programma principale:

```bash
python laser.py
```

-----

## 🖼️ Screenshot

[Aggiungi uno screenshot o un video qui che mostri l'applicazione in azione. Se possibile, mostra la mappa e la sezione di troubleshooting.]

-----

## 💡 Contributi e Futuri Sviluppi

Il progetto è in continua evoluzione e sono aperti a contributi.

I prossimi passi includono:

  * Modularizzazione completa del codice per una maggiore scalabilità.
  * Implementazione di un sistema di routing con algoritmi come `Dijkstra` o `A*`.
  * Sviluppo di un sistema di troubleshooting più avanzato con tecniche di `Natural Language Processing` (NLP).
  * Funzionalità di esportazione dati (`PDF`/`Excel`).

-----

## ✍️ Autore

**DavideConzon**

  * **GitHub:** [https://github.com/DavideConzon](https://www.google.com/search?q=https://github.com/DavideConzon)
  * **LinkedIn:** [Link al tuo profilo LinkedIn]

-----

## ⚖️ Licenza

Questo progetto è rilasciato sotto licenza MIT.
