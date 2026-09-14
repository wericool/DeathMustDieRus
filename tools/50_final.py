# -*- coding: utf-8 -*-
"""
Assemble the final Russian table used by the builder.

  in : 02_translation/ru_normalized.json      (register-normalised merge)
       02_translation/affix_batches/out_affix_*.json  (genitive affix nouns)
  out: 02_translation/ru_build.json
       02_translation/build_report.txt

Also validates every entry against the English source: [[n]] markers, rich-text
tags, newline counts and leading/trailing spaces must survive, and no entry may
be left untranslated.
"""
import json, os, re, sys, collections

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"E:\Games\DeathMustDieRus"
T = os.path.join(ROOT, "02_translation")

SRC = os.path.join(T, "ru_normalized.json")
AFFIX_DIR = os.path.join(T, "affix_batches")
DST = os.path.join(T, "ru_build.json")
REPORT = os.path.join(T, "build_report.txt")

MARKER = re.compile(r"\[\[\d+\]\]")
SMART = re.compile(r"\{[^{}]*\}")
TAG = re.compile(r"<[^>]+>")

# English sources that are broken placeholders in the game data itself and are
# deliberately left untranslated (verified: 2997x "eoline", empty colour tags, emoticons)
JUNK = re.compile(r"^(eoline|<color=#999999>\s*</color>|<3|:\(\)?)$")

# item names are assembled as "<subtype> <prefix>" / "<subtype> <prefix> и <suffix>",
# so the affix tables must hold genitive noun phrases (see tools/42..47).
NOVA_FIX = {
    "морозной новы": "морозного взрыва",
    "ядовитой новы": "ядовитого взрыва",
    "огненной новы": "огненного взрыва",
}

# small grammar repairs found by the final proof-read
TEXT_FIX = [
    ("с здоровьем", "со здоровьем"),
]


def restore_slots(en: str, ru: str) -> str:
    """Turn the [[n]] markers of the translation back into the game's own tokens.

    tools/14_units.py replaced every non-nested smart-string token {...} of the
    English source with an indexed [[n]] marker; here we put the original token
    text back, using the marker index as the identity of the token.
    """
    slots = SMART.findall(en)
    if "[[" not in ru:
        return ru

    def repl(m):
        n = int(m.group(1))
        return slots[n] if 0 <= n < len(slots) else m.group(0)

    return re.sub(r"\[\[(\d+)\]\]", repl, ru)


def main():
    ru = json.load(open(SRC, encoding="utf-8"))
    strings = json.load(open(os.path.join(T, "strings_en.json"), encoding="utf-8"))

    # ---- 1. affixes -> genitive noun phrases (overrides the batch translation)
    affix = {}
    for fn in sorted(os.listdir(AFFIX_DIR)):
        if not (fn.startswith("out_affix_") and fn.endswith(".json")):
            continue
        d = json.load(open(os.path.join(AFFIX_DIR, fn), encoding="utf-8"))
        affix.update(d["translations"])
    print("affix keys:", len(affix))

    n_pref = n_suff = 0
    for key, v in affix.items():
        g = NOVA_FIX.get(v["genitive"], v["genitive"])
        for coll, idkey in (("Loc_ItemPrefixes", "prefix_id"), ("Loc_ItemSuffixes", "suffix_id")):
            i = str(v[idkey])
            if i in ru.get(coll, {}):
                ru[coll][i] = g
                if coll == "Loc_ItemPrefixes":
                    n_pref += 1
                else:
                    n_suff += 1
    print("patched prefixes: %d, suffixes: %d" % (n_pref, n_suff))

    # ---- 2. text repairs
    fixes = 0
    for coll, m in ru.items():
        for i, s in list(m.items()):
            if not isinstance(s, str):
                continue
            ns = s
            for a, b in TEXT_FIX:
                ns = ns.replace(a, b)
            if ns != s:
                m[i] = ns
                fixes += 1
    print("text repairs:", fixes)

    # ---- 3. markers back to the game's own tokens + validation
    problems = collections.defaultdict(list)
    stats = collections.Counter()
    for coll, meta in strings.items():
        table = ru.get(coll, {})
        for row in meta["entries"]:
            i = str(row["id"])
            en = row.get("en") or ""
            ru_s = table.get(i)
            stats["entries"] += 1
            if not en.strip():
                stats["empty_source"] += 1
                continue
            if not ru_s:
                if JUNK.match(en.strip()) or not re.search(r"[A-Za-z\u0400-\u04FF]", en):
                    stats["junk_source"] += 1
                else:
                    problems["missing"].append((coll, i, en))
                continue
            restored = restore_slots(en, ru_s)
            table[i] = restored
            stats["translated"] += 1
            if sorted(SMART.findall(en)) != sorted(SMART.findall(restored)) or "[[" in restored:
                problems["markers"].append((coll, i, en, restored))
            if sorted(TAG.findall(en)) != sorted(TAG.findall(restored)):
                problems["tags"].append((coll, i, en, restored))
            if en.count("\n") != restored.count("\n"):
                problems["newlines"].append((coll, i, en, restored))
            if en[:1].isspace() != restored[:1].isspace() or en[-1:].isspace() != restored[-1:].isspace():
                problems["edge-space"].append((coll, i, en, restored))
            if re.search(r"[A-Za-z]{4,}", restored) and not re.search(r"[A-Za-z]{4,}", en):
                problems["latin"].append((coll, i, en, restored))

    json.dump(ru, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=0)

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("entries: %d, translated: %d, empty source: %d\n" % (
            stats["entries"], stats["translated"], stats["empty_source"]))
        f.write("problem counts: %s\n\n" % {k: len(v) for k, v in problems.items()})
        for kind, rows in problems.items():
            f.write("=== %s (%d) ===\n" % (kind, len(rows)))
            for r in rows[:60]:
                f.write("   %s\n" % (r,))
    print("stats:", dict(stats))
    print("problems:", {k: len(v) for k, v in problems.items()})
    print("wrote", DST, "and", REPORT)


if __name__ == "__main__":
    main()
