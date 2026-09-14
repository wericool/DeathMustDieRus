# -*- coding: utf-8 -*-
"""Identify junk units and build translation batches."""
import json, os, re, collections

ROOT = r"E:\Games\DeathMustDieRus"
TR = os.path.join(ROOT, "02_translation")
units = json.load(open(os.path.join(TR, "units.json"), encoding="utf-8"))

TAG = re.compile(r"</?[a-zA-Z][^>]*>")
MARK = re.compile(r"\[\[\d+\]\]")

junk = []
real = []
for u in units:
    t = TAG.sub("", u["skeleton"])
    t = MARK.sub("", t).strip()
    if not t or not re.search(r"[A-Za-z]", t) or t.lower() == "eoline":
        junk.append(u)
    else:
        real.append(u)

print("units total:", len(units))
print("junk units :", len(junk), "covering entries:", sum(u["count"] for u in junk))
for u in sorted(junk, key=lambda x: -x["count"])[:10]:
    print("    %-40r x%d" % (u["skeleton"][:40], u["count"]))
print("real units :", len(real), "covering entries:", sum(u["count"] for u in real))
print("real chars :", sum(len(u["skeleton"]) for u in real))

# where do junk units live?
colls = collections.Counter()
for u in junk:
    for c in u["colls"]:
        colls[c] += u["count"]
print("junk by collection:", dict(colls.most_common(10)))

with open(os.path.join(TR, "units_real.json"), "w", encoding="utf-8") as f:
    json.dump(real, f, ensure_ascii=False, indent=1)
with open(os.path.join(TR, "units_junk.json"), "w", encoding="utf-8") as f:
    json.dump(junk, f, ensure_ascii=False, indent=1)

# ---- batching: keep units of the same collection together, cap by chars ----
by_coll = collections.defaultdict(list)
for u in real:
    by_coll[u["colls"][0]].append(u)

MAXCH = 9000
batches = []
cur = []
curch = 0
for coll in sorted(by_coll, key=lambda c: -len(by_coll[c])):
    for u in sorted(by_coll[coll], key=lambda x: x["uid"]):
        L = len(u["skeleton"]) + 40
        if cur and (curch + L > MAXCH or len(cur) >= 220):
            batches.append(cur)
            cur, curch = [], 0
        cur.append(u)
        curch += L
if cur:
    batches.append(cur)

os.makedirs(os.path.join(TR, "batches"), exist_ok=True)
manifest = []
for i, b in enumerate(batches):
    colls = sorted({c for u in b for c in u["colls"]})
    data = {
        "batch": i,
        "collections": colls,
        "units": [{"uid": u["uid"], "src": u["skeleton"]} for u in b],
    }
    p = os.path.join(TR, "batches", "batch_%03d.json" % i)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    manifest.append({"batch": i, "file": p, "n": len(b),
                     "chars": sum(len(u["skeleton"]) for u in b), "collections": colls})

with open(os.path.join(TR, "batches", "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=1)

print()
print("batches:", len(batches))
for m in manifest:
    print("   batch %3d  units=%-4d chars=%-6d %s" % (m["batch"], m["n"], m["chars"], ",".join(m["collections"])[:80]))
