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


RISK_COLUMN_ALIASES = {
    "churn": ["churn", "is_churn", "resilie", "resiliation", "attrition"],
    "payment_delay_days": [
        "payment_delay_days",
        "retard_paiement_jours",
        "days_late",
        "late_days",
    ],
    "payment_incidents": [
        "payment_incidents",
        "incidents_paiement",
        "nb_incidents",
        "late_payments",
    ],
    "satisfaction_score": [
        "satisfaction_score",
        "satisfaction",
        "customer_satisfaction",
        "csat",
    ],
}

RISK_THRESHOLDS = {
    "payment_delay_days": 30,
    "payment_incidents": 3,
    "satisfaction_score_max": 2,
}

RECOMMENDATIONS = [
    {
        "id": "rec-contact-retard",
        "title": "Relancer les clients en retard de paiement",
        "description": "Mettre en place une relance proactive pour les clients depassant le seuil de retard.",
    },
    {
        "id": "rec-suivi-satisfaction",
        "title": "Lancer un suivi satisfaction cible",
        "description": "Contacter les clients avec un score de satisfaction faible pour identifier les irritants.",
    },
    {
        "id": "rec-plan-retention",
        "title": "Construire un plan de retention",
        "description": "Prioriser les clients en risque de churn avec une offre ou un accompagnement dedie.",
    },
]


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
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recommendation_id TEXT NOT NULL,
                recommendation_title TEXT NOT NULL,
                action_title TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



def normalize_key(key: str) -> str:
    return key.strip().lower().replace(" ", "_")


def find_value_by_alias(row: dict, aliases: list[str]):
    normalized_row = {normalize_key(str(key)): value for key, value in row.items()}
    for alias in aliases:
        if alias in normalized_row:
            return normalized_row[alias]
    return None


def parse_float(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(",", ".")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return None

    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "oui"}:
        return True
    if text in {"0", "false", "no", "non"}:
        return False
    return None


def is_risk_client(row: dict) -> bool:
    churn_value = find_value_by_alias(row, RISK_COLUMN_ALIASES["churn"])
    churn = parse_bool(churn_value)
    if churn is True:
        return True

    delay_days = parse_float(find_value_by_alias(row, RISK_COLUMN_ALIASES["payment_delay_days"]))
    if delay_days is not None and delay_days >= RISK_THRESHOLDS["payment_delay_days"]:
        return True

    incidents = parse_float(find_value_by_alias(row, RISK_COLUMN_ALIASES["payment_incidents"]))
    if incidents is not None and incidents >= RISK_THRESHOLDS["payment_incidents"]:
        return True

    satisfaction = parse_float(find_value_by_alias(row, RISK_COLUMN_ALIASES["satisfaction_score"]))
    if satisfaction is not None and satisfaction <= RISK_THRESHOLDS["satisfaction_score_max"]:
        return True

    return False


def get_risk_clients_count() -> tuple[int, int]:
    total_clients = 0
    risk_clients = 0

    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute("SELECT row_data FROM imported_rows").fetchall()

    for (row_json,) in rows:
        try:
            payload = json.loads(row_json)
        except json.JSONDecodeError:
            continue

        total_clients += 1
        if is_risk_client(payload):
            risk_clients += 1

    return total_clients, risk_clients


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/risk-clients")
def risk_clients():
    total_clients, risk_clients = get_risk_clients_count()
    return jsonify(
        {
            "ok": True,
            "total_clients": total_clients,
            "risk_clients": risk_clients,
            "criteria": {
                "churn": "churn = true/oui/yes/1",
                "payment_delay_days": f">= {RISK_THRESHOLDS['payment_delay_days']} jours de retard",
                "payment_incidents": f">= {RISK_THRESHOLDS['payment_incidents']} incidents",
                "satisfaction_score": f"<= {RISK_THRESHOLDS['satisfaction_score_max']}",
            },
        }
    )


@app.get("/api/recommendations")
def get_recommendations():
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute(
            """
            SELECT id, recommendation_id, recommendation_title, action_title, created_at
            FROM actions
            ORDER BY id DESC
            """
        ).fetchall()

    actions = [
        {
            "id": row[0],
            "recommendation_id": row[1],
            "recommendation_title": row[2],
            "action_title": row[3],
            "created_at": row[4],
        }
        for row in rows
    ]
    return jsonify({"ok": True, "recommendations": RECOMMENDATIONS, "actions": actions})


@app.post("/api/actions")
def create_action():
    payload = request.get_json(silent=True) or {}
    recommendation_id = str(payload.get("recommendation_id", "")).strip()
    action_title = str(payload.get("action_title", "")).strip()

    if not recommendation_id:
        return jsonify({"ok": False, "message": "La recommandation est obligatoire."}), 400

    if not action_title:
        return jsonify({"ok": False, "message": "Le titre de l'action est obligatoire."}), 400

    recommendation = next(
        (item for item in RECOMMENDATIONS if item["id"] == recommendation_id),
        None,
    )
    if recommendation is None:
        return jsonify({"ok": False, "message": "Recommandation introuvable."}), 404

    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            cursor = connection.execute(
                """
                INSERT INTO actions (recommendation_id, recommendation_title, action_title)
                VALUES (?, ?, ?)
                """,
                (recommendation_id, recommendation["title"], action_title),
            )
            connection.commit()
            action_id = cursor.lastrowid
    except sqlite3.DatabaseError:
        return jsonify({"ok": False, "message": "Erreur base de donnees lors du stockage."}), 500

    return (
        jsonify(
            {
                "ok": True,
                "message": "Action creee et sauvegardee avec succes.",
                "action": {
                    "id": action_id,
                    "recommendation_id": recommendation_id,
                    "recommendation_title": recommendation["title"],
                    "action_title": action_title,
                },
            }
        ),
        201,
    )
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


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

