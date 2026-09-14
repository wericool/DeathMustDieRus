# -*- coding: utf-8 -*-
"""
Merge per-batch translations into the final per-entry Russian table.

  in : 02_translation/out/out_*.json      (uid -> russian)
       02_translation/units_real.json     (uid -> skeleton)
       02_translation/unit_index.json     (coll -> id -> uid)
       02_translation/strings_en.json     (source ids per collection)
       02_translation/overrides.json      (optional, {coll: {id: ru}} — wins over everything)
  out: 02_translation/ru_units.json        (uid -> ru)
       02_translation/ru_final.json        (coll -> {id: ru})  — complete, ready to inject
       02_translation/merge_report.txt
"""
import json, os, re, sys, collections

ROOT = r"E:\Games\DeathMustDieRus"
TR = os.path.join(ROOT, "02_translation")

MARK = re.compile(r"\[\[(\d+)\]\]")
TAG_OPEN = re.compile(r"<([a-zA-Z][^>]*)>")


def marker_multiset(s):
    return collections.Counter(int(m) for m in MARK.findall(s))


def tag_multiset(s):
    return collections.Counter(TAG_OPEN.findall(s))


def main():
    units = {u["uid"]: u for u in json.load(open(os.path.join(TR, "units_real.json"), encoding="utf-8"))}
    index = json.load(open(os.path.join(TR, "unit_index.json"), encoding="utf-8"))
    src = json.load(open(os.path.join(TR, "strings_en.json"), encoding="utf-8"))

    ru_units = {}
    files = sorted(f for f in os.listdir(os.path.join(TR, "out")) if f.startswith("out_") and f.endswith(".json"))
    bad_files = []
    for fn in files:
        p = os.path.join(TR, "out", fn)
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            bad_files.append((fn, "JSON error: %s" % e))
            continue
        tr = d.get("translations") or d
        for k, v in tr.items():
            try:
                uid = int(k)
            except ValueError:
                continue
            if isinstance(v, str) and v.strip():
                ru_units[uid] = v

    print("loaded %d translation files, %d unit translations" % (len(files), len(ru_units)))
    for fn, err in bad_files:
        print("  BAD FILE:", fn, err)

    problems = collections.Counter()
    missing = []
    details = []
    for uid, u in units.items():
        ru = ru_units.get(uid)
        if not ru:
            missing.append(uid)
            continue
        if marker_multiset(u["skeleton"]) != marker_multiset(ru):
            problems["marker mismatch"] += 1
            details.append(("marker", uid, u["skeleton"], ru))
        if tag_multiset(u["skeleton"]) != tag_multiset(ru):
            problems["tag mismatch"] += 1
            details.append(("tag", uid, u["skeleton"], ru))
        if u["skeleton"].count("\n") != ru.count("\n"):
            problems["newline mismatch"] += 1
            details.append(("newline", uid, u["skeleton"], ru))
        if u["skeleton"][:1].isspace() != ru[:1].isspace() or u["skeleton"][-1:].isspace() != ru[-1:].isspace():
            problems["edge-space mismatch"] += 1
            details.append(("space", uid, u["skeleton"], ru))
        if not re.search(r"[А-Яа-яЁё]", ru) and re.search(r"[A-Za-z]{3,}", u["skeleton"]):
            problems["no cyrillic"] += 1
            details.append(("nocyr", uid, u["skeleton"], ru))

    # build per-entry final table
    overrides = {}
    op = os.path.join(TR, "overrides.json")
    if os.path.exists(op):
        overrides = json.load(open(op, encoding="utf-8"))
        print("overrides loaded for %d collections" % len(overrides))

    ru_final = {}
    untranslated = []
    for coll, ids in index.items():
        ru_final[coll] = {}
        for sid, uid in ids.items():
            v = ru_units.get(uid)
            if v is None:
                untranslated.append((coll, sid, uid))
                v = ""
            ru_final[coll][sid] = v
        for sid, v in overrides.get(coll, {}).items():
            if sid in ru_final[coll]:
                ru_final[coll][sid] = v
            else:
                ru_final[coll][sid] = v

    json.dump(ru_units, open(os.path.join(TR, "ru_units.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(ru_final, open(os.path.join(TR, "ru_final.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    lines = []
    lines.append("translation files: %d, unit translations: %d / %d" % (len(files), len(ru_units), len(units)))
    lines.append("missing units: %d" % len(missing))
    lines.append("problem counts: %s" % dict(problems))
    lines.append("")
    lines.append("=== units with structural problems ===")
    for kind, uid, s, r in details:
        lines.append("[%s] uid=%d\n   EN: %r\n   RU: %r" % (kind, uid, s, r))
    lines.append("")
    lines.append("=== missing units (no translation) ===")
    for uid in missing:
        lines.append("uid=%d  %r  colls=%s" % (uid, units[uid]["skeleton"], units[uid]["colls"]))
    lines.append("")
    lines.append("=== entries without translation: %d ===" % len(untranslated))
    for coll, sid, uid in untranslated[:200]:
        lines.append("  %s id=%s uid=%s" % (coll, sid, uid))

    open(os.path.join(TR, "merge_report.txt"), "w", encoding="utf-8").write("\n".join(lines))
    print("missing units:", len(missing))
    print("problems:", dict(problems))
    print("entries without translation:", len(untranslated))
    print("report -> 02_translation/merge_report.txt")


if __name__ == "__main__":
    main()
