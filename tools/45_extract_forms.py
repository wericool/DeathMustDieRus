# -*- coding: utf-8 -*-
"""Exhaustive extraction of formal-address forms in the merged translation."""
import json, os, re, sys, collections

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"E:\Games\DeathMustDieRus"
T = os.path.join(ROOT, "02_translation")
ru = json.load(open(os.path.join(T, "ru_final.json"), encoding="utf-8"))

pat_all = re.compile(r"[А-Яа-яЁё]+")
pat_verb = re.compile(r"(етесь|итесь|ётесь|аетесь|яетесь|ете|ите|ёте|аете|яете|уете|йте)$", re.I)
pat_pron = re.compile(r"^(вы|вас|вам|вами|ваш|ваша|ваше|ваши|вашего|вашей|ваших|вашему|вашим|вашими|вашем)$", re.I)

verbs = collections.Counter()
prons = collections.Counter()
ctx = collections.defaultdict(list)

for coll, m in ru.items():
    for i, s in m.items():
        if not isinstance(s, str):
            continue
        for w in pat_all.findall(s):
            lw = w.lower()
            if pat_pron.match(lw):
                prons[w] += 1
            elif pat_verb.search(lw) and len(lw) > 4:
                verbs[w] += 1
                if len(ctx[w]) < 2:
                    ctx[w].append("%s|%s: %s" % (coll, i, s[:100]))

print("### PRONOUNS (%d distinct)" % len(prons))
for w, n in prons.most_common():
    print("   %-12s %d" % (w, n))

print()
print("### VERB-LIKE FORMS (%d distinct)" % len(verbs))
for w, n in verbs.most_common():
    print("   %-22s %-4d %s" % (w, n, ctx[w][0][:120] if ctx[w] else ""))

# any remaining '-ся' second person and other tell-tales
print()
print("### other checks")
for token in ("Вам", "вам", "Вами", "вами"):
    ids = [(c, i, s[:90]) for c, m in ru.items() for i, s in m.items()
           if isinstance(s, str) and re.search(r"\b%s\b" % token, s)]
    print("  %s: %d" % (token, len(ids)))
