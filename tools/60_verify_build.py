# -*- coding: utf-8 -*-
"""Spot-check: does the built bundle actually contain the final RU strings?"""
import json, sys, collections
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
BUNDLE = r"E:\Games\DeathMustDieRus\03_build\StandaloneWindows64\localization-string-tables-english(en)_assets_all.bundle"
RU = r"E:\Games\DeathMustDieRus\02_translation\ru_build.json"

env = UnityPy.load(BUNDLE)
tables = {}
for obj in env.objects:
    if obj.type.name == "MonoBehaviour":
        try:
            d = obj.read_typetree()
        except Exception:
            continue
        name = d.get("m_Name", "")
        if name.startswith("Loc_") and "Shared Data" not in name:
            tables[name] = d

print("tables in bundle:", len(tables))
sample = list(tables)[0]
d = tables[sample]
print("sample table:", sample, "keys:", list(d.keys())[:15])

# StringTable: m_TableData is usually a list of {id, value} or a dict m_Entries
ru = json.load(open(RU, encoding="utf-8"))

def entries_of(d):
    td = d.get("m_TableData") or d.get("Entries") or []
    out = {}
    for e in td:
        if isinstance(e, dict) and "m_Id" in e:
            out[str(e["m_Id"])] = e.get("m_Localized") or e.get("m_Value") or ""
    return out

total = cyr = 0
percoll = {}
for name, d in tables.items():
    base = name  # e.g. Loc_BoonNames_en
    coll = base.rsplit("_", 1)[0] if base.endswith(("_en", "_bg")) else base
    es = entries_of(d)
    n_cyr = sum(1 for v in es.values() if any("\u0400" <= ch <= "\u04FF" for ch in v))
    percoll[base] = (len(es), n_cyr)
    total += len(es); cyr += n_cyr

print("total entries in bundle: %d, with cyrillic: %d" % (total, cyr))
for base in sorted(percoll):
    n, c = percoll[base]
    print("  %-45s %5d entries, %5d cyr" % (base, n, c))

# print 3 sample strings from Loc_GeneralUI_en and Loc_BoonNames_en
for want in ("Loc_GeneralUI_en", "Loc_BoonNames_en", "Loc_AppUI_en"):
    if want in tables:
        es = entries_of(tables[want])
        print("---", want)
        for k in list(es)[:6]:
            print("   %s = %r" % (k, es[k]))
