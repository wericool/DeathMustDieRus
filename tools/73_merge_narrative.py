# -*- coding: utf-8 -*-
"""
Merge Nar_* chunk translations -> validate -> produce RU CSVs.
Outputs: 02_translation/narrative/ru/<Nar_X>.csv  + merge_report_narrative.txt
"""
import os, sys, json, re, collections

sys.stdout.reconfigure(encoding="utf-8")
DIR = r"E:\Games\DeathMustDieRus\02_translation\narrative"
CHUNKS = os.path.join(DIR, "chunks")
OUT = os.path.join(DIR, "out")
RU = os.path.join(DIR, "ru")
os.makedirs(RU, exist_ok=True)
FILES = ["Nar_Heroes.csv", "Nar_Self.csv", "Nar_Gods.csv", "Nar_Monsters.csv"]

FEM = r"(?:сделала|победила|выиграла|устала|пришла|видела|слышала|знала|смогла|успела|убила|потеряла|нашла|забыла|стала|родилась|поняла|решила|справилась|погибла|вернулась|хотела|думала|считала|искала|жила|умерла|проиграла|соскучилась|отбила|побывала|тренировалась|влюбилась|поверила)"
MASC = r"(?:сделал\b|победил\b|выиграл\b|устал\b|пришёл|видел\b|слышал\b|знал\b|смог\b|успел\b|убил\b|потерял|нашёл|забыл\b|стал\b|родился|понял\b|решил\b|справился|погиб\b|вернулся|хотел\b|думал\b|считал\b|искал\b|жил\b|умер\b|проиграл\b|соскучился|отбил\b|побывал|тренировался|влюбился|поверил)"
# only FIRST-PERSON self-reference is a gender error; 2nd/3rd person is fine
FEM1 = re.compile(r"\bя\b[^.!?]{0,40}?" + MASC)
MASC1 = re.compile(r"\bя\b[^.!?]{0,40}?" + FEM)
FEM_SELF = re.compile(r"^(?:я\s+)?(?:готова|рада|должна|согласна|уверена|виновата)\b")
MASC_SELF = re.compile(r"^(?:я\s+)?(?:готов\b|рад\b|должен\b|согласен\b|уверен\b|виноват\b)\b")
LAT = re.compile(r"[A-Za-z]{4,}")

FEM_SPEAKERS = {"sor", "ass", "war", "dru", "Justice", "Vengeance", "Vengeance0", "Serenity", "Earth", "Mort", "Mort0", "Aisa", "Lachi", "Clo", "Fates"}
MASC_SPEAKERS = {"kni", "bar", "ran", "Wrath", "Conquest", "Conquest0", "Water", "Time", "sho", "tra", "snow"}
DRAWL = {"sho", "tra", "snow"}

# 1. collect translations
merged = collections.defaultdict(dict)  # file -> {i: ru}
problems = []
for fn in sorted(os.listdir(OUT)):
    if not fn.endswith(".json"):
        continue
    d = json.load(open(os.path.join(OUT, fn), encoding="utf-8"))
    tr = d.get("translations", {})
    base = fn.replace(".json", "")
    file = None
    for f in FILES:
        if base.startswith(f.replace(".csv", "")):
            file = f
            break
    if file is None:
        problems.append(("chunkfile", fn, "no source match"))
        continue
    for k, v in tr.items():
        merged[file][str(k)] = v

# 2. validate
report = []
counts = collections.Counter()
for fn in FILES:
    path = os.path.join(DIR, fn)
    lines = open(path, encoding="utf-8").read().splitlines()
    hdr = lines[0].split(";")
    i_spk = hdr.index("speaker")
    i_en = next(i for i, h in enumerate(hdr) if h.strip().lower().startswith("english"))
    ncol = len(hdr)
    rows = lines[1:]
    last_spk = ""
    todo = 0
    for idx, l in enumerate(rows, start=1):
        parts = l.split(";")
        spk = parts[i_spk] if len(parts) > i_spk else ""
        en = parts[i_en] if len(parts) > i_en else ""
        real = spk if spk not in ("", "~", "ini", "@fade") else ""
        if real:
            last_spk = real
        eff = real or last_spk
        ru = merged[fn].get(str(idx))
        if not en.strip():
            continue
        todo += 1
        where = "%s:%d(%s)" % (fn, idx, eff)
        if ru is None:
            problems.append(("missing", where, en[:80]))
            continue
        if not ru.strip():
            problems.append(("empty", where, en[:80]))
            continue
        if ";" in ru:
            problems.append(("semicolon", where, ru[:80]))
            continue
        low = ru.lower()
        if eff in FEM_SPEAKERS and (FEM1.search(low) or MASC_SELF.match(low)):
            problems.append(("gender-fem-speaker", where, ru[:80]))
        if eff in MASC_SPEAKERS and (MASC1.search(low) or FEM_SELF.match(low)):
            problems.append(("gender-masc-speaker", where, ru[:80]))
        if LAT.search(ru) and not LAT.search(en):
            problems.append(("latin", where, ru[:80]))

n_tr = sum(len(v) for v in merged.values())
print("translations merged: %d" % n_tr)
print("problems: %d" % len(problems))
for p in problems[:80]:
    print("  %-20s %-32s %s" % p)

with open(os.path.join(DIR, "merge_report_narrative.txt"), "w", encoding="utf-8") as f:
    f.write("translations: %d\nproblems: %d\n" % (n_tr, len(problems)))
    for p in problems:
        f.write("%-20s %-32s %s\n" % p)

# 3. write RU CSVs (drop problematic lines -> keep EN there)
bad_keys = {(p[1].split(":")[0], int(p[1].split(":")[1].split("(")[0])) for p in problems if ":" in p[1]}
for fn in FILES:
    path = os.path.join(DIR, fn)
    lines = open(path, encoding="utf-8").read().splitlines()
    hdr = lines[0].split(";")
    i_spk = hdr.index("speaker")
    i_en = next(i for i, h in enumerate(hdr) if h.strip().lower().startswith("english"))
    ncol = len(hdr)
    out_lines = [lines[0]]
    for idx, l in enumerate(lines[1:], start=1):
        parts = l.split(";")
        while len(parts) < ncol:
            parts.append("")
        parts = parts[:ncol]
        en = parts[i_en]
        ru = merged[fn].get(str(idx))
        if en.strip() and ru and (fn, idx) not in bad_keys:
            parts[i_en] = ru.replace("\n", " ").strip()
        out_lines.append(";".join(parts))
    dst = os.path.join(RU, fn)
    open(dst, "w", encoding="utf-8", newline="").write("\n".join(out_lines) + "\n")
    print("wrote", dst)
