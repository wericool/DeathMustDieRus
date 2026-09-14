# -*- coding: utf-8 -*-
"""Neutralise gendered player-address strings in ru_build.json (v2 fixes)."""
import json, sys

sys.stdout.reconfigure(encoding="utf-8")
P = r"E:\Games\DeathMustDieRus\02_translation\ru_build.json"
ru = json.load(open(P, encoding="utf-8"))

FIX = {
 ("Loc_DoodadMessages", "1"):   "<color=#999999>Дар принят!</color>",
 ("Loc_DoodadMessages", "2"):   "<color=#999999>Проклятие!</color>",
 ("Loc_DoodadMessages", "8"):   "<color=#999999>Твоя добродетель признана.</color>",
 ("Loc_DoodadMessages", "18"):  "<color=#999999>Теперь за твои деяния на тебе проклятие!</color>",
 ("Loc_DoodadMessages", "52"):  "Нужно поторопиться!",
 ("Loc_DoodadMessages", "65"):  "Проклинаю тебя за неблагодарность!",
 ("Loc_DoodadMessages", "130"): "Тогда ищи подсказки самостоятельно!",
 ("Loc_DoodadMessages", "136"): "Что ж, похоже, ты и в одиночку справишься.",
}

n = 0
for (coll, i), v in FIX.items():
    old = ru.get(coll, {}).get(i)
    if old is None:
        print("!! missing", coll, i)
        continue
    ru[coll][i] = v
    n += 1
    print("patched %-22s %-4s\n   was: %s\n   now: %s" % (coll, i, old[:90], v[:90]))

# Loc_EncounterDescriptions id=30: 'изрядно проголодался' -> neutral
c = "Loc_EncounterDescriptions"
s = ru[c]["30"]
ru[c]["30"] = s.replace("Внизу небось уже изрядно проголодался", "Внизу небось уже вовсю хочется есть")
s = ru[c]["101"]
ru[c]["101"] = s.replace("Я знаю, зачем ты забрёл так далеко", "Я знаю, что привело тебя так далеко")

json.dump(ru, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("fixed:", n + 2)
