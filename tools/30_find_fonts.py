# -*- coding: utf-8 -*-
"""Locate TMP font assets and inspect their Cyrillic coverage."""
import os, re, sys, collections

GAME = r"D:\Steam\steamapps\common\Death Must Die"
DATA = os.path.join(GAME, "Death Must Die_Data")

NEEDLES = [b"_Sdf", b"TMP_FontAsset", b"Sdf"]

def scan(paths):
    hits = collections.defaultdict(list)
    for p in paths:
        size = os.path.getsize(p)
        with open(p, "rb") as f:
            chunk = b""
            off = 0
            while True:
                buf = f.read(8 << 20)
                if not buf:
                    break
                data = chunk + buf
                for n in NEEDLES:
                    start = 0
                    while True:
                        i = data.find(n, start)
                        if i < 0:
                            break
                        # grab surrounding ascii
                        s = max(0, i - 60)
                        ctx = data[s:i + 40]
                        txt = re.sub(rb"[^\x20-\x7e]+", b" ", ctx).decode("ascii", "replace")
                        hits[p].append((off + i, txt.strip()))
                        start = i + 1
                chunk = data[-80:]
                off += len(buf)
    return hits


def main():
    files = []
    for root, dirs, fs in os.walk(DATA):
        if "StreamingAssets" in root:
            continue
        for f in fs:
            p = os.path.join(root, f)
            if os.path.getsize(p) > 1000:
                files.append(p)
    files.sort()
    print("scanning", len(files), "files...")
    hits = scan(files)
    for p, lst in hits.items():
        print("=" * 90)
        print(os.path.relpath(p, GAME), "->", len(lst), "hits")
        seen = set()
        for off, txt in lst[:80]:
            if txt in seen:
                continue
            seen.add(txt)
            print("   @%-12d %s" % (off, txt))
            if len(seen) > 40:
                break


if __name__ == "__main__":
    main()
