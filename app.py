'''from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

DB_PATH = "iomt.db"

# ===================== FETCH DATA =====================
def get_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT device_id, heart_rate, timestamp, status
        FROM heart_rate_data
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()
    conn.close()

    data = []
    for r in rows:
        data.append({
            "device_id": r[0],
            "heart_rate": r[1],
            "timestamp": r[2],
            "status": r[3]
        })

    return data

# ===================== ROUTES =====================

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/data")
def data():
    return jsonify(get_data())

# ===================== RUN =====================

if __name__ == "__main__":
    print("📊 Dashboard running at http://127.0.0.1:5000")
    app.run(debug=True)
    '''




from flask import Flask, render_template, jsonify, send_file
import sqlite3
import io
from reportlab.platypus import SimpleDocTemplate, Table

app = Flask(__name__)

DB_PATH = "iomt.db"

# ===================== FETCH DATA =====================
def get_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT device_id, heart_rate, status, timestamp
        FROM heart_rate_data
        ORDER BY id DESC LIMIT 20
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows

# ===================== HOME =====================
@app.route("/")
def index():
    return render_template("index.html")

# ===================== API =====================
@app.route("/data")
def data():
    rows = get_data()

    result = []
    for r in rows:
        result.append({
            "device": r[0],
            "heart_rate": r[1],
            "status": r[2],
            "timestamp": r[3]
        })

    return jsonify(result)

# ===================== PDF EXPORT =====================
@app.route("/export")
def export_pdf():
    rows = get_data()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    table_data = [["Device", "Heart Rate", "Status", "Timestamp"]]
    for r in rows:
        table_data.append(list(r))

    table = Table(table_data)
    doc.build([table])

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="report.pdf")

# ===================== ATTACK SIM =====================
@app.route("/attack")
def attack():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO heart_rate_data
        (device_id, heart_rate, timestamp, nonce, encrypted_data, hmac_value, signature, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "FAKE_DEVICE",
        None,
        9999999999,
        "fake_nonce",
        "tampered_data",
        "bad_hmac",
        "bad_sig",
        "TAMPERED"
    ))

    conn.commit()
    conn.close()

    return "Attack Injected!"

# ===================== RUN =====================
if __name__ == "__main__":
    app.run(debug=True)