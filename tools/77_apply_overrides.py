# -*- coding: utf-8 -*-
"""
Apply review overrides (review/out_*.json) to ru_build.json with validation:
token/tag multiset must match EN source. Writes review/apply_report.txt.
"""
import json, sys, os, re

sys.stdout.reconfigure(encoding="utf-8")
T = r"E:\Games\DeathMustDieRus\02_translation"
en = json.load(open(os.path.join(T, "strings_en.json"), encoding="utf-8"))
ru = json.load(open(os.path.join(T, "ru_build.json"), encoding="utf-8"))
other_all = json.load(open(os.path.join(T, "strings_anotherrus.json"), encoding="utf-8"))

SMART = re.compile(r"\{[^{}]*\}")
TAG = re.compile(r"<[^>]+>")

# --- step 0: restore leading/trailing whitespace from EN (layout matters)
ws_fixed = 0
for coll, meta in en.items():
    tbl = ru.get(coll)
    if not tbl:
        continue
    for e in meta["entries"]:
        i = str(e["id"])
        src = e.get("en") or ""
        v = tbl.get(i)
        if not v or not src:
            continue
        lead_src = src[: len(src) - len(src.lstrip())]
        trail_src = src[len(src.rstrip()):]
        nv = v
        if lead_src and not nv[: len(nv) - len(nv.lstrip())]:
            nv = lead_src + nv
        if trail_src and not nv[len(nv.rstrip()):]:
            nv = nv + trail_src
        if nv != v:
            tbl[i] = nv
            ws_fixed += 1
print("whitespace restored on %d entries" % ws_fixed)

applied = skipped = 0
report = []
GROUP_FALLBACK_COLL = {"doodads": "Loc_DoodadMessages"}
for fn in sorted(os.listdir(os.path.join(T, "review"))):
    if not (fn.startswith("out_") and fn.endswith(".json")):
        continue
    d = json.load(open(os.path.join(T, "review", fn), encoding="utf-8-sig"))
    for coll, ids in d.get("overrides", {}).items():
        if isinstance(ids, str):
            key = coll
            coll = GROUP_FALLBACK_COLL.get(d.get("group", ""), coll)
            ids = {key: ids}
        other_tbl = other_all.get(coll + "_en", {})
        src_tbl = {str(e["id"]): e.get("en") or "" for e in en.get(coll, {}).get("entries", [])}
        for i, v in ids.items():
            src = src_tbl.get(str(i))
            if src is None:
                report.append(("no-src", coll, i, v[:60]))
                skipped += 1
                continue
            if sorted(SMART.findall(src)) != sorted(SMART.findall(v)) or sorted(TAG.findall(src)) != sorted(TAG.findall(v)):
                report.append(("tokens", coll, i, v[:60]))
                skipped += 1
                continue
            if not v.strip():
                skipped += 1
                continue
            ru[coll][str(i)] = v
            applied += 1

json.dump(ru, open(os.path.join(T, "ru_build.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
with open(os.path.join(T, "review", "apply_report.txt"), "w", encoding="utf-8") as f:
    f.write("applied: %d, skipped: %d\n" % (applied, skipped))
    for r in report:
        f.write("%s %s %s %s\n" % r)
print("applied:", applied, "skipped:", skipped)
for r in report[:20]:
    print("  ", r)
