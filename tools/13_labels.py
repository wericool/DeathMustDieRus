# -*- coding: utf-8 -*-
"""Extract the reusable label vocabulary from mechanical tables."""
import json, re, collections

TR = r"E:\Games\DeathMustDieRus\02_translation\strings_en.json"
d = json.load(open(TR, encoding="utf-8"))

stats = d["Loc_Stats"]["entries"]
print("=== Loc_Stats pattern analysis ===")
pat = re.compile(r"^(?P<label>[^:{}\[\]]*?)\s*:\s*(?P<ph>(\{[^{}]*\}|\s)*)$")
labels = collections.Counter()
other = []
for e in stats:
    v = e["en"]
    m = pat.match(v)
    if m and m.group("label").strip():
        labels[m.group("label").strip()] += 1
    else:
        other.append((e["key"], v))
print("matched label:placeholder ->", sum(labels.values()), "distinct labels:", len(labels))
print("unmatched:", len(other))
for k, v in other[:40]:
    print("    %-28s %r" % (k, v[:80]))
print()
print("--- distinct stat labels ---")
for l, c in sorted(labels.items()):
    print("   %-45s x%d" % (l, c))

print()
print("=== rich-text wrapped labels in Loc_Stats ===")
colored = collections.Counter()
for e in stats:
    for m in re.finditer(r"<color=(#[0-9a-fA-F]+)>([^<]*)</color>", e["en"]):
        colored[(m.group(2), m.group(1))] += 1
print("distinct colored fragments:", len(colored))
for (txt, col), c in colored.most_common(60):
    print("   %-40s %-10s x%d" % (txt, col, c))
