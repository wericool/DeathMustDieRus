# -*- coding: utf-8 -*-
"""
Round-trip test: modify a StringTable value inside a bundle, save it, reload,
and verify every table/entry is intact except the intended change.
"""
import os, sys, json, hashlib, shutil
import UnityPy

ROOT = r"E:\Games\DeathMustDieRus"
SRC = os.path.join(ROOT, "00_original_bundles", "localization-string-tables-bulgarian(bg)_assets_all.bundle")
WORK = os.path.join(ROOT, "09_test")
os.makedirs(WORK, exist_ok=True)
DST = os.path.join(WORK, "rt_bg.bundle")


def snapshot(path):
    env = UnityPy.load(path)
    snap = {}
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        d = obj.read()
        nm = getattr(d, "m_Name", None)
        if not nm:
            continue
        if hasattr(d, "m_TableData") and d.m_TableData is not None:
            snap[nm] = {e.m_Id: e.m_Localized for e in d.m_TableData}
    return snap


def main():
    print("original snapshot ...")
    before = snapshot(SRC)
    print("  tables:", len(before), "entries:", sum(len(v) for v in before.values()))

    print("load + modify ...")
    env = UnityPy.load(SRC)
    changed = 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        d = obj.read()
        if getattr(d, "m_Name", "") == "Loc_AppUI_bg":
            for e in d.m_TableData:
                if e.m_Id == 1 or changed == 0:
                    e.m_Localized = "ТЕСТ РУССКОГО ТЕКСТА — длинная строка для проверки изменения размера объекта"
                    changed += 1
            d.save()
            print("  patched", d.m_Name, "entries changed:", changed)
            break
    print("save ...")
    data = env.file.save(packer="lz4")
    if isinstance(data, str):
        data = data.encode()
    with open(DST, "wb") as f:
        f.write(data)
    print("  wrote", DST, len(data), "bytes (orig", os.path.getsize(SRC), ")")

    print("reload + verify ...")
    after = snapshot(DST)
    print("  tables:", len(after), "entries:", sum(len(v) for v in after.values()))
    problems = []
    if set(before) != set(after):
        problems.append("table set differs: missing=%s extra=%s" %
                        (set(before) - set(after), set(after) - set(before)))
    diffs = 0
    for t in before:
        if t not in after:
            continue
        if set(before[t]) != set(after[t]):
            problems.append("entry-id set differs in %s" % t)
            continue
        for k, v in before[t].items():
            if after[t][k] != v:
                diffs += 1
                if diffs <= 5:
                    print("   DIFF %s id=%s\n      old=%r\n      new=%r" % (t, k, v, after[t][k]))
    print("  total value diffs:", diffs, "(expected 1)")
    print("  PROBLEMS:", problems if problems else "none")

    # container / bundle name check
    for path in (SRC, DST):
        e = UnityPy.load(path)
        for o in e.objects:
            if o.type.name == "AssetBundle":
                dd = o.read()
                print("  %-12s bundle m_Name=%s container_entries=%d" %
                      (os.path.basename(path), dd.m_Name, len(dd.m_Container)))
                break


if __name__ == "__main__":
    main()
