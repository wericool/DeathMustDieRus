# -*- coding: utf-8 -*-
"""Find which string tables fail to be written back by UnityPy, and why."""
import os, sys, json, traceback
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"E:\Games\DeathMustDieRus"
ORIG = os.path.join(ROOT, "00_original_bundles")
EN = "localization-string-tables-english(en)_assets_all.bundle"

env = UnityPy.load(os.path.join(ORIG, EN))
ok, bad = [], []
for obj in env.objects:
    if obj.type.name != "MonoBehaviour":
        continue
    d = obj.read()
    name = getattr(d, "m_Name", "") or ""
    if not name.endswith("_en") or not hasattr(d, "m_TableData") or d.m_TableData is None:
        continue
    # force one change so save() actually serialises
    e0 = d.m_TableData[0]
    orig = e0.m_Localized
    e0.m_Localized = orig + " "
    try:
        d.save()
        ok.append(name)
        e0.m_Localized = orig
        d.save()
    except Exception as ex:
        bad.append((name, type(ex).__name__, str(ex)[:120]))
        e0.m_Localized = orig

print("OK  :", len(ok))
print("FAIL:", len(bad))
for n, t, m in bad:
    print("   %-46s %s %s" % (n, t, m))

# inspect metadata footprint of a failing table
if bad:
    target = bad[0][0]
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        d = obj.read()
        if getattr(d, "m_Name", "") != target:
            continue
        md = [len(getattr(e, "m_Metadata", None).m_Entries) if getattr(e, "m_Metadata", None) is not None else None
              for e in d.m_TableData[:200]]
        import collections
        print("metadata entry counts for", target, ":", collections.Counter(md))
        for e in d.m_TableData:
            m = getattr(e, "m_Metadata", None)
            if m is not None and getattr(m, "m_Entries", None):
                print("   non-empty metadata at id", e.m_Id, repr(m.m_Entries)[:200])
                break
        break
