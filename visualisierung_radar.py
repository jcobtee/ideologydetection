import json
import os
import numpy as np
import matplotlib.pyplot as plt

# -------------------------
# Ausgabeordner
# -------------------------

output_dir = "ergebnisse_visualisiert"
os.makedirs(output_dir, exist_ok=True)

# -------------------------
# Daten laden
# -------------------------

with open("gpt_ergebnisse2/zusammenfassung.json", "r", encoding="utf-8") as f:
    films = json.load(f)

# -------------------------
# Daten vorbereiten
# -------------------------

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

category_labels = [
    "Totalitarianism",
    "National\nHonour",
    "Racial\nSuperiority",
    "Freedom from\nTyranny",
    "Universal\nEquality",
    "Guardian of\nCivilization",
    "Necessity\nof War",
    "Enemy\nImagery",
    "Heroism &\nSacrifice",
]

us_films = [f for f in films if f["source_group"] == "us subs"]
ns_films = [f for f in films if f["source_group"] == "nazi subs"]

us_means = [np.mean([f["scores"][cat] for f in us_films]) for cat in categories]
ns_means = [np.mean([f["scores"][cat] for f in ns_films]) for cat in categories]

# Radar braucht geschlossene Kurve
N = len(categories)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]

us_vals = us_means + us_means[:1]
ns_vals = ns_means + ns_means[:1]

# -------------------------
# Radardiagramm
# -------------------------

COLOR_US = "#219ebc"
COLOR_NS = "#e76f51"

fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True), facecolor="white")
ax.set_facecolor("#fcfcfc")

# Linien und Flächen
ax.plot(angles, us_vals, color=COLOR_US, linewidth=2, linestyle="solid", label="US Filme")
ax.fill(angles, us_vals, color=COLOR_US, alpha=0.15)

ax.plot(angles, ns_vals, color=COLOR_NS, linewidth=2, linestyle="solid", label="NS Filme")
ax.fill(angles, ns_vals, color=COLOR_NS, alpha=0.15)

# Achsenbeschriftung
ax.set_xticks(angles[:-1])
ax.set_xticklabels(category_labels, fontsize=10)

# Skala
ax.set_ylim(0, 3)
ax.set_yticks([0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
ax.set_yticklabels(["0.5", "1.0", "1.5", "2.0", "2.5", "3.0"], fontsize=8, color="gray")
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.xaxis.grid(True, linestyle="--", alpha=0.3)

# Legende & Titel
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=11, frameon=True, shadow=True)
ax.set_title("Ideologische Profile im Vergleich\n(Durchschnittliche Scores)", 
             fontsize=14, fontweight="bold", pad=20)

plt.tight_layout()
plt.savefig(f"{output_dir}/radardiagramm.png", dpi=300, bbox_inches="tight")
plt.show()
print("Radardiagramm gespeichert.")
