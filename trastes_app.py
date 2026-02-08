from flask import Flask, request, render_template_string, redirect, url_for
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

EXCEL_FILE = "huishoud_log.xlsx"

# Maak Excel-bestand aan als het nog niet bestaat
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["activiteit", "persoon", "datum", "tijd"])
    df.to_excel(EXCEL_FILE, index=False)

HTML = """
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <title>Huishoudlog</title>

    <!-- 🌙 Dark mode -->
    <style>
        body {
            background-color: #121212;
            color: #e0e0e0;
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 20px;
        }
        select, button {
            padding: 10px;
            margin: 8px;
            font-size: 16px;
            background-color: #1e1e1e;
            color: white;
            border: 1px solid #333;
            border-radius: 5px;
        }
        button {
            cursor: pointer;
        }
        table {
            margin: auto;
            border-collapse: collapse;
            width: 90%;
        }
        th, td {
            border: 1px solid #333;
            padding: 8px;
        }
        th {
            background-color: #1f1f1f;
        }
    </style>

    <!-- 🎉 Confetti -->
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
</head>
<body>

    <h1>Huishoudelijke taken</h1>

    <form method="POST" onsubmit="confettiStart()">
        <select name="activiteit" required>
            <option value="">Kies een activiteit</option>
            <option value="Afwas gedaan">Ik heb de afwas gedaan</option>
            <option value="Afgedroogd">Ik heb afgedroogd</option>
            <option value="Gekookt">Ik heb gekookt</option>
        </select>

        <select name="persoon" required>
            <option value="">Wie?</option>
            <option value="Monze">Monze</option>
            <option value="Nelson">Nelson</option>
            <option value="Samen">Samen</option>
        </select>

        <br>
        <button type="submit">Opslaan</button>
    </form>

    <h2>Logboek</h2>

    <table>
        <tr>
            <th>Activiteit</th>
            <th>Persoon</th>
            <th>Datum</th>
            <th>Tijd</th>
        </tr>
        {% for _, rij in data.iterrows() %}
        <tr>
            <td>{{ rij.activiteit }}</td>
            <td>{{ rij.persoon }}</td>
            <td>{{ rij.datum }}</td>
            <td>{{ rij.tijd }}</td>
        </tr>
        {% endfor %}
    </table>

    <script>
        function confettiStart() {
            confetti({
                particleCount: 150,
                spread: 80,
                origin: { y: 0.6 }
            });
        }
    </script>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        activiteit = request.form["activiteit"]
        persoon = request.form["persoon"]

        nu = datetime.now()
        datum = nu.strftime("%Y-%m-%d")
        tijd = nu.strftime("%H:%M:%S")

        df = pd.read_excel(EXCEL_FILE)
        df.loc[len(df)] = [activiteit, persoon, datum, tijd]
        df.to_excel(EXCEL_FILE, index=False)

        return redirect(url_for("index"))

    df = pd.read_excel(EXCEL_FILE)
    return render_template_string(HTML, data=df)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
