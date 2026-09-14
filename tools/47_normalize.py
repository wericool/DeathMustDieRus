# -*- coding: utf-8 -*-
"""
Normalise the second-person register of the merged translation.

The 62 batches were translated by different agents and the register came out
split: 1131 entries address the player informally («ты») and 744 formally («вы»).
The Russian target register for this game is the informal one, so every formal
form is converted here with an explicit, exhaustive word table (no blind regex
on verb endings, which would destroy plural imperatives such as «Нажмите»).

Entries listed in ALLOWLIST legitimately use the plural «вы» (a letter written by
a pompous in-game lawyer, NPCs talking to each other, the player addressing a
group of NPCs) and are left untouched.
"""
import json, os, re, sys, collections

sys.stdout.reconfigure(encoding="utf-8")
ROOT = r"E:\Games\DeathMustDieRus"
T = os.path.join(ROOT, "02_translation")

SRC = os.path.join(T, "ru_final.json")
DST = os.path.join(T, "ru_normalized.json")
DIFF = os.path.join(T, "register_diff.txt")

ALLOWLIST = {
    ("Loc_EncounterChoices", "297"),        # player shouting at a group of NPCs
    ("Loc_EncounterDescriptions", "133"),   # pompous in-game letter, polite on purpose
    ("Loc_ItemUniquesFlavorText", "112"),   # NPCs addressing each other
    ("Loc_ItemUniquesFlavorText", "118"),
}

# 2nd person plural -> 2nd person singular (present/future + plural imperatives)
VERBS = {
    # --- present / future
    "получаете": "получаешь", "теряете": "теряешь", "можете": "можешь",
    "лечите": "лечишь", "преодолеваете": "преодолеваешь",
    "собираете": "собираешь", "убиваете": "убиваешь", "уклоняетесь": "уклоняешься",
    "становитесь": "становишься", "попадаете": "попадаешь", "совершаете": "совершаешь",
    "атакуете": "атакуешь", "повышаете": "повышаешь", "превращаете": "превращаешь",
    "превращаетесь": "превращаешься", "подбираете": "подбираешь",
    "восстанавливаете": "восстанавливаешь", "входите": "входишь",
    "проходите": "проходишь", "перемещаетесь": "перемещаешься",
    "используете": "используешь", "лечитесь": "лечишься",
    "посетите": "посетишь", "восстановите": "восстановишь",
    "нанесёте": "нанесёшь", "переживёте": "переживёшь", "выпьете": "выпьешь",
    "разрушаете": "разрушаешь", "снимаете": "снимаешь", "будете": "будешь",
    "управляете": "управляешь", "оставляете": "оставляешь", "убьёте": "убьёшь",
    "активируете": "активируешь", "накладываете": "накладываешь",
    "умрёте": "умрёшь", "выходите": "выходишь", "возродитесь": "возродишься",
    "требуете": "требуешь", "хотите": "хочешь", "знаете": "знаешь",
    "видите": "видишь", "едите": "ешь",
    # --- plural imperatives
    "получите": "получи", "выберите": "выбери", "отвергните": "отвергни",
    "воззовите": "воззови", "призовите": "призови", "вылечите": "вылечи",
    "найдите": "найди", "проявите": "прояви", "подайте": "подай", "дайте": "дай",
    "взлетите": "взлети", "загляните": "загляни", "сожгите": "сожги",
    "помните": "помни", "прочитайте": "прочитай", "сразитесь": "сразись",
    "впитайте": "впитай", "слушайте": "слушай", "попробуйте": "попробуй",
    "отпустите": "отпусти", "делайте": "делай", "уйдите": "уйди",
    "высвободите": "высвободи", "выпустите": "выпусти", "посмотрите": "посмотри",
    "снимайте": "снимай", "убивайте": "убивай", "раскройте": "раскрой",
    "помогите": "помоги", "садитесь": "садись", "перевернитесь": "перевернись",
    "откройте": "открой", "попросите": "попроси", "разбудите": "разбуди",
    "вглядитесь": "вглядись", "держитесь": "держись", "выпейте": "выпей",
    "уничтожьте": "уничтожь", "обращайте": "обращай", "пожертвуйте": "пожертвуй",
    "давайте": "давай", "спрашивайте": "спрашивай", "здравствуйте": "здравствуй",
}

