# -*- coding: utf-8 -*-
"""
Decisive in-game verification.

Problem: the log only reports glyphs that are MISSING, and plain English text also
renders without warnings — so "no warnings" alone cannot prove the game loaded our
Russian bundle rather than the original English one.

Solution: temporarily inject a probe character that PT Serif cannot possibly have
(U+3004, a CJK ideographic iteration mark) into a string that is guaranteed to be
drawn on the main menu.  If the game loads our bundle, TMP logs a missing-glyph
warning for exactly \u3004 and for nothing else.  Cyrillic producing no warnings
then proves both facts at once:
    * the modified bundle IS the one being loaded, and
    * Cyrillic is rendered correctly (glyphs found or dynamically added).

Usage:
    python tools\\93_probe.py patch    # install the probe into the game
    python tools\\93_probe.py run [s]  # launch, kill, parse the log
    python tools\\93_probe.py clean    # restore the real Russian build
"""
import json, os, re, shutil, subprocess, sys, time
import UnityPy

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = r"E:\Games\DeathMustDieRus"
BUILD = os.path.join(ROOT, "03_build")
GAME = r"D:\Steam\steamapps\common\Death Must Die"
AAWIN = os.path.join(GAME, "Death Must Die_Data", "StreamingAssets", "aa", "StandaloneWindows64")
EN = "localization-string-tables-english(en)_assets_all.bundle"
LOG = os.path.join(os.environ["USERPROFILE"], "AppData", "LocalLow", "Realm Archive",
                   "Death Must Die", "Player.log")
PROBE = "\u3004"
TARGET = "90024878080"          # Loc_AppUI "Play"
COLL = "Loc_AppUI"


def load_tables(path):
    env = UnityPy.load(path)
    out = []
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        t = obj.parse_as_dict()
        if isinstance(t, dict) and isinstance(t.get("m_Name"), str) and t["m_Name"].endswith("_en"):
            out.append((obj, t, t["m_Name"]))
    return env, out


def patch():
    src = os.path.join(BUILD, "StandaloneWindows64", EN)
    dst = os.path.join(AAWIN, EN)
    env, tables = load_tables(src)
    done = 0
    for obj, t, name in tables:
        if not name.startswith(COLL):
            continue
        for e in t["m_TableData"]:
            if str(e["m_Id"]) == TARGET:
                print("  original:", repr(e["m_Localized"]))
                e["m_Localized"] = e["m_Localized"] + PROBE
                print("  probe   :", repr(e["m_Localized"]))
                done += 1
        if done:
            obj.save_typetree(t)
    if not done:
        raise SystemExit("target entry not found")
    data = env.file.save(packer="lz4")
    if isinstance(data, str):
        data = data.encode()
    shutil.copy2(dst, dst + ".rusbak")
    open(dst, "wb").write(data)
    print("probe installed ->", dst)


def clean():
    dst = os.path.join(AAWIN, EN)
    bak = dst + ".rusbak"
    src = os.path.join(BUILD, "StandaloneWindows64", EN)
    if os.path.exists(bak):
        os.remove(bak)
    shutil.copy2(src, dst)
    print("restored real build ->", dst)


def run(seconds=55):
    for p in ("Player.log", "Player-prev.log"):
        fp = os.path.join(os.path.dirname(LOG), p)
        if os.path.exists(fp):
            os.remove(fp)
    print("launching for %ds ..." % seconds)
    proc = subprocess.Popen([os.path.join(GAME, "Death Must Die.exe")], cwd=GAME,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(seconds)
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    if not os.path.exists(LOG):
        print("NO LOG WRITTEN")
        return
    txt = open(LOG, encoding="utf-8", errors="replace").read()
    missing = re.findall(r"Unicode value \\(u[0-9A-Fa-f]{4}) was not found in the \[([^\]]+)\]", txt)
    import collections
    c = collections.Counter(u.upper() for u, f in missing)
    print("missing-glyph warnings:", len(missing))
    for u, n in c.most_common(40):
        print("   U+%-6s x%d" % (u, n))
    print("PROBE U+3004 seen:", "YES -> our bundle is loaded" if "3004" in c else "NO -> bundle NOT loaded!")
    cyr = {u for u in c if "0400" <= u <= "04FF"}
    print("cyrillic missing       :", sorted(cyr) if cyr else "none  <- good")
    for pat in ("Unable to add the requested character", "Exception", "Addressables", "CRC",
                "Failed to load", "hash"):
        n = len(re.findall(pat, txt, re.I))
        if n:
            print("   note: %r x%d" % (pat, n))
    print("--- log tail ---")
    print("\n".join(txt.splitlines()[-10:]))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "patch":
        patch()
    elif cmd == "run":
        run(int(sys.argv[2]) if len(sys.argv) > 2 else 55)
    elif cmd == "clean":
        clean()
