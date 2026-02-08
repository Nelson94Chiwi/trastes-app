from flask import Flask, request, render_template_string
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt

app = Flask(__name__)

EXCEL_FILE = "trastes.xlsx"
GRAPH_FILE = "static/grafiek.png"

os.makedirs("static", exist_ok=True)

# Maak Excel bestand aan als het niet bestaat
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=["activiteit", "persoon", "datum", "tijd"])
    df.to_excel(EXCEL_FILE, index=False)

# Activiteiten en personen
ACTIVITEITEN = [
    "Afgewassen",
    "Afgedroogd",
    "Gekookt"
]

PERSONEN = [
    "Nelson",
    "Monze",
    "Beide"
]

# HTML met dark mode
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Taakregistratie</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #e0e0e0;
            text-align: center;
            padding: 20px;
        }

        h2 { color: #ffffff; }

        select, button {
            width: 85%;
            padding: 14px;
            margin: 10px 0;
            font-size: 16px;
            border-radius: 10px;
            border: none;
        }

        select {
            background-color: #1e1e1e;
            color: #ffffff;
            border: 1px solid #333;
        }

        button {
            background-color: #2a2a2a;
            color: #ffffff;
            cursor: pointer;
        }

        button:hover { background-color: #3a3a3a; }

        hr { border: 1px solid #333; margin: 30px 0; }

        img {
            max-width: 95%;
            margin-top: 20px;
            border-radius: 12px;
            background-color: #ffffff;
            padding: 10px;
        }

        p { color: #8aff8a; font-weight: bold; }
    </style>
</head>
<body>
    <h2>🧽🍳 Taakregistratie</h2>

    <form method="post">
        <select name="persoon" required>
            <option value="">Selecteer persoon</option>
            {% for p in personen %}
            <option value="{{ p }}">{{ p }}</option>
            {% endfor %}
        </select>

        <button name="activiteit" value="Afgewassen">🧽 Afgewassen</button>
        <button name="activiteit" value="Afgedroogd">🍽️ Afgedroogd</button>
        <button name="activiteit" value="Gekookt">🍳 Gekookt</button>
    </form>

    <hr>

    <h2>📊 Statistieken</h2>

    <form method="post">
        <select name="activiteit_stats" required>
            <option value="">Selecteer activiteit</option>
            {% for act in activiteiten %}
            <option value="{{ act }}">{{ act }}</option>
            {% endfor %}
        </select>

        <button type="submit">Bekijk percentages</button>
    </form>

    {% if grafiek %}
        <img src="{{ grafiek }}">
    {% endif %}

    {% if bericht %}
        <p>{{ bericht }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    bericht = None
    grafiek = None

    df = pd.read_excel(EXCEL_FILE)

    if request.method == "POST":

        # Activiteit registreren
        if "activiteit" in request.form:
            persoon = request.form["persoon"]
            activiteit = request.form["activiteit"]
            nu = datetime.now()

            rijen = []

            if persoon == "Beide":
                for p in ["Nelson", "Monze"]:
                    rijen.append({
                        "activiteit": activiteit,
                        "persoon": p,
                        "datum": nu.date().isoformat(),
                        "tijd": nu.time().strftime("%H:%M:%S")
                    })
            else:
                rijen.append({
                    "activiteit": activiteit,
                    "persoon": persoon,
                    "datum": nu.date().isoformat(),
                    "tijd": nu.time().strftime("%H:%M:%S")
                })

            df = pd.concat([df, pd.DataFrame(rijen)], ignore_index=True)
            df.to_excel(EXCEL_FILE, index=False)

            bericht = "✅ Registratie opgeslagen"

        # Statistieken
        if "activiteit_stats" in request.form:
            act = request.form["activiteit_stats"]
            data = df[df["activiteit"] == act]

            if not data.empty:
                counts = data["persoon"].value_counts()
                percentages = counts / counts.sum() * 100

                plt.figure()
                plt.pie(
                    percentages,
                    labels=percentages.index,
                    autopct="%1.1f%%",
                    startangle=90
                )
                plt.title(f"Percentage '{act}'")
                plt.tight_layout()
                plt.savefig(GRAPH_FILE)
                plt.close()

                grafiek = GRAPH_FILE
            else:
                bericht = "⚠️ Geen gegevens voor deze activiteit"

    return render_template_string(
        HTML,
        bericht=bericht,
        grafiek=grafiek,
        activiteiten=ACTIVITEITEN,
        personen=PERSONEN
    )

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

