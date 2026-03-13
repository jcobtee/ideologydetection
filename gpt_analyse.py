"""
GPT Ideologie-Analyse – NS vs. US Propagandafilme
==================================================
Nimmt JSON-Blöcke aus us_subs_json/ und nazi_subs_json/
und kategorisiert sie nach ideologischen Mustern.

Voraussetzungen:
    pip install openai

API Key setzen:
    export OPENAI_API_KEY="dein_key_hier"
"""

import os
import json
import time
import glob
from openai import OpenAI

# ─────────────────────────────────────────────
# 1. KONFIGURATION
# ─────────────────────────────────────────────

QUELLEN = [
    {"input_dir": "us_subs_json",   "group": "us subs"},
    {"input_dir": "nazi_subs_json", "group": "nazi subs"},
]

OUTPUT_DIR       = "gpt_ergebnisse3"
MODEL            = "gpt-4.1-mini-2025-04-14"
BLOCKS_PER_CHUNK = 10  

# ─────────────────────────────────────────────
# 2. SETUP
# ─────────────────────────────────────────────

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("⚠ OPENAI_API_KEY nicht gesetzt!")
    print("  export OPENAI_API_KEY='dein_key_hier'")
    exit(1)

client = OpenAI(api_key=api_key)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# 3. PROMPT
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert in film history, propaganda analysis, and ideology studies 
specializing in World War II era films. Your task is to analyze subtitle excerpts from wartime 
films for ideological content, using the analytical framework from Howard, Benjamin: 
'War of the Films: A Comparative Analysis of World War II Propaganda Film'.

For each text excerpt, rate the presence of the following ideological categories on a scale of 0-3:
0 = not present
1 = weakly present / implicit
2 = moderately present
3 = strongly present / explicit

GERMAN FILM CATEGORIES (Howard):
- totalitarianism: Glorification of obedience, subordination of the individual to state/party/leader, 
  dissent portrayed as weakness or treason
- national_honour: Self-sacrifice for the nation as highest virtue, glorification of military 
  achievement, shame and restoration as narrative drive
- racial_superiority: Hierarchization of human groups, dehumanization of enemies, 
  purity ideology, biologically justified exclusion

AMERICAN FILM CATEGORIES (Howard):
- freedom_from_tyranny: Axis powers as existential threat to free societies, war as defense 
  not aggression, democratic values as universally worth protecting [PRIMARY CATEGORY]
- universal_equality: Emphasis on shared human dignity, multiculturalism as American strength, 
  common humanity across borders
- guardian_of_civilization: America as moral world power, duty to intervene, 
  self-image as liberator
- necessity_of_war: Justification of war involvement, isolation no longer tenable, 
  entry into war as unavoidable response

SHARED CATEGORIES (applicable to both):
- enemy_imagery: Dehumanization or demonization of enemies, threat construction
- heroism_sacrifice: Glorification of self-sacrifice, duty, military heroism, dying for the cause

Respond ONLY with a valid JSON object in exactly this format, no other text:
{
  "totalitarianism": 0,
  "national_honour": 0,
  "racial_superiority": 0,
  "freedom_from_tyranny": 0,
  "universal_equality": 0,
  "guardian_of_civilization": 0,
  "necessity_of_war": 0,
  "enemy_imagery": 0,
  "heroism_sacrifice": 0,
  "reasoning": "brief explanation in 1-2 sentences"
}"""

# ─────────────────────────────────────────────
# 4. ANALYSEFUNKTIONEN
# ─────────────────────────────────────────────

KATEGORIEN = [
    "totalitarianism", "national_honour", "racial_superiority",
    "freedom_from_tyranny", "universal_equality", "guardian_of_civilization",
    "necessity_of_war", "enemy_imagery", "heroism_sacrifice"
]

def analysiere_chunk(text, film_name, chunk_id):
    """Schickt einen Textchunk an GPT und gibt Scores zurück."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": f"Film: {film_name}\n\nSubtitle excerpt:\n{text}"}
            ],
        )
        content = response.choices[0].message.content.strip()
        # JSON aus der Antwort extrahieren
        content = content[content.find("{"):content.rfind("}") + 1]
        result  = json.loads(content)
        result["chunk_id"] = chunk_id
        return result
    except Exception as e:
        print(f"    ✗ Fehler bei Chunk {chunk_id}: {e}")
        return None


