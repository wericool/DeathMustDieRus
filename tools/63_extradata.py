# -*- coding: utf-8 -*-
"""Parse AssetBundleRequestOptions JSON objects embedded in m_ExtraDataString."""
import json, sys, base64, struct, re

sys.stdout.reconfigure(encoding="utf-8")
PATHS = {
 "orig":  r"E:\Games\DeathMustDieRus\backup_game\catalog.json",
 "ours":  r"E:\Games\DeathMustDieRus\03_build\catalog.json",
 "other": r"E:\Games\DeathMustDieRus\AnotherRus\Death Must Die_Data\StreamingAssets\aa\catalog.json",
}

def objects(blob):
    """Find all UTF-16LE JSON strings starting with '{' and ending with '}'."""
    out = []
    i = 0
    n = len(blob)
    pat = re.compile(rb"\{\x00")
    for m in pat.finditer(blob):
        start = m.start()
        # decode forward until '}\x00' followed by non-utf16 or end: try increasing
        # decode the maximal run of utf16 chars starting at start
        chars = bytearray()
        j = start
        while j + 1 < n:
            c = blob[j] | (blob[j+1] << 8)
            chars += bytes([blob[j], blob[j+1]])
            j += 2
            if c == ord("}"):
                break
        try:
            s = chars.decode("utf-16-le")
            obj = json.loads(s)
            out.append((start, j, s, obj))
        except Exception:
            pass
    return out

res = {}
for k, p in PATHS.items():
    blob = base64.b64decode(json.load(open(p, encoding="utf-8"))["m_ExtraDataString"])
    objs = objects(blob)
    res[k] = (blob, objs)
    print(k, "objects parsed:", len(objs))

# compare field by field, assuming same order
_, oo = res["orig"]
for which in ("ours", "other"):
    _, ob = res[which]
    print("=== diffs orig vs", which)
    nd = 0
    for idx, ((s1, e1, j1, a), (s2, e2, j2, b)) in enumerate(zip(oo, ob)):
        if a != b:
            keys = set(a) | set(b)
            delta = {kk: (a.get(kk), b.get(kk)) for kk in keys if a.get(kk) != b.get(kk)}
            name = b.get("m_BundleName") or a.get("m_BundleName") or ("idx%d" % idx)
            print("  #%d %s" % (idx, name))
            for kk, (va, vb) in delta.items():
                print("      %s: %r -> %r" % (kk, va, vb))
            nd += 1
            if nd > 40:
                print("  ... more")
                break
    if nd == 0:
        print("  (identical)")
