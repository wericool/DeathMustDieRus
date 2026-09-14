# -*- coding: utf-8 -*-
"""Extract all string tables from the AnotherRus bundle to JSON for comparison."""
import json, sys
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
BUNDLE = r"E:\Games\DeathMustDieRus\AnotherRus\Death Must Die_Data\StreamingAssets\aa\StandaloneWindows64\localization-string-tables-english(en)_assets_all.bundle"
OUT = r"E:\Games\DeathMustDieRus\02_translation\strings_anotherrus.json"

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
            es = {}
            for e in (d.get("m_TableData") or []):
                if isinstance(e, dict) and "m_Id" in e:
                    es[str(e["m_Id"])] = e.get("m_Localized") or e.get("m_Value") or ""
            tables[name] = es

json.dump(tables, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
total = sum(len(v) for v in tables.values())
cyr = sum(1 for v in tables.values() for s in v.values() if any("\u0400" <= ch <= "\u04FF" for ch in s))
print("tables: %d, entries: %d, cyrillic: %d" % (len(tables), total, cyr))
for k in sorted(tables):
    es = tables[k]
    c = sum(1 for s in es.values() if any("\u0400" <= ch <= "\u04FF" for ch in s))
    print("  %-45s %5d entries, %5d cyr" % (k, len(es), c))
