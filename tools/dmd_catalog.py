# -*- coding: utf-8 -*-
"""Helpers for reading/writing the Addressables catalog.json of Death Must Die."""
import json, base64, struct


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
        body = extra[off:off + n].decode("utf-16-le")
        off += n
        recs.append({"typeidx": typeidx, "asm": asm, "cls": cls,
                     "json": json.loads(body), "start": start, "end": off})
    return recs


def build_extra(recs):
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


def load_catalog(path):
    cat = json.load(open(path, encoding="utf-8"))
    extra = base64.b64decode(cat["m_ExtraDataString"])
    return cat, extra, parse_extra(extra)


def save_catalog(cat, recs, path):
    cat["m_ExtraDataString"] = base64.b64encode(build_extra(recs)).decode("ascii")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cat, f, ensure_ascii=False)


def set_no_crc(recs, bundle_names):
    """Disable CRC verification for the given AssetBundle internal names."""
    changed = []
    for r in recs:
        j = r["json"]
        if j.get("m_BundleName") in bundle_names:
            j["m_Crc"] = 0
            j["m_UseCrcForCachedBundles"] = False
            changed.append(j["m_BundleName"])
    return changed
