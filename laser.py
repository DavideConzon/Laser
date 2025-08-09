#AGGIUNGERE POSSIBILITA' DI SELEZIONARE OGNI QUANTO LA MANUTENZIONE ALL'AGGIUNTA DEL LASER
#EVIDENZIARE CON VERSE-GIALLO-ROSSO LE DATE DI PROSSIMAMANUTENZIONE 
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QComboBox, QTextEdit, QHBoxLayout
from PyQt5.QtCore import Qt

import pandas as pd

import sqlite3
import re
import sys
from datetime import datetime, timedelta

import folium
from folium.map import Icon

import sqlite3
import webbrowser
import os

import subprocess



#PARTE CHE CREA I DATABASE E LANCIA GLI SCRIPT DI POPOLAMENTO
"""
# Ottieni la directory corrente del file laser.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# Lancia gli script nella stessa cartella
subprocess.run(['python', os.path.join(current_dir, 'popola_luoghi.py')])
subprocess.run(['python', os.path.join(current_dir, 'faker_laser.py')])
subprocess.run(['python', os.path.join(current_dir, 'popola_locazioni_da_luoghi.py')])
"""

# Connessione al database
conn = sqlite3.connect("laser.db")
cursor = conn.cursor()

# Assicuriamoci che esista la tabella laser
cursor.execute("""
    CREATE TABLE IF NOT EXISTS laser (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marca TEXT,
        modello TEXT,
        codice_seriale TEXT,
        data_collaudo TEXT,
        data_manutenzione TEXT,
        locazione TEXT,
        stato TEXT
    )
""")
conn.commit()

# Lista modelli
marca_fissa = "quanta system"
modelli = [
    "cyber tm", "cyber ho 60", "cyber ho 100", "cyber ho 150",
    "fiber dust", "fiber dust pro",
    "cyber ho 100 Magneto", "cyber ho 150 Magneto",
    "Litho", "Litho Evo",
    "opera evo"
]


#cursor.execute("DROP TABLE IF EXISTS manutenzioni")
#conn.commit()

# Creazione tabella per le manutenzioni
cursor.execute("""
    CREATE TABLE IF NOT EXISTS manutenzioni (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_laser INTEGER,
        data_manutenzione TEXT NOT NULL,
        tipo_manutenzione TEXT,
        tecnico TEXT,
        note TEXT,
        FOREIGN KEY(id_laser) REFERENCES laser(id)
    )
""")
conn.commit()

# Creazione tabella per le gare
cursor.execute("""
CREATE TABLE IF NOT EXISTS gara (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codice_seriale TEXT UNIQUE,
    ente TEXT,
    data_gara TEXT,
    numero_gara TEXT,
    note TEXT
)
""")
conn.commit()




"""Finestra per la registrazione di un laser"""
# Connessione al database principale
conn = sqlite3.connect("laser.db")
cursor = conn.cursor()

