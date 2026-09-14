# -*- coding: utf-8 -*-
"""
Build the Russian localisation bundles.

  in : 00_original_bundles/*.bundle , 02_translation/ru_build.json
  out: 03_build/StandaloneWindows64/localization-string-tables-english(en)_assets_all.bundle
       03_build/StandaloneWindows64/localization-string-tables-bulgarian(bg)_assets_all.bundle
       03_build/catalog.json

Notes
-----
The string tables are MonoBehaviour assets whose entries carry [SerializeReference]
metadata, which UnityPy's *object* writer cannot serialise.  Reading and writing the
typetree as a plain dict (obj.parse_as_dict / obj.save_typetree) works for all 54
tables, so that is what we use here.

The English bundle is replaced with the Russian text (the game has no language
selector and always resolves to locale "en").  The Bulgarian bundle is patched with
the same values defensively, so Russian shows up even if the locale ever resolves
to "bg".
"""
import os, sys, json, shutil
import UnityPy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dmd_catalog as dc

ROOT = r"E:\Games\DeathMustDieRus"
ORIG = os.path.join(ROOT, "00_original_bundles")
BUILD = os.path.join(ROOT, "03_build")
OUTDIR = os.path.join(BUILD, "StandaloneWindows64")

EN_BUNDLE = "localization-string-tables-english(en)_assets_all.bundle"
BG_BUNDLE = "localization-string-tables-bulgarian(bg)_assets_all.bundle"

RU = json.load(open(os.path.join(ROOT, "02_translation", "ru_build.json"), encoding="utf-8"))


def coll_of(name, suffix):
    return name[: -len(suffix)] if name.endswith(suffix) else name


def read_tables(path, locale_suffix):
    """Return [(obj, tree, coll, name)] for every string table of that locale."""
    env = UnityPy.load(path)
    out = []
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            tree = obj.parse_as_dict()
        except Exception:
            continue
        if not isinstance(tree, dict):
            continue
        name = tree.get("m_Name")
        if not isinstance(name, str) or not name.endswith(locale_suffix):
            continue
        if not tree.get("m_TableData"):
            continue
        out.append((obj, tree, coll_of(name, locale_suffix), name))
    return env, out


def patch_bundle(src_name, locale_suffix, out_name=None, dry=False):
    src = os.path.join(ORIG, src_name)
    env, tables = read_tables(src, locale_suffix)
    stats = {"tables": 0, "entries": 0, "translated": 0, "kept": 0,
             "changed_tables": 0, "missing_coll": []}
    for obj, tree, coll, name in tables:
        table = RU.get(coll)
        if table is None:
            stats["missing_coll"].append(coll)
            continue
        stats["tables"] += 1
        changed = False
        for e in tree["m_TableData"]:
            stats["entries"] += 1
            v = table.get(str(e["m_Id"]))
            if v:
                if e["m_Localized"] != v:
                    e["m_Localized"] = v
                    changed = True
                stats["translated"] += 1
            else:
                stats["kept"] += 1
        if changed:
            stats["changed_tables"] += 1
            if not dry:
                obj.save_typetree(tree)
    if not dry:
        os.makedirs(OUTDIR, exist_ok=True)
        data = env.file.save(packer="lz4")
        if isinstance(data, str):
            data = data.encode()
        open(os.path.join(OUTDIR, out_name or src_name), "wb").write(data)
        stats["bytes"] = len(data)
    return stats


def verify(out_name, locale_suffix, sample=6):
    """Re-open the built bundle and verify the Russian text is really there."""
    path = os.path.join(OUTDIR, out_name)
    env, tables = read_tables(path, locale_suffix)
    bad = []
    shown = 0
    total = 0
    ru_total = 0
    for obj, tree, coll, name in tables:
        table = RU.get(coll, {})
        for e in tree["m_TableData"]:
            total += 1
            want = table.get(str(e["m_Id"]))
            if not want:
                continue
            ru_total += 1
            if e["m_Localized"] != want:
                bad.append((coll, e["m_Id"]))
            elif shown < sample and len(want) > 25:
                print("   %-26s %r" % (coll, want[:70]))
                shown += 1
    print("   verified tables=%d entries=%d russian=%d mismatches=%d" % (
        len(tables), total, ru_total, len(bad)))
    return bad


def main():
    os.makedirs(OUTDIR, exist_ok=True)

    print("=== English string tables -> Russian ===")
    en_stats = patch_bundle(EN_BUNDLE, "_en")
    print(json.dumps(en_stats, ensure_ascii=False, indent=1))

    print("=== Bulgarian string tables (defensive, values only) ===")
    bg_stats = patch_bundle(BG_BUNDLE, "_bg")
    print(json.dumps(bg_stats, ensure_ascii=False, indent=1))

    print("=== verify EN bundle round-trip ===")
    bad = verify(EN_BUNDLE, "_en")
    if bad:
        print("   !! MISMATCHES:", bad[:10])

    # id alignment between the two locales (guards the defensive BG patch)
    print("=== id alignment en vs bg ===")
    _, ten = read_tables(os.path.join(ORIG, EN_BUNDLE), "_en")
    _, tbg = read_tables(os.path.join(ORIG, BG_BUNDLE), "_bg")
    me = {c: {str(e["m_Id"]) for e in t["m_TableData"]} for _, t, c, _ in ten}
    mb = {c: {str(e["m_Id"]) for e in t["m_TableData"]} for _, t, c, _ in tbg}
    diff = 0
    for c in me:
        d = len(me[c] ^ mb.get(c, set()))
        if d:
            diff += d
            print("   %-40s symmetric-difference=%d (en=%d bg=%d)" % (c, d, len(me[c]), len(mb.get(c, set()))))
    print("   total id mismatches:", diff)

    # catalog: disable CRC for the two bundles we rewrote
    bundle_internal = {}
    for fn in (EN_BUNDLE, BG_BUNDLE):
        env = UnityPy.load(os.path.join(ORIG, fn))
        for o in env.objects:
            if o.type.name == "AssetBundle":
                bundle_internal[fn] = o.read().m_Name
                break
    print("internal bundle names:", bundle_internal)

    cat, extra, recs = dc.load_catalog(os.path.join(ORIG, "catalog.json"))
    for fn in (EN_BUNDLE, BG_BUNDLE):
        bn = bundle_internal.get(fn, "").replace(".bundle", "")
        changed = dc.set_no_crc(recs, {bn})
        print("crc disabled for", bn, "->", changed)
    dc.save_catalog(cat, recs, os.path.join(BUILD, "catalog.json"))

    cat2, _, recs2 = dc.load_catalog(os.path.join(BUILD, "catalog.json"))
    for r in recs2:
        j = r["json"]
        if j["m_BundleName"] in {b.replace(".bundle", "") for b in bundle_internal.values()}:
            print("  verified:", j["m_BundleName"], "crc =", j["m_Crc"],
                  "useCrc =", j["m_UseCrcForCachedBundles"])
    print("done ->", BUILD)


if __name__ == "__main__":
    main()
