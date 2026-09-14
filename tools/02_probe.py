# -*- coding: utf-8 -*-
"""Probe: can we read StringTable MonoBehaviour fields (typetree present)?"""
import os, json
import UnityPy

BUNDLES = r"E:\Games\DeathMustDieRus\00_original_bundles"
en = os.path.join(BUNDLES, "localization-string-tables-english(en)_assets_all.bundle")

env = UnityPy.load(en)
for obj in env.objects:
    if obj.type.name != "MonoBehaviour":
        continue
    print("--- reading", obj.path_id)
    try:
        data = obj.read()
    except Exception as e:
        print("   READ FAIL:", e)
        continue
    print("   class:", type(data).__name__)
    print("   m_Name:", getattr(data, "m_Name", None))
    print("   m_Script:", getattr(data, "m_Script", None))
    tt = getattr(obj, "serialized_type", None)
    print("   serialized_type:", tt)
    if hasattr(data, "__dict__"):
        keys = [k for k in data.__dict__.keys()]
        print("   __dict__ keys:", keys)
        for k in keys:
            v = data.__dict__[k]
            s = repr(v)
            print("      %-24s %s" % (k, s[:300]))
    print("   has tree:", getattr(obj, "has_type_tree", None))
    break
