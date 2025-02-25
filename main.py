import sys
import os
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtCharts import *
import sqlite3
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('bfem.db')
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Table Jury
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS jury (
            id INTEGER PRIMARY KEY,
            region TEXT,
            departement TEXT,
            localite TEXT,
            centre_examen TEXT,
            president TEXT,
            telephone TEXT
        )
        ''')
        
        # Table Candidat
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidat (
            numero_table TEXT PRIMARY KEY,
            nom TEXT,
            prenom TEXT,
            date_naissance TEXT,
            lieu_naissance TEXT,
            sexe TEXT,
            nationnalite TEXT,
            epreuve_facultative TEXT,
            aptitude_sportive TEXT    
        )
        ''')

        # Table Livret Scolaire
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS livret_scolaire (
            numero_table TEXT PRIMARY KEY,
            tentatives INTEGER DEFAULT 1,
            moyenne_6e REAL,
            moyenne_5e REAL,
            moyenne_4e REAL,
            moyenne_3e REAL,
            moyenne_cycle REAL,
            FOREIGN KEY (numero_table) REFERENCES candidat (numero_table)
        )
        ''')
        self.conn.commit()
        
        # Table Notes Tour 1
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes_tour1 (
            numero_table TEXT PRIMARY KEY,
            compo_franc REAL,
            dictee REAL,
            etude_texte REAL,
            instruction_civique REAL,
            histoire_geo REAL,
            mathematiques REAL,
            pc_lv2 REAL,
            svt REAL,
            anglais_ecrit REAL,
            anglais_oral REAL,
            eps REAL,
            epreuve_facultative REAL,
            FOREIGN KEY (numero_table) REFERENCES candidat (numero_table)
        )
        ''')
        
        # Table Notes Tour 2
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes_tour2 (
            numero_table TEXT PRIMARY KEY,
            compo_franc REAL,
            mathematiques REAL,
            pc_lv2 REAL,
            FOREIGN KEY (numero_table) REFERENCES candidat (numero_table)
        )
        ''')
        
        # Table Résultats tour 1
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultats (
            numero_table TEXT PRIMARY KEY,
            tour INTEGER,
            points_total REAL,
            moyenne REAL,
            resultat TEXT,
            FOREIGN KEY (numero_table) REFERENCES candidat (numero_table)
        )
        ''')
        # Table Résultats tour 2
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultats2 (
            numero_table TEXT PRIMARY KEY,
            tour INTEGER,
            points_total REAL,
            moyenne REAL,
            resultat TEXT,
            FOREIGN KEY (numero_table) REFERENCES candidat (numero_table)
        )
        ''')
        self.conn.commit()




# implémentation des differentes classe 


class JurySettingsWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        self.load_jury()
        
    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.region_input = QLineEdit()
        self.dept_input = QLineEdit()
        self.localite_input = QLineEdit()
        self.centre_input = QLineEdit()
        self.president_input = QLineEdit()
        self.telephone_input = QLineEdit()
        
        layout.addRow("Région (IA):", self.region_input)
        layout.addRow("Département (IEF):", self.dept_input)
        layout.addRow("Localité:", self.localite_input)
        layout.addRow("Centre d'examen:", self.centre_input)
        layout.addRow("Président du jury:", self.president_input)
        layout.addRow("Téléphone:", self.telephone_input)
        
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.save_jury)
        layout.addRow(save_btn)
        
    def load_jury(self):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM jury LIMIT 1")
        jury = cursor.fetchone()
        
        if jury:
            self.region_input.setText(jury[1])
            self.dept_input.setText(jury[2])
            self.localite_input.setText(jury[3])
            self.centre_input.setText(jury[4])
            self.president_input.setText(jury[5])
            self.telephone_input.setText(jury[6])
            
    def save_jury(self):
        cursor = self.db.conn.cursor()
        
        data = (
            self.region_input.text(),
            self.dept_input.text(),
            self.localite_input.text(),
            self.centre_input.text(),
            self.president_input.text(),
            self.telephone_input.text()
        )
        
        cursor.execute("DELETE FROM jury")  # Clear existing data
        cursor.execute("""
        INSERT INTO jury (region, departement, localite, centre_examen, president, telephone)
        VALUES (?, ?, ?, ?, ?, ?)
        """, data)
        
        self.db.conn.commit()
        QMessageBox.information(self, "Succès", "Paramètres du jury enregistrés")


        

class CandidatForm(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Formulaire
        form_layout = QFormLayout()
        
        self.numero_input = QLineEdit()
        self.nom_input = QLineEdit()
        self.prenom_input = QLineEdit()
        self.date_naiss_input = QDateEdit()
        self.lieu_naiss_input = QLineEdit()
        self.sexe_input = QComboBox()
        self.sexe_input.addItems(['M', 'F'])
        self.nationnalite_input = QLineEdit()
        self.epreuve_facultative_input = QComboBox()
        self.epreuve_facultative_input.addItems(['Neutre','Musique','Couture','Dessin'])
        self.aptitude_sportive_input = QComboBox()
        self.aptitude_sportive_input.addItems(['Apte','Inapte'])
        
        form_layout.addRow("N° de table:", self.numero_input)
        form_layout.addRow("Nom:", self.nom_input)
        form_layout.addRow("Prénom:", self.prenom_input)
        form_layout.addRow("Date de naissance:", self.date_naiss_input)
        form_layout.addRow("Lieu de naissance:", self.lieu_naiss_input)
        form_layout.addRow("Sexe:", self.sexe_input)
        form_layout.addRow("Nationnalite:", self.nationnalite_input)
        form_layout.addRow("Epreuve facultative:", self.epreuve_facultative_input)
        form_layout.addRow("Aptitude sportive:", self.aptitude_sportive_input)
        
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.save_candidat)
        
        clear_btn = QPushButton("Effacer")
        clear_btn.clicked.connect(self.clear_form)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(clear_btn)
        
        # Table des candidats
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "N° table", "Nom", "Prénom", "Date naiss.", "Lieu naiss.", "Sexe", "Nationnalite", "Epreuve fac", "Aptitude sp"
        ])
        
        layout.addLayout(form_layout)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.table)
        
        self.load_candidats()
        
    def save_candidat(self):
        data = (
            self.numero_input.text(),
            self.nom_input.text(),
            self.prenom_input.text(),
            self.date_naiss_input.date().toString("dd/MM/yyyy"),
            self.lieu_naiss_input.text(),
            self.sexe_input.currentText(),
            self.nationnalite_input.text(),
            self.epreuve_facultative_input.currentText(),
            self.aptitude_sportive_input.currentText()
        )
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO candidat 
        (numero_table, nom, prenom, date_naissance, lieu_naissance, sexe, nationnalite, epreuve_facultative, aptitude_sportive)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        
        self.db.conn.commit()
        self.clear_form()
        self.load_candidats()
        QMessageBox.information(self, "Succès", "Candidat enregistré")
        
    def clear_form(self):
        self.numero_input.clear()
        self.nom_input.clear()
        self.prenom_input.clear()
        self.date_naiss_input.setDate(QDate.currentDate())
        self.lieu_naiss_input.clear()
        self.sexe_input.setCurrentIndex(0)
        self.nationnalite_input.clear()
        self.epreuve_facultative_input.setCurrentIndex(0)
        self.aptitude_sportive_input.setCurrentIndex(0)
        
    def load_candidats(self):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM candidat ORDER BY numero_table")
        
        self.table.setRowCount(0)
        for row, candidat in enumerate(cursor.fetchall()):
            self.table.insertRow(row)
            for col, value in enumerate(candidat[:9]):  # Premiers 9 champs
                self.table.setItem(row, col, QTableWidgetItem(str(value)))





class LivretScolaireWidget(QWidget):

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        # Section sélection candidat
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Candidat:"))
        self.candidat_combo = QComboBox()
        self.candidat_combo.currentIndexChanged.connect(self.load_livret)
        select_layout.addWidget(self.candidat_combo, stretch=1)
        layout.addLayout(select_layout)
        # Formulaire
        form_layout = QFormLayout()
        # Nombre de tentatives
        self.tentatives_input = QSpinBox()
        self.tentatives_input.setMinimum(1)
        form_layout.addRow("Nombre de tentatives:", self.tentatives_input)
        # Moyennes
        self.moyenne_inputs = {}
        for classe in ["6e", "5e", "4e", "3e"]:
            spin = QDoubleSpinBox()
            spin.setRange(0, 20)
            spin.setDecimals(2)
            spin.valueChanged.connect(self.calculate_moyenne_cycle)
            self.moyenne_inputs[classe] = spin
            form_layout.addRow(f"Moyenne {classe}:", spin)
        # Moyenne cycle (calculée)
        self.moyenne_cycle = QDoubleSpinBox()
        self.moyenne_cycle.setRange(0, 20)
        self.moyenne_cycle.setDecimals(2)
        self.moyenne_cycle.setReadOnly(True)
        form_layout.addRow("Moyenne du cycle:", self.moyenne_cycle)
        layout.addLayout(form_layout)
        # Boutons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.save_livret)
        clear_btn = QPushButton("Effacer")
        clear_btn.clicked.connect(self.clear_form)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(clear_btn)
        layout.addLayout(buttons_layout)
        # Chargement initial des candidats
        self.load_candidats()
    def load_candidats(self):
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT numero_table, nom, prenom 
            FROM candidat 
            ORDER BY nom, prenom
        """)
        self.candidat_combo.clear()
        self.candidat_combo.addItem("Sélectionner un candidat...", None)
        for numero, nom, prenom in cursor.fetchall():
            display_text = f"{nom} {prenom} (N°{numero})"
            self.candidat_combo.addItem(display_text, numero)
    def calculate_moyenne_cycle(self):
        total = sum(spin.value() for spin in self.moyenne_inputs.values())
        moyenne = total / len(self.moyenne_inputs)
        self.moyenne_cycle.setValue(moyenne)
    def load_livret(self):
        numero_table = self.candidat_combo.currentData()
        if not numero_table:
            self.clear_form()
            return
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT tentatives, moyenne_6e, moyenne_5e, moyenne_4e, moyenne_3e
            FROM livret_scolaire 
            WHERE numero_table = ?
        """, (numero_table,))
        data = cursor.fetchone()
        if data:
            self.tentatives_input.setValue(data[0])
            for i, classe in enumerate(["6e", "5e", "4e", "3e"]):
                self.moyenne_inputs[classe].setValue(data[i+1] or 0)
        else:
            self.clear_form()
    def save_livret(self):
        numero_table = self.candidat_combo.currentData()
        if not numero_table:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un candidat")
            return
        data = [
            numero_table,
            self.tentatives_input.value(),
            *[self.moyenne_inputs[c].value() for c in ["6e", "5e", "4e", "3e"]],
            self.moyenne_cycle.value()
        ]
        cursor = self.db.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO livret_scolaire 
            (numero_table, tentatives, moyenne_6e, moyenne_5e, moyenne_4e, moyenne_3e, moyenne_cycle)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, data)
        self.db.conn.commit()
        QMessageBox.information(self, "Succès", "Livret scolaire enregistré")
    def clear_form(self):
        self.tentatives_input.setValue(1)
        for spin in self.moyenne_inputs.values():
            spin.setValue(0)



class NotesInput(QWidget):
    # Définir matieres comme attribut de classe (static)
    matieres = {
        'compo_franc': ('Composition Française', 2),
        'dictee': ('Dictée', 1),
        'etude_texte': ('Étude de texte', 1),
        'instruction_civique': ('Instruction Civique', 1),
        'histoire_geo': ('Histoire-Géographie', 2),
        'mathematiques': ('Mathématiques', 4),
        'pc_lv2': ('PC/LV2', 2),
        'svt': ('SVT', 2),
        'anglais_ecrit': ('Anglais Écrit', 2),
        'anglais_oral': ('Anglais Oral', 1),
        'epreuve_facultative':('Epreuve Facultative', 1),
        'eps': ('EPS', 1)
    }
    matieres2 = {
        'compo_franc': ('Composition Française', 3),
        'mathematiques': ('Mathématiques', 3),
        'pc_lv2': ('PC/LV2', 2)
    }

    def __init__(self, db, tour=1):
        super().__init__()
        # Initialiser TOUS les attributs avant setup_ui
        self.db = db
        self.tour = tour
        self.note_inputs = {}  # Initialiser le dictionnaire vide ici
        self.candidat_combo = None
        self.total_label = None
        
        # Appeler setup_ui APRÈS avoir initialisé tous les attributs
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Sélection du candidat
        layout.addLayout(self.setup_candidat_selection())
        
        # Grille des notes
        grid = QGridLayout()
        
        grid.addWidget(QLabel("Matière"), 0, 0)
        grid.addWidget(QLabel("Coef"), 0, 1)
        grid.addWidget(QLabel("Note"), 0, 2)
        grid.addWidget(QLabel("Points"), 0, 3)
        
        if self.tour ==1 :
            for row, (code, (matiere, coef)) in enumerate(self.matieres.items(), 1):
                grid.addWidget(QLabel(matiere), row, 0)
                grid.addWidget(QLabel(str(coef)), row, 1)
                
                note_input = QDoubleSpinBox()
                note_input.setRange(0, 20)
                note_input.setDecimals(2)
                note_input.valueChanged.connect(self.calculate_points)
                self.note_inputs[code] = note_input  # Maintenant c'est sûr que note_inputs existe
                
                points_label = QLabel("0")
                points_label.setAlignment(Qt.AlignRight)
                note_input.points_label = points_label
                
                grid.addWidget(note_input, row, 2)
                grid.addWidget(points_label, row, 3)
                
            layout.addLayout(grid)
        else:
            for row, (code, (matiere, coef)) in enumerate(self.matieres2.items(), 1):
                grid.addWidget(QLabel(matiere), row, 0)
                grid.addWidget(QLabel(str(coef)), row, 1)
                
                note_input = QDoubleSpinBox()
                note_input.setRange(0, 20)
                note_input.setDecimals(2)
                note_input.valueChanged.connect(self.calculate_points)
                self.note_inputs[code] = note_input  # Maintenant c'est sûr que note_inputs existe
                
                points_label = QLabel("0")
                points_label.setAlignment(Qt.AlignRight)
                note_input.points_label = points_label
                
                grid.addWidget(note_input, row, 2)
                grid.addWidget(points_label, row, 3)
                
            layout.addLayout(grid)
        
        # Total
        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel("Total des points:"))
        self.total_label = QLabel("0")
        total_layout.addWidget(self.total_label)
        layout.addLayout(total_layout)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.save_notes)
        clear_btn = QPushButton("Effacer")
        clear_btn.clicked.connect(self.clear_notes)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(clear_btn)
        layout.addLayout(buttons_layout)

    # ... Le reste du code reste inchangé ...


    def setup_candidat_selection(self):
        select_layout = QHBoxLayout()
        
        # Label avec style
        label = QLabel("Candidat:")
        label.setStyleSheet("font-weight: bold;")
        
        # ComboBox des candidats
        self.candidat_combo = QComboBox()
        self.candidat_combo.setMinimumWidth(300)
        self.candidat_combo.setEditable(True)
        self.candidat_combo.setInsertPolicy(QComboBox.NoInsert)
        
        # Ajout d'un placeholder
        self.candidat_combo.addItem("Sélectionner un candidat...")
        self.candidat_combo.setCurrentIndex(0)
        
        # Bouton de rafraîchissement
        refresh_btn = QPushButton()
        refresh_btn.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        refresh_btn.setToolTip("Rafraîchir la liste des candidats")
        refresh_btn.clicked.connect(self.load_candidats)
        
        # Organisation du layout
        select_layout.addWidget(label)
        select_layout.addWidget(self.candidat_combo, stretch=1)
        select_layout.addWidget(refresh_btn)
        
        # Connexion du signal de changement
        self.candidat_combo.currentIndexChanged.connect(self.on_candidat_changed)
        
        # Chargement initial des candidats
        self.load_candidats()
        
        return select_layout
        
    def load_candidats(self):
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                SELECT numero_table, nom, prenom 
                FROM candidat 
                ORDER BY nom, prenom
            """)
            
            current_value = self.candidat_combo.currentData()
            
            self.candidat_combo.clear()
            self.candidat_combo.addItem("Sélectionner un candidat...", None)
            
            for numero, nom, prenom in cursor.fetchall():
                display_text = f"{nom} {prenom} (N°{numero})"
                self.candidat_combo.addItem(display_text, numero)
                
            if current_value:
                index = self.candidat_combo.findData(current_value)
                if index >= 0:
                    self.candidat_combo.setCurrentIndex(index)
                    
        except sqlite3.Error as e:
            QMessageBox.critical(
                self,
                "Erreur de base de données",
                f"Impossible de charger la liste des candidats : {str(e)}"
            )
            
    def on_candidat_changed(self, index):
        numero_table = self.candidat_combo.currentData()
        if numero_table:
            self.load_notes(numero_table)
        else:
            self.clear_notes()
            
    def calculate_points(self):
        total = 0
        if self.tour == 1:
            for code, (_, coef) in self.matieres.items():
                note = self.note_inputs[code].value()
                if code == 'eps':
                    note = note - 10
                
                if code == 'epreuve_facultative':
                    if note < 10:
                        note = 0
                    else :
                        note = note - 10
                points = note * coef
                self.note_inputs[code].points_label.setText(f"{points:.2f}")
                total += points
                
            self.total_label.setText(f"{total:.2f}")
        else:
            for code, (_, coef) in self.matieres2.items():
                note = self.note_inputs[code].value()
                points = note * coef
                self.note_inputs[code].points_label.setText(f"{points:.2f}")
                total += points
                
            self.total_label.setText(f"{total:.2f}")

        
    def save_notes(self):
        if self.candidat_combo.currentIndex() <= 0:  # Vérifie si un candidat est sélectionné
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un candidat")
            return
            
        numero_table = self.candidat_combo.currentData()
        if self.tour == 1:
            values = [numero_table]
            for code in self.matieres:
                values.append(self.note_inputs[code].value())
            
                cursor = self.db.conn.cursor()
                table = f"notes_tour{self.tour}"
                placeholders = ", ".join(["?"] * len(values))
                columns = "numero_table, " + ", ".join(self.matieres.keys())
        else:
            values = [numero_table]
            for code in self.matieres2:
                values.append(self.note_inputs[code].value())
                cursor = self.db.conn.cursor()
                table = f"notes_tour{self.tour}"
                placeholders = ", ".join(["?"] * len(values))
                columns = "numero_table, " + ", ".join(self.matieres2.keys())
        
        try:
            cursor.execute(f"""
            INSERT OR REPLACE INTO {table} 
            ({columns}) VALUES ({placeholders})
            """, values)
            
            self.db.conn.commit()
            QMessageBox.information(self, "Succès", "Notes enregistrées avec succès")
            
        except sqlite3.Error as e:
            QMessageBox.critical(
                self,
                "Erreur de base de données",
                f"Impossible d'enregistrer les notes : {str(e)}"
            )
            
    def clear_notes(self):
        for input in self.note_inputs.values():
            input.setValue(0)
            
    def load_notes(self, numero_table):
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(f"SELECT * FROM notes_tour{self.tour} WHERE numero_table = ?", 
                         (numero_table,))
            
            notes = cursor.fetchone()
            if notes:
                for i, (code, input) in enumerate(self.note_inputs.items(), 1):
                    input.setValue(notes[i] if notes[i] is not None else 0)
            else:
                self.clear_notes()
                
        except sqlite3.Error as e:
            QMessageBox.critical(
                self,
                "Erreur de base de données",
                f"Impossible de charger les notes : {str(e)}"
            )





class DeliberationWidget(QWidget):
    def __init__(self, db,tour=1):
        super().__init__()
        self.tour = tour
        self.db = db
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # En-tête
        header = QLabel("Délibération des résultats")
        header.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(header)
        
        # Table des résultats
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "N° table", "Nom", "Prénom", 
            "Points Tour 1", "Moyenne Tour 1",
            "Points Tour 2", "Moyenne Tour 2",
            "Résultat", "Repêchage"
        ])
        
        layout.addWidget(self.table)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Actualiser")
        refresh_btn.clicked.connect(self.load_resultats)
        
        calculate_btn = QPushButton("Calculer les résultats")
        calculate_btn.clicked.connect(self.calculate_resultats)
        
        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addWidget(calculate_btn)
        
        layout.addLayout(buttons_layout)
        
        self.load_resultats()
        
    def load_resultats(self):
        cursor = self.db.conn.cursor()
        cursor.execute("""
        SELECT 
            c.numero_table,
            c.nom,
            c.prenom,
            r.points_total,
            r.moyenne,
            r2.points_total,
            r2.moyenne,
            r.resultat
        FROM candidat c
        LEFT JOIN resultats r ON c.numero_table = r.numero_table 
        LEFT JOIN resultats2 r2 ON c.numero_table =  r2.numero_table
        ORDER BY c.numero_table
        """)
        
        self.table.setRowCount(0)
        for row, data in enumerate(cursor.fetchall()):
            self.table.insertRow(row)
            for col, value in enumerate(data):
                item = QTableWidgetItem(str(value) if value is not None else "-")
                self.table.setItem(row, col, item)
                
            # Ajout du checkbox pour le repêchage
            repechage = QCheckBox()
            self.table.setCellWidget(row, 8, repechage)
            
    def calculate_resultats(self):
        cursor = self.db.conn.cursor()
        
        # Pour chaque candidat
        cursor.execute("SELECT numero_table FROM candidat")
        for (numero_table,) in cursor.fetchall():
            # if self.tour == 1 
                # Calcul tour 1
                cursor.execute("""
                SELECT *
                FROM notes_tour1
                WHERE numero_table = ?
                """, (numero_table,))
                
                notes = cursor.fetchone()
                if notes:
                    total_points = 0
                    total_coef = 0
                    
                    for i, (_, (_, coef)) in enumerate(NotesInput.matieres.items(), 1):
                        if notes[i] is not None:
                            total_points += notes[i] * coef
                            total_coef += coef
                            
                    moyenne = total_points / total_coef if total_coef > 0 else 0
                    
                    # Détermination du résultat
                    # if total_points >= 171:
                    if total_points >= 180:
                        resultat = "Admis" 
                    # elif total_points < 144: 
                    elif total_points < 153: 
                        resultat = "Échec"
                            
                    else : 
                        resultat = "2em tour"
                    if resultat == "Échec":
                        checkbox = self.table.cellWidget(
                            self.find_row(numero_table), 6
                        )
                        if checkbox and checkbox.isChecked():
                            resultat = "Repêché - Admis"
                    
                    # Enregistrement
                    cursor.execute("""
                    INSERT OR REPLACE INTO resultats 
                    (numero_table, tour, points_total, moyenne, resultat)
                    VALUES (?, 1, ?, ?, ?)
                    """, (numero_table, total_points, moyenne, resultat))
            # else :
            # Calcul tour 2
                cursor.execute("""
                SELECT *
                FROM notes_tour2
                WHERE numero_table = ?
                """, (numero_table,))
                
                notes = cursor.fetchone()
                if notes:
                    total_points = 0
                    total_coef = 0
                    
                    for i, (_, (_, coef)) in enumerate(NotesInput.matieres2.items(), 1):
                        if notes[i] is not None:
                            total_points += notes[i] * coef
                            total_coef += coef
                            
                    moyenne = total_points / total_coef if total_coef > 0 else 0
                    
                    # Détermination du résultat
                    resultat = "Admis" if total_points >= 76 else "Échec"
                    if resultat == "Échec":
                        checkbox = self.table.cellWidget(
                            self.find_row(numero_table), 6
                        )
                        if checkbox and checkbox.isChecked():
                            resultat = "Repêché - Admis"
                    
                    # Enregistrement
                    cursor.execute("""
                    INSERT OR REPLACE INTO resultats2 
                    (numero_table, tour, points_total, moyenne, resultat)
                    VALUES (?, 2, ?, ?, ?)
                    """, (numero_table, total_points, moyenne, resultat))
                
        self.db.conn.commit()
        self.load_resultats()
        QMessageBox.information(self, "Succès", "Résultats calculés et enregistrés")
        
    def find_row(self, numero_table):
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == numero_table:
                return row
        return -1
    




class StatisticsWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Cartes de statistiques
        stats_layout = QHBoxLayout()
        
        self.total_card = self.create_stat_card("Total Candidats")
        self.admis_card = self.create_stat_card("Admis")
        self.echec_card = self.create_stat_card("Échecs")
        
        stats_layout.addWidget(self.total_card)
        stats_layout.addWidget(self.admis_card)
        stats_layout.addWidget(self.echec_card)
        
        layout.addLayout(stats_layout)
        
        # Graphique
        self.chart_view = self.create_chart()
        layout.addWidget(self.chart_view)
        
        # Bouton de rafraîchissement
        refresh_btn = QPushButton("Actualiser les statistiques")
        refresh_btn.clicked.connect(self.update_statistics)
        layout.addWidget(refresh_btn)
        
        self.update_statistics()
        
    def create_stat_card(self, title):
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        
        value_label = QLabel("0")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        percent_label = QLabel("0%")
        percent_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(percent_label)
        
        group.value_label = value_label
        group.percent_label = percent_label
        
        return group
        
    def create_chart(self):
        # Création du graphique
        chart = QChart()
        chart.setTitle("Résultats par Tour")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Création de la série de barres
        series = QBarSeries()
        
        # Ajout des données (seront mises à jour plus tard)
        set1 = QBarSet("Tour 1")
        set2 = QBarSet("Tour 2")
        
        series.append(set1)
        series.append(set2)
        
        chart.addSeries(series)
        
        # Axe des catégories
        categories = ["Admis", "Repêchés", "Échecs"]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Axe des valeurs
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        # Vue du graphique
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        return chart_view
        
    def update_statistics(self):
        cursor = self.db.conn.cursor()
        
        # Calcul des statistiques
        cursor.execute("SELECT COUNT(*) FROM candidat")
        total = cursor.fetchone()[0]
        
        cursor.execute("""
        SELECT 
            COUNT(CASE WHEN resultat = 'Admis' OR resultat = 'Repêché - Admis' THEN 1 END) as admis,
            COUNT(CASE WHEN resultat = 'Échec' THEN 1 END) as echecs
        FROM resultats
        """)
        
        stats = cursor.fetchone()
        admis, echecs = stats if stats else (0, 0)
        
        # Mise à jour des cartes
        self.total_card.value_label.setText(str(total))
        self.total_card.percent_label.setText("100%")
        
        self.admis_card.value_label.setText(str(admis))
        self.admis_card.percent_label.setText(f"{(admis/total*100 if total else 0):.1f}%")
        
        self.echec_card.value_label.setText(str(echecs))
        self.echec_card.percent_label.setText(f"{(echecs/total*100 if total else 0):.1f}%")
        
        # Mise à jour du graphique
        self.update_chart()
        
    def update_chart(self):
        cursor = self.db.conn.cursor()
        
        # Statistiques par tour
        cursor.execute("""
        SELECT 
            tour,
            COUNT(CASE WHEN resultat = 'Admis' OR resultat = 'Repêché - Admis' THEN 1 END) as admis,
            COUNT(CASE WHEN resultat LIKE '%Repêché%' THEN 1 END) as repeches,
            COUNT(CASE WHEN resultat = 'Échec' THEN 1 END) as echecs
        FROM resultats
        GROUP BY tour
        """)
        
        stats = cursor.fetchall()
        
        # Mise à jour du graphique
        chart = self.chart_view.chart()
        series = chart.series()[0]
        
        if stats:
            series.clear()
            for tour_stats in stats:
                tour, admis, repeches, echecs = tour_stats
                bar_set = QBarSet(f"Tour {tour}")
                bar_set.append([admis, repeches, echecs])
                series.append(bar_set)




# Définir la classe DocumentGeneratorWidget
class DocumentGeneratorWidget(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        label = QLabel("GENERATEUR DE DOCUMENT PAS ENCORE IMPLEMENTE")
        layout.addWidget(label)
        self.setLayout(layout)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BFEM Manager")
        self.setMinimumSize(1000, 800)
        
        self.db = Database()
        
        self.setup_ui()
        
    def setup_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Onglets
        self.tabs.addTab(JurySettingsWidget(self.db), "Paramètres du jury")
        self.tabs.addTab(CandidatForm(self.db), "Gestion des candidats")
        self.tabs.addTab(LivretScolaireWidget(self.db), "Livret Scolaire")
        
        notes_widget = QTabWidget()
        notes_widget.addTab(NotesInput(self.db, tour=1), "Premier Tour")
        notes_widget.addTab(NotesInput(self.db, tour=2), "Second Tour")
        self.tabs.addTab(notes_widget, "Saisie des notes")
        
        self.tabs.addTab(DeliberationWidget(self.db), "Délibérations")
        self.tabs.addTab(StatisticsWidget(self.db), "Statistiques")
        self.tabs.addTab(DocumentGeneratorWidget(self.db), "Documents")





if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Application du style Fusion
    app.setStyle("Fusion")
    
    # Création et affichage de la fenêtre principale
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
