# -*- coding: utf-8 -*-
"""Parse Nar_* CSVs (header-driven column indices), list speakers, cut chunks."""
import os, sys, json, collections

sys.stdout.reconfigure(encoding="utf-8")
DIR = r"E:\Games\DeathMustDieRus\02_translation\narrative"
CHUNKS = os.path.join(DIR, "chunks")
os.makedirs(CHUNKS, exist_ok=True)

FILES = ["Nar_Heroes.csv", "Nar_Self.csv", "Nar_Gods.csv", "Nar_Monsters.csv"]

speakers = collections.Counter()
all_rows = {}
for fn in FILES:
    path = os.path.join(DIR, fn)
    lines = open(path, encoding="utf-8").read().splitlines()
    hdr = lines[0].split(";")
    i_spk = hdr.index("speaker")
    i_en = next(i for i, h in enumerate(hdr) if h.strip().lower().startswith("english"))
    ncol = len(hdr)
    rows = []
    bad = 0
    last_spk = ""
    for i, l in enumerate(lines[1:], start=1):
        parts = l.split(";")
        if len(parts) != ncol:
            bad += 1
        spk = parts[i_spk] if len(parts) > i_spk else ""
        en = parts[i_en] if len(parts) > i_en else ""
        real = spk if spk not in ("", "~", "ini", "@fade") else ""
        if real:
            last_spk = real
        eff = real or last_spk  # effective speaker (inherited for continuations)
        speakers[eff] += 1
        rows.append({"i": i, "speaker": spk, "eff": eff, "en": en})
    all_rows[fn] = rows
    print("%-18s lines=%4d badcols=%d en_nonempty=%d" % (
        fn, len(rows), bad, sum(1 for r in rows if r["en"].strip())))

print("\nspeakers:")
for s, c in speakers.most_common():
    print("  %-12s %d" % (s or "<empty>", c))

# chunks
for stale in os.listdir(CHUNKS):
    os.remove(os.path.join(CHUNKS, stale))
CHUNK = 140
meta = []
n = 0
for fn in FILES:
    rows = all_rows[fn]
    todo = [r for r in rows if r["en"].strip()]
    for ci in range(0, len(todo), CHUNK):
        part = todo[ci:ci + CHUNK]
        lo, hi = part[0]["i"], part[-1]["i"]
        chunk = {
            "file": fn,
            "lines": [
                {
                    "i": r["i"],
                    "speaker": r["speaker"],
                    "eff": r["eff"],
                    "en": r["en"],
                    "ctx": [x["en"] for x in rows if 0 < r["i"] - x["i"] <= 2 and x["en"].strip()],
                }
                for r in part
            ],
        }
        name = "%s_%03d_%03d" % (fn.replace(".csv", ""), lo, hi)
        with open(os.path.join(CHUNKS, name + ".json"), "w", encoding="utf-8") as f:
            json.dump(chunk, f, ensure_ascii=False, indent=1)
        meta.append({"chunk": name, "file": fn, "lo": lo, "hi": hi, "n": len(part)})
        n += 1
json.dump(meta, open(os.path.join(CHUNKS, "_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("chunks:", n)
