# -*- coding: utf-8 -*-
"""Launch the game for N seconds, kill it, and archive Player.log under a label.

    python tools/94_abtest.py <label> [seconds]
"""
import os, re, subprocess, sys, time, shutil, collections

sys.stdout.reconfigure(encoding="utf-8")
GAME = r"D:\Steam\steamapps\common\Death Must Die"
LOGDIR = os.path.join(os.environ["USERPROFILE"], "AppData", "LocalLow", "Realm Archive", "Death Must Die")
LOG = os.path.join(LOGDIR, "Player.log")
OUT = r"E:\Games\DeathMustDieRus\09_test"

label = sys.argv[1]
seconds = int(sys.argv[2]) if len(sys.argv) > 2 else 60

for p in ("Player.log", "Player-prev.log"):
    fp = os.path.join(LOGDIR, p)
    if os.path.exists(fp):
        os.remove(fp)

print("launching %s for %ds ..." % (label, seconds))
proc = subprocess.Popen([os.path.join(GAME, "Death Must Die.exe")], cwd=GAME,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(seconds)
subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)

os.makedirs(OUT, exist_ok=True)
dst = os.path.join(OUT, "log_%s.txt" % label)
if os.path.exists(LOG):
    shutil.copy2(LOG, dst)
    txt = open(dst, encoding="utf-8", errors="replace").read()
else:
    txt = ""
    print("NO LOG")

print("archived ->", dst)
tables = re.findall(r"LoadTableOperation`2, Selected Locale: ([^,]+), Table: TableReference\(([^)]+)\)", txt)
dep = len(re.findall(r"Dependency Exception", txt))
inv = len(re.findall(r"Invalid path in AssetBundleProvider", txt))
glyph = re.findall(r"Unicode value \\(u[0-9A-Fa-f]{4}) was not found in the \[([^\]]+)\]", txt)
print("dependency-exceptions :", dep)
print("invalid-path errors   :", inv)
print("failed table loads    :", len(tables))
print("   tables:", sorted({t for _, t in tables}))
print("missing-glyph warnings:", len(glyph))
c = collections.Counter(u.upper() for u, f in glyph)
for u, n in c.most_common(20):
    print("   U+%-6s x%d" % (u, n))
print("probe U+3004:", "SEEN" if "3004" in c else "not seen")
print("--- tail ---")
print("\n".join(txt.splitlines()[-6:]))
