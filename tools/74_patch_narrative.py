# -*- coding: utf-8 -*-
"""
Patch translated Nar_* CSVs into the font-patched sharedassets0.assets (03_build/Data).
"""
import os, sys
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
RU = r"E:\Games\DeathMustDieRus\02_translation\narrative\ru"
ASSETS = r"E:\Games\DeathMustDieRus\03_build\Data\sharedassets0.assets"
BAK = ASSETS + ".pre_narr"

if not os.path.exists(BAK):
    import shutil
    shutil.copy2(ASSETS, BAK)
    print("backup ->", BAK)
else:
    import shutil
    shutil.copy2(BAK, ASSETS)  # start from the pre_narr state each run
    print("restored from", BAK)

env = UnityPy.load(ASSETS)
patched = []
for obj in env.objects:
    if obj.type.name != "TextAsset":
        continue
    d = obj.read()
    name = d.m_Name
    if not name.startswith("Nar_"):
        continue
    src = os.path.join(RU, name + ".csv")
    if not os.path.exists(src):
        print("!! no RU csv for", name)
        continue
    text = open(src, encoding="utf-8").read()
    tree = obj.parse_as_dict()
    tree["m_Script"] = text
    obj.save_typetree(tree)
    patched.append((name, len(text)))

print("patched:", patched)
data = env.file.save(packer="lz4")
if isinstance(data, str):
    data = data.encode()
open(ASSETS, "wb").write(data)
print("saved", ASSETS, len(data), "bytes")

# verify round-trip
env2 = UnityPy.load(ASSETS)
for obj in env2.objects:
    if obj.type.name == "TextAsset":
        d = obj.read()
        if d.m_Name.startswith("Nar_"):
            s = d.m_Script
            if isinstance(s, bytes):
                s = s.decode("utf-8", errors="replace")
            first = s.splitlines()[1] if len(s.splitlines()) > 1 else ""
            print("verify %-14s %7d chars | %s" % (d.m_Name, len(s), first[:100]))
