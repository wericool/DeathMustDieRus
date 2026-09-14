# -*- coding: utf-8 -*-
"""Extract Nar_* TextAssets (narrative CSVs) from the ORIGINAL sharedassets0.assets."""
import os, sys, csv, io
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
SRC = r"E:\Games\DeathMustDieRus\backup_game\sharedassets0.assets"
OUT = r"E:\Games\DeathMustDieRus\02_translation\narrative"
os.makedirs(OUT, exist_ok=True)

env = UnityPy.load(SRC)
found = []
for obj in env.objects:
    if obj.type.name == "TextAsset":
        d = obj.read()
        name = d.m_Name
        if name.startswith("Nar_"):
            script = d.m_Script
            if isinstance(script, bytes):
                script = script.decode("utf-8", errors="replace")
            found.append((name, len(script)))
            p = os.path.join(OUT, name + ".csv")
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(script)

for name, ln in sorted(found):
    print("%-16s %7d chars" % (name, ln))

# show head of Nar_Heroes to confirm column layout
p = os.path.join(OUT, "Nar_Heroes.csv")
lines = open(p, encoding="utf-8").read().splitlines()
print("Nar_Heroes lines:", len(lines))
for l in lines[:8]:
    print("   ", l[:180])
