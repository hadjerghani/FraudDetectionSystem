"""
app.py  —  Fraud Detection Dashboard
=====================================
Connects to the 'fraud_detection' PostgreSQL database that was populated
by load_transactions.ipynb and predict_transaction.ipynb.

Tables used
-----------
  transactions       : transaction_id, transaction_time, v1..v28, amount, fraud_flag
  fraud_predictions  : transaction_id, predicted_label

Model
-----
  fraud_model.pkl  — LogisticRegression trained on [Time, V1..V28, Amount]
  loaded once at startup; used for the live-score API endpoint.

Run
---
  cd src/
  python app.py            # development
  flask run --debug        # hot-reload

  (or from the root fraud-detection-system/ folder)
  python src/app.py
"""

import os
import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify, abort
from sqlalchemy import create_engine, text

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/fraud_detection"
)

# fraud_model.pkl lives one level up from src/ (at project root)
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, "..", "fraud_model.pkl"))

# Feature order expected by the model  (must match training order exactly)
MODEL_FEATURES = [
    "Time",
    "V1","V2","V3","V4","V5","V6","V7","V8","V9","V10",
    "V11","V12","V13","V14","V15","V16","V17","V18","V19","V20",
    "V21","V22","V23","V24","V25","V26","V27","V28",
    "Amount"
]

# ─────────────────────────────────────────────────────────────────────────────
# App factory
# ─────────────────────────────────────────────────────────────────────────────

app    = Flask(__name__)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Load ML model once at startup (avoids disk I/O on every request)
try:
    model = joblib.load(MODEL_PATH)
    print(f"✅  Model loaded from {MODEL_PATH}")
except FileNotFoundError:
    model = None
    print(f"⚠️   Model not found at {MODEL_PATH} — /api/predict will return 503")


# ─────────────────────────────────────────────────────────────────────────────
# Helper: run a SQL query and return list-of-dicts
# ─────────────────────────────────────────────────────────────────────────────

def query(sql: str, params: dict = None) -> list[dict]:
    """Execute *sql* and return rows as a list of plain dicts."""
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params or {}).mappings().all()
    return [dict(r) for r in rows]


def scalar(sql: str, params: dict = None):
    """Execute *sql* and return the first column of the first row."""
    with engine.connect() as conn:
        return conn.execute(text(sql), params or {}).scalar()


