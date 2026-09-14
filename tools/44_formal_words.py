# -*- coding: utf-8 -*-
"""Collect every formal-address word and every 2nd-person-plural verb form."""
import json, os, re, sys, collections

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"E:\Games\DeathMustDieRus"
T = os.path.join(ROOT, "02_translation")
ru = json.load(open(os.path.join(T, "ru_final.json"), encoding="utf-8"))

formal = collections.Counter()
verbs = collections.Counter()
ctx = collections.defaultdict(list)

for coll, m in ru.items():
    for i, s in m.items():
        if not isinstance(s, str):
            continue
        for w in re.findall(r"[А-Яа-яЁё-]+", s):
            lw = w.lower()
            if lw in ("вы", "вас", "вам", "вами", "ваш", "ваша", "ваше", "ваши",
                      "вашего", "вашей", "ваших", "вашему", "вашим", "вашими", "вашем"):
                formal[w] += 1
            if re.search(r"(ете|ите|ёте|аете|яете|уете)$", lw) and len(lw) > 4:
                verbs[w] += 1
                if len(ctx[w]) < 3:
                    ctx[w].append(s[:110])

print("=== formal address words ===")
for w, n in formal.most_common():
    print("  %-10s %d" % (w, n))

print()
print("=== words ending in -ете/-ите/-ёте (%d distinct) ===" % len(verbs))
for w, n in verbs.most_common():
    print("  %-24s %-4d | %s" % (w, n, " || ".join(ctx[w])[:150]))
