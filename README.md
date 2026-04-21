# 📊 Projet Data Management — Analyse Clients

## 🧠 Description

Cette application permet d’importer un fichier CSV contenant des données clients afin de :

* Visualiser des indicateurs clés (KPI)
* Analyser le portefeuille client
* Classifier les clients selon leur valeur
* Générer des recommandations
* Assurer la traçabilité des actions

L’objectif est de fournir un outil simple d’aide à la décision pour un manager.

---

## 🚀 Fonctionnalités

### 📥 Ingestion de données

* Import de fichier CSV
* Lecture des données avec Python (Pandas)
* Gestion des erreurs d’import

### 📊 KPI

* Nombre total de clients
* Chiffre d’affaires total

### 🧠 Analyse

* Classification des clients :

  * À relancer
  * À surveiller
  * À fidéliser
* Recommandations associées
* Justification des décisions

### 🗂️ Traçabilité

* Historique des actions (upload, consultation KPI…)
* Logs côté backend

---

## 🏗️ Architecture

* **Frontend** : HTML + JavaScript (vanilla)
* **Backend** : Python (FastAPI)
* **Data processing** : Pandas

---

## ⚙️ Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd project
```

---

### 2. Installer les dépendances backend

```bash
pip install -r backend/requirements.txt
```

Si besoin :

```bash
pip install fastapi uvicorn pandas python-multipart
```

---

### 3. Lancer le backend

```bash
uvicorn backend.main:app --reload
```

Accès API :

```
http://localhost:8000/docs
```

---

### 4. Lancer le frontend

Option simple :

* Ouvrir `frontend/index.html`

Option recommandée :

```bash
cd frontend
python -m http.server 5500
```

Puis :

```
http://localhost:5500
```

---

## 📄 Format du fichier CSV

Exemple :

```csv
client_id,chiffre_affaires,segment
1,1200,VIP
2,500,Standard
3,3000,VIP
```

---

## 🧪 Utilisation

1. Importer un fichier CSV
2. Visualiser les KPI
3. Consulter la classification des clients
4. Voir les recommandations et justifications
5. Consulter l’historique des actions

---

## 📝 Logs & Historique

* Les actions importantes sont enregistrées
* Consultables via l’interface
* Logs visibles dans le terminal backend

---

## ✅ Definition of Done

* Code fonctionnel
* Fonctionnalités démontrables
* README complet
* Instructions claires
* Projet prêt à être repris

---

## 👨‍💻 Auteur

Projet réalisé dans le cadre du module Data Management.
