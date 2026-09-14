# -*- coding: utf-8 -*-
"""
Patch TMP font assets so Cyrillic can be rasterised at runtime.

Root cause found: TextBody_Sdf (the TMP default font asset, PT Serif, Dynamic)
has an atlas that is 96% full and m_IsMultiAtlasTexturesEnabled = 0, so
TryAddCharacterInternal() fails and every Cyrillic character is replaced by a space.

Fix: enable multi-atlas textures (TMP then calls SetupNewAtlasTexture() and grows
a fresh readable atlas at runtime).  Additionally TextBody_Sdf is appended to the
fallback table of the fonts that cannot reach it (their own source font, Bluu Next,
has no Cyrillic at all and two of them are Static with a NULL source font).

Usage:
    python 40_font_patch.py probe      # report only
    python 40_font_patch.py patch      # backup + patch in place
    python 40_font_patch.py restore    # restore from backup
"""
import os
import shutil
import sys
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
import UnityPy.environment as _envmod

GAME = r"D:\Steam\steamapps\common\Death Must Die"
DATA = os.path.join(GAME, "Death Must Die_Data")
ROOT = r"E:\Games\DeathMustDieRus"
BKP = os.path.join(ROOT, "backup_game")

TARGET_FILES = ["sharedassets0.assets", "resources.assets"]

# font asset name -> (source file that hosts it)
HOSTS = {
    "sharedassets0.assets": ["TextBody_Sdf", "TextHeaders_Sdf"],
    "resources.assets": ["PtSerifRegular_Font_Sdf", "TextBody_Bulletin_Sdf",
                         "TextBody_Items_Sdf", "TextHeaders_Items_Sdf"],
}

# name of the font asset that has PT Serif + Cyrillic + readable atlas
PT_SERIF_BODY = "TextBody_Sdf"
# file id (1-based Unity external index) of the file hosting PT_SERIF_BODY, per host file
PT_REF = {
    "sharedassets0.assets": (0, 32376),   # local
    "resources.assets": (2, 32376),       # externals[1] == sharedassets0.assets
}


def setup():
    g = TypeTreeGenerator("2021.3.11f1")
    g.load_local_dll_folder(os.path.join(DATA, "Managed"))
    _envmod.Environment.typetree_generator = g


def is_font_asset(d):
    return hasattr(d, "m_AtlasPopulationMode") and hasattr(d, "m_CharacterTable")


def walk():
    """Yield (host_filename, obj, data) for every TMP font asset found."""
    for host in TARGET_FILES:
        path = os.path.join(DATA, host)
        env = UnityPy.load(path)
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            raw = obj.get_raw_data()
            if b"_Sdf" not in raw:
                continue
            try:
                d = obj.read()
            except Exception:
                continue
            if not is_font_asset(d):
                continue
            yield host, env, obj, d


def probe():
    for host, env, obj, d in walk():
        fb = getattr(d, "m_FallbackFontAssetTable", None) or []
        fbs = ["%s:%s" % (e.m_FileID, e.m_PathID) for e in fb]
        src = getattr(d, "m_SourceFontFile", None)
        print("%-22s %-26s pid=%-6s mode=%s multi=%s atlas=%sx%s src=%s:%s fb=%s" % (
            host, d.m_Name, obj.path_id, d.m_AtlasPopulationMode,
            d.m_IsMultiAtlasTexturesEnabled, d.m_AtlasWidth, d.m_AtlasHeight,
            getattr(src, "m_FileID", "?"), getattr(src, "m_PathID", "?"), fbs))


def patch():
    # ---- backup
    os.makedirs(BKP, exist_ok=True)
    for host in TARGET_FILES:
        dst = os.path.join(BKP, host)
        if not os.path.exists(dst):
            shutil.copy2(os.path.join(DATA, host), dst)
            print("backed up", host)

    for host in TARGET_FILES:
        path = os.path.join(DATA, host)
        env = UnityPy.load(path)
        changed = 0
        report = []
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            raw = obj.get_raw_data()
            if b"_Sdf" not in raw:
                continue
            try:
                d = obj.read()
            except Exception:
                continue
            if not is_font_asset(d):
                continue
            name = d.m_Name
            touched = []

            if not d.m_IsMultiAtlasTexturesEnabled:
                d.m_IsMultiAtlasTexturesEnabled = True
                touched.append("multi-atlas=1")

            # make sure every font can reach the PT Serif body font
            want = PT_REF[host]
            fb = getattr(d, "m_FallbackFontAssetTable", None)
            if fb is not None and name != PT_SERIF_BODY:
                have = {(e.m_FileID, e.m_PathID) for e in fb}
                if want not in have:
                    from UnityPy.classes import PPtr
                    fb.append(PPtr(m_FileID=want[0], m_PathID=want[1]))
                    touched.append("+=fallback %s:%s" % want)

            if touched:
                obj.save_typetree(d)
                changed += 1
                report.append("  %-26s %s" % (name, ", ".join(touched)))
        if changed:
            data = env.file.save()
            if isinstance(data, str):
                data = data.encode()
            open(path, "wb").write(data)
            print("%s: %d font(s) patched, wrote %d bytes (was %d)" % (
                host, changed, len(data), os.path.getsize(os.path.join(BKP, host))))
            for r in report:
                print(r)
        else:
            print(host, ": nothing to change")


def restore():
    for host in TARGET_FILES:
        src = os.path.join(BKP, host)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(DATA, host))
            print("restored", host)
        else:
            print("no backup for", host)


if __name__ == "__main__":
    setup()
    cmd = sys.argv[1] if len(sys.argv) > 1 else "probe"
    {"probe": probe, "patch": patch, "restore": restore}[cmd]()
