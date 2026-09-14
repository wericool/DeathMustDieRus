# -*- coding: utf-8 -*-
"""Recon: list every object inside the localization bundles."""
import os, sys, collections
import UnityPy

BUNDLES = r"E:\Games\DeathMustDieRus\00_original_bundles"

def main():
    for fn in sorted(os.listdir(BUNDLES)):
        if not fn.endswith(".bundle"):
            continue
        path = os.path.join(BUNDLES, fn)
        print("=" * 100)
        print("BUNDLE:", fn, os.path.getsize(path), "bytes")
        env = UnityPy.load(path)
        counter = collections.Counter()
        rows = []
        for obj in env.objects:
            counter[obj.type.name] += 1
            name = ""
            try:
                if obj.type.name in ("MonoBehaviour", "TextAsset", "AssetBundle"):
                    d = obj.read()
                    name = getattr(d, "m_Name", "") or getattr(d, "name", "")
            except Exception as e:
                name = "<err %s>" % e
            rows.append((obj.type.name, obj.path_id, name))
        for t, c in counter.most_common():
            print("   %-24s %d" % (t, c))
        for t, pid, name in rows:
            print("      %-20s pathid=%-20s %s" % (t, pid, name))
        # container / assetbundle info
        for obj in env.objects:
            if obj.type.name == "AssetBundle":
                d = obj.read()
                print("   AssetBundle m_Name:", d.m_Name)
                try:
                    print("   container:", d.m_Container)
                except Exception:
                    pass

if __name__ == "__main__":
    main()
