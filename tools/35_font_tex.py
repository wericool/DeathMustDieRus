# -*- coding: utf-8 -*-
"""Check atlas texture readability and Font asset data availability."""
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

for path in [os.path.join(DATA, "sharedassets0.assets"), os.path.join(DATA, "resources.assets")]:
    print("=" * 90)
    print(os.path.basename(path))
    env = UnityPy.load(path)
    for obj in env.objects:
        if obj.type.name == "Font":
            d = obj.read()
            fd = getattr(d, "m_FontData", None)
            print("  Font %s %r  m_FontData=%s bytes  m_FontSize=%s  m_Ascent=%s" % (
                obj.path_id, getattr(d, "m_Name", None),
                len(fd) if fd is not None else None,
                getattr(d, "m_FontSize", None), getattr(d, "m_Ascent", None)))
        elif obj.type.name == "Texture2D":
            raw = obj.get_raw_data()
            if b"Atlas" not in raw[:400]:
                continue
            try:
                d = obj.read()
            except Exception:
                continue
            nm = getattr(d, "m_Name", "")
            if "Atlas" not in nm:
                continue
            print("  Tex2D %s %r  %sx%s  fmt=%s  mip=%s  isReadable=%s  imageSize=%s" % (
                obj.path_id, nm, getattr(d, "m_Width", None), getattr(d, "m_Height", None),
                getattr(d, "m_TextureFormat", None), getattr(d, "m_MipCount", None),
                getattr(d, "m_IsReadable", "<absent>"),
                getattr(getattr(d, "m_StreamData", None), "size", None)))

    # TMP_Settings
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        raw = obj.get_raw_data()
        if b"TMP Settings" not in raw and b"TMP_Settings" not in raw and b"Default Font Asset" not in raw:
            continue
        try:
            d = obj.read()
        except Exception as e:
            print("  settings read fail", e); continue
        nm = getattr(d, "m_Name", "")
        if "Settings" not in nm:
            continue
        print("  SETTINGS %r" % nm)
        for k in ("m_defaultFontAsset", "m_fallbackFontAssets", "m_getFontFeaturesAtRuntime",
                  "m_missingGlyphCharacter", "m_defaultSpriteAsset", "m_warningsDisabled"):
            v = getattr(d, k, "<absent>")
            if isinstance(v, list):
                v = ["%s:%s" % (e.m_FileID, e.m_PathID) for e in v]
            print("     %-32s %s" % (k, repr(v)[:160]))
