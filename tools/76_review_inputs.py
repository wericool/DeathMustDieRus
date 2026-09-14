# -*- coding: utf-8 -*-
"""
Build review inputs for the "best of both" pass: entries where our RU differs
from AnotherRus RU. Only non-empty EN, both RU variants present and different.
Output: 02_translation/review/in_<group>.json
"""
import json, sys, os

sys.stdout.reconfigure(encoding="utf-8")
T = r"E:\Games\DeathMustDieRus\02_translation"
en = json.load(open(os.path.join(T, "strings_en.json"), encoding="utf-8"))
ours = json.load(open(os.path.join(T, "ru_build.json"), encoding="utf-8"))
other_all = json.load(open(os.path.join(T, "strings_anotherrus.json"), encoding="utf-8"))
OUTDIR = os.path.join(T, "review")
os.makedirs(OUTDIR, exist_ok=True)

GROUPS = {
 "boons":      ["Loc_BoonDescriptions", "Loc_BoonNames", "Loc_BoonMisc", "Loc_Gods"],
 "gifts":      ["Loc_GiftDescriptions"],
 "encounters": ["Loc_EncounterDescriptions", "Loc_EncounterNames"],
 "choices":    ["Loc_EncounterChoices"],
 "doodads":    ["Loc_DoodadMessages"],
 "affixes":    ["Loc_ItemAffixes", "Loc_ItemAffixesShort"],
 "uniques":    ["Loc_ItemUniques", "Loc_ItemUniquesFlavorText"],
 "talents":    ["Loc_TalentNames", "Loc_TalentDescriptions", "Loc_TalentFlavorText"],
 "stats1":     ["Loc_Stats"],
 "achievements": ["Loc_AchievementNames", "Loc_AchievementCategories", "Loc_AchievementConditions", "Loc_AchievementRewards", "Loc_UnlockNotifications"],
 "ui":         ["Loc_AppUI", "Loc_GeneralUI", "Loc_Controls", "Loc_Results", "Loc_TooltipTitles", "Loc_TooltipTexts"],
 "items_misc": ["Loc_ItemClasses", "Loc_ItemCoreStats", "Loc_ItemGeneral", "Loc_ItemPrefixes", "Loc_ItemSuffixes", "Loc_ItemSubtypes", "Loc_ItemType", "Loc_ItemRarities", "Loc_Rarities", "Loc_ItemSpecialAffixNames", "Loc_MapObjectNames", "Loc_MonsterNames", "Loc_RealmNames"],
 "chars":      ["Loc_CharacterNames", "Loc_CharacterClasses", "Loc_CharacterSpecies", "Loc_CharacterBackstories", "Loc_CharacterStats", "Loc_CharacterStatsInfo"],
 "statuses":   ["Loc_StatusNames", "Loc_StatusDescriptions", "Loc_KeywordNames", "Loc_KeywordDescriptions", "Loc_DarknessChallenge", "Loc_DarknessChallengeDescriptions", "Loc_DarknessGeneral"],
}

total = 0
for g, colls in GROUPS.items():
    rows = []
    for coll in colls:
        other_tbl = other_all.get(coll + "_en", {})
        for e in en.get(coll, {}).get("entries", []):
            i = str(e["id"])
            src = (e.get("en") or "").strip()
            a = (ours.get(coll, {}).get(i) or "").strip()
            b = (other_tbl.get(i) or "").strip()
            if not src or not a or not b or a == b:
                continue
            rows.append({"coll": coll, "id": i, "en": e.get("en"), "ours": a, "theirs": b})
    p = os.path.join(OUTDIR, "in_%s.json" % g)
    json.dump({"group": g, "rows": rows}, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    total += len(rows)
    print("%-14s %5d rows -> %s" % (g, len(rows), p))
print("total diffs:", total)
