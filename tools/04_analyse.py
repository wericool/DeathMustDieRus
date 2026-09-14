# -*- coding: utf-8 -*-
"""Analyse dumped structure: keys, string counts, locale assets."""
import os, json, collections

ROOT = r"E:\Games\DeathMustDieRus"
OUT = os.path.join(ROOT, "01_extracted")

def load(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as f:
        return json.load(f)

shared = load("localization-assets-shared_assets_all.json")
print("=== SHARED DATA (first asset) ===")
for o in shared["objects"]:
    if o["type"] == "MonoBehaviour":
        d = o["data"]
        print("name:", d.get("m_Name"))
        print("keys:", list(d.keys()))
        print(json.dumps(d, ensure_ascii=False)[:1500])
        break

print()
print("=== LOCALES ===")
loc = load("localization-locales_assets_all.json")
for o in loc["objects"]:
    if o["type"] == "MonoBehaviour":
        print(json.dumps(o["data"], ensure_ascii=False, indent=1)[:2500])
        print("---")

print()
print("=== STRING TABLE TOTALS ===")
for tag in ["english(en)", "bulgarian(bg)"]:
    d = load("localization-string-tables-%s_assets_all.json" % tag)
    total = 0
    empt = 0
    names = []
    for o in d["objects"]:
        if o["type"] != "MonoBehaviour":
            continue
        dd = o["data"]
        names.append((dd.get("m_Name"), len(dd.get("m_TableData") or [])))
        for e in (dd.get("m_TableData") or []):
            total += 1
            if not e.get("m_Localized"):
                empt += 1
    print(tag, "tables:", len(names), "entries:", total, "empty:", empt)
    for n, c in sorted(names):
        print("    %-45s %d" % (n, c))
