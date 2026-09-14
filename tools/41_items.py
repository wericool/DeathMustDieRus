# -*- coding: utf-8 -*-
"""Inspect the item-name generation tables."""
import json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"E:\Games\DeathMustDieRus"
T = os.path.join(ROOT, "02_translation")

strings = json.load(open(os.path.join(T, "strings_en.json"), encoding="utf-8"))
ru = json.load(open(os.path.join(T, "ru_final.json"), encoding="utf-8"))


def show(name, limit):
    rows = strings[name]["entries"]
    rmap = ru.get(name, {})
    print("=" * 100)
    print("%s: %d entries, translated=%d" % (name, len(rows), len(rmap)))
    for r in rows[:limit]:
        i = str(r["id"])
        print("   key=%-12s EN=%-26r RU=%r" % (r.get("key", ""), r.get("en", ""), rmap.get(i)))
    keys = [r.get("key") for r in rows]
    return keys


show("Loc_ItemGeneral", 12)
pk = show("Loc_ItemPrefixes", 22)
sk = show("Loc_ItemSuffixes", 22)
show("Loc_ItemSubtypes", 30)
show("Loc_ItemSpecialAffixNames", 12)
show("Loc_ItemAffixesShort", 8)

pk = set(k for k in pk if k)
sk = set(k for k in sk if k)
print("=" * 100)
print("prefix entries=%d keys=%d | suffix entries=%d keys=%d | shared keys=%d" % (
    len(pk), len(pk), len(sk), len(sk), len(pk & sk)))
