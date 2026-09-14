# -*- coding: utf-8 -*-
"""Read TMP_FontAsset objects using a generated typetree."""
import os, sys, json, collections
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

GAME = r"D:\Steam\steamapps\common\Death Must Die"
DATA = os.path.join(GAME, "Death Must Die_Data")

import UnityPy.environment as _envmod

_gen = TypeTreeGenerator("2021.3.11f1")
_gen.load_local_dll_folder(os.path.join(DATA, "Managed"))
_envmod.Environment.typetree_generator = _gen
print("typetree generator ready")

WANT = ("TextHeaders_Sdf", "TextBody_Sdf", "PtSerifRegular_Font_Sdf",
        "TextBody_Bulletin_Sdf", "TextBody_Items_Sdf", "TextHeaders_Items_Sdf")

FILES = [os.path.join(DATA, "sharedassets0.assets"), os.path.join(DATA, "resources.assets")]


def cyr_info(chars):
    cy = sorted(c for c in chars if 0x0400 <= c <= 0x04FF)
    return len(cy), cy[:10], cy[-5:]


def main():
    for path in FILES:
        env = UnityPy.load(path)
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            raw = obj.get_raw_data()
            if not any(w.encode() in raw for w in WANT):
                continue
            try:
                d = obj.read()
            except Exception as e:
                print("FAILED", obj.path_id, type(e).__name__, e)
                continue
            nm = getattr(d, "m_Name", "?")
            if nm not in WANT:
                continue
            print("=" * 90)
            print("%s  (path_id=%s)  in %s" % (nm, obj.path_id, os.path.basename(path)))
            print("  m_Version:", getattr(d, "m_Version", None))
            print("  m_AtlasPopulationMode:", getattr(d, "m_AtlasPopulationMode", None))
            print("  m_IsMultiAtlasTexturesEnabled:", getattr(d, "m_IsMultiAtlasTexturesEnabled", None))
            fi = getattr(d, "m_FaceInfo", None)
            if fi is not None:
                print("  FaceInfo:", {k: getattr(fi, k, None) for k in ("m_FamilyName", "m_StyleName", "m_PointSize", "m_UnitsPerEM")})
            ct = getattr(d, "m_CharacterTable", None) or []
            codes = []
            for c in ct:
                u = getattr(c, "m_Unicode", None)
                if u is None and isinstance(c, dict):
                    u = c.get("m_Unicode")
                codes.append(u)
            codes = [c for c in codes if c is not None]
            n, first, last = cyr_info(codes)
            print("  CharacterTable: n=%d  cyrillic=%d  first_cyr=%s last_cyr=%s" % (len(codes), n, [hex(x) for x in first], [hex(x) for x in last]))
            gt = getattr(d, "m_GlyphTable", None) or []
            print("  GlyphTable: n=%d" % len(gt))

            def show(name):
                v = getattr(d, name, None)
                if v is None:
                    print("  %s: <absent>" % name); return
                out = []
                for e in v:
                    fid = getattr(e, "m_FileID", None)
                    pid = getattr(e, "m_PathID", None)
                    if fid is None and isinstance(e, dict):
                        fid, pid = e.get("m_FileID"), e.get("m_PathID")
                    out.append("%s:%s" % (fid, pid))
                print("  %s: %s" % (name, out))
            show("m_FallbackFontAssetTable")
            show("m_AtlasTextures")
            src = getattr(d, "m_SourceFontFile", None)
            print("  m_SourceFontFile:", src)
            print("  m_SourceFontFileGUID:", getattr(d, "m_SourceFontFileGUID", None))
            print("  m_SourceFontFilePath:", getattr(d, "m_SourceFontFilePath", None))
            fas = getattr(d, "m_FontAssetCreationSettings", None)
            if fas is not None:
                cs = getattr(fas, "m_CharacterSet", None)
                print("  CreationSettings.CharacterSet: %r (len %s)" % ((cs or "")[:80], len(cs or "")))


if __name__ == "__main__":
    main()