# Connessione a luoghi.db solo per uso interno
luoghi_db_path = "luoghi.db"
#"C:\Users\david\luoghi.db"
class AddLaserWindow(QtWidgets.QWidget):
    def __init__(self, parent, laser=None):
        super().__init__()
        self.parent = parent
        self.laser = laser
        self.setWindowTitle("Modifica Laser" if laser else "Aggiungi Laser")
        self.setGeometry(200, 150, 600, 500)

        import sqlite3
        self.conn_luoghi = sqlite3.connect('luoghi.db')

        container = QtWidgets.QVBoxLayout()
        titolo = QtWidgets.QLabel("Modifica Laser" if laser else "Aggiungi Nuovo Laser")
        titolo.setAlignment(QtCore.Qt.AlignCenter)
        titolo.setStyleSheet("font-size: 26px; font-weight: bold; margin-bottom: 20px;")
        container.addWidget(titolo)

        form_layout = QtWidgets.QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        self.modello_combo = QtWidgets.QComboBox()
        self.modello_combo.addItems(modelli)
        self.modello_combo.currentTextChanged.connect(self.aggiorna_seriale)

        self.seriale_entry = QtWidgets.QLineEdit()
        self.collaudo_entry = QtWidgets.QLineEdit()
        self.manutenzione_entry = QtWidgets.QLineEdit()
        self.locazione_entry = QtWidgets.QLineEdit()

        # Setup completamento automatico da luoghi.db - disabilitato perché usiamo lista suggerimenti personalizzata
        # self.completer = QtWidgets.QCompleter()
        # self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        # self.locazione_entry.setCompleter(self.completer)

        self.locazione_entry.textChanged.connect(self.aggiorna_suggerimenti_locazione)

        self.stato_combo = QtWidgets.QComboBox()
        self.stato_combo.addItems(["Attivo", "In manutenzione", "Fuori servizio"])

        # Campi gara
        self.ente_entry = QtWidgets.QLineEdit()
        self.data_gara_entry = QtWidgets.QLineEdit()
        self.numero_gara_entry = QtWidgets.QLineEdit()
        self.note_gara_entry = QtWidgets.QLineEdit()

        # Stili
        style_lineedit = """
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
        """
        style_combobox = """
            QComboBox {
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
        """
        for widget in [self.seriale_entry, self.collaudo_entry, self.manutenzione_entry,
                       self.locazione_entry, self.ente_entry, self.data_gara_entry,
                       self.numero_gara_entry, self.note_gara_entry]:
            widget.setStyleSheet(style_lineedit)

        self.modello_combo.setStyleSheet(style_combobox)
        self.stato_combo.setStyleSheet(style_combobox)

        # Aggiunta campi laser
        form_layout.addRow("Modello:", self.modello_combo)
        form_layout.addRow("Codice Seriale:", self.seriale_entry)
        form_layout.addRow("Data Collaudo (YYYY-MM-DD):", self.collaudo_entry)
        form_layout.addRow("Data Manutenzione (YYYY-MM-DD):", self.manutenzione_entry)
        form_layout.addRow("Locazione:", self.locazione_entry)
        form_layout.addRow("Stato:", self.stato_combo)

        # Aggiunta campi gara
        form_layout.addRow("Ente:", self.ente_entry)
        form_layout.addRow("Data Gara (YYYY-MM-DD):", self.data_gara_entry)
        form_layout.addRow("Numero Gara:", self.numero_gara_entry)
        form_layout.addRow("Note Gara:", self.note_gara_entry)

        container.addLayout(form_layout)

        # Lista suggerimenti per la locazione (invisibile di default)
        self.suggerimenti_list = QtWidgets.QListWidget()
        self.suggerimenti_list.hide()
        self.suggerimenti_list.setMaximumHeight(100)
        self.suggerimenti_list.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        container.addWidget(self.suggerimenti_list)

        # Collegamento selezione suggerimento
        self.suggerimenti_list.itemClicked.connect(self.seleziona_suggerimento)

        pulsanti = QtWidgets.QHBoxLayout()
        pulsanti.setSpacing(30)

        self.salva_btn = QtWidgets.QPushButton("💾 Salva")
        self.salva_btn.clicked.connect(self.salva_laser)

        self.indietro_btn = QtWidgets.QPushButton("↩️ Indietro")
        self.indietro_btn.clicked.connect(self.indietro)

        for btn in [self.salva_btn, self.indietro_btn]:
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    font-size: 16px;
                    border-radius: 10px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            pulsanti.addWidget(btn)

        container.addLayout(pulsanti)
        self.setLayout(container)
        self.showMaximized()

        if self.laser:
            self.carica_dati()

    def carica_dati(self):
        self.modello_combo.setCurrentText(self.laser[2])
        self.seriale_entry.setText(self.laser[3])
        self.collaudo_entry.setText(self.laser[4])
        self.manutenzione_entry.setText(self.laser[5])
        self.locazione_entry.setText(self.laser[6])
        self.stato_combo.setCurrentText(self.laser[7])

        # Carica dati gara se presenti
        cursor.execute("SELECT * FROM gara WHERE codice_seriale=?", (self.laser[3],))
        gara = cursor.fetchone()
        if gara:
            self.ente_entry.setText(gara[2])
            self.data_gara_entry.setText(gara[3])
            self.numero_gara_entry.setText(gara[4])
            self.note_gara_entry.setText(gara[5])

    def aggiorna_seriale(self, modello):
        modello = modello.lower()
        if "fiber dust" in modello and "pro" in modello:
            self.seriale_entry.setText("TFN")
        elif "fiber dust" in modello:
            self.seriale_entry.setText("TFL")
        elif "cyber ho" in modello and "magneto" in modello:
            self.seriale_entry.setText("CYM")
        elif "cyber ho" in modello:
            self.seriale_entry.setText("CYH")
        elif "cyber tm" in modello:
            self.seriale_entry.setText("CYT")
        elif "litho evo" in modello:
            self.seriale_entry.setText("LHV")
        elif "litho" in modello:
            self.seriale_entry.setText("LHT")
        elif "opera evo" in modello:
            self.seriale_entry.setText("DNL")

    def aggiorna_suggerimenti_locazione(self):
        testo_digitato = self.locazione_entry.text().strip()
        if not testo_digitato:
            self.suggerimenti_list.clear()
            self.suggerimenti_list.hide()
            return

        cursor_luoghi = self.conn_luoghi.cursor()
        cursor_luoghi.execute("SELECT nome_clinica FROM places WHERE nome_clinica LIKE ? LIMIT 10", (f"{testo_digitato}%",))
        risultati = cursor_luoghi.fetchall()

        self.suggerimenti_list.clear()
        if risultati:
            for r in risultati:
                self.suggerimenti_list.addItem(r[0])
            self.suggerimenti_list.show()
        else:
            self.suggerimenti_list.hide()

    def seleziona_suggerimento(self, item):
        self.locazione_entry.setText(item.text())
        self.suggerimenti_list.hide()

    def salva_laser(self):
        # Qui rimane il tuo codice salva_laser esistente (con eventuale correzione sul controllo luoghi)
        # Per esempio:
        import re
        modello = self.modello_combo.currentText()
        codice_seriale = self.seriale_entry.text().strip()
        data_collaudo = self.collaudo_entry.text().strip()
        data_manutenzione = self.manutenzione_entry.text().strip()
        locazione = self.locazione_entry.text().strip()
        stato = self.stato_combo.currentText()

        ente = self.ente_entry.text().strip()
        data_gara = self.data_gara_entry.text().strip()
        numero_gara = self.numero_gara_entry.text().strip()
        note = self.note_gara_entry.text().strip()

        if not all([modello, codice_seriale, data_collaudo, data_manutenzione, locazione, stato]):
            QtWidgets.QMessageBox.warning(self, "Attenzione", "Compila tutti i campi laser.")
            return

        # Verifica codice seriale duplicato
        if not self.laser:
            cursor.execute("SELECT COUNT(*) FROM laser WHERE codice_seriale=?", (codice_seriale,))
            if cursor.fetchone()[0] > 0:
                QtWidgets.QMessageBox.warning(self, "Attenzione", "Il numero di serie esiste già nel database.")
                return

        # Validazione codice seriale
        pattern = r"^(CYT|CYH|CYM|TFL|TFN|LHT|LHV|DNL)\d{4}-\d{4}$"
        if not re.match(pattern, codice_seriale):
            QtWidgets.QMessageBox.critical(self, "Errore", "Il codice seriale deve essere nel formato AAA1234-5678")
            return

        # Verifica locazione valida in luoghi.db
        cursor_luoghi = self.conn_luoghi.cursor()
        cursor_luoghi.execute("SELECT COUNT(*) FROM places WHERE nome_clinica=?", (locazione,))
        if cursor_luoghi.fetchone()[0] == 0:
            QtWidgets.QMessageBox.warning(self, "Attenzione", "La locazione inserita non è presente nel database luoghi.db.")
            return

        # Inserisci o aggiorna laser nel database laser.db
        if self.laser:
            cursor.execute("""
                UPDATE laser SET modello=?, codice_seriale=?, data_collaudo=?, data_manutenzione=?,
                locazione=?, stato=?
                WHERE id=?
            """, (modello, codice_seriale, data_collaudo, data_manutenzione, locazione, stato, self.laser[0]))
        else:
            cursor.execute("""
                INSERT INTO laser (modello, codice_seriale, data_collaudo, data_manutenzione, locazione, stato)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (modello, codice_seriale, data_collaudo, data_manutenzione, locazione, stato))
        conn.commit()

        # Gestione dati gara
        cursor.execute("SELECT COUNT(*) FROM gara WHERE codice_seriale=?", (codice_seriale,))
        if cursor.fetchone()[0] > 0:
            cursor.execute("""
                UPDATE gara SET ente=?, data_gara=?, numero_gara=?, note=?
                WHERE codice_seriale=?
            """, (ente, data_gara, numero_gara, note, codice_seriale))
        else:
            cursor.execute("""
                INSERT INTO gara (codice_seriale, ente, data_gara, numero_gara, note)
                VALUES (?, ?, ?, ?, ?)
            """, (codice_seriale, ente, data_gara, numero_gara, note))
        conn.commit()

        QtWidgets.QMessageBox.information(self, "Successo", "Laser salvato correttamente.")
        self.parent.aggiorna_lista_laser()
        #self.close()

    
    def aggiorna_lista_laser(self):
        # Supponiamo tu abbia una QTableWidget o QListWidget per mostrare i laser
        # Qui svuoti e ricarichi i dati dal DB aggiornato
        self.lista_laser.clear()
        cursor.execute("SELECT * FROM laser ORDER BY modello")
        laser = cursor.fetchall()
        for l in laser:
            # aggiungi gli elementi alla tua lista (modifica in base al widget usato)
            self.lista_laser.addItem(f"{l[2]} - {l[3]}")

    def indietro(self):
        self.close()
        self.parent.show()

    def closeEvent(self, event):
        # Chiude la connessione al database luoghi.db quando si chiude la finestra
        self.conn_luoghi.close()
        event.accept()




"""Finestra principale per visualizzare i laser"""
class VisualizzaLaserWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Elenco Laser")
        self.setGeometry(100, 100, 1200, 600)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(20)

        titolo = QtWidgets.QLabel("Elenco Laser Installati")
        titolo.setAlignment(QtCore.Qt.AlignCenter)
        titolo.setStyleSheet("font-size: 26px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(titolo)

        self.filtro_entry = QtWidgets.QLineEdit()
        self.filtro_entry.setPlaceholderText("🔍 Cerca per modello, seriale o locazione...")
        self.filtro_entry.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        self.filtro_entry.textChanged.connect(self.aggiorna_tabella)
        layout.addWidget(self.filtro_entry)

        self.tabella = QtWidgets.QTableWidget()
        self.tabella.setColumnCount(10)
        self.tabella.setHorizontalHeaderLabels([
            "ID", "Marca", "Modello", "Seriale", "Collaudo", "Manutenzione",
            "Prossima Manutenzione", "Locazione", "Stato", "Accessorio"
        ])
        self.tabella.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.tabella.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                font-size: 13px;
                gridline-color: #ccc;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.tabella)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(20)

        self.modifica_btn = QtWidgets.QPushButton("✏️ Modifica selezionato")
        self.elimina_btn = QtWidgets.QPushButton("🗑️ Elimina selezionato")
        self.indietro_btn = QtWidgets.QPushButton("↩️ Indietro")

        for btn in [self.modifica_btn, self.elimina_btn, self.indietro_btn]:
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    font-size: 15px;
                    border-radius: 10px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn_layout.addWidget(btn)

        self.modifica_btn.clicked.connect(self.modifica_laser)
        self.elimina_btn.clicked.connect(self.elimina_laser)
        self.indietro_btn.clicked.connect(self.torna_indietro)

        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.showMaximized()
        self.aggiorna_tabella()


    def aggiorna_tabella(self):
        filtro = self.filtro_entry.text()
        query = "SELECT * FROM laser WHERE modello LIKE ? OR codice_seriale LIKE ? OR locazione LIKE ?"
        wildcard = f"%{filtro}%"
        cursor.execute(query, (wildcard, wildcard, wildcard))
        risultati = cursor.fetchall()

        self.tabella.setRowCount(len(risultati))
        for riga_idx, riga in enumerate(risultati):
            # Inserisci le prime 6 colonne (fino a 'data_manutenzione')
            for col_idx in range(6):
                self.tabella.setItem(riga_idx, col_idx, QtWidgets.QTableWidgetItem(str(riga[col_idx])))

            # Calcola la prossima manutenzione (colonna 6)
            data_manutenzione_str = riga[5]  # data_manutenzione
            try:
                data_manutenzione = datetime.strptime(data_manutenzione_str, "%Y-%m-%d")
                prossima_manutenzione = data_manutenzione + timedelta(days=365)
                prossima_manutenzione_str = prossima_manutenzione.strftime("%Y-%m-%d")
            except Exception:
                prossima_manutenzione_str = "N/A"
            self.tabella.setItem(riga_idx, 6, QtWidgets.QTableWidgetItem(prossima_manutenzione_str))

            # Colonne successive: locazione (7), stato (8), accessorio (9)
            for offset, valore in enumerate(riga[6:], start=7):
                self.tabella.setItem(riga_idx, offset, QtWidgets.QTableWidgetItem(str(valore)))

        self.tabella.resizeColumnsToContents()



    def modifica_laser(self):
        selected = self.tabella.currentRow()
        if selected >= 0:
            id_laser = int(self.tabella.item(selected, 0).text())
            cursor.execute("SELECT * FROM laser WHERE id=?", (id_laser,))
            laser = cursor.fetchone()
            self.hide()
            self.modifica_window = AddLaserWindow(self, laser)
            self.modifica_window.show()

    def elimina_laser(self):
        selected = self.tabella.currentRow()
        if selected >= 0:
            id_laser = int(self.tabella.item(selected, 0).text())
            conferma = QtWidgets.QMessageBox.question(self, "Conferma", "Sei sicuro di voler eliminare questo laser?",
                                                      QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if conferma == QtWidgets.QMessageBox.Yes:
                cursor.execute("DELETE FROM laser WHERE id=?", (id_laser,))
                conn.commit()
                self.aggiorna_tabella()

    def torna_indietro(self):
        self.close()
        self.parent.show()


"""Finestra per la gestione delle manutenzioni"""
class GestioneManutenzioniWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Gestione Manutenzioni")
        self.setGeometry(100, 100, 800, 600)
        self.laser_corrente = None

        container = QtWidgets.QVBoxLayout()

        # Titolo
        titolo = QtWidgets.QLabel("Gestione Manutenzioni")
        titolo.setAlignment(QtCore.Qt.AlignCenter)
        titolo.setStyleSheet("font-size: 26px; font-weight: bold; margin-bottom: 20px;")
        container.addWidget(titolo)

        # === Ricerca Laser ===
        ricerca_group = QtWidgets.QGroupBox("Ricerca Laser")
        ricerca_layout = QtWidgets.QFormLayout()
        ricerca_layout.setVerticalSpacing(15)
        ricerca_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        self.search_field = QtWidgets.QLineEdit()
        self.regione_field = QtWidgets.QLineEdit()

        style_lineedit = """
            QLineEdit {
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
        """
        self.search_field.setStyleSheet(style_lineedit)
        self.regione_field.setStyleSheet(style_lineedit)

        self.search_button = QtWidgets.QPushButton("🔍 Cerca per Seriale")
        self.regione_button = QtWidgets.QPushButton("📍 Filtra per Regione")
        for btn in [self.search_button, self.regione_button]:
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    font-size: 16px;
                    border-radius: 10px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)

        self.search_button.clicked.connect(self.ricerca_laser)
        self.regione_button.clicked.connect(self.filtra_laser_per_regione)

        ricerca_layout.addRow("Seriale:", self.search_field)
        ricerca_layout.addRow("", self.search_button)
        ricerca_layout.addRow("Regione:", self.regione_field)
        ricerca_layout.addRow("", self.regione_button)
        ricerca_group.setLayout(ricerca_layout)
        container.addWidget(ricerca_group)

        # === Tabella ===
        self.tabella = QtWidgets.QTableWidget()
        self.tabella.setColumnCount(5)
        self.tabella.setHorizontalHeaderLabels(["ID Laser", "Modello", "Data Manutenzione", "Tecnico", "Note"])
        self.tabella.horizontalHeader().setStretchLastSection(True)
        self.tabella.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                font-weight: bold;
                border: 1px solid #ccc;
            }
        """)
        container.addWidget(self.tabella)

        # === Sezione Dettagli Manutenzione ===
        dettagli_group = QtWidgets.QGroupBox("Aggiungi / Modifica Manutenzione")
        dettagli_layout = QtWidgets.QFormLayout()
        dettagli_layout.setVerticalSpacing(15)
        dettagli_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        self.tecnico_input = QtWidgets.QLineEdit()
        self.note_input = QtWidgets.QTextEdit()
        self.data_manutenzione_input = QtWidgets.QDateEdit()
        self.data_manutenzione_input.setDate(QtCore.QDate.currentDate())
        self.data_manutenzione_input.setCalendarPopup(True)

        style_textedit = """
            QTextEdit {
                border: 2px solid #ccc;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
        """
        self.tecnico_input.setStyleSheet(style_lineedit)
        self.note_input.setStyleSheet(style_textedit)
        self.data_manutenzione_input.setStyleSheet(style_lineedit)

        dettagli_layout.addRow("Tecnico:", self.tecnico_input)
        dettagli_layout.addRow("Note:", self.note_input)
        dettagli_layout.addRow("Data Manutenzione:", self.data_manutenzione_input)
        dettagli_group.setLayout(dettagli_layout)
        container.addWidget(dettagli_group)

        # === Pulsanti Azione ===
        pulsanti_layout = QtWidgets.QHBoxLayout()
        pulsanti_layout.setSpacing(30)

        self.aggiungi_btn = QtWidgets.QPushButton("💾 Salva")
        self.elimina_btn = QtWidgets.QPushButton("🗑️ Elimina")
        self.indietro_btn = QtWidgets.QPushButton("↩️ Indietro")

        for btn in [self.aggiungi_btn, self.elimina_btn, self.indietro_btn]:
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    font-size: 16px;
                    border-radius: 10px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            pulsanti_layout.addWidget(btn)

        container.addLayout(pulsanti_layout)

        self.setLayout(container)
        self.showMaximized()

         # === Collegamenti Funzioni ===
        self.aggiungi_btn.clicked.connect(self.aggiungi_o_salva_manutenzione)
        self.elimina_btn.clicked.connect(self.elimina_manutenzione)
        self.indietro_btn.clicked.connect(self.torna_indietro)
     


    def filtra_laser_per_regione(self):
        regione = self.regione_field.text()
        if regione:
            try:
                conn = sqlite3.connect('laser.db')
                cur = conn.cursor()

                # Esegui la query per filtrare per regione
                cur.execute("SELECT id, codice_seriale, marca, modello, data_collaudo, locazione, stato FROM laser WHERE locazione LIKE ?", ('%' + regione + '%',))

                risultati = cur.fetchall()

                if risultati:
                    self.tabella.setRowCount(0)
                    for laser in risultati:
                        row_position = self.tabella.rowCount()
                        self.tabella.insertRow(row_position)
                        self.tabella.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(laser[0])))
                        self.tabella.setItem(row_position, 1, QtWidgets.QTableWidgetItem(laser[3]))  # modello
                        self.tabella.setItem(row_position, 2, QtWidgets.QTableWidgetItem(str(laser[4])))  # data collaudo
                        self.tabella.setItem(row_position, 3, QtWidgets.QTableWidgetItem(laser[5]))  # locazione
                        self.tabella.setItem(row_position, 4, QtWidgets.QTableWidgetItem(laser[6]))  # stato
                else:
                    QtWidgets.QMessageBox.warning(self, "Nessun risultato", f"Nessun laser trovato per la regione {regione}.")
            except sqlite3.Error as e:
                QtWidgets.QMessageBox.critical(self, "Errore di connessione", f"Errore durante l'accesso al database: {e}")
            finally:
                conn.close()
        else:
            QtWidgets.QMessageBox.warning(self, "Errore", "Inserisci una regione per filtrare.")

    def ricerca_laser(self):
        seriale = self.search_field.text()
        if seriale:
            laser = self.cerca_laser_per_seriale(seriale)
            if laser:
                self.laser_corrente = laser
                self.visualizza_manutenzioni(laser)
            else:
                QtWidgets.QMessageBox.warning(self, "Errore", "Laser non trovato.")
        else:
            QtWidgets.QMessageBox.warning(self, "Errore", "Inserisci un seriale valido.")

    def cerca_laser_per_seriale(self, codice_seriale):
        conn = sqlite3.connect('laser.db')
        cursor = conn.cursor()

        cursor.execute("""SELECT id, codice_seriale, marca, modello, data_collaudo, locazione, stato FROM laser WHERE codice_seriale = ?""", (codice_seriale,))

        laser = cursor.fetchone()
        conn.close()

        if laser:
            return {
                'id_laser': laser[0],
                'codice_seriale': laser[1],
                'marca': laser[2],
                'modello': laser[3],
                'data_collaudo': laser[4],
                'locazione': laser[5],
                'stato': laser[6]
            }
        return None

    def visualizza_manutenzioni(self, laser):
        id_laser = laser['id_laser']
        manutenzioni = self.cerca_manutenzioni_per_id_laser(id_laser)

        self.tabella.setRowCount(0)
        self.tabella.setColumnCount(5)
        self.tabella.setHorizontalHeaderLabels(["ID", "Modello", "Data Manutenzione", "Tecnico", "Note"])

        if manutenzioni:
            for manutenzione in manutenzioni:
                row_position = self.tabella.rowCount()
                self.tabella.insertRow(row_position)
                self.tabella.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(manutenzione[0])))  # ID manutenzione
                self.tabella.setItem(row_position, 1, QtWidgets.QTableWidgetItem(laser['modello']))
                self.tabella.setItem(row_position, 2, QtWidgets.QTableWidgetItem(str(manutenzione[1])))
                self.tabella.setItem(row_position, 3, QtWidgets.QTableWidgetItem(manutenzione[2]))
                self.tabella.setItem(row_position, 4, QtWidgets.QTableWidgetItem(manutenzione[3]))


    def aggiungi_o_salva_manutenzione(self):
        if not self.laser_corrente:
            QtWidgets.QMessageBox.warning(self, "Errore", "Nessun laser selezionato.")
            return

        id_laser = self.laser_corrente['id_laser']
        tecnico = self.tecnico_input.text()
        note = self.note_input.toPlainText()
        data = self.data_manutenzione_input.date().toString('yyyy-MM-dd')

        if not tecnico or not note:
            QtWidgets.QMessageBox.warning(self, "Attenzione", "Compila tutti i campi.")
            return

        try:
            conn = sqlite3.connect("laser.db")
            cursor = conn.cursor()

            cursor.execute(""" 
                INSERT INTO manutenzioni (id_laser, data_manutenzione, tecnico, note) 
                VALUES (?, ?, ?, ?)
            """, (id_laser, data, tecnico, note))
            conn.commit()

            QtWidgets.QMessageBox.information(self, "Successo", "Manutenzione aggiunta con successo.")
        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(self, "Errore", f"Errore durante il salvataggio: {e}")
        finally:
            conn.close()

    def elimina_manutenzione(self):
        selected = self.tabella.currentRow()
        if selected >= 0:
            item = self.tabella.item(selected, 0)
            if item is None:
                QtWidgets.QMessageBox.warning(self, "Attenzione", "Seleziona una manutenzione valida.")
                return
            try:
                id_manutenzione = int(item.text())  # Prima colonna: ID manutenzione
            except ValueError:
                QtWidgets.QMessageBox.warning(self, "Attenzione", "ID manutenzione non valido.")
                return

            conferma = QtWidgets.QMessageBox.question(
                self, "Conferma eliminazione",
                "Sei sicuro di voler eliminare questa manutenzione?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if conferma == QtWidgets.QMessageBox.Yes:
                try:
                    conn = sqlite3.connect("laser.db")
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM manutenzioni WHERE id=?", (id_manutenzione,))
                    conn.commit()
                    QtWidgets.QMessageBox.information(self, "Eliminato", "Manutenzione eliminata con successo.")
                    self.visualizza_manutenzioni(self.laser_corrente)  # ricarica
                except sqlite3.Error as e:
                    QtWidgets.QMessageBox.critical(self, "Errore", f"Errore durante l'eliminazione: {e}")
                finally:
                    conn.close()
        else:
            QtWidgets.QMessageBox.warning(self, "Attenzione", "Seleziona una manutenzione da eliminare.")



    
    def aggiorna_tabella(self):
        filtro = self.filtro_entry.text()
        regione = self.regione_field.text()
        if filtro:
            query = "SELECT * FROM laser WHERE (modello LIKE ? OR codice_seriale LIKE ? OR locazione LIKE ?)"
            wildcard = f"%{filtro}%"
        elif regione:
            query = "SELECT * FROM laser WHERE locazione LIKE ?"
            wildcard = f"%{regione}%"
        else:
            query = "SELECT * FROM laser"
            wildcard = '%'
        cursor.execute(query, (wildcard, wildcard, wildcard))
        risultati = cursor.fetchall()

        self.tabella.setRowCount(len(risultati))
        for riga_idx, riga in enumerate(risultati):
            for col_idx, valore in enumerate(riga):
                self.tabella.setItem(riga_idx, col_idx, QtWidgets.QTableWidgetItem(str(valore)))
        self.tabella.resizeColumnsToContents()

    def cerca_manutenzioni_per_id_laser(self, id_laser):
        try:
            conn = sqlite3.connect("laser.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, data_manutenzione, tecnico, note 
                FROM manutenzioni 
                WHERE id_laser = ? 
                ORDER BY data_manutenzione DESC
            """, (id_laser,))
            manutenzioni = cursor.fetchall()
            return manutenzioni
        except sqlite3.Error as e:
            QtWidgets.QMessageBox.critical(self, "Errore", f"Errore durante la lettura delle manutenzioni: {e}")
            return []
        finally:
            conn.close()


    def torna_indietro(self):
        self.close()
        self.parent.show()



"""Finestra per la risoluzione dei problemi del laser"""
class TroubleshootingWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent  # Salvo la finestra chiamante
        
        self.setWindowTitle("Troubleshooting Laser")
        self.setGeometry(200, 150, 700, 500)

        container = QtWidgets.QVBoxLayout()
        
        # Titolo
        titolo = QtWidgets.QLabel("Risoluzione Problemi Laser")
        titolo.setAlignment(QtCore.Qt.AlignCenter)
        titolo.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px; color: #2c3e50;")
        container.addWidget(titolo)

        # Form Layout
        form_layout = QtWidgets.QFormLayout()
        form_layout.setVerticalSpacing(20)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight)

        # ComboBox Modello
        self.model_selector = QtWidgets.QComboBox()
        self.model_selector.currentTextChanged.connect(self.load_problems)
        self.model_selector.setStyleSheet(self._combo_style())

        # ComboBox Problema
        self.problem_selector = QtWidgets.QComboBox()
        self.problem_selector.currentTextChanged.connect(self.show_details)
        self.problem_selector.setStyleSheet(self._combo_style())

        form_layout.addRow("Seleziona modello laser:", self.model_selector)
        form_layout.addRow("Seleziona problema:", self.problem_selector)

        container.addLayout(form_layout)

        # Testo Causa
        self.cause_label = QtWidgets.QLabel("Causa:")
        self.cause_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 20px;")
        self.cause_text = QtWidgets.QTextEdit()
        self.cause_text.setReadOnly(True)
        self.cause_text.setStyleSheet(self._textedit_style())

        # Testo Soluzione
        self.solution_label = QtWidgets.QLabel("Soluzione:")
        self.solution_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-top: 20px;")
        self.solution_text = QtWidgets.QTextEdit()
        self.solution_text.setReadOnly(True)
        self.solution_text.setStyleSheet(self._textedit_style())

        container.addWidget(self.cause_label)
        container.addWidget(self.cause_text)
        container.addWidget(self.solution_label)
        container.addWidget(self.solution_text)

        # Pulsanti Chiudi e Indietro
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()

        # Pulsante Indietro
        self.indietro_btn = QtWidgets.QPushButton("↩️ Indietro")
        self.indietro_btn.setMinimumHeight(40)
        self.indietro_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                border-radius: 10px;
                padding: 10px 30px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.indietro_btn.clicked.connect(self.torna_indietro)
        btn_layout.addWidget(self.indietro_btn)

        # Pulsante Chiudi
        self.close_btn = QtWidgets.QPushButton("Chiudi")
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setMinimumHeight(40)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
                border-radius: 10px;
                padding: 10px 30px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_layout.addWidget(self.close_btn)

        container.addLayout(btn_layout)

        self.setLayout(container)
        self.showMaximized()

        # Caricamento dati excel
        base_path = os.path.dirname(os.path.abspath(__file__))
        excel_path = os.path.join(base_path, "troubleshooting.xlsx")

        try:
            self.troubleshooting_data = pd.read_excel(excel_path, sheet_name=None)
            # Pulizia preliminare: rimuove spazi dalle colonne e normalizza testo
            for k, df in self.troubleshooting_data.items():
                df.columns = df.columns.str.strip()
                for col in ['PROBLEMA', 'CAUSA', 'SOLUZIONE']:
                    if col in df.columns:
                        df[col] = df[col].astype(str).str.strip().replace('nan', '')
                    else:
                        # Se manca una colonna, creala vuota
                        df[col] = ''
                self.troubleshooting_data[k] = df
            self.model_selector.addItems(self.troubleshooting_data.keys())
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Errore", f"Errore nel caricamento del file troubleshooting.xlsx:\n{str(e)}")
            self.troubleshooting_data = {}

    def load_problems(self, model):
        self.problem_selector.clear()
        self.cause_text.clear()
        self.solution_text.clear()

        if model in self.troubleshooting_data:
            self.current_df = self.troubleshooting_data[model]
            # Prendi problemi unici, rimuovendo eventuali spazi bianchi e stringhe vuote
            problemi = self.current_df["PROBLEMA"].dropna().astype(str).str.strip()
            problemi = problemi[problemi != ''].unique().tolist()
            self.problem_selector.addItems(problemi)

    def show_details(self, problema):
        if hasattr(self, "current_df") and problema:
            # Normalizza problema cercato
            problema_norm = problema.strip()
            # Cerca la riga ignorando spazi e minuscole
            df = self.current_df.copy()
            df['PROBLEMA_clean'] = df['PROBLEMA'].astype(str).str.strip()
            entry = df[df['PROBLEMA_clean'] == problema_norm]
            if not entry.empty:
                causa = entry.iloc[0]["CAUSA"]
                soluzione = entry.iloc[0]["SOLUZIONE"]
                self.cause_text.setText(str(causa))
                self.solution_text.setText(str(soluzione))
            else:
                self.cause_text.clear()
                self.solution_text.clear()

    # Resto della classe invariato
    def _combo_style(self):
        return """
            QComboBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                padding: 6px;
                font-size: 15px;
                min-width: 250px;
                color: #2c3e50;
            }
            QComboBox:hover {
                border-color: #2980b9;
            }
            QComboBox:focus {
                border-color: #1abc9c;
            }
        """

    def _textedit_style(self):
        return """
            QTextEdit {
                border: 2px solid #95a5a6;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #ecf0f1;
                color: #2c3e50;
                min-height: 100px;
            }
        """

    def torna_indietro(self):
        self.close()
        if self.parent:
            self.parent.show()



""" Finestra per la gestione dei contratti di gara appalto """
class GestioneGaraWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Gestione Contratti di Gara")
        self.setGeometry(100, 100, 800, 600)

        layout_principale = QtWidgets.QVBoxLayout()
        layout_principale.setSpacing(20)
        layout_principale.setContentsMargins(40, 40, 40, 40)

        titolo = QtWidgets.QLabel("📄 Contratti di Gara Appalto")
        titolo.setAlignment(QtCore.Qt.AlignCenter)
        titolo.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 30px;")
        layout_principale.addWidget(titolo)

        # Campo ricerca per codice seriale
        self.input_codice_seriale = QtWidgets.QLineEdit()
        self.input_codice_seriale.setPlaceholderText("Inserisci codice seriale laser")
        self.input_codice_seriale.setStyleSheet("padding: 12px; font-size: 16px;")
        layout_principale.addWidget(self.input_codice_seriale)

        self.btn_cerca = QtWidgets.QPushButton("🔍 Cerca Contratto")
        self.btn_cerca.setStyleSheet("font-size: 18px; padding: 12px;")
        self.btn_cerca.clicked.connect(self.cerca_gara)
        layout_principale.addWidget(self.btn_cerca)

        # QLabel per mostrare i risultati della ricerca
        self.risultato_label = QtWidgets.QLabel("")
        self.risultato_label.setWordWrap(True)
        self.risultato_label.setStyleSheet("font-size: 16px; margin-top: 20px;")
        layout_principale.addWidget(self.risultato_label)

        # Pulsante Indietro
        self.btn_indietro = QtWidgets.QPushButton("🔙 Indietro")
        self.btn_indietro.setStyleSheet(
            "font-size: 18px; padding: 12px; background-color: #e74c3c; color: white;"
        )
        self.btn_indietro.clicked.connect(self.torna_indietro)
        layout_principale.addWidget(self.btn_indietro)

        self.setLayout(layout_principale)
        self.showMaximized()

    def cerca_gara(self):
        codice_seriale = self.input_codice_seriale.text().strip()
        if not codice_seriale:
            self.risultato_label.setText("⚠️ Inserisci un codice seriale.")
            return

        conn = sqlite3.connect("laser.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ente, data_gara, numero_gara, note FROM gara WHERE codice_seriale=?",
            (codice_seriale,),
        )
        risultato = cursor.fetchone()
        conn.close()

        if risultato:
            ente, data_gara, numero_gara, note = risultato
            self.risultato_label.setText(f"""
                <b>Ente:</b> {ente}<br>
                <b>Data Gara:</b> {data_gara}<br>
                <b>Numero Gara:</b> {numero_gara}<br>
                <b>Note:</b> {note}
            """)
        else:
            self.risultato_label.setText("⚠️ Nessuna gara trovata per questo codice seriale.")

    def torna_indietro(self):
        self.close()
        if self.parent:
            self.parent.show()




""" Funzione per mostrare la mappa con le cliniche e i laser """
def mostra_mappa():
    

    conn_luoghi = sqlite3.connect("luoghi.db")
    cursor_luoghi = conn_luoghi.cursor()

    conn_laser = sqlite3.connect("laser.db")
    cursor_laser = conn_laser.cursor()

    cursor_luoghi.execute("SELECT nome_clinica, luogo, latitudine, longitudine, regione FROM places")
    cliniche = cursor_luoghi.fetchall()

    cursor_laser.execute("SELECT codice_seriale, locazione, stato FROM laser")
    laser_dati = cursor_laser.fetchall()

    conn_luoghi.close()
    conn_laser.close()

    # Normalizziamo i nomi cliniche da luoghi.db in minuscolo senza spazi iniziali/finali
    cliniche_norm = [(nome.strip().lower(), lat, lon, regione) for nome, _, lat, lon, regione in cliniche]

    # Raggruppiamo i laser per locazione (minuscolo e stripped)
    laser_per_locazione = {}
    for seriale, locazione, stato in laser_dati:
        if locazione:
            key = locazione.strip().lower()
            if key not in laser_per_locazione:
                laser_per_locazione[key] = []
            laser_per_locazione[key].append((seriale, stato))

    print(f"Laser locazioni totali: {len(laser_per_locazione)}")

    mappa = folium.Map(location=[42.5, 12.5], zoom_start=6)

    cliniche_mostrate = 0
    # Per ogni clinica, cerchiamo se la sua stringa appare **dentro** qualche locazione laser
    for nome_clinica, lat, lon, regione in cliniche_norm:
        if lat is not None and lon is not None:
            laser_trovati = []
            for locazione_key, laser_list in laser_per_locazione.items():
                if nome_clinica in locazione_key:
                    laser_trovati.extend(laser_list)

            if not laser_trovati:
                print(f"Nessun laser per la clinica '{nome_clinica}'")
                continue

            popup_html = f"<strong>{nome_clinica.title()}</strong><br>{regione}<br><br>"

            for seriale, stato in laser_trovati:
                colore = {
                    "attivo": "green",
                    "in manutenzione": "orange",
                    "fuori uso": "red"
                }.get(stato.strip().lower(), "gray")

                emoji = {
                    "green": "🟢",
                    "orange": "🟡",
                    "red": "🔴",
                    "gray": "⚪"
                }[colore]

                popup_html += f"{emoji} <b>{seriale}</b> – {stato}<br>"

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(mappa)

            cliniche_mostrate += 1

    print(f"Cliniche mostrate sulla mappa: {cliniche_mostrate}")

    mappa_path = os.path.abspath("mappa_laser.html")
    mappa.save(mappa_path)

    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    webbrowser.get(f'"{edge_path}" %s').open("file://" + mappa_path)



""" Classe principale dell'applicazione """
class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestione Laser Chirurgici")
        self.setGeometry(100, 100, 800, 600)

        # Layout principale
        layout_principale = QtWidgets.QVBoxLayout()

        titolo = QtWidgets.QLabel("Dashboard Gestione Laser")
        titolo.setAlignment(QtCore.Qt.AlignCenter)
        titolo.setStyleSheet("font-size: 32px; font-weight: bold; margin-bottom: 30px;")
        layout_principale.addWidget(titolo)

        # Layout pulsanti in griglia
        griglia = QtWidgets.QGridLayout()
        griglia.setSpacing(30)

        self.add_button = QtWidgets.QPushButton("➕ Aggiungi Laser")
        self.view_button = QtWidgets.QPushButton("📋 Visualizza Laser")
        self.manutenzione_button = QtWidgets.QPushButton("🔧 Manutenzioni")
        self.troubleshooting_button = QtWidgets.QPushButton("❓ Troubleshooting")
        self.btn_mappa = QtWidgets.QPushButton("🗺️ Mappa Laser")
        self.contratti_button = QtWidgets.QPushButton("📄 Contratti Gara Appalto")  
        self.quit_button = QtWidgets.QPushButton("⏻ Esci")

        pulsanti = [
            (self.add_button, 0, 0),
            (self.view_button, 0, 1),
            (self.manutenzione_button, 1, 0),
            (self.troubleshooting_button, 2, 0),
            (self.btn_mappa, 1, 1),
            (self.contratti_button, 2, 1),
            (self.quit_button, 3, 0, 1, 2)
        ]

        for widget, row, col, *span in pulsanti:
            widget.setMinimumHeight(80)
            if span:
                griglia.addWidget(widget, row, col, *span)
            else:
                griglia.addWidget(widget, row, col)

        layout_principale.addLayout(griglia)
        self.setLayout(layout_principale)

        # Collegamenti
        self.add_button.clicked.connect(self.apri_add_laser_window)
        self.view_button.clicked.connect(self.apri_visualizza_laser_window)
        self.manutenzione_button.clicked.connect(self.apri_manutenzione_window)
        self.troubleshooting_button.clicked.connect(self.apri_troubleshooting_window)
        self.btn_mappa.clicked.connect(mostra_mappa)
        self.contratti_button.clicked.connect(self.apri_gara_window)
        self.quit_button.clicked.connect(self.close)

        # Stile moderno
        self.app = QtWidgets.QApplication.instance()
        self.app.setStyleSheet("""
            QWidget {
                background-color: #f2f2f2;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 20px;
                padding: 20px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLabel {
                color: #2c3e50;
            }
        """)

        self.showMaximized()

    def apri_add_laser_window(self):
        self.hide()
        self.add_window = AddLaserWindow(self)
        self.add_window.show()

    def apri_visualizza_laser_window(self):
        self.hide()
        self.view_window = VisualizzaLaserWindow(self)
        self.view_window.show()

    def apri_manutenzione_window(self):
        self.hide()
        self.manutenzione_window = GestioneManutenzioniWindow(self)
        self.manutenzione_window.show()

    def apri_troubleshooting_window(self):
        self.troubleshooting_window = TroubleshootingWindow(parent=self)
        self.troubleshooting_window.show()
        self.hide()

    def apri_gara_window(self):
        self.hide()
        self.gara_window = GestioneGaraWindow(self)
        self.gara_window.show()

    def aggiorna_tabella(self):
        try:
            self.view_window.aggiorna_tabella()
        except AttributeError:
            pass  # Se la finestra non è ancora stata aperta, non fare nulla

    def aggiorna_lista_laser(self):
        # Aggiorna la tabella nella finestra VisualizzaLaserWindow se aperta
        try:
            self.view_window.aggiorna_tabella()
        except AttributeError:
            pass



    
# Avvio dell'applicazione
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())

