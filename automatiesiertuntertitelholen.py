"""
Groq Whisper Transkription – NS Propagandafilme (Plain Text)
=============================================================
Voraussetzungen:
    pip install groq internetarchive pydub

ffmpeg muss installiert sein:
"""

import os
import math
import time
import internetarchive as ia
from groq import Groq
from pydub import AudioSegment

# ───────────────
# KONFIGURATION
# ───────────────

NAZI_FILME = [
'1937-alarm-in-peking-gustav-frohlich-peter-voss-paul-westermeier-herbert-hubner-',

'1943-Besatzung-Dora',

'1941-Carl-Peters',

'1940-feinde-brigitte-horney-willy-birgel-beppo-brem',

'flucht-ins-dunkel-1939',

'1942-fronttheater-rene-deltgen-heli-finkenzeller-hilde-von-stolz',

'1942-GPU',

'1942-himmelhunde-josef-kamper-georg-vogelsang-albert-florath',

'himmelsturmer-1941',

'1941-ich-klage-an-paula-wessely-matthias-wiemann',

'1939-im-kampf-gegen-den-weltfeind-deutsche-freiwillige-in-spanien-1h-23m-448x-336',

'jakko-1941',

'joseph-grobbels-jud-suss-1940',

'1941-Jungens',

'kadetten-1939-hard-sub',

'kameraden-auf-see-1938-german-movie_202307',

'1941-kampfgeschwader-lutzow',

'videoplayback_20220722',

'1941-Kopf-hoch-Johannes',

'wehrmacht-ss-videos-und-musik-gruppe',

'1937-mein-sohn-der-herr-minister-hilde-korber-heli-finkenzeller-hans-moser-hans-',

'ohmkruger1941',

'1937-ritt-in-die-freiheit-willy-birgel-viktor-staal-hansi-knotek',

'1939-Robert-und-Bertram',

'1940-Die-Rothschilds-Aktien-auf-Waterloo',

'der-stammbaum-des-dr.-pistorius-1939',

'1941-Stukas',

'togger-1937',

'1941-u-boote-westwarts-josef-sieber-ilse-werner-gekurzte-version',

'1937-Unternehmen-Michael',

'1941-Venus-vor-Gericht',
]

AUSGABE_ORDNER  = 'transkripte/nazi'
DOWNLOAD_ORDNER = 'downloads'
MAX_CHUNK_MB    = 24

# ─────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
os.makedirs(AUSGABE_ORDNER,  exist_ok=True)
os.makedirs(DOWNLOAD_ORDNER, exist_ok=True)

# ─────────────────────────────────────────────
# HILFSFUNKTIONEN
# ─────────────────────────────────────────────

def finde_videodatei(film_id):
    item = ia.get_item(film_id)
    for ext in ['.mp4', '.mpeg', '.mpg', '.ogv', '.avi']:
        for f in item.files:
            name = f['name'].lower()
            if name.endswith(ext) and 'thumb' not in name:
                print(f'  → Gefunden: {f["name"]} ({int(f.get("size",0))/1e9:.1f} GB)')
                return f['name']
    return None


def audio_zu_chunks(audio_pfad):
    audio = AudioSegment.from_file(audio_pfad)
    groesse_mb = os.path.getsize(audio_pfad) / (1024 * 1024)
    n_chunks = math.ceil(groesse_mb / MAX_CHUNK_MB)
    chunk_dauer_ms = len(audio) // n_chunks
    print(f'  → {groesse_mb:.0f} MB → {n_chunks} Chunks')

    chunks = []
    for i in range(n_chunks):
        start_ms = i * chunk_dauer_ms
        end_ms   = min((i + 1) * chunk_dauer_ms, len(audio))
        chunk_pfad = f'{DOWNLOAD_ORDNER}/chunk_{i}.mp3'
        audio[start_ms:end_ms].export(chunk_pfad, format='mp3', bitrate='64k')
        chunks.append(chunk_pfad)
    return chunks


