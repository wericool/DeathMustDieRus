# -*- coding: utf-8 -*-
"""Launch the game for N seconds, kill it, then report TMP font warnings."""
import os, subprocess, sys, time, re

GAME = r"D:\Steam\steamapps\common\Death Must Die"
EXE = os.path.join(GAME, "Death Must Die.exe")
LOG = os.path.join(os.environ["USERPROFILE"], "AppData", "LocalLow", "Realm Archive",
                   "Death Must Die", "Player.log")

SECONDS = int(sys.argv[1]) if len(sys.argv) > 1 else 55


def main():
    for p in ("Player.log", "Player-prev.log"):
        fp = os.path.join(os.path.dirname(LOG), p)
        if os.path.exists(fp):
            os.remove(fp)
    print("launching for %ds ..." % SECONDS)
    proc = subprocess.Popen([EXE], cwd=GAME, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(SECONDS)
    # kill the whole tree
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    if not os.path.exists(LOG):
        print("NO LOG WRITTEN")
        return
    txt = open(LOG, encoding="utf-8", errors="replace").read()
    missing = re.findall(r"Unicode value \\(u[0-9A-Fa-f]{4}) was not found in the \[([^\]]+)\]", txt)
    if missing:
        import collections
        c = collections.Counter((f, u) for u, f in missing)
        print("!! MISSING GLYPHS: %d warnings" % len(missing))
        for (f, u), n in c.most_common(30):
            print("   font=%-26s U+%s x%d" % (f, u[1:].upper(), n))
    else:
        print("OK - no missing-glyph warnings at all")
    for pat in ("Unable to add the requested character", "isReadable", "Exception",
                "Please make the texture"):
        n = len(re.findall(pat, txt))
        if n:
            print("   also: %r x%d" % (pat, n))
    print("--- log tail ---")
    print("\n".join(txt.splitlines()[-12:]))


if __name__ == "__main__":
    main()
