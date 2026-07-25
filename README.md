# 🌐 AI Translation & Image Similarity Search Web Application

## 📌 Description

Ce projet est une application web développée avec **Flask** qui combine plusieurs technologies d'Intelligence Artificielle, de traitement du langage naturel (NLP), de vision par ordinateur et de bases de données afin de fournir plusieurs fonctionnalités dans une seule plateforme.

L'application permet de :

* 🌍 Traduire du texte entre différentes langues grâce à **Google Translate**.
* 💾 Enregistrer l'historique des traductions dans **MongoDB**.
* 🔎 Rechercher des traductions enregistrées.
* 📄 Détecter le plagiat en comparant un texte avec les textes déjà stockés.
* 📊 Calculer le taux de similarité entre deux textes.
* 🖼️ Rechercher des images similaires à l'aide du modèle **OpenAI CLIP**.
* 🔐 Gérer un espace administrateur permettant uniquement à l'administrateur d'ajouter des images dans la base de données.

---

## 🚀 Fonctionnalités

### 🌍 Traduction de texte

* Détection automatique de la langue.
* Traduction vers plusieurs langues.
* Sauvegarde des traductions dans MongoDB.

### 🔎 Recherche de traductions

* Recherche par texte original.
* Recherche par texte traduit.
* Recherche insensible à la casse.

### 📄 Détection de plagiat

* Comparaison d'un texte avec toutes les traductions enregistrées.
* Calcul du score de similarité.
* Classement des résultats selon leur taux de similarité.

### 📊 Similarité entre deux textes

* Calcul du pourcentage de similarité à l'aide de l'algorithme **SequenceMatcher** de Python.

### 🖼️ Recherche d'images similaires

* Upload d'images (réservé à l'administrateur).
* Extraction des caractéristiques des images avec **OpenAI CLIP (ViT-B/32)**.
* Stockage des vecteurs d'embedding dans MongoDB.
* Calcul de la similarité cosinus entre l'image recherchée et les images enregistrées.
* Affichage des 5 images les plus similaires.

### 🔐 Authentification

* Connexion administrateur.
* Protection de l'ajout d'images.
* Gestion des sessions avec Flask.

---

## 🛠️ Technologies utilisées

### Backend

* Python
* Flask

### Intelligence Artificielle

* OpenAI CLIP
* Transformers (Hugging Face)
* PyTorch
* NumPy

### Traitement du langage naturel

* Google Translate API (googletrans)
* difflib

### Base de données

* MongoDB

### Moteur de recherche

* Elasticsearch

### Gestion des images

* Pillow (PIL)

### Frontend

* HTML
* CSS
* JavaScript
* Jinja2

---

## 📂 Structure du projet

```text
project/
│
├── app.py
├── templates/
│   ├── index.html
│   └── login.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── images/
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

```bash
git clone https://github.com/username/project.git

cd project

pip install -r requirements.txt
```

Lancer MongoDB :

```bash
mongod
```

Lancer Elasticsearch :

```bash
elasticsearch
```

Démarrer l'application :

```bash
python app.py
```

Puis ouvrir :

```
http://127.0.0.1:5000
```

---

## 📚 Bibliothèques principales

* Flask
* pymongo
* transformers
* torch
* pillow
* numpy
* googletrans
* elasticsearch

---

## 🎯 Objectifs du projet

Ce projet a été développé dans le but d'explorer l'intégration de plusieurs domaines de l'Intelligence Artificielle dans une seule application web :

* Natural Language Processing (NLP)
* Computer Vision
* Recherche sémantique
* Détection de similarité
* Gestion de bases de données NoSQL
* Développement Web avec Flask

---

## 👩‍💻 Auteur

**Soukayna Rachdi**

Master BIAM (Bioinformatique & Intelligence Artificielle pour la Médecine de Précision)

FSDM Fès – Maroc
