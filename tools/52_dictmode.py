# -*- coding: utf-8 -*-
"""Test writing string tables through UnityPy's dict typetree mode."""
import os, sys, json, traceback
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"E:\Games\DeathMustDieRus"
ORIG = os.path.join(ROOT, "00_original_bundles")
EN = "localization-string-tables-english(en)_assets_all.bundle"

env = UnityPy.load(os.path.join(ORIG, EN))
ok, bad = [], []
tables = []
for obj in env.objects:
    if obj.type.name != "MonoBehaviour":
        continue
    tree = obj.parse_as_dict()
    if not isinstance(tree, dict):
        continue
    name = tree.get("m_Name", "")
    if not isinstance(name, str) or not name.endswith("_en"):
        continue
    td = tree.get("m_TableData")
    if not td:
        continue
    tables.append((obj, tree, name))

print("tables:", len(tables))
for obj, tree, name in tables:
    e0 = tree["m_TableData"][0]
    orig = e0["m_Localized"]
    e0["m_Localized"] = orig + " "
    try:
        obj.save_typetree(tree)
        ok.append(name)
    except Exception as ex:
        bad.append((name, type(ex).__name__, str(ex)[:150]))
    finally:
        e0["m_Localized"] = orig
        try:
            obj.save_typetree(tree)
        except Exception:
            pass

print("OK  :", len(ok))
print("FAIL:", len(bad))
for n, t, m in bad:
    print("   %-46s %s %s" % (n, t, m))

# round-trip: save the whole bundle and re-open it
data = env.file.save(packer="lz4")
if isinstance(data, str):
    data = data.encode()
out = os.path.join(ROOT, "09_test", "dictmode_test.bundle")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "wb").write(data)
print("wrote", out, len(data))
env2 = UnityPy.load(out)
n = 0
for o in env2.objects:
    if o.type.name == "MonoBehaviour":
        t = o.parse_as_dict()
        if isinstance(t, dict) and t.get("m_TableData"):
            n += 1
print("re-opened, tables:", n)
