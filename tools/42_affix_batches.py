# -*- coding: utf-8 -*-
"""Build the affix (prefix/suffix) genitive-noun translation batches.

The game builds item names as:
    single: <subtype> <prefix>            (template "{1} {0}")
    double: <subtype> <prefix> и <suffix> (template "{1} {0} и {2}")
so both the prefix and the suffix text must be a Russian GENITIVE noun phrase
("Кольчуга защиты", "Клинок казни и могущества").
"""
import json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"E:\Games\DeathMustDieRus"
T = os.path.join(ROOT, "02_translation")
OUT = os.path.join(T, "affix_batches")
os.makedirs(OUT, exist_ok=True)

strings = json.load(open(os.path.join(T, "strings_en.json"), encoding="utf-8"))
ru = json.load(open(os.path.join(T, "ru_final.json"), encoding="utf-8"))

pref = {r["key"]: r for r in strings["Loc_ItemPrefixes"]["entries"] if r.get("key")}
suff = {r["key"]: r for r in strings["Loc_ItemSuffixes"]["entries"] if r.get("key")}
ru_s = ru.get("Loc_ItemSuffixes", {})
ru_p = ru.get("Loc_ItemPrefixes", {})

keys = sorted(set(pref) & set(suff))
items = []
for k in keys:
    items.append({
        "key": k,
        "en_prefix": pref[k].get("en", ""),
        "en_suffix": suff[k].get("en", ""),
        "ru_prefix_now": ru_p.get(str(pref[k]["id"]), ""),
        "ru_suffix_now": ru_s.get(str(suff[k]["id"]), ""),
        "prefix_id": pref[k]["id"],
        "suffix_id": suff[k]["id"],
    })

print("shared affix keys:", len(items))
n = 2
size = (len(items) + n - 1) // n
for i in range(n):
    part = items[i * size:(i + 1) * size]
    if not part:
        continue
    fp = os.path.join(OUT, "affix_%03d.json" % i)
    json.dump({"part": i, "count": len(part), "items": part}, open(fp, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("wrote", fp, len(part))
