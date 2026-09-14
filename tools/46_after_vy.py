# -*- coding: utf-8 -*-
"""Extract the word that follows 'вы/Вы' to catch predicate adjectives, and show allowlist entries."""
import json, os, re, sys, collections

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"E:\Games\DeathMustDieRus"
T = os.path.join(ROOT, "02_translation")
ru = json.load(open(os.path.join(T, "ru_final.json"), encoding="utf-8"))

nxt = collections.Counter()
for coll, m in ru.items():
    for i, s in m.items():
        if not isinstance(s, str):
            continue
        for mm in re.finditer(r"\b([Вв]ы|[Вв]ас|[Вв]ам)\s+([А-Яа-яЁё-]+)", s):
            nxt[mm.group(2).lower()] += 1

print("### word following вы/вас/вам (top 80)")
for w, n in nxt.most_common(80):
    print("   %-24s %d" % (w, n))

print()
print("### entries to inspect for the allowlist")
for key in [("Loc_EncounterChoices", "297"),
            ("Loc_EncounterDescriptions", "133"),
            ("Loc_ItemUniquesFlavorText", "112"),
            ("Loc_ItemUniquesFlavorText", "118")]:
    s = ru.get(key[0], {}).get(key[1])
    print("=" * 90)
    print("%s/%s:" % key)
    print(s)