def analysiere_film(json_path):
    """Analysiert einen Film und gibt aggregierte Scores zurück."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    film_name = data["film"]
    source    = data["source_group"]
    blocks    = data["blocks"]

    print(f"\n  [{source}] {film_name} ({len(blocks)} Blöcke)")

    # Blöcke zu Chunks zusammenfassen
    chunks = []
    for i in range(0, len(blocks), BLOCKS_PER_CHUNK):
        chunk_text = " ".join([b["text"] for b in blocks[i:i + BLOCKS_PER_CHUNK]])
        chunks.append((i // BLOCKS_PER_CHUNK + 1, chunk_text))

    # Jeden Chunk analysieren
    chunk_results = []
    for chunk_id, chunk_text in chunks:
        print(f"    Chunk {chunk_id}/{len(chunks)}...", end=" ", flush=True)
        result = analysiere_chunk(chunk_text, film_name, chunk_id)
        if result:
            chunk_results.append(result)
            print("✓")
        else:
            print("✗")
        time.sleep(0.3)

    if not chunk_results:
        print("  ⚠ Keine Ergebnisse für diesen Film")
        return None

    # Durchschnitt über alle Chunks
    aggregiert = {
        kat: round(sum(r[kat] for r in chunk_results if kat in r) / len(chunk_results), 3)
        for kat in KATEGORIEN
    }

    return {
        "film":          film_name,
        "source_group":  source,
        "n_chunks":      len(chunk_results),
        "scores":        aggregiert,
        "chunk_details": chunk_results,
    }

# ─────────────────────────────────────────────
# 5. ALLE FILME VERARBEITEN
# ─────────────────────────────────────────────

alle_ergebnisse = []

for quelle in QUELLEN:
    input_dir = quelle["input_dir"]
    json_files = sorted(glob.glob(os.path.join(input_dir, "*.json")))

    if not json_files:
        print(f"⚠ Keine JSON-Dateien in '{input_dir}'")
        continue

    print(f"\n{'═'*60}")
    print(f"{quelle['group'].upper()} – {len(json_files)} Filme")
    print(f"{'═'*60}")

    for json_path in json_files:
        film_name   = os.path.basename(json_path).replace(".json", "")
        output_path = os.path.join(OUTPUT_DIR, f"{film_name}_analyse.json")

        # Überspringen falls schon analysiert
        if os.path.exists(output_path):
            print(f"  ⏭  Bereits vorhanden: {film_name}")
            with open(output_path, 'r') as f:
                alle_ergebnisse.append(json.load(f))
            continue

        ergebnis = analysiere_film(json_path)
        if ergebnis:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(ergebnis, f, ensure_ascii=False, indent=2)
            alle_ergebnisse.append(ergebnis)

# ─────────────────────────────────────────────
# 6. ZUSAMMENFASSUNG
# ─────────────────────────────────────────────

nazi_filme = [e for e in alle_ergebnisse if "nazi" in e.get("source_group", "")]
us_filme   = [e for e in alle_ergebnisse if "us"   in e.get("source_group", "")]

def mittelwert(filme, kat):
    werte = [f["scores"][kat] for f in filme if kat in f.get("scores", {})]
    return round(sum(werte) / len(werte), 3) if werte else 0.0

print(f"\n{'═'*65}")
print(f"ERGEBNISSE – Durchschnittliche Ideologie-Scores (0–3)")
print(f"{'═'*65}")
print(f"{'Kategorie':<25} {'NS-Filme (' + str(len(nazi_filme)) + ')':>15} {'US-Filme (' + str(len(us_filme)) + ')':>15}")
print("─" * 57)
for kat in KATEGORIEN:
    ns = mittelwert(nazi_filme, kat)
    us = mittelwert(us_filme,   kat)
    print(f"{kat:<25} {ns:>15.3f} {us:>15.3f}")

# Gesamtergebnis speichern
summary_path = os.path.join(OUTPUT_DIR, "zusammenfassung.json")
with open(summary_path, 'w', encoding='utf-8') as f:
    json.dump(alle_ergebnisse, f, ensure_ascii=False, indent=2)
print(f"\nAlle Ergebnisse gespeichert in: {summary_path}")
