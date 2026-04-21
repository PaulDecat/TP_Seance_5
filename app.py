import csv
import io
import json
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data.db"
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {"csv"}

UPLOAD_FOLDER.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(_error):
    return (
        jsonify(
            {
                "ok": False,
                "message": "Fichier trop volumineux. Taille maximale autorisee: 50 Mo.",
            }
        ),
        413,
    )


def init_db() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS imported_rows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file TEXT NOT NULL,
                row_data TEXT NOT NULL
            )
            """
        )
        connection.commit()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



def extract_segment(row: dict) -> str:
    for key, value in row.items():
        if key is None:
            continue
        normalized_key = key.strip().lower()
        if normalized_key in {"segment", "segmentation", "client_segment", "customer_segment"}:
            segment_value = str(value).strip()
            return segment_value if segment_value else "Non renseigne"
    return "Non renseigne"


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/import")
def import_csv():
    if "file" not in request.files:
        return jsonify({"ok": False, "message": "Aucun fichier envoye."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"ok": False, "message": "Aucun fichier selectionne."}), 400

    if not allowed_file(file.filename):
        return (
            jsonify(
                {
                    "ok": False,
                    "message": "Erreur: seuls les fichiers CSV sont acceptes.",
                }
            ),
            400,
        )

    filename = secure_filename(file.filename)
    file_path = UPLOAD_FOLDER / filename

    try:
        file.save(file_path)

        with file_path.open("r", encoding="utf-8") as csv_file:
            csv_text = csv_file.read()

        reader = csv.DictReader(io.StringIO(csv_text))
        if reader.fieldnames is None:
            file_path.unlink(missing_ok=True)
            return jsonify({"ok": False, "message": "Le fichier CSV est vide ou invalide."}), 400

        rows = []
        for row in reader:
            rows.append((filename, json.dumps(row, ensure_ascii=True)))

        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.executemany(
                "INSERT INTO imported_rows (source_file, row_data) VALUES (?, ?)",
                rows,
            )
            connection.commit()

        return (
            jsonify(
                {
                    "ok": True,
                    "message": f"Upload reussi: {len(rows)} ligne(s) importee(s).",
                }
            ),
            200,
        )
    except UnicodeDecodeError:
        file_path.unlink(missing_ok=True)
        return jsonify({"ok": False, "message": "Le fichier CSV doit etre encode en UTF-8."}), 400
    except csv.Error:
        file_path.unlink(missing_ok=True)
        return jsonify({"ok": False, "message": "Le contenu du fichier CSV est invalide."}), 400
    except sqlite3.DatabaseError:
        return jsonify({"ok": False, "message": "Erreur base de donnees lors du stockage."}), 500
    except OSError:
        return jsonify({"ok": False, "message": "Erreur lors de l'enregistrement du fichier."}), 500


@app.get("/api/segments")
def get_segments_distribution():
    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            cursor = connection.execute("SELECT row_data FROM imported_rows")
            rows = cursor.fetchall()
    except sqlite3.DatabaseError:
        return jsonify({"ok": False, "message": "Erreur base de donnees lors de la lecture."}), 500

    segment_counts = {}
    invalid_rows = 0

    for (raw_row,) in rows:
        try:
            row_data = json.loads(raw_row)
            if not isinstance(row_data, dict):
                invalid_rows += 1
                continue
        except json.JSONDecodeError:
            invalid_rows += 1
            continue

        segment = extract_segment(row_data)
        segment_counts[segment] = segment_counts.get(segment, 0) + 1

    if not segment_counts:
        return (
            jsonify(
                {
                    "ok": False,
                    "message": "Aucune donnee segmentable disponible.",
                    "segments": [],
                    "total_clients": 0,
                }
            ),
            200,
        )

    sorted_segments = sorted(segment_counts.items(), key=lambda item: item[1], reverse=True)
    total_clients = sum(segment_counts.values())
    segments = [
        {"label": label, "count": count, "percentage": round((count / total_clients) * 100, 2)}
        for label, count in sorted_segments
    ]

    return (
        jsonify(
            {
                "ok": True,
                "message": "Repartition des segments calculee.",
                "segments": segments,
                "total_clients": total_clients,
                "ignored_rows": invalid_rows,
            }
        ),
        200,
    )

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

