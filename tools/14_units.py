# -*- coding: utf-8 -*-
"""
Build translation units.

A "unit" is an English skeleton in which every smart-string token  {...}  is
replaced by an indexed marker  [[n]]  (rich-text tags are kept inline so the
wrapped word still gets translated).  Identical skeletons collapse into one
unit, which massively reduces the workload and guarantees consistency.

Outputs (02_translation/):
  units.json        - [{uid, skeleton, n_slots, sources:[...], colls:[...], count}]
  unit_index.json   - per-collection/id -> uid
"""
import json, re, os, collections

ROOT = r"E:\Games\DeathMustDieRus"
TR = os.path.join(ROOT, "02_translation")

SMART = re.compile(r"\{[^{}]*\}")


def to_skeleton(s):
    """Replace smart-string tokens with indexed markers."""
    slots = []

    def repl(m):
        slots.append(m.group(0))
        return "[[%d]]" % (len(slots) - 1)

    skel = SMART.sub(repl, s)
    return skel, slots


def main():
    d = json.load(open(os.path.join(TR, "strings_en.json"), encoding="utf-8"))
    units = {}          # skeleton -> unit
    index = {}          # coll -> {id: uid}
    stats = collections.Counter()

    for coll, t in d.items():
        index[coll] = {}
        for e in t["entries"]:
            src = e["en"]
            if not src or not src.strip():
                continue
            skel, slots = to_skeleton(src)
            u = units.get(skel)
            if u is None:
                u = {"uid": len(units), "skeleton": skel, "n_slots": len(slots),
                     "slot_samples": slots[:6], "count": 0,
                     "examples": [], "colls": []}
                units[skel] = u
            u["count"] += 1
            if len(u["examples"]) < 3 and src not in u["examples"]:
                u["examples"].append(src)
            if coll not in u["colls"]:
                u["colls"].append(coll)
            index[coll][str(e["id"])] = u["uid"]

    ulist = sorted(units.values(), key=lambda u: (-u["count"], u["uid"]))
    for i, u in enumerate(ulist):
        u["uid"] = i

    # rebuild index with final uids
    index = {}
    for coll, t in d.items():
        index[coll] = {}
        for e in t["entries"]:
            src = e["en"]
            if not src or not src.strip():
                continue
            skel, _ = to_skeleton(src)
            index[coll][str(e["id"])] = units[skel]["uid"]

    with open(os.path.join(TR, "units.json"), "w", encoding="utf-8") as f:
        json.dump(ulist, f, ensure_ascii=False, indent=1)
    with open(os.path.join(TR, "unit_index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False)

    total = sum(u["count"] for u in ulist)
    chars = sum(len(u["skeleton"]) for u in ulist)
    print("entries covered :", total)
    print("unique units    :", len(ulist))
    print("unit chars      :", chars)
    print("avg unit len    :", round(chars / len(ulist), 1))

    print("\n--- top 25 most frequent skeletons ---")
    for u in ulist[:25]:
        print("%5d  %s" % (u["count"], u["skeleton"][:100]))

    # bucket by size for batching
    print("\n--- unit length histogram ---")
    hist = collections.Counter()
    for u in ulist:
        L = len(u["skeleton"])
        hist[(L // 50) * 50] += 1
    for k in sorted(hist):
        print("   %4d-%4d : %d" % (k, k + 49, hist[k]))


if __name__ == "__main__":
    main()
