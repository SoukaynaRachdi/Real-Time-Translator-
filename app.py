from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory, flash, session
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from googletrans import Translator, LANGUAGES  # type: ignore
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np
import torch
import os
import difflib
from elasticsearch import Elasticsearch

# -------------------------- Flask Setup --------------------------
app = Flask(__name__)
app.secret_key = "secret123"
UPLOAD_FOLDER = "images"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -------------------------- MongoDB --------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["projet_db"]
collection_traduction = db["traductions"]
collection_images = db["images"]

# Supprimer les documents images sans embedding
collection_images.delete_many({"embedding": {"$exists": False}})

# -------------------------- Elasticsearch --------------------------
es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "image_search"

# -------------------------- CLIP --------------------------
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
SIMILARITY_THRESHOLD = 0.70  # 🔹 Seulement les images proches

# -------------------------- Google Translate --------------------------
translator = Translator()

# -------------------------- Fonctions Utilitaires --------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_embedding(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        features = model.get_image_features(**inputs)
    emb = features[0].numpy()
    emb = emb / np.linalg.norm(emb)
    return emb.tolist()

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# -------------------------- Routes HTML --------------------------
@app.route("/")
def index():
    return render_template("index.html", image_results=[])

@app.route("/images/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# -------------------------- Admin Login --------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Nom d'admin et mot de passe
        if username == "admin" and password == "admin123":
            session["is_admin"] = True
            flash("Connexion réussie !")
            return redirect(url_for("images"))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect !")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    flash("Déconnecté.")
    return redirect(url_for("index"))

# -------------------------- Traduction --------------------------
@app.route("/traduire", methods=["POST"])
def traduire():
    data = request.json
    texte = data.get("texte", "")
    src_lang = data.get("sourceLang", "auto")
    dest_lang = data.get("targetLang", "en")

    if not texte:
        return jsonify({"error": "Texte vide !"}), 400

    try:
        result = translator.translate(texte, src=src_lang, dest=dest_lang)
        traduction_doc = {
            "texte_original": texte,
            "texte_traduit": result.text,
            "source_lang": src_lang,
            "target_lang": dest_lang
        }
        res_mongo = collection_traduction.insert_one(traduction_doc)

        return jsonify({
            "texte_original": texte,
            "traduction": result.text,
            "source_lang": src_lang,
            "target_lang": dest_lang,
            "_id": str(res_mongo.inserted_id)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/langues", methods=["GET"])
def langues():
    return jsonify(LANGUAGES)

# -------------------------- Recherche texte --------------------------
@app.route("/recherche", methods=["POST"])
def recherche():
    data = request.json
    texte = data.get("texte", "")

    if not texte:
        return jsonify({"error": "Texte vide !"}), 400

    try:
        query = {
            "$or": [
                {"texte_traduit": {"$regex": texte, "$options": "i"}},
                {"texte_original": {"$regex": texte, "$options": "i"}}
            ]
        }
        docs = list(collection_traduction.find(query))
        resultats = [{"texte_original": doc["texte_original"], "texte_traduit": doc["texte_traduit"]} for doc in docs]
        return jsonify({"resultats": resultats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/similarite_deux_textes", methods=["POST"])
def similarite_deux_textes():
    data = request.json
    texte1 = data.get("texte1", "")
    texte2 = data.get("texte2", "")

    if not texte1 or not texte2:
        return jsonify({"error": "Veuillez fournir les deux textes !"}), 400

    try:
        score = difflib.SequenceMatcher(None, texte1, texte2).ratio()
        return jsonify({"similarite": score})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/plagiat", methods=["POST"])
def plagiat():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Requête invalide (JSON manquant)"}), 400

    texte = data.get("texte", "").strip()

    if not texte:
        return jsonify({"error": "Texte vide !"}), 400

    try:
        docs = list(collection_traduction.find({}))
        seuil = 0.5
        resultats = []

        for doc in docs:
            texte_original = doc.get("texte_original", "")
            texte_traduit = doc.get("texte_traduit", "")

            # Calcul similarité avec original
            score_original = difflib.SequenceMatcher(
                None, texte, texte_original
            ).ratio()

            # Calcul similarité avec traduction
            score_traduit = difflib.SequenceMatcher(
                None, texte, texte_traduit
            ).ratio()

            # On prend le score le plus élevé
            score_final = max(score_original, score_traduit)

            if score_final >= seuil:
                resultats.append({
                    "source_originale": texte_original,
                    "texte_traduit": texte_traduit,
                    "score": round(score_final, 2)
                })

        resultats.sort(key=lambda x: x["score"], reverse=True)

        return jsonify({
            "nombre_sources": len(resultats),
            "plagiat": resultats
        })

    except Exception as e:
        print("Erreur plagiat:", e)
        return jsonify({"error": str(e)}), 500

# -------------------------- Upload et recherche d'images --------------------------
@app.route("/images", methods=["GET", "POST"])
def images():
    results = []

    # ---------------- Upload image (admin only) ----------------
    if request.method == "POST" and "image" in request.files:
        if not session.get("is_admin"):
            flash("Seul l'admin peut uploader des images !")
            return redirect(url_for("login"))

        file = request.files["image"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            emb = get_image_embedding(path)
            collection_images.insert_one({"filename": filename, "embedding": emb})
            flash("Image uploaded successfully!")
            return redirect(url_for("images"))

    # ---------------- Search image (all users) ----------------
    if request.method == "POST" and "query_image" in request.files:
        file = request.files["query_image"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], "query_" + filename)
            file.save(path)
            query_emb = get_image_embedding(path)

            sims = []
            for doc in collection_images.find():
                if "embedding" not in doc:
                    continue
                score = cosine_similarity(query_emb, np.array(doc["embedding"]))
                if score >= SIMILARITY_THRESHOLD:
                    if os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], doc["filename"])):
                        sims.append({
                            "filename": doc["filename"],
                            "score": round(score, 2)
                            })

            sims.sort(key=lambda x: x["score"], reverse=True)
            results = sims[:5]

    return render_template("index.html", image_results=results)

# -------------------------- Lancer le serveur --------------------------
if __name__ == "__main__":
    app.run(debug=True)
