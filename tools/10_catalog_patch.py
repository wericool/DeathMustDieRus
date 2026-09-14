# -*- coding: utf-8 -*-
"""Parse & patch Addressables catalog: read AssetBundleRequestOptions JSON per bundle."""
import os, json, base64, struct, re

ROOT = r"E:\Games\DeathMustDieRus"
CAT = os.path.join(ROOT, "00_original_bundles", "catalog.json")


def rd_varint(buf, off):
    result = 0
    shift = 0
    while True:
        b = buf[off]
        off += 1
        result |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            break
        shift += 7
    return result, off


def rd_str(buf, off):
    n, off = rd_varint(buf, off)
    return buf[off:off + n].decode("utf-8", "replace"), off + n


def parse_extra(extra):
    off = 0
    recs = []
    while off < len(extra):
        start = off
        typeidx, off = rd_varint(extra, off)
        asm, off = rd_str(extra, off)
        cls, off = rd_str(extra, off)
        n = struct.unpack_from("<i", extra, off)[0]
        off += 4
        # JSON body is UTF-16LE, preceded by a 4-byte length (in bytes)
        body = extra[off:off + n].decode("utf-16-le")
        off += n
        obj = json.loads(body)
        recs.append({"typeidx": typeidx, "asm": asm, "cls": cls, "json": obj,
                     "start": start, "end": off, "len": n})
    return recs


def build_extra(recs):
    """Re-serialize records back to the binary blob format."""
    out = bytearray()

    def wr_varint(v):
        while True:
            b = v & 0x7F
            v >>= 7
            if v:
                out.append(b | 0x80)
            else:
                out.append(b)
                break

    def wr_str(s):
        b = s.encode("utf-8")
        wr_varint(len(b))
        out.extend(b)

    for r in recs:
        wr_varint(r["typeidx"])
        wr_str(r["asm"])
        wr_str(r["cls"])
        body = json.dumps(r["json"], separators=(",", ":")).encode("utf-16-le")
        out.extend(struct.pack("<i", len(body)))
        out.extend(body)
    return bytes(out)


def load():
    cat = json.load(open(CAT, encoding="utf-8"))
    extra = base64.b64decode(cat["m_ExtraDataString"])
    return cat, extra


def main():
    cat, extra = load()
    recs = parse_extra(extra)
    print("records:", len(recs))
    for r in recs:
        j = r["json"]
        print("%-70s crc=%-12s size=%-10s uwr=%s cachedcrc=%s hash=%s" % (
            j.get("m_BundleName"), j.get("m_Crc"), j.get("m_BundleSize"),
            j.get("m_UseUWRForLocalBundles"), j.get("m_UseCrcForCachedBundles"), j.get("m_Hash")))
    # verify re-serialization is lossless
    rt = build_extra(recs)
    print("roundtrip identical:", rt == extra, len(rt), len(extra))
    if rt != extra:
        for i in range(min(len(rt), len(extra))):
            if rt[i] != extra[i]:
                print("first diff at", i, extra[i - 20:i + 20].hex(), "|", rt[i - 20:i + 20].hex())
                break
    print()
    print("field keys of one record:", list(recs[0]["json"].keys()))


if __name__ == "__main__":
    main()
