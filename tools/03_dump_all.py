# -*- coding: utf-8 -*-
"""Dump full structure of every localization bundle into JSON for analysis."""
import os, json, collections
import UnityPy

ROOT = r"E:\Games\DeathMustDieRus"
BUNDLES = os.path.join(ROOT, "00_original_bundles")
OUT = os.path.join(ROOT, "01_extracted")
os.makedirs(OUT, exist_ok=True)


def conv(v, depth=0):
    if depth > 6:
        return "<deep>"
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, (list, tuple)):
        return [conv(x, depth + 1) for x in v]
    if hasattr(v, "__dict__"):
        d = {}
        for k, val in v.__dict__.items():
            if k in ("object_reader", "assets_file", "assetsfile"):
                continue
            d[k] = conv(val, depth + 1)
        return d
    return repr(v)


def dump_bundle(fn):
    path = os.path.join(BUNDLES, fn)
    env = UnityPy.load(path)
    out = {"bundle_file": fn, "size": os.path.getsize(path), "objects": []}
    for obj in env.objects:
        rec = {"type": obj.type.name, "path_id": obj.path_id}
        if obj.type.name in ("MonoBehaviour", "TextAsset", "AssetBundle"):
            data = obj.read()
            rec["data"] = conv(data)
        if obj.type.name == "MonoBehaviour":
            st = obj.serialized_type
            rec["script_id"] = st.script_id.hex() if st and st.script_id else None
        out["objects"].append(rec)
    return out


def main():
    summary = {}
    for fn in sorted(os.listdir(BUNDLES)):
        if not fn.endswith(".bundle"):
            continue
        print("dumping", fn)
        d = dump_bundle(fn)
        name = fn.replace(".bundle", "") + ".json"
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        summary[fn] = collections.Counter(o["type"] for o in d["objects"])
    print(json.dumps({k: dict(v) for k, v in summary.items()}, indent=1))


if __name__ == "__main__":
    main()
