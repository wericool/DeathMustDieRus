# -*- coding: utf-8 -*-
"""Scan all game asset files for UI objects related to language selection."""
import os, sys, re
import UnityPy

GAME = r"D:\Steam\steamapps\common\Death Must Die"
DATA = os.path.join(GAME, "Death Must Die_Data")

TARGETS = ["Option_Locale", "OptsScreen_Language", "OptionSelectionGroupEntry",
           "LocalizationManager", "OptionsSubScreen"]

files = []
for root, dirs, fs in os.walk(DATA):
    if "StreamingAssets" in root:
        continue
    for f in fs:
        if f.endswith((".assets", ".unity", ".resource")) or re.match(r"^level\d+$", f):
            files.append(os.path.join(root, f))
files.sort(key=lambda p: os.path.getsize(p))
print("asset files to scan:", len(files))


def main():
    found = {t: [] for t in TARGETS}
    for path in files:
        try:
            env = UnityPy.load(path)
        except Exception as e:
            print("  skip", os.path.basename(path), e)
            continue
        # map script path_id -> class name
        scripts = {}
        mbs = []
        for obj in env.objects:
            if obj.type.name == "MonoScript":
                try:
                    d = obj.read()
                    scripts[obj.path_id] = getattr(d, "m_ClassName", "") or ""
                except Exception:
                    pass
            elif obj.type.name == "MonoBehaviour":
                mbs.append(obj)
        for obj in mbs:
            try:
                d = obj.read()
            except Exception:
                continue
            nm = getattr(d, "m_Name", "") or ""
            scr = getattr(d, "m_Script", None)
            cls = ""
            try:
                if scr is not None and getattr(scr, "path_id", 0):
                    cls = scripts.get(scr.path_id, "")
            except Exception:
                pass
            for t in TARGETS:
                if t in cls or t in nm:
                    found[t].append((os.path.basename(path), obj.path_id, nm, cls))
        del env
    print()
    for t in TARGETS:
        print("== %s : %d hits" % (t, len(found[t])))
        for r in found[t][:20]:
            print("     %-28s pid=%-20s name=%-28s cls=%s" % r)


if __name__ == "__main__":
    main()
