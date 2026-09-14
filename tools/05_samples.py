# -*- coding: utf-8 -*-
"""Show sample strings from interesting tables (item generation parts etc)."""
import os, json

ROOT = r"E:\Games\DeathMustDieRus"
OUT = os.path.join(ROOT, "01_extracted")

def load(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as f:
        return json.load(f)

en = load("localization-string-tables-english(en)_assets_all.json")
bg = load("localization-string-tables-bulgarian(bg)_assets_all.json")
shared = load("localization-assets-shared_assets_all.json")

# map shared table collection -> {id: key}
keymap = {}
for o in shared["objects"]:
    if o["type"] != "MonoBehaviour":
        continue
    d = o["data"]
    cn = d.get("m_TableCollectionName")
    if not cn:
        continue
    keymap[cn] = {e["m_Id"]: e["m_Key"] for e in (d.get("m_Entries") or [])}

def tables(doc):
    res = {}
    for o in doc["objects"]:
        if o["type"] != "MonoBehaviour":
            continue
        d = o["data"]
        res[d["m_Name"]] = d
    return res

enT = tables(en)
bgT = tables(bg)

for tn in ["Loc_ItemPrefixes_en", "Loc_ItemSuffixes_en", "Loc_ItemSubtypes_en",
           "Loc_ItemClasses_en", "Loc_ItemType_en", "Loc_ItemGeneral_en",
           "Loc_ItemRarities_en", "Loc_Rarities_en", "Loc_ItemCoreStats_en",
           "Loc_ItemSpecialAffixNames_en", "Loc_ItemAffixes_en", "Loc_ItemAffixesShort_en",
           "Loc_Stats_en", "Loc_BoonDescriptions_en", "Loc_ItemUniques_en"]:
    d = enT.get(tn)
    if not d:
        print("MISSING", tn); continue
    coll = d["m_Name"].rsplit("_en", 1)[0]
    km = keymap.get(coll, {})
    print("=" * 90)
    print(tn, "entries:", len(d["m_TableData"]))
    for e in d["m_TableData"][:12]:
        print("   id=%-5s key=%-34s val=%s" % (e["m_Id"], km.get(e["m_Id"], "?"), repr(e["m_Localized"])[:110]))
    # show bg counterpart for 5
    b = bgT.get(tn.replace("_en", "_bg"))
    if b:
        print("   --- bg ---")
        for e in b["m_TableData"][:5]:
            print("   id=%-5s key=%-34s val=%s" % (e["m_Id"], km.get(e["m_Id"], "?"), repr(e["m_Localized"])[:110]))
