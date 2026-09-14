# -*- coding: utf-8 -*-
"""Analyse translation workload: unique strings, volume, placeholder inventory."""
import json, re, collections

TR = r"E:\Games\DeathMustDieRus\02_translation\strings_en.json"
d = json.load(open(TR, encoding="utf-8"))

allv = []
per = {}
for coll, t in d.items():
    vals = [e["en"] for e in t["entries"]]
    per[coll] = vals
    allv.extend(vals)

nonempty = [v for v in allv if v and v.strip()]
uniq = set(nonempty)
print("total entries      :", len(allv))
print("non-empty          :", len(nonempty))
print("unique non-empty   :", len(uniq))
print("total chars        :", sum(len(v) for v in nonempty))
print("unique chars       :", sum(len(v) for v in uniq))
print("avg len            :", round(sum(len(v) for v in uniq) / len(uniq), 1))

# smart string / placeholder inventory
pat_smart = re.compile(r"\{[^{}]*\}")
pat_tag = re.compile(r"</?[a-zA-Z][^>]*>")
ph = collections.Counter()
for v in uniq:
    for m in pat_smart.findall(v):
        ph[m] += 1
print()
print("distinct smart-string tokens:", len(ph))
for k, c in ph.most_common(30):
    print("   %-40s %d" % (k, c))

print()
print("with rich text tags:", sum(1 for v in uniq if pat_tag.search(v)))
tags = collections.Counter()
for v in uniq:
    for m in pat_tag.findall(v):
        tags[m] += 1
for k, c in tags.most_common(20):
    print("   %-40s %d" % (k, c))

print()
print("=== per-collection unique counts ===")
for coll, vals in sorted(per.items(), key=lambda kv: -len(kv[1])):
    ne = [v for v in vals if v and v.strip()]
    print("%-40s entries=%-6d unique=%-6d chars=%d" % (coll, len(vals), len(set(ne)), sum(len(v) for v in ne)))
