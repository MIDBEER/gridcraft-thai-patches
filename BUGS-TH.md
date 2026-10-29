# Thai-language bugs in GridCraft 0.12.1 — findings and leads

Tested on **GridCraft 0.12.1 (Windows 11, portable build)** on 2026-10-28, upstream source at
`11bb673` (2026-10-27). Reproductions are in `tests/workbooks/`; screenshots were taken with
`tools/shot_gridcraft.ps1`. "Verified" means seen in the real app; "lead" means read in source only.

| # | Bug | Upstream issue | Status here |
|---|-----|----------------|-------------|
| 1 | Digits / Latin float above Thai (and CJK) text in the same cell | [#502](https://github.com/storytold/gridcraft/issues/502), #1265, #2621 | Verified. Patch drafted (**not built, not run**) |
| 2 | PDF export and printing drop every Thai glyph | #1416 | Verified. Not started |
| 3 | Ten Thai worksheet functions return `#NAME?` | #2810 | Verified. Not started |
| 4 | Thai/Buddhist-calendar number formats ignored | none found (search not exhaustive) | Verified. Not started |
| 5 | Thai collation: leading vowels (เ แ โ ใ ไ) sort after all consonants | #1235 (PR #1241 open) | Verified. Upstream PR exists |
| 6 | Wrap Text breaks Thai words in the middle | none found | Verified. Lead below |
| 7 | Cell fonts (TH Sarabun New, Angsana, Cordia…) may not be applied | related PR #1573 | **Unconfirmed** — see below |

## 1. Digits float above Thai text

**Symptom.** In a cell such as `ห้อง 101 ชั้น 2 จำนวน 35 คน`, the digits and Latin letters are drawn
smaller and higher than the Thai. Same for every font name and size tried (9–16 pt; Tahoma, Leelawadee UI,
TH Sarabun New, Angsana New, Cordia New, Courier New), though see #7 on whether those names were applied at all.
File data is fine; display only. Screenshot: [`docs/images/before-floating-digits.png`](docs/images/before-floating-digits.png).

**Root cause (from source).** GridCraft puts the Thai glyphs in a *fallback* face (`sys-thai`, Leelawadee UI
on Windows, loaded in `crates/ui-egui/src/theme/font_fallback.rs`). The pinned egui fork
(`storytold/egui` `6d518fc`) places a fallback face's glyphs by `FontTweak::fallback_align`, whose
default is `Center`: it centres the fallback's row box in the first face's row box. Leelawadee UI has a
different ascent/descent from the cell face, so Thai lands lower than the digits, which sit on the first
face's baseline. The same enum has `Baseline`, documented as the right choice for "fonts for scripts the
first font lacks, such as Thai or Arabic" (`crates/epaint/src/text/font_tweak.rs`; layout in
`text_layout.rs` ~l.1473). `grep fallback_align` over GridCraft returns nothing: it is never set.

**Patch** `patches/0001-script-fallback-faces-sit-on-the-baseline.patch` (+39/−2): sets
`set_baseline_fallback(true)` on every script fallback face and every embedded craft face except the
symbol faces (`sys-symbols*`, `Zsym`), plus a unit test. It applies cleanly to `11bb673`.

> **Not verified.** There was no Rust toolchain on the machine, so the patch has not been compiled, the
> new test has not run, and nobody has looked at a build with the patch. Row height will also grow slightly
> for Thai text (that is what `Baseline` does). Please build and look before merging.
> The workflows in `.github/workflows/` exist to do exactly that on GitHub's runners; they have not run yet either.

## 2. PDF export / print drops Thai

`crates/pdf/src/lib.rs` writes only the 14 standard PDF fonts (not embedded, WinAnsi) plus a non-embedded
Adobe-GB1 CID fallback for CJK. Thai has no path at all. A test export of a Thai+digits sheet kept the digits
and Latin and dropped all Thai. **Lead:** embed a subset of a Thai-capable TrueType face as a Type0 /
CIDFontType2 font with a `ToUnicode` map (WordCraft's sibling PDF writer uses Krilla).

## 3. Missing Thai functions

Only `BAHTTEXT` is implemented (`crates/functions/src/text.rs`; output checked: correct). These return `#NAME?`:
`THAIYEAR`, `THAIDIGIT`, `ISTHAIDIGIT`, `THAIMONTHOFYEAR`, `THAIDAYOFWEEK`, `THAISTRINGLENGTH`,
`THAINUMSTRING`, `THAINUMSOUND`, `ROUNDBAHTUP`, `ROUNDBAHTDOWN` (plus the Chinese `NUMBERSTRING`). Their names
exist only in the `.xls` import table (`crates/xlsx/src/xls/ftab.rs`). **Good first issue:** pure functions
with unit tests; check each against Excel with a Thai locale.

## 4. Thai / Buddhist-calendar formats

No Excel was available, so the "Excel" values here and in #5 come from knowledge of its Thai-locale behaviour,
not from a side-by-side run. For 2026-10-28, `[$-107041E]d mmmm yyyy` gives `28 October 2026` (Excel Thai: `28 ตุลาคม 2569`),
`[$-D07041E]…` ignores Thai digits, `[$-th-TH]d/m/yyyy` stays Gregorian, and `bbbb` is printed literally.
`TEXT()` behaves the same. Likely in `crates/numfmt`.

## 5. Thai collation

`"เก" < "ขา"` evaluates `FALSE` (code-point order puts เ U+0E40 after every consonant). Thai collation ignores
the leading vowel at the first level, so it should be `TRUE`. Affects `SORT`, comparisons and the Sort dialog.

## 6. Wrap Text breaks mid-word

With the sample text in `tests/workbooks/make_thaitest_wrap.py` (Tahoma 12, wrap on, no spaces in the text),
`ช่วงเช้า` wraps as `ช่|วงเช้า`: the line is cut between the consonant and its tone-marked vowel cluster, in the
middle of a word. (Re-checked 2026-10-29 in GridCraft 0.12.1 with the current sample text.) The fork's default `SimpleLineBreaker` documents that it
"does not know where Thai, Lao, Khmer or Burmese words end, so text in those scripts wraps between grapheme
clusters" (`crates/epaint/src/text/line_break.rs`). The fork has a `LineBreaker` trait and
`Context::set_line_breaker`; GridCraft never installs one. **Lead:** install a breaker backed by a Thai word
dictionary (the trait's own example uses `craft_text::segment`; ICU4X's segmenter is another option).

## 7. Cell fonts possibly ignored (unconfirmed)

In automated screenshots, cells set to Calibri, Tahoma, Leelawadee UI, TH Sarabun New, Angsana New and Cordia New
rendered identically, which would mean the named fonts were not used. This could be a test artefact: the font
rebind in `crates/ui-egui/src/app/fonts.rs` runs on a frame after the background font scan finishes, and an
idle window may never get that frame. Check by hand with a real mouse before reporting.
