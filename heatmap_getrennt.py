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

with open("gpt_ergebnisse/zusammenfassung.json", "r", encoding="utf-8") as f:
    films = json.load(f)

# -------------------------
# Konfiguration
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

category_labels = [c.replace("_", "\n") for c in categories]

COLOR_US = "#219ebc"
COLOR_NS = "#e76f51"



# -------------------------
# Hilfsfunktion: Heatmap
# -------------------------

def plot_heatmap(group_films, title, filename, color):
    # Namen kürzen
    labels = [f["film"] for f in group_films]
    matrix = np.array([[f["scores"][cat] for cat in categories] for f in group_films])

    n = len(group_films)
    fig, ax = plt.subplots(figsize=(14, max(8, n * 0.38 + 2)), facecolor="white")
    ax.set_facecolor("#fcfcfc")

    # Eigene Colormap basierend auf Gruppenfarbe
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("custom", ["#f7f7f7", color], N=256)

    im = ax.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=3)

    # Achsen
    ax.set_xticks(np.arange(len(categories)))
    ax.set_xticklabels(category_labels, fontsize=9)
    ax.set_yticks(np.arange(n))
    ax.set_yticklabels(labels, fontsize=9)

    # Werte in Zellen
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix[i, j]
            text_color = "white" if val > 1.8 else "#333333"
            ax.text(j, i, f"{val:.1f}", ha="center", va="center",
                    fontsize=8, color=text_color)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.02, pad=0.02)
    cbar.set_label("Score (0–3)", fontsize=10, fontweight="bold")

    ax.set_title(title, fontsize=14, pad=20, fontweight="bold")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/{filename}", dpi=300, bbox_inches="tight")
    plt.show()
    print(f"✓ {filename} gespeichert.")

# -------------------------
# Heatmaps erstellen
# -------------------------

us_films = [f for f in films if f["source_group"] == "us subs"]
ns_films = [f for f in films if f["source_group"] == "nazi subs"]

plot_heatmap(
    us_films,
    title="Ideologische Scores – US Filme",
    filename="heatmap_us.png",
    color=COLOR_US,
)

plot_heatmap(
    ns_films,
    title="Ideologische Scores – NS Filme",
    filename="heatmap_ns.png",
    color=COLOR_NS,
)
