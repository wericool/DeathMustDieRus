# -*- coding: utf-8 -*-
"""
Build 03_build catalog.json from the ORIGINAL with the proven AnotherRus strategy:
  - m_Crc = 0 for ALL 8 localization bundles
  - m_RedirectLimit = 255
Everything else stays byte-identical to the original catalog.
"""
import json, sys, base64, re, struct

sys.stdout.reconfigure(encoding="utf-8")
SRC = r"E:\Games\DeathMustDieRus\backup_game\catalog.json"
DST = r"E:\Games\DeathMustDieRus\03_build\catalog.json"

cat = json.load(open(SRC, encoding="utf-8"))
blob = bytearray(base64.b64decode(cat["m_ExtraDataString"]))

def objects(blob):
    out = []
    for m in re.finditer(rb"\{\x00", bytes(blob)):
        start = m.start()
        chars = bytearray()
        j = start
        n = len(blob)
        while j + 1 < n:
            c = blob[j] | (blob[j + 1] << 8)
            chars += bytes([blob[j], blob[j + 1]])
            j += 2
            if c == ord("}"):
                break
        try:
            obj = json.loads(chars.decode("utf-16-le"))
            out.append((start, j, obj))
        except Exception:
            pass
    return out

objs = objects(blob)
assert len(objs) == 8, "expected 8 bundle option objects, got %d" % len(objs)

# patch from the end so earlier offsets stay valid
for start, end, obj in sorted(objs, key=lambda e: -e[0]):
    obj["m_Crc"] = 0
    obj["m_RedirectLimit"] = 255
    text = json.dumps(obj, separators=(",", ":"))
    data = text.encode("utf-16-le")
    blob[start:end] = data
    blob[start - 4:start] = struct.pack("<i", len(data))

cat["m_ExtraDataString"] = base64.b64encode(bytes(blob)).decode("ascii")

# verify round-trip
check = objects(base64.b64decode(cat["m_ExtraDataString"]))
for start, end, obj in check:
    print("%-40s crc=%d redirect=%d" % (obj.get("m_BundleName", "?"), obj.get("m_Crc", -1), obj.get("m_RedirectLimit", -1)))
assert len(check) == 8

json.dump(cat, open(DST, "w", encoding="utf-8"))
print("written", DST)
