# -*- coding: utf-8 -*-
"""Decode the Addressables catalog blobs to see whether bundle CRC is stored."""
import os, json, base64, struct, re

ROOT = r"E:\Games\DeathMustDieRus"
cat = json.load(open(os.path.join(ROOT, "00_original_bundles", "catalog.json"), encoding="utf-8"))

print("m_LocatorId:", cat["m_LocatorId"])
print("m_BuildResultHash:", cat["m_BuildResultHash"])
print("providerIds:", cat["m_ProviderIds"])
print("resourceTypes:", cat["m_resourceTypes"])
print("instanceProviderData:", cat["m_InstanceProviderData"])
print("sceneProviderData:", cat["m_SceneProviderData"])
print("resourceProviderData:", cat["m_ResourceProviderData"])
print("InternalIdPrefixes:", cat.get("m_InternalIdPrefixes"))
print("n InternalIds:", len(cat["m_InternalIds"]))

for key in ("m_KeyDataString", "m_BucketDataString", "m_EntryDataString", "m_ExtraDataString"):
    raw = base64.b64decode(cat[key])
    print("=" * 80)
    print(key, "decoded bytes:", len(raw))
    ascii_runs = re.findall(rb"[\x20-\x7e]{6,}", raw)
    print("  ascii runs (first 25):")
    for s in ascii_runs[:25]:
        print("     ", s.decode("ascii", "replace"))
    print("  head hex:", raw[:64].hex())

# look for AssetBundleRequestOptions-ish content
extra = base64.b64decode(cat["m_ExtraDataString"])
for m in re.finditer(rb"m_Crc|AssetBundleRequestOptions|Crc", extra):
    print("FOUND", m.group(), "at", m.start())
