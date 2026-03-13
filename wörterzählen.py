import os

dirs = {
    "US Subs":    "us_subs_txt",
    "Nazi Subs":  "nazi subs",
}

total_words = 0

for group, folder in dirs.items():
    group_words = 0
    dateien = [f for f in os.listdir(folder) if f.endswith(".txt")]
    for dateiname in dateien:
        with open(os.path.join(folder, dateiname), "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        group_words += len(text.split())
    print(f"{group}: {group_words:,} Wörter ({len(dateien)} Dateien)")
    total_words += group_words

print(f"\nGesamt: {total_words:,} Wörter")
print(f"Geschätzte Token: {int(total_words / 0.75):,}")