# Death Must Die — Russian localisation: translator guide

You are translating the video game **Death Must Die** (roguelite hack-and-slash, dark-fantasy
mythology setting: the player descends into the Underworld to kill Death, helped by a pantheon
of gods) from **English to Russian**.

## Your task

1. Read your assigned batch file, e.g. `E:\Games\DeathMustDieRus\02_translation\batches\batch_007.json`.
   It looks like:
   ```json
   {
     "batch": 7,
     "collections": ["Loc_BoonNames"],
     "units": [
       {"uid": 1234, "src": "You gain [[0]] Revivals."},
       {"uid": 1235, "src": "<color=#c24538>Strike</color> Damage"}
     ]
   }
   ```
2. Translate **every** `src` into Russian.
3. Write the result to `E:\Games\DeathMustDieRus\02_translation\out\out_007.json` (same number as
   the batch), in exactly this shape:
   ```json
   {"batch": 7, "translations": {"1234": "Вы получаете [[0]] возрождений.", "1235": "<color=#c24538>Урон удара</color>"}}
   ```
   Keys are the `uid` values **as strings**. Every uid from the input must be present exactly once.

## Absolute rules (a violation breaks the game)

1. **Keep every `[[n]]` marker.** Each marker is a runtime value slot (a number, a percentage…).
   - The same markers must appear in the output, each exactly once: `[[0]]`, `[[1]]`, `[[2]]` …
   - You **may and should move them** inside the sentence so the Russian reads naturally.
   - Never translate, delete, duplicate, renumber or reformat a marker. Never write `[[ 0 ]]`.
2. **Keep every rich-text tag byte-for-byte**: `<color=#797ca0>`, `</color>`, `<b>`, `</b>`,
   `<i>`, `<sprite=0>`, `<size=...>`. Translate only the text *inside* them.
   Keep the same opening/closing pairing as the source.
3. **Keep escape sequences** exactly: `\n` (line break) stays `\n`.
4. **Keep leading and trailing spaces.** If the source has a trailing space, the translation must
   have one too (this affects layout).
5. Never output an empty string for a non-empty source.
6. Never add commentary, notes, alternatives, quotes or parentheses of your own. Output only JSON.

## Style

- Player-facing address: informal **«ты»** ("Ты получаешь…", "Твоя атака…").
- Stat/tooltip text: neutral, terse, no trailing period unless the source has one.
- Sentence case, not Title Case: «Урон атаки», not «Урон Атаки».
- Prefer short, idiomatic gamer Russian over literal translation.
- Russian needs more characters than English: stay compact, but never sacrifice clarity.
  Do not exceed roughly 1.4× the source length in UI labels (batch collections named
  `Loc_AppUI`, `Loc_GeneralUI`, `Loc_Controls`, `Loc_Results`, `Loc_Tooltip*`).
- Numbers, `%`, `DPS`, `HP`, roman numerals, and the `[bracketed]` choice labels stay as-is.
  However, the English unit `s` for seconds becomes `с` («{0}s Attack Time» → «{0} с — время атаки»).
- Do **not** translate Latin-script proper names of gods/heroes — see GLOSSARY for the accepted
  Russian spellings.
- Keep the register of the game: dark, mythological, a little wry.

## Terminology

Read `E:\Games\DeathMustDieRus\02_translation\GLOSSARY.md` **before translating** and use its
translations verbatim, including inside longer sentences. It is the single source of truth so that
all 62 batches stay consistent. If a term you need is missing, derive it from the closest glossary
entry using the same logic, and keep it consistent within your batch.

## Reference — already-fixed UI strings

These are the most visible strings in the game; use them exactly:

| English | Russian |
|---|---|
| Play | Играть |
| Options | Настройки |
| Quit | Выход |
| Controls | Управление |
| Display | Экран |
| Audio | Звук |
| Gameplay | Геймплей |
| Accessibility | Доступность |
| Language | Язык |
| Text | Текст |
| End Run | Завершить забег |
| Patch Notes | Список изменений |
| Wishlist | В желаемое |
| Reset | Сбросить |
| Cancel | Отмена |
| Unequip | Снять |
| Clear | Очистить |
| Results | Итоги |
| Resume | Продолжить |

## Self-check before you finish

- [ ] The output file exists and is valid JSON (UTF-8, no BOM issues).
- [ ] `len(translations) == len(units)` and the uid sets are identical.
- [ ] For every unit, the multiset of `[[n]]` markers is identical to the source.
- [ ] For every unit, `<color=...>`/`</color>`/`<b>`/`</b>` counts match the source.
- [ ] `\n` counts match the source.
- [ ] No English sentences left untranslated (short Latin terms like `DPS` are fine).
- [ ] Report back in one short line: `batch N: ok, M/M units`.

Use a small Python script to run the checks — do not eyeball 200 entries.
