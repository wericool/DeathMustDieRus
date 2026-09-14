# -*- coding: utf-8 -*-
"""Parse ContentCatalogData.m_ExtraDataString to extract AssetBundleRequestOptions (CRC, hash, size)."""
import os, json, base64, struct

ROOT = r"E:\Games\DeathMustDieRus"
cat = json.load(open(os.path.join(ROOT, "00_original_bundles", "catalog.json"), encoding="utf-8"))
extra = base64.b64decode(cat["m_ExtraDataString"])
internal = cat["m_InternalIds"]

# Record layout (Addressables 1.21 ContentCatalogData.Write):
#   int32 typeIndex-ish?  -> actually: 3x int32 (assemblyNameIdx? no) ...
# We derive it empirically below.
print("extra bytes:", len(extra))

# known: 8 records. find record starts by locating the assembly-name string start
asm = b"Unity.ResourceManager, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null"
cls = b"UnityEngine.ResourceManagement.ResourceProviders.AssetBundleRequestOptions"
starts = []
i = 0
while True:
    i = extra.find(asm, i + 1 if i > 0 else 0)
    if i < 0:
        break
    if i == 0 or extra[i - 1] in (bytes([len(asm)]),):
        starts.append(i - 4 if i >= 4 else i)
print("record candidates:", starts)

# Simpler: split on the asm string, each record prefix is 4 bytes
parts = extra.split(asm)
print("parts:", len(parts))
for idx, p in enumerate(parts):
    print("--- part", idx, "len", len(p))

# Let's decode part[0] header
print("part0 hex:", parts[0][:16].hex())
