"""
SRT → TXT Konverter
====================
Konvertiert alle SRT-Untertiteldateien in saubere TXT-Dateien.

US-Filme: "us subs/" (.srt) → "us_subs_txt/"
"""

import os
import re

# ─────────────────────────────────────────────
# KONFIGURATION
# ─────────────────────────────────────────────

INPUT_DIR  = "us subs"
OUTPUT_DIR = "us_subs_txt"

# ─────────────────────────────────────────────
# PARSER
# ─────────────────────────────────────────────

def srt_to_clean_text(filepath):
    """Extrahiert reinen Dialogtext aus einer SRT-Datei als zusammenhängenden String."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Zeitstempel entfernen
    content = re.sub(r'\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}', '', content)
    # Blocknummern entfernen
    content = re.sub(r'^\d+$', '', content, flags=re.MULTILINE)
    # HTML-Tags entfernen
    content = re.sub(r'<[^>]+>', '', content)
    # Eckige Klammern entfernen
    content = re.sub(r'\[.*?\]', '', content)
    # Zeilenumbrüche zu Leerzeichen
    content = content.replace('\n', ' ').replace('\r', ' ')
    # Mehrfache Leerzeichen bereinigen
    content = re.sub(r' +', ' ', content).strip()

    return content

# ─────────────────────────────────────────────
# AUSFÜHREN
# ─────────────────────────────────────────────

os.makedirs(OUTPUT_DIR, exist_ok=True)

dateien = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith(".srt")])
print(f"\n── US Subs ({len(dateien)} Dateien) → '{OUTPUT_DIR}/' ──\n")

for dateiname in dateien:
    input_path  = os.path.join(INPUT_DIR, dateiname)
    film_name   = dateiname.replace(".srt", "")
    output_path = os.path.join(OUTPUT_DIR, f"{film_name}.txt")

    text = srt_to_clean_text(input_path)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"  ✓ {film_name}")

print("\nFertig!")