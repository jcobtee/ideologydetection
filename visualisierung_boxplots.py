import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

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

# Farben (aus dem Säulendiagramm übernommen)
COLOR_US = "#219ebc"
COLOR_NS = "#e76f51"

# -------------------------
# Boxplots
# -------------------------

fig, axes = plt.subplots(3, 3, figsize=(16, 12), facecolor="white")
fig.suptitle("Verteilung ideologischer Scores – US vs. NS Filme", fontsize=15, fontweight="bold", y=1.01)

axes_flat = axes.flatten()

for i, cat in enumerate(categories):
    ax = axes_flat[i]
    ax.set_facecolor("#fcfcfc")

    us_vals = df[df["source"] == "us subs"][cat].values
    ns_vals = df[df["source"] == "nazi subs"][cat].values

    bp = ax.boxplot(
        [us_vals, ns_vals],
        patch_artist=True,
        widths=0.5,
        medianprops=dict(color="white", linewidth=2),
        whiskerprops=dict(linewidth=1.2),
        capprops=dict(linewidth=1.2),
        flierprops=dict(marker="o", markersize=4, linestyle="none", alpha=0.6),
    )

    bp["boxes"][0].set_facecolor(COLOR_US)
    bp["boxes"][0].set_alpha(0.85)
    bp["fliers"][0].set_markerfacecolor(COLOR_US)
    bp["fliers"][0].set_markeredgecolor(COLOR_US)

    bp["boxes"][1].set_facecolor(COLOR_NS)
    bp["boxes"][1].set_alpha(0.85)
    bp["fliers"][1].set_markerfacecolor(COLOR_NS)
    bp["fliers"][1].set_markeredgecolor(COLOR_NS)

    # Einzelpunkte (Jitter) drüberzeichnen
    jitter = 0.08
    ax.scatter(np.random.normal(1, jitter, len(us_vals)), us_vals,
               color=COLOR_US, alpha=0.4, s=18, zorder=3)
    ax.scatter(np.random.normal(2, jitter, len(ns_vals)), ns_vals,
               color=COLOR_NS, alpha=0.4, s=18, zorder=3)

    ax.set_xticks([1, 2])
    ax.set_xticklabels(["US", "NS"], fontsize=10)
    ax.set_title(cat.replace("_", " ").title(), fontsize=10, fontweight="bold", pad=6)
    ax.set_ylim(-0.2, 3.3)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=8)

# Legende
legend_elements = [
    Patch(facecolor=COLOR_US, alpha=0.85, label="US Filme"),
    Patch(facecolor=COLOR_NS, alpha=0.85, label="NS Filme"),
]
fig.legend(handles=legend_elements, loc="upper right", fontsize=11,
           frameon=True, shadow=True, bbox_to_anchor=(1.0, 1.0))

plt.tight_layout()
plt.savefig(f"{output_dir}/boxplots.png", dpi=300, bbox_inches="tight")
plt.show()
print("Boxplots gespeichert.")
