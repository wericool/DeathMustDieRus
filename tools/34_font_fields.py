# -*- coding: utf-8 -*-
"""Full dump of the TMP font asset fields we need for patching."""
import os
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
import UnityPy.environment as _envmod

GAME = r"D:\Steam\steamapps\common\Death Must Die"
DATA = os.path.join(GAME, "Death Must Die_Data")

_g = TypeTreeGenerator("2021.3.11f1")
_g.load_local_dll_folder(os.path.join(DATA, "Managed"))
_envmod.Environment.typetree_generator = _g

WANT = ("TextHeaders_Sdf", "TextBody_Sdf", "PtSerifRegular_Font_Sdf",
        "TextBody_Bulletin_Sdf", "TextBody_Items_Sdf", "TextHeaders_Items_Sdf")

FIELDS = ["m_AtlasPopulationMode", "m_IsMultiAtlasTexturesEnabled", "m_ClearDynamicDataOnBuild",
          "m_AtlasWidth", "m_AtlasHeight", "m_AtlasPadding", "m_AtlasRenderMode",
          "m_AtlasTextureIndex", "m_AtlasTextures", "m_UsedGlyphRects", "m_FreeGlyphRects",
          "m_FallbackFontAssetTable", "m_SourceFontFile", "m_SourceFontFileGUID",
          "m_SourceFontFilePath", "m_Material", "m_MaterialHashCode", "m_HashCode"]


def main():
    for path in [os.path.join(DATA, "sharedassets0.assets"), os.path.join(DATA, "resources.assets")]:
        env = UnityPy.load(path)
        # externals
        sf = list(env.files.values())[0]
        try:
            exts = [getattr(e, "path", None) or getattr(e, "name", None) for e in sf.externals]
            print("EXTERNALS of", os.path.basename(path), exts)
        except Exception as e:
            print("externals err", e)
        # Font objects
        for obj in env.objects:
            if obj.type.name == "Font":
                d = obj.read()
                print("   FONT path_id=%s name=%r" % (obj.path_id, getattr(d, "m_Name", None)))
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            raw = obj.get_raw_data()
            if not any(w.encode() in raw for w in WANT):
                continue
            d = obj.read()
            nm = getattr(d, "m_Name", None)
            if nm not in WANT:
                continue
            print("=" * 90)
            print("%s  path_id=%s  file=%s" % (nm, obj.path_id, os.path.basename(path)))
            for f in FIELDS:
                v = getattr(d, f, "<absent>")
                if isinstance(v, list):
                    if v and hasattr(v[0], "m_FileID"):
                        v = ["%s:%s" % (e.m_FileID, e.m_PathID) for e in v]
                    else:
                        v = "list(n=%d) %s" % (len(v), repr(v[:3])[:110])
                print("   %-32s %s" % (f, repr(v)[:150]))
            # atlas texture info
            for e in (getattr(d, "m_AtlasTextures", None) or []):
                try:
                    t = e.deref_parse_as_object()
                    print("   ATLAS %s:%s -> %s  %dx%d fmt=%s mip=%s" % (
                        e.m_FileID, e.m_PathID, getattr(t, "m_Name", None),
                        getattr(t, "m_Width", None), getattr(t, "m_Height", None),
                        getattr(t, "m_TextureFormat", None), getattr(t, "m_MipCount", None)))
                except Exception as ex:
                    print("   ATLAS deref fail:", ex)


if __name__ == "__main__":
    main()
