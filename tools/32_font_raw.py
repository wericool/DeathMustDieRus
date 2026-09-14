# -*- coding: utf-8 -*-
"""Dump readable strings + raw layout info from the TMP font MonoBehaviour objects."""
import os, re, sys, collections
import UnityPy

GAME = r"D:\Steam\steamapps\common\Death Must Die"
DATA = os.path.join(GAME, "Death Must Die_Data")

FILES = [
    os.path.join(DATA, "sharedassets0.assets"),
    os.path.join(DATA, "resources.assets"),
]

NEEDLE = b"PT Serif"
NEEDLE2 = b"TextHeaders_Sdf"


def strings_in(buf, minlen=3):
    out = []
    for m in re.finditer(rb"[\x20-\x7e]{%d,}" % minlen, buf):
        out.append((m.start(), m.group().decode("ascii", "replace")))
    return out


def main():
    for path in FILES:
        print("=" * 100)
        print(os.path.basename(path))
        env = UnityPy.load(path)
        for obj in env.objects:
            if obj.type.name != "MonoBehaviour":
                continue
            raw = obj.get_raw_data()
            if NEEDLE not in raw and NEEDLE2 not in raw:
                continue
            print("-" * 90)
            print("path_id:", obj.path_id, "size:", len(raw))
            ss = strings_in(raw)
            for off, s in ss[:60]:
                print("   @%-6d %s" % (off, s[:120]))
            print("   --- int32 view of first 160 bytes ---")
            import struct
            vals = struct.unpack_from("<%dI" % (min(len(raw), 160) // 4), raw, 0)
            print("   ", " ".join(str(v) for v in vals[:40]))


if __name__ == "__main__":
    main()
