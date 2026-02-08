from flask import Flask, request, render_template_string, redirect, url_for
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os
import json
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# --- Google Sheets setup using environment variable ---
creds_json = os.environ.get("GOOGLE_CREDENTIALS")
if not creds_json:
    raise Exception("Environment variable GOOGLE_CREDENTIALS not found!")

creds_dict = json.loads(creds_json)
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
CREDS = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
CLIENT = gspread.authorize(CREDS)

SHEET_ID = "1OCs9FrtgBBpgNjUNYEIPQkIXe-vH54mJtjk5gYV9iFo"
SHEET = CLIENT.open_by_key(SHEET_ID).sheet1

# --- HTML template ---
HTML = """
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <title>Huishoudlog</title>
    <style>
        body {background-color:#121212; color:#e0e0e0; font-family:Arial,sans-serif; text-align:center; padding:20px;}
        select,button {padding:10px;margin:8px;font-size:16px;background-color:#1e1e1e;color:white;border:1px solid #333;border-radius:5px;}
        button{cursor:pointer;}
        table{margin:auto;border-collapse:collapse;width:90%;}
        th,td{border:1px solid #333;padding:8px;}
        th{background-color:#1f1f1f;}
        img {margin: 20px 0; max-width: 80%;}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
</head>
<body>

<h1>Huishoudelijke taken</h1>

<form method="POST" onsubmit="confettiStart()">
    <select name="activiteit" required>
        <option value="">📝Kies een activiteit</option>
        <option value="Afwas gedaan">🧼 Ik heb de afwas gedaan</option>
        <option value="Afgedroogd">Ik heb afgedroogd</option>
        <option value="Gekookt">🍳 Ik heb gekookt</option>
    </select>

    <select name="persoon" required>
        <option value="">👤 Wie?</option>
        <option value="Monze">Monze</option>
        <option value="Nelson">Nelson</option>
        <option value="Samen">🤝 Samen</option>
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

<h2>Percentage grafieken per activiteit</h2>
{% for activiteit, img in graphs.items() %}
<h3>{{ activiteit }}</h3>
<img src="data:image/png;base64,{{ img }}" alt="{{ activiteit }}">
{% endfor %}

<script>
function confettiStart() {
    confetti({particleCount:150,spread:80,origin:{y:0.6}});
}
</script>

</body>
</html>
"""

# --- Helper function to convert Matplotlib figure to base64 ---
def plot_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', facecolor='#121212')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        activiteit = request.form["activiteit"]
        persoon = request.form["persoon"]
        nu = datetime.now()
        datum = nu.strftime("%Y-%m-%d")
        tijd = nu.strftime("%H:%M:%S")
        SHEET.append_row([activiteit, persoon, datum, tijd])
        return redirect(url_for("index"))

    records = SHEET.get_all_records()
    df = pd.DataFrame(records)

    # --- Generate pie charts per activity ---
    graphs = {}
    if not df.empty:
        for activiteit in df['activiteit'].unique():
            df_activity = df[df['activiteit'] == activiteit]
            counts = df_activity['persoon'].value_counts()
            fig, ax = plt.subplots()
            ax.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=['#00FFFF','#FF00FF','#FFFF00'], textprops={'color':'white'})
            ax.set_title(f"{activiteit} - percentage per persoon", color='white')
            graphs[activiteit] = plot_to_base64(fig)

    return render_template_string(HTML, data=df, graphs=graphs)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
