# -*- coding: utf-8 -*-
"""Analyse register (ты vs вы) and terminology consistency across the merged translation."""
import json, os, re, sys, collections

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"E:\Games\DeathMustDieRus"
T = os.path.join(ROOT, "02_translation")
ru = json.load(open(os.path.join(T, "ru_final.json"), encoding="utf-8"))
strings = json.load(open(os.path.join(T, "strings_en.json"), encoding="utf-8"))

INFORMAL = re.compile(r"\b(ты|тебя|тебе|тобой|тобою|твой|твоя|твоё|твое|твои|твоего|твоей|твоих|твоему|твоим|твоими|твоём|твоем)\b", re.I)
FORMAL = re.compile(r"\b(вы|вас|вам|вами|ваш|ваша|ваше|ваши|вашего|вашей|ваших|вашему|вашим|вашими|вашем)\b", re.I)

per_coll = collections.defaultdict(lambda: [0, 0])
inf_ids, frm_ids = [], []
for coll, m in ru.items():
    for i, s in m.items():
        if not isinstance(s, str):
            continue
        a = len(INFORMAL.findall(s))
        b = len(FORMAL.findall(s))
        if a:
            per_coll[coll][0] += a
            inf_ids.append((coll, i, s))
        if b:
            per_coll[coll][1] += b
            frm_ids.append((coll, i, s))

print("collections with informal forms: %d, entries: %d" % (sum(1 for v in per_coll.values() if v[0]), len(inf_ids)))
print("collections with formal forms:   %d, entries: %d" % (sum(1 for v in per_coll.values() if v[1]), len(frm_ids)))
print()
print("%-40s %8s %8s" % ("collection", "informal", "formal"))
for coll in sorted(per_coll, key=lambda c: -(per_coll[c][0] + per_coll[c][1])):
    a, b = per_coll[coll]
    print("%-40s %8d %8d" % (coll, a, b))

print()
print("=== sample informal ===")
for c, i, s in inf_ids[:6]:
    print("  [%s/%s] %s" % (c, i, s[:150]))
print("=== sample formal ===")
for c, i, s in frm_ids[:6]:
    print("  [%s/%s] %s" % (c, i, s[:150]))

# terminology conflicts
print()
print("=== term candidates ===")
TERMS = ["Снегосватч", "Снежный", "Снежнохвойн", "Быстросеребро", "стремительного серебра",
         "Импы", "Импица", "Арбитр", "арбитр", "Даркмур", "Прайм", "прайм"]
for t in TERMS:
    colls = collections.Counter()
    for coll, m in ru.items():
        for i, s in m.items():
            if isinstance(s, str) and t.lower() in s.lower():
                colls[coll] += 1
    if colls:
        print("  %-24s total=%-5d %s" % (t, sum(colls.values()), dict(colls.most_common(6))))
