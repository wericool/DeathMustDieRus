# -*- coding: utf-8 -*-
"""Build translator-friendly extraction: JSON + CSV, keyed by shared table data."""
import os, json, csv, collections

ROOT = r"E:\Games\DeathMustDieRus"
EX = os.path.join(ROOT, "01_extracted")
TR = os.path.join(ROOT, "02_translation")
os.makedirs(TR, exist_ok=True)

def load(name):
    with open(os.path.join(EX, name), encoding="utf-8") as f:
        return json.load(f)

shared = load("localization-assets-shared_assets_all.json")
en = load("localization-string-tables-english(en)_assets_all.json")
bg = load("localization-string-tables-bulgarian(bg)_assets_all.json")


def collect_keys():
    """tableCollectionName -> {id: key}, plus guid + name"""
    out = {}
    for o in shared["objects"]:
        if o["type"] != "MonoBehaviour":
            continue
        d = o["data"]
        cn = d.get("m_TableCollectionName")
        if not cn:
            continue
        out[cn] = {
            "guid": d.get("m_TableCollectionNameGuidString"),
            "keys": {e["m_Id"]: e["m_Key"] for e in (d.get("m_Entries") or [])},
        }
    return out


KEYS = collect_keys()


def collect_tables(doc):
    res = {}
    for o in doc["objects"]:
        if o["type"] != "MonoBehaviour":
            continue
        d = o["data"]
        nm = d.get("m_Name")
        if not nm:
            continue
        res[nm] = {
            "path_id": o["path_id"],
            "locale": (d.get("m_LocaleId") or {}).get("m_Code"),
            "shared": d.get("m_SharedData"),
            "entries": d.get("m_TableData") or [],
        }
    return res


EN = collect_tables(en)
BG = collect_tables(bg)

# shared-table name for each en string table: Loc_X_en -> Loc_X
def coll_of(name, suffix):
    return name[: -len(suffix)] if name.endswith(suffix) else name


report = []
data = {}
for tn, t in sorted(EN.items()):
    coll = coll_of(tn, "_en")
    km = KEYS.get(coll, {}).get("keys", {})
    bg_t = BG.get(coll + "_bg", {})
    bg_map = {e["m_Id"]: e.get("m_Localized", "") for e in bg_t.get("entries", [])}
    items = []
    for e in t["entries"]:
        eid = e["m_Id"]
        items.append({
            "id": eid,
            "key": km.get(eid, "<no-key>"),
            "en": e.get("m_Localized", ""),
            "ru": "",
            "bg": bg_map.get(eid, ""),
        })
    data[coll] = {
        "tableCollection": coll,
        "guid": KEYS.get(coll, {}).get("guid"),
        "en_table_name": tn,
        "en_path_id": t["path_id"],
        "locale": t["locale"],
        "entries": items,
    }
    n_empty = sum(1 for i in items if not i["en"])
    report.append((coll, len(items), n_empty, len(km)))

# also list bg tables that have no en counterpart
for tn, t in sorted(BG.items()):
    coll = coll_of(tn, "_bg")
    if coll not in data:
        print("!! bg-only collection:", coll, len(t["entries"]))

with open(os.path.join(TR, "strings_en.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

# flat CSV
with open(os.path.join(TR, "strings_en.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["tableCollection", "id", "key", "en", "ru", "bg"])
    for coll, d in data.items():
        for i in d["entries"]:
            w.writerow([coll, i["id"], i["key"], i["en"], i["ru"], i["bg"]])

total = sum(len(d["entries"]) for d in data.values())
print("collections:", len(data), "total entries:", total)
print("%-45s %7s %7s %7s" % ("collection", "entries", "empty", "keys"))
for coll, n, e, k in report:
    flag = "  <-- KEY MISMATCH" if k and k != n else ""
    print("%-45s %7d %7d %7d%s" % (coll, n, e, k, flag))
