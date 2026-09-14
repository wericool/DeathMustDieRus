# -*- coding: utf-8 -*-
"""Collect vocabulary that must be translated once and reused (glossary source)."""
import json, re, collections, os

ROOT = r"E:\Games\DeathMustDieRus"
TR = os.path.join(ROOT, "02_translation")
units = json.load(open(os.path.join(TR, "units_real.json"), encoding="utf-8"))

SMART = re.compile(r"\{[^{}]*\}")
TAG = re.compile(r"</?[a-zA-Z][^>]*>")

# 1) distinct stat labels from Loc_Stats style units: "Label: [[n]]"
labels = collections.Counter()
for u in units:
    m = re.match(r"^(?:\{(?:inv|neg)\})?(.+?):\s*\[\[\d+\]\]", u["skeleton"])
    if m:
        labels[m.group(1).strip()] += u["count"]

# 2) all units that are short (<= 45 chars) and have no marker -> pure terms
terms = collections.Counter()
for u in units:
    s = u["skeleton"]
    if "[[ " in s:
        continue
    if len(s) <= 46 and not SMART.search(s):
        terms[s] += u["count"]

out = []
out.append("# Vocabulary dump for glossary\n")
out.append("## Distinct stat labels (%d)\n" % len(labels))
for l, c in sorted(labels.items()):
    out.append("%-62s x%d" % (l, c))
out.append("\n\n## Short term units (%d)\n" % len(terms))
for t, c in sorted(terms.items()):
    out.append("%-62s x%d" % (t, c))

p = os.path.join(TR, "vocab_dump.txt")
open(p, "w", encoding="utf-8").write("\n".join(out))
print("wrote", p, "labels:", len(labels), "terms:", len(terms))