# ─────────────────────────────────────────────────────────────────────────────
# PAGE ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    """
    Main dashboard — KPI cards are server-rendered for instant first paint.
    Charts are populated asynchronously by dashboard.js via /api/* endpoints.
    """
    # ── KPI queries ──────────────────────────────────────────────────────────
    total_txn = scalar("SELECT COUNT(*) FROM transactions") or 0

    fraud_count = scalar("""
        SELECT COUNT(*) FROM fraud_predictions WHERE predicted_label = 1
    """) or 0

    legit_count = total_txn - fraud_count

    fraud_rate = round((fraud_count / total_txn * 100), 2) if total_txn > 0 else 0.0

    total_amount = scalar("SELECT ROUND(SUM(amount)::NUMERIC, 2) FROM transactions") or 0.0

    fraud_amount = scalar("""
        SELECT ROUND(SUM(t.amount)::NUMERIC, 2)
        FROM transactions t
        JOIN fraud_predictions p ON t.transaction_id = p.transaction_id
        WHERE p.predicted_label = 1
    """) or 0.0

    # How many rows have BOTH predicted AND actual fraud (true positives)
    true_positives = scalar("""
        SELECT COUNT(*)
        FROM transactions t
        JOIN fraud_predictions p ON t.transaction_id = p.transaction_id
        WHERE t.fraud_flag = 1 AND p.predicted_label = 1
    """) or 0

    kpis = {
        "total_txn"    : f"{total_txn:,}",
        "fraud_count"  : f"{fraud_count:,}",
        "legit_count"  : f"{legit_count:,}",
        "fraud_rate"   : fraud_rate,
        "total_amount" : f"{total_amount:,.2f}",
        "fraud_amount" : f"{fraud_amount:,.2f}",
        "true_positives": f"{true_positives:,}",
    }

    return render_template("dashboard.html", kpis=kpis)


# ─────────────────────────────────────────────────────────────────────────────

@app.route("/alerts")
def alerts():
    """
    Fraud alerts page — every transaction the model flagged as fraud.
    Supports pagination and a filter toggle to show only 'True Positives'
    (where fraud_flag also equals 1).
    """
    page         = request.args.get("page", 1, type=int)
    per_page     = min(request.args.get("per_page", 50, type=int), 200)
    tp_only      = request.args.get("tp_only", "false").lower() == "true"
    offset       = (page - 1) * per_page

    extra_where = "AND t.fraud_flag = 1" if tp_only else ""

    rows = query(f"""
        SELECT
            t.transaction_id,
            t.transaction_time,
            ROUND(t.amount::NUMERIC, 2)   AS amount,
            t.fraud_flag,
            p.predicted_label,
            -- Convenience classification for template badges
            CASE
                WHEN t.fraud_flag = 1 AND p.predicted_label = 1 THEN 'TP'
                WHEN t.fraud_flag = 0 AND p.predicted_label = 1 THEN 'FP'
                ELSE 'OTHER'
            END AS result_type
        FROM transactions t
        JOIN fraud_predictions p ON t.transaction_id = p.transaction_id
        WHERE p.predicted_label = 1
        {extra_where}
        ORDER BY t.amount DESC
        LIMIT :limit OFFSET :offset
    """, {"limit": per_page, "offset": offset})

    total = scalar(f"""
        SELECT COUNT(*)
        FROM transactions t
        JOIN fraud_predictions p ON t.transaction_id = p.transaction_id
        WHERE p.predicted_label = 1
        {extra_where}
    """)

    import math
    pages = math.ceil(total / per_page) if total else 1

    return render_template(
        "alerts.html",
        rows=rows,
        total=total,
        page=page,
        pages=pages,
        per_page=per_page,
        tp_only=tp_only,
    )


# ─────────────────────────────────────────────────────────────────────────────

@app.route("/transactions")
def transactions():
    """
    Full transaction table with optional fraud-status filter.
    Joins with fraud_predictions to show both ground-truth and model label.
    """
    page       = request.args.get("page", 1, type=int)
    per_page   = min(request.args.get("per_page", 50, type=int), 200)
    status     = request.args.get("status", "all")   # all | fraud | legit
    offset     = (page - 1) * per_page

    status_where = {
        "fraud" : "AND p.predicted_label = 1",
        "legit" : "AND p.predicted_label = 0",
    }.get(status, "")

    rows = query(f"""
        SELECT
            t.transaction_id,
            t.transaction_time,
            ROUND(t.amount::NUMERIC, 2) AS amount,
            t.fraud_flag,
            p.predicted_label
        FROM transactions t
        LEFT JOIN fraud_predictions p ON t.transaction_id = p.transaction_id
        WHERE 1=1 {status_where}
        ORDER BY t.transaction_id ASC
        LIMIT :limit OFFSET :offset
    """, {"limit": per_page, "offset": offset})

    total = scalar(f"""
        SELECT COUNT(*)
        FROM transactions t
        LEFT JOIN fraud_predictions p ON t.transaction_id = p.transaction_id
        WHERE 1=1 {status_where}
    """)

    import math
    pages = math.ceil(total / per_page) if total else 1

    return render_template(
        "transactions.html",
        rows=rows,
        total=total,
        page=page,
        pages=pages,
        per_page=per_page,
        status=status,
    )


# ─────────────────────────────────────────────────────────────────────────────
# JSON API ROUTES  (consumed by Chart.js in dashboard.js)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/chart/fraud-split")
def api_fraud_split():
    """Doughnut chart — predicted fraud vs. legitimate counts."""
    fraud = scalar("SELECT COUNT(*) FROM fraud_predictions WHERE predicted_label = 1") or 0
    total = scalar("SELECT COUNT(*) FROM fraud_predictions") or 0
    return jsonify({
        "labels": ["Fraud", "Legitimate"],
        "values": [fraud, total - fraud],
    })


@app.route("/api/chart/amount-distribution")
def api_amount_distribution():
    """
    Bar chart — transaction count and fraud count bucketed by amount range.
    Buckets: <10 | 10–50 | 50–100 | 100–500 | 500–1000 | >1000
    """
    rows = query("""
        SELECT
            CASE
                WHEN t.amount < 10    THEN '< $10'
                WHEN t.amount < 50    THEN '$10–$50'
                WHEN t.amount < 100   THEN '$50–$100'
                WHEN t.amount < 500   THEN '$100–$500'
                WHEN t.amount < 1000  THEN '$500–$1k'
                ELSE '> $1k'
            END                                              AS bucket,
            COUNT(*)                                         AS total,
            SUM(CASE WHEN p.predicted_label = 1 THEN 1 ELSE 0 END) AS fraud
        FROM transactions t
        LEFT JOIN fraud_predictions p ON t.transaction_id = p.transaction_id
        GROUP BY 1
        ORDER BY MIN(t.amount)
    """)
    return jsonify({
        "labels": [r["bucket"] for r in rows],
        "total" : [r["total"]  for r in rows],
        "fraud" : [r["fraud"]  for r in rows],
    })


@app.route("/api/chart/confusion-matrix")
def api_confusion_matrix():
    """
    Returns TP / FP / TN / FN counts for the 2×2 confusion matrix card.
    """
    row = query("""
        SELECT
            SUM(CASE WHEN t.fraud_flag=1 AND p.predicted_label=1 THEN 1 ELSE 0 END) AS tp,
            SUM(CASE WHEN t.fraud_flag=0 AND p.predicted_label=1 THEN 1 ELSE 0 END) AS fp,
            SUM(CASE WHEN t.fraud_flag=1 AND p.predicted_label=0 THEN 1 ELSE 0 END) AS fn,
            SUM(CASE WHEN t.fraud_flag=0 AND p.predicted_label=0 THEN 1 ELSE 0 END) AS tn
        FROM transactions t
        JOIN fraud_predictions p ON t.transaction_id = p.transaction_id
    """)[0]
    return jsonify(row)


@app.route("/api/chart/top-amounts")
def api_top_amounts():
    """
    Horizontal bar — top 10 highest-amount fraud transactions.
    """
    rows = query("""
        SELECT
            t.transaction_id,
            ROUND(t.amount::NUMERIC, 2) AS amount
        FROM transactions t
        JOIN fraud_predictions p ON t.transaction_id = p.transaction_id
        WHERE p.predicted_label = 1
        ORDER BY t.amount DESC
        LIMIT 10
    """)
    return jsonify({
        "labels": [f"#{r['transaction_id']}" for r in rows],
        "values": [float(r["amount"]) for r in rows],
    })


# ─────────────────────────────────────────────────────────────────────────────
# LIVE PREDICTION ENDPOINT
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Score a single transaction on-the-fly with the loaded LogisticRegression.

    POST JSON body:
    {
      "Time": 0,
      "V1": -1.36, "V2": -0.07, ..., "V28": -0.02,
      "Amount": 149.62
    }

    Response:
    {
      "predicted_label": 1,
      "fraud_probability": 0.8731,
      "is_fraud": true
    }
    """
    if model is None:
        return jsonify({"error": "Model not loaded"}), 503

    payload = request.get_json(force=True, silent=True)
    if not payload:
        return jsonify({"error": "Invalid JSON"}), 400

    # Validate all required features are present
    missing = [f for f in MODEL_FEATURES if f not in payload]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    try:
        X    = pd.DataFrame([{f: payload[f] for f in MODEL_FEATURES}])
        prob = float(model.predict_proba(X)[0][1])   # P(fraud)
        pred = int(model.predict(X)[0])
        return jsonify({
            "predicted_label"   : pred,
            "fraud_probability" : round(prob, 4),
            "is_fraud"          : pred == 1,
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)