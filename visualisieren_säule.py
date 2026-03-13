import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------
# Ausgabeordner
# -------------------------

output_dir = "ergebnisse_visualisiert"
os.makedirs(output_dir, exist_ok=True)

# -------------------------
# Daten laden
# -------------------------

with open("gpt_ergebnisse3/zusammenfassung.json", "r", encoding="utf-8") as f:
    films = json.load(f)

# -------------------------
# DataFrame erstellen
# -------------------------

rows = []

for film in films:
    row = {"source": film["source_group"]}
    row.update(film["scores"])
    rows.append(row)

df = pd.DataFrame(rows)

categories = [
    "totalitarianism",
    "national_honour",
    "racial_superiority",
    "freedom_from_tyranny",
    "universal_equality",
    "guardian_of_civilization",
    "necessity_of_war",
    "enemy_imagery",
    "heroism_sacrifice",
]

# -------------------------
# Mittelwerte pro Gruppe
# -------------------------

group_means = df.groupby("source")[categories].mean()

us_scores = group_means.loc["us subs"]
ns_scores = group_means.loc["nazi subs"]



# -------------------------
# Säulendiagramm - Sortierte Kategorien
# -------------------------

# 1. Definierte Reihenfolge festlegen
sorted_categories = [
    # "Nazi" Kategorien
    "totalitarianism", 
    "racial_superiority", 
    "national_honour",
    # "USA" Kategorien
    "freedom_from_tyranny", 
    "universal_equality", 
    "guardian_of_civilization",
    "necessity_of_war",
    # Neutrale / Gemeinsame Kategorien
    "enemy_imagery", 
    "heroism_sacrifice"
]

# 2. Scores basierend auf der neuen Reihenfolge extrahieren
us_vals = [us_scores[cat] for cat in sorted_categories]
ns_vals = [ns_scores[cat] for cat in sorted_categories]

# 3. Plotting
x = np.arange(len(sorted_categories))
width = 0.35

plt.figure(figsize=(14, 7), facecolor="white")
ax = plt.gca()
ax.set_facecolor("#fcfcfc")

# Balken zeichnen
plt.bar(x - width/2, us_vals, width, label="US Filme", color="#219ebc", edgecolor="white")
plt.bar(x + width/2, ns_vals, width, label="NS Filme", color="#e76f51", edgecolor="white")

# Formatierung
# Labels für die X-Achse (Unterstriche durch Zeilenumbrüche für bessere Lesbarkeit ersetzen)
clean_labels = [c.replace("_", "\n") for c in sorted_categories]

plt.xticks(x, clean_labels, fontsize=10)
plt.ylabel("Durchschnittlicher Score (0-10)", fontweight='bold')
plt.title("Ideologische Profile im Vergleich (Thematisch sortiert)", fontsize=14, pad=20, fontweight='bold')
plt.legend(frameon=True, shadow=True)

# Hilfslinien für bessere Ablesbarkeit der Werte
ax.yaxis.grid(True, linestyle='--', alpha=0.7)
ax.set_axisbelow(True) # Gitter hinter die Balken legen

plt.tight_layout()
plt.savefig(f"{output_dir}/saeulendiagramm_sortiert.png", dpi=300)
plt.show()