# ─────────────────────────────────────────────
# HAUPTFUNKTION
# ─────────────────────────────────────────────

def verarbeite_film(film_id):
    txt_pfad = f'{AUSGABE_ORDNER}/{film_id}.txt'

    if os.path.exists(txt_pfad):
        print(f'  ⏭  Bereits vorhanden: {film_id}.txt')
        return True

    print(f'\n{"─"*50}\n{film_id}\n{"─"*50}')

    # 1. Video runterladen
    video_datei = finde_videodatei(film_id)
    if not video_datei:
        print('  ✗ Keine Videodatei gefunden!')
        return False

    video_pfad = f'{DOWNLOAD_ORDNER}/{film_id}.{video_datei.split(".")[-1]}'
    if not os.path.exists(video_pfad):
        print('  ↓ Lade herunter ...')
        ia.download(film_id, files=[video_datei], destdir=DOWNLOAD_ORDNER, no_directory=True)
        heruntergeladen = f'{DOWNLOAD_ORDNER}/{video_datei}'
        if os.path.exists(heruntergeladen):
            os.rename(heruntergeladen, video_pfad)

    # 2. Audio extrahieren
    audio_pfad = f'{DOWNLOAD_ORDNER}/{film_id}.mp3'
    if not os.path.exists(audio_pfad):
        print('  🎵 Audio extrahieren ...')
        os.system(f'ffmpeg -i "{video_pfad}" -ac 1 -ar 16000 -q:a 0 "{audio_pfad}" -y -loglevel quiet')
    os.remove(video_pfad)

    # 3. In Chunks aufteilen falls nötig
    audio_groesse_mb = os.path.getsize(audio_pfad) / (1024 * 1024)
    chunks = audio_zu_chunks(audio_pfad) if audio_groesse_mb > MAX_CHUNK_MB else [audio_pfad]

    # 4. Transkribieren – plain text, kein timestamp
    print(f'  🎙 Transkribiere {len(chunks)} Chunk(s) ...')
    gesamt_text = []
    start = time.time()

    for i, chunk_pfad in enumerate(chunks):
        print(f'    Chunk {i+1}/{len(chunks)} ...')
        with open(chunk_pfad, 'rb') as f:
            response = client.audio.transcriptions.create(
                file=(os.path.basename(chunk_pfad), f.read()),
                model='whisper-large-v3-turbo',
                language='de',
                response_format='text',   # plain text, keine Zeitstempel
                temperature=0.0
            )
        gesamt_text.append(response)
        if chunk_pfad != audio_pfad:
            os.remove(chunk_pfad)
        if i < len(chunks) - 1:
            time.sleep(1)

    # 5. Als .txt speichern
    with open(txt_pfad, 'w', encoding='utf-8') as f:
        f.write('\n'.join(gesamt_text))

    os.remove(audio_pfad)
    print(f'  ✓ Fertig in {(time.time()-start)/60:.1f} min → {txt_pfad}')
    return True


# ─────────────────────────────────────────────
# AUSFÜHREN
# ─────────────────────────────────────────────

if __name__ == '__main__':
    if not os.environ.get('GROQ_API_KEY'):
        print('⚠ GROQ_API_KEY nicht gesetzt!\n  export GROQ_API_KEY="dein_key_hier"')
        exit(1)

    erfolgreich, fehlgeschlagen = [], []
    for film_id in NAZI_FILME:
        try:
            ok = verarbeite_film(film_id)
            (erfolgreich if ok else fehlgeschlagen).append(film_id)
        except Exception as e:
            print(f'  ✗ Fehler: {e}')
            fehlgeschlagen.append(film_id)

    print(f'\n{"═"*50}')
    print(f'✓ {len(erfolgreich)} erfolgreich  ✗ {len(fehlgeschlagen)} fehlgeschlagen')
    if fehlgeschlagen:
        print(f'Fehlgeschlagen: {fehlgeschlagen}')