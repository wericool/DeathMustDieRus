# -*- coding: utf-8 -*-
"""Inspect TMP_FontAsset objects in the game's main data files."""
import os, sys, collections, traceback
import UnityPy

GAME = r"D:\Steam\steamapps\common\Death Must Die"
DATA = os.path.join(GAME, "Death Must Die_Data")

TARGETS = ["TextHeaders_Sdf", "TextBody_Sdf", "PtSerifRegular_Font_Sdf",
           "TextBody_Bulletin_Sdf", "TextBody_Items_Sdf", "TextHeaders_Items_Sdf"]

FILES = [
    os.path.join(DATA, "sharedassets0.assets"),
    os.path.join(DATA, "resources.assets"),
]


def cyr(s):
    return sum(1 for c in s if 0x0400 <= ord(c) <= 0x04FF)


def main():
    for path in FILES:
        print("=" * 100)
        print(os.path.basename(path))
        env = UnityPy.load(path)
        n_mb = 0
        ok = 0
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            n_mb += 1
            try:
                d = obj.read()
                ok += 1
            except Exception:
                continue
            nm = getattr(d, "m_Name", "") or ""
            if nm not in TARGETS:
                continue
            print("-" * 90)
            print("FONT:", nm, " path_id:", obj.path_id)
            keys = list(d.__dict__.keys())
            print("  fields:", keys)
            for k in keys:
                if k in ("object_reader", "references"):
                    continue
                v = getattr(d, k, None)
                if k == "m_CharacterTable":
                    chars = []
                    for c in v:
                        chars.append(getattr(c, "m_Unicode", None))
                    cr = [c for c in chars if c and 0x0400 <= c <= 0x04FF]
                    print("     m_CharacterTable: n=%d, cyrillic=%d" % (len(chars), len(cr)))
                    print("     sample unicode:", [hex(c) for c in chars[:20] if c])
                elif k == "m_GlyphTable":
                    print("     m_GlyphTable: n=%d" % len(v))
                elif isinstance(v, (str, int, float, bool)) or v is None:
                    print("     %-34s %r" % (k, v))
                elif isinstance(v, (list, tuple)):
                    print("     %-34s list n=%d %s" % (k, len(v), repr(v[:6])[:140]))
                else:
                    print("     %-34s %s" % (k, repr(v)[:140]))
        print("  MonoBehaviours: %d, readable: %d" % (n_mb, ok))


if __name__ == "__main__":
    main()
