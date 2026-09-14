# -*- coding: utf-8 -*-
"""
Smoke test: patch two main-menu strings in the ENGLISH string-table bundle,
install it into the game together with a CRC-disabled catalog, so we can verify
in-game that a modified bundle actually loads.
"""
import os, sys, json, shutil
import UnityPy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dmd_catalog as dc

ROOT = r"E:\Games\DeathMustDieRus"
ORIG = os.path.join(ROOT, "00_original_bundles")
GAME = r"D:\Steam\steamapps\common\Death Must Die"
AA = os.path.join(GAME, "Death Must Die_Data", "StreamingAssets", "aa")
AAW = os.path.join(AA, "StandaloneWindows64")
BKP = os.path.join(ROOT, "backup_game")
TMP = os.path.join(ROOT, "09_test")

EN_BUNDLE = "localization-string-tables-english(en)_assets_all.bundle"

TESTS = {
    90024878080: "ИГРАТЬ (RU)",        # main_play
    121721233408: "НАСТРОЙКИ (RU)",    # main_opts
    146819948544: "ВЫХОД (RU)",        # main_quit
}


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "install"
    os.makedirs(BKP, exist_ok=True)
    os.makedirs(os.path.join(BKP, "StandaloneWindows64"), exist_ok=True)

    if action == "restore":
        for f in os.listdir(os.path.join(BKP, "StandaloneWindows64")):
            shutil.copy2(os.path.join(BKP, "StandaloneWindows64", f), os.path.join(AAW, f))
            print("restored", f)
        shutil.copy2(os.path.join(BKP, "catalog.json"), os.path.join(AA, "catalog.json"))
        print("restored catalog.json")
        return

    # ---- backup
    for f in (EN_BUNDLE,):
        dst = os.path.join(BKP, "StandaloneWindows64", f)
        if not os.path.exists(dst):
            shutil.copy2(os.path.join(AAW, f), dst)
            print("backed up", f)
    if not os.path.exists(os.path.join(BKP, "catalog.json")):
        shutil.copy2(os.path.join(AA, "catalog.json"), os.path.join(BKP, "catalog.json"))
        print("backed up catalog.json")

    # ---- patch bundle
    env = UnityPy.load(os.path.join(ORIG, EN_BUNDLE))
    n = 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        d = obj.read()
        if getattr(d, "m_Name", "") == "Loc_AppUI_en":
            for e in d.m_TableData:
                if e.m_Id in TESTS:
                    print("  patch id=%s %r -> %r" % (e.m_Id, e.m_Localized, TESTS[e.m_Id]))
                    e.m_Localized = TESTS[e.m_Id]
                    n += 1
            d.save()
    print("patched", n, "entries")
    data = env.file.save(packer="lz4")
    if isinstance(data, str):
        data = data.encode()
    os.makedirs(TMP, exist_ok=True)
    tmp_bundle = os.path.join(TMP, EN_BUNDLE)
    open(tmp_bundle, "wb").write(data)
    print("wrote test bundle", len(data), "bytes (orig", os.path.getsize(os.path.join(ORIG, EN_BUNDLE)), ")")

    # ---- install
    shutil.copy2(tmp_bundle, os.path.join(AAW, EN_BUNDLE))
    print("installed bundle ->", AAW)

    # ---- patch catalog
    envb = UnityPy.load(os.path.join(ORIG, EN_BUNDLE))
    bn = None
    for o in envb.objects:
        if o.type.name == "AssetBundle":
            bn = o.read().m_Name.replace(".bundle", "")
            break
    cat, extra, recs = dc.load_catalog(os.path.join(ORIG, "catalog.json"))
    ch = dc.set_no_crc(recs, {bn})
    dc.save_catalog(cat, recs, os.path.join(AA, "catalog.json"))
    print("catalog CRC disabled for", bn, ch)


if __name__ == "__main__":
    main()
