# -*- coding: utf-8 -*-
"""Decode AssetBundleRequestOptions records from catalog m_ExtraDataString."""
import os, json, base64, struct

ROOT = r"E:\Games\DeathMustDieRus"
cat = json.load(open(os.path.join(ROOT, "00_original_bundles", "catalog.json"), encoding="utf-8"))
extra = base64.b64decode(cat["m_ExtraDataString"])
ids = cat["m_InternalIds"]


def rd_varint(buf, off):
    """BinaryWriter.Write(string) uses a 7-bit encoded length prefix."""
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
    s = buf[off:off + n].decode("utf-8", "replace")
    return s, off + n


def main():
    off = 0
    recs = []
    while off < len(extra):
        start = off
        typeidx, off = rd_varint(extra, off)
        asm, off = rd_str(extra, off)
        cls, off = rd_str(extra, off)
        # object body: parse AssetBundleRequestOptions
        b = {}
        b["_typeidx"] = typeidx
        b["_asm"] = asm
        b["_cls"] = cls
        # heuristic: read 4-byte len + string repeatedly until we find m_BundleName pattern
        p = off
        m_Hash, p2 = rd_str(extra, p)
        b["m_Hash"] = m_Hash
        b["m_Crc"] = struct.unpack_from("<I", extra, p2)[0]
        b["m_Timeout"] = struct.unpack_from("<i", extra, p2 + 4)[0]
        b["m_ChunkedTransfer"] = extra[p2 + 8]
        b["m_RedirectLimit"] = struct.unpack_from("<i", extra, p2 + 9)[0]
        b["m_RetryCount"] = struct.unpack_from("<i", extra, p2 + 13)[0]
        m_BundleName, p3 = rd_str(extra, p2 + 17)
        b["m_BundleName"] = m_BundleName
        b["m_AssetLoadMode"] = struct.unpack_from("<i", extra, p3)[0]
        b["m_BundleSize"] = struct.unpack_from("<q", extra, p3 + 4)[0]
        b["m_UseCrcForCachedBundles"] = extra[p3 + 12]
        b["m_UseUWRForLocalBundles"] = extra[p3 + 13]
        b["m_ClearOtherCachedVersionsWhenLoaded"] = extra[p3 + 14]
        end = p3 + 15
        # align to 4
        end = (end + 3) & ~3
        b["_recstart"] = start
        b["_recend"] = end
        recs.append(b)
        off = end
    print(json.dumps(recs, indent=1))
    print()
    for r in recs:
        print("bundle=%-70s crc=%-12d size=%-10d hash=%s useCrcForCached=%s" %
              (r["m_BundleName"], r["m_Crc"], r["m_BundleSize"], r["m_Hash"], r["m_UseCrcForCachedBundles"]))


if __name__ == "__main__":
    main()
