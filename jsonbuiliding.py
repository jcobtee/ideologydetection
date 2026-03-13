"""
JSON Builder – Einheitlicher Konverter für US und NS Filme
===========================================================
Verarbeitet beide Gruppen nach demselben Prinzip:
Satzbasierte Aufteilung → konsistente Blockgröße.

Voraussetzung: US-SRT-Dateien wurden bereits mit srt_to_txt.py
               in "us_subs_txt/" konvertiert.

US-Filme:   "us_subs_txt/"   (.txt) → "us_subs_json/"
NS-Filme:   "nazi subs/"     (.txt) → "nazi_subs_json/"
"""

import os
import re
import json

# ─────────────────────────────────────────────
# KONFIGURATION
# ─────────────────────────────────────────────

QUELLEN = [
    {
        "input_dir":  "us_subs_txt",
        "output_dir": "us_subs_json",
        "group":      "us subs",
    },
    {
        "input_dir":  "nazi subs",
        "output_dir": "nazi_subs_json",
        "group":      "nazi subs",
    },
]

SENTENCES_PER_BLOCK = 10  # Gilt einheitlich für beide Gruppen

# ─────────────────────────────────────────────
# PARSER
# ─────────────────────────────────────────────

def parse_txt(filepath):
    """Liest eine TXT-Datei und gibt eine Liste von Sätzen zurück."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Metadaten entfernen
    content = re.sub(r'\[.*?\]', '', content)
    content = re.sub(r'untertitel.*?20\d\d', '', content, flags=re.IGNORECASE)
    content = re.sub(r'(zdf|ard|ndr|wdr|mdr)[\w\s]*', '', content, flags=re.IGNORECASE)

    # Zeilenumbrüche normalisieren
    content = content.replace('\n', ' ').replace('\r', ' ')
    content = re.sub(r' +', ' ', content).strip()

    # Auslassungspunkte schützen
    content = content.replace('...', '###')

    # Nach echten Satzenden splitten
    sentences = re.split(r'(?<=[.!?])\s+', content)

    # Auslassungspunkte wiederherstellen, leere Einträge entfernen
    sentences = [s.replace('###', '...').strip() for s in sentences if s.strip()]

    return sentences

# ─────────────────────────────────────────────
# JSON BUILDER
# ─────────────────────────────────────────────

def baue_json(filepath, film_name, source_group):
    """Baut ein strukturiertes JSON-Objekt aus einer TXT-Datei."""
    sentences = parse_txt(filepath)

    blocks = []
    for i in range(0, len(sentences), SENTENCES_PER_BLOCK):
        block_sentences = sentences[i:i + SENTENCES_PER_BLOCK]
        block_text      = " ".join(block_sentences)
        blocks.append({
            "film":         film_name,
            "source_group": source_group,
            "block_id":     len(blocks) + 1,
            "text":         block_text,
        })

    return {
        "film":         film_name,
        "source_group": source_group,
        "n_blocks":     len(blocks),
        "blocks":       blocks,
    }

# ─────────────────────────────────────────────
# AUSFÜHREN
# ─────────────────────────────────────────────

for quelle in QUELLEN:
    input_dir  = quelle["input_dir"]
    output_dir = quelle["output_dir"]
    group      = quelle["group"]

    os.makedirs(output_dir, exist_ok=True)

    dateien = sorted([f for f in os.listdir(input_dir) if f.endswith(".txt")])
    print(f"\n── {group} ({len(dateien)} Dateien) → '{output_dir}/' ──\n")

    for dateiname in dateien:
        input_path  = os.path.join(input_dir, dateiname)
        film_name   = dateiname.replace(".txt", "")
        output_path = os.path.join(output_dir, f"{film_name}.json")

        if os.path.exists(output_path):
            print(f"  ⏭  Bereits vorhanden: {film_name}")
            continue

        daten = baue_json(input_path, film_name, group)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(daten, f, ensure_ascii=False, indent=2)

        print(f"  ✓ {film_name} ({daten['n_blocks']} Blöcke, {daten['n_blocks'] * SENTENCES_PER_BLOCK} Sätze)")

print("\nFertig!")