# 🧮 Gestion du BFEM – Jury Moderne (PC/LV2)

Ce projet est un **prototype de logiciel** pour la gestion des données des candidats et la **délibération** lors de l’examen du **BFEM au Sénégal**.  
L’application est développée en **Python** avec une interface graphique PySide6 et une base de données **SQLite**. 

Le modèle de données cible un **seul jury** de la session **Moderne (PC/LV2)** pour simplifier la conception.

---

## 🎯 Objectifs

- Gérer les **informations des candidats**, leurs livrets scolaires et leurs notes d’examen.   
- Automatiser les **calculs de points, moyennes, bonus/malus et décisions** (admis, second tour, échec, repêchage). 
- Permettre l’édition de **listes, PV, relevés de notes** et diverses statistiques. 

---

## 🧱 Modèle de données (résumé)

### Table Candidat

Principaux attributs : 

- `Numero_Table` : entier, numéro de table du candidat.  
- `Prenom_s`, `Nom` : chaînes de caractères.  
- `Date_Naissance`, `Lieu_Naissance`.  
- `Sexe` : M/F.  
- `Nationalite`.  
- `Choix_Epr_Facultative` : booléen (OUI/NON).  
- `Epreuve_Facultative` : Couture, Dessin, Musique.  
- `Aptitude_Sportive` : booléen (Apte / Inapte).  

### Table Livret Scolaire

- `Nombre_de_fois` : nombre de tentatives au BFEM.  
- `Moyenne_6e`, `Moyenne_5e`, `Moyenne_4e`, `Moyenne_3e`, `Moyenne_Cycle`. 

### Table Notes – 1er tour

- Notes : `Compo_Franc`, `Dictee`, `Etude_de_texte`, `Instruction_Civique`, `Histoire_Geographie`, `Mathematiques`, `PC_LV2`, `SVT`, `Anglais1`, `Anglais_Oral`, `EPS`, `Epreuve_Facultative`.  
- Coefficients associés : `Coef1` à `Coef10` et `Coef7`, `Coef8`, etc. 

### Table Notes – 2ᵉ tour

- `Francais`, `Mathematiques`, `PC_LV2` avec coefficients `CoefA`, `CoefB`, `CoefC`. 

---

## 📐 Règles métiers implémentées (RM1–RM16)

Principales règles à intégrer dans la logique métier : 

- **RM1** : Toutes les épreuves sont notées sur 20.  
- **RM2** : EPS → si note > 10, bonus = note − 10 ; sinon malus = 10 − note.  
- **RM3** : Épreuve facultative → bonus = note − 10 si note > 10, sinon 0.  
- **RM4** : Le candidat est **admis d’office** si total ≥ 180 points.  
- **RM5** : Le candidat va au **second tour** si total ≥ 153 points.  
- **RM6** : Le candidat **échoue** si total < 153 points.  
- **RM7** : Candidat **repêchable** si moyenne de cycle ≥ 12.  
- **RM8** : Repêchable d’office au 1er tour si total ∈ [171 ; 179,9].  
- **RM9** : Repêchable pour 2ᵉ tour si total ∈ [144 ; 152,9].  
- **RM10** : Au 2ᵉ tour, seules les notes Français, Mathématiques, PC/LV2 (avec leurs coefficients) sont prises en compte.  
- **RM11** : Au 2ᵉ tour, repêchable si total ∈ [76 ; 79,9].  
- **RM12** : Un candidat ayant passé le BFEM **plus de 2 fois** ne peut pas être repêché.  
- **RM13** : Génération d’un **numéro d’anonymat unique** par épreuve pour la correction.  
- **RM14** : Épreuves facultatives : Couture, Dessin, Musique.  
- **RM15** : Si le candidat est **Inapte** ou n’a pas choisi d’épreuve facultative, aucune note ne doit être saisie pour ces épreuves.  
- **RM16** : Toutes les notes sont saisies **sous anonymat** (un anonymat principal lie tous les numéros de correction).  

---

## 🖥️ Fonctionnalités de l’application

Le prototype doit proposer, via des formulaires graphiques : [file:92]

- **Paramétrage du jury** : région (IA), département (IEF), localité, centre d’examen, président de jury, téléphone.  
- **Gestion des candidats (CRUD)** : création, modification, suppression, consultation.  
- **Générateur automatique d’anonymat** pour la correction et la saisie des notes au 1er et au 2ᵉ tour.  
- **Suivi de la délibération** pour les deux tours (totaux, décisions, repêchage).  
- **Gestion des repêchages** selon les règles RM7 à RM12.  
- **Impression en PDF** des listes : candidats, anonymats, résultats, PV de délibération.  
- **Statistiques** : taux de réussite, répartition des décisions, etc.  
- **Génération des relevés de notes** pour le 1er et le 2ᵉ tour.  



---

## 🛠️ Stack technique (prévisionnelle)

- **Python 3.x**  
- **GUI** : PySide6
- **Base de données** : SQLite (`bfem.db`)  
- **Génération PDF** : bibliothèque au choix (ReportLab, FPDF, etc.)  

---

## 🚀 Installation et exécution

1. **Cloner le dépôt**

mkdir SunuBEFM

git clone https://github.com/BemvindoTech/SunuBFEM.git

cd SunuBEFM


2. **Créer un environnement virtuel**

python -m venv venv

Linux / macOS
source venv/bin/activate

Windows
venv\Scripts\activate


3. **Installer les dépendances**

pip install -r requirements.txt


4. **Initialiser la base de données**

python init_db.py


5. **Lancer l’application**

python main.py