# -*- coding: utf-8 -*-
"""Dump our built bundle tables to JSON, then compare ours vs AnotherRus vs EN."""
import json, sys, re
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
BUNDLE = r"E:\Games\DeathMustDieRus\03_build\StandaloneWindows64\localization-string-tables-english(en)_assets_all.bundle"
OUT = r"E:\Games\DeathMustDieRus\02_translation\strings_ourbuild.json"

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
print("our bundle dumped:", len(tables), "tables")

en = json.load(open(r"E:\Games\DeathMustDieRus\02_translation\strings_en.json", encoding="utf-8"))
other = json.load(open(r"E:\Games\DeathMustDieRus\02_translation\strings_anotherrus.json", encoding="utf-8"))
ours = tables

cyr = re.compile(r"[\u0400-\u04FF]")

stats = []
for tbl in sorted(ours):
    if tbl not in other:
        continue
    oe, oo = ours[tbl], other[tbl]
    n = len(oe)
    ru_o = sum(1 for s in oe.values() if cyr.search(s))
    ru_t = sum(1 for s in oo.values() if cyr.search(s))
    same = sum(1 for k in oe if k in oo and oe[k] == oo[k])
    ours_same_en = sum(1 for k in oe if oe[k] == (en.get(tbl.rsplit("_",1)[0], {}).get("entries") or [{}]))
    stats.append((tbl, n, ru_o, ru_t, same))

print("%-45s %6s %8s %8s %8s" % ("table", "entries", "RU ours", "RU their", "identical"))
for t, n, a, b, s in stats:
    print("%-45s %6d %8d %8d %8d" % (t, n, a, b, s))
tot = sum(s[1] for s in stats)
print("TOTAL entries %d, ru ours %d, ru theirs %d" % (tot, sum(s[2] for s in stats), sum(s[3] for s in stats)))