# words that are future tense only when they directly follow "вы/Вы";
# elsewhere they are plural imperatives
FUTURE_IF_AFTER_VY = {"восстановите": "восстановишь", "наносите": "наносишь"}
IMPERATIVE = {"восстановите": "восстанови", "наносите": "наноси"}

PRONOUNS = {
    "вы": "ты", "вас": "тебя", "вам": "тебе", "вами": "тобой",
    "ваш": "твой", "ваша": "твоя", "ваше": "твоё", "ваши": "твои",
    "вашего": "твоего", "вашей": "твоей", "ваших": "твоих",
    "вашему": "твоему", "вашим": "твоим", "вашими": "твоими", "вашем": "твоём",
}

# predicate adjectives that agreed with the plural pronoun
PREDICATE = [
    ("становишься неуязвимы", "становишься неуязвим"),
    ("ты невидимы", "ты невидим"),
    ("ты должны", "ты должен"),
    ("ты обязаны", "ты обязан"),
    ("ты готовы", "ты готов"),
    ("ты мертвы", "ты мёртв"),
    ("ты живы", "ты жив"),
    ("ты способны", "ты способен"),
    ("ты вынуждены", "ты вынужден"),
    ("ты довольны", "ты доволен"),
]

WORD = re.compile(r"[А-Яа-яЁё-]+")
SENT_END = ".!?…\n\"'«»)]"


def cap_like(src, dst):
    if src[:1].isupper():
        return dst[:1].upper() + dst[1:]
    return dst


def is_sentence_start(text, pos):
    i = pos - 1
    while i >= 0 and text[i] in " \t":
        i -= 1
    return i < 0 or text[i] in SENT_END


def prev_token(text, pos):
    i = pos - 1
    while i >= 0 and text[i] in " \t":
        i -= 1
    j = i
    while j >= 0 and (text[j].isalpha() or text[j] == "-"):
        j -= 1
    return text[j + 1:i + 1].lower()


def fix_entry(text):
    def verb_sub(m):
        w = m.group(0)
        low = w.lower()
        if low in FUTURE_IF_AFTER_VY:
            if prev_token(text, m.start()) in ("вы", "вас", "вам"):
                return cap_like(w, FUTURE_IF_AFTER_VY[low])
            return cap_like(w, IMPERATIVE[low])
        if low in VERBS:
            return cap_like(w, VERBS[low])
        return w
    text = WORD.sub(verb_sub, text)

    out, last = [], 0
    for m in WORD.finditer(text):
        w = m.group(0)
        low = w.lower()
        if low in PRONOUNS:
            rep = PRONOUNS[low]
            if w[:1].isupper() and is_sentence_start(text, m.start()):
                rep = rep[:1].upper() + rep[1:]
            out.append(text[last:m.start()])
            out.append(rep)
            last = m.end()
    out.append(text[last:])
    text = "".join(out)

    for a, b in PREDICATE:
        text = text.replace(a, b)
    return text


def main():
    ru = json.load(open(SRC, encoding="utf-8"))
    dst = {}
    diffs = []
    changed = 0
    for coll, m in ru.items():
        nm = {}
        for i, s in m.items():
            if isinstance(s, str) and (coll, i) not in ALLOWLIST:
                ns = fix_entry(s)
                if ns != s:
                    changed += 1
                    diffs.append((coll, i, s, ns))
                nm[i] = ns
            else:
                nm[i] = s
        dst[coll] = nm
    json.dump(dst, open(DST, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    with open(DIFF, "w", encoding="utf-8") as f:
        f.write("register normalisation: %d entries changed\n\n" % changed)
        for coll, i, a, b in diffs:
            f.write("=== %s/%s\n  - %s\n  + %s\n" % (coll, i, a.replace("\n", "\\n"), b.replace("\n", "\\n")))
    print("entries changed:", changed)
    print("wrote", DST, "and", DIFF)


if __name__ == "__main__":
    main()
