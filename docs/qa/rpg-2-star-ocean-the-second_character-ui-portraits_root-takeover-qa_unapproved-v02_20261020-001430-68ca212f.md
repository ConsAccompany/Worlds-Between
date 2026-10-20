# Character UI portraits — bounded Codex takeover, producer-tree technical candidate

Scope: one optional UI portrait kit and its growth/dialogue hooks. Work was performed only in `work/dual03/ds-ui-portraits`; canonical game checkout, ledger, Bible, Site, Git index, providers and accounts were not changed. DeepSeek was stopped by its bounded deadline, not credit/quota. Global stop was absent before mutations. Creator art/canon/full-sprite approval and production credit remain separate.

## Concrete repairs

- DeepSeek had already corrected actual exploration host typing from Control to Node before takeover. The final code retains this fix.
- Nested manifest dictionaries/string/boolean/integer fields now fail cleanly before typed assignments/conversions. Added malformed roi/display_rect/PNG/hash/transform/fractional-size tests.
- Dialogue fit uses the intended344×186 text rectangle; checking live Label.size was unsound because long text can expand its minimum height. Overflow refuses the portrait layout and restores original UI layout/full strings/callbacks. For extremely long artificial text, fallback is compared with the original UI given the same text; this is not a promise that arbitrary text fits the original UI.
- Party icon revert restores original icon texture, expansion and alignment as well as geometry/filter/clip settings.
- Root rejected eye-only28px crops after actual native inspection. Whole-head square ROIs now explicitly downsample existing display pixels to28×28 using integer nearest centers `floor((2*x+1)*source_size/56)`; hairline/face/chin are represented. The32px bronze/teal frame stays separate runtime decoration. No repaint, synthesis, new identity, original portrait alteration or dialogue-layout alteration. Original eye-only package and failed evidence remain preserved.

## Verified results

- Final **604/604 actual normal runtime checks**, unfiltered checked runner, fresh unique APPDATA/LOCALAPPDATA, Dummy audio, native640 and representative1280 viewports; clean7.922s. Two real audio mix boundaries observed after detach/free.
- Actual normal growth EN/ZH, male/female hero plus Liang/Zhao/Ji identity mapping, exact frame pixels, real mouse selection and map→growth→Back route, legacy flag priority, recruit/assist callbacks, trace/system/unknown hiding,72viewport-bounds checks, original callback/full-text preservation and clean overflow rejection.
- Default-off growth/dialogue native captures equal original e600241 baseline pixels exactly; labels preserved. Baseline fixture source hashes are pinned in runtime report. This producer-tree check is not yet proof of the parent's newer canonical combined source.
- **111 independent package checks /3,920RGBA pixels:** source crops equal committed canonical bytes, independent vectorized nearest sampling, exact PNG hashes, one-layer ORA XML/PNG/composite equality, five source manifests unchanged, truthful AI/unapproved provenance, same-runtime deterministic rebuild of21files and checksums. No GUI SaveAs/native-editor reliability or cross-runtime compressed-byte equality claim.
- Root personally viewed final native male/female whole-head party captures and accepted the technical crop/layout correction only. The supporting Codex inspector viewed the native EN/ZH dialogue captures. Creator art/canon approval remains false.

## Failures preserved and excluded from clean claims

- The original producer's certificate-filtering launcher removed actual engine ERROR lines before the checked runner. It is disallowed and excluded from shipping. None of the takeover passes used it.49historical producer logs (including filtered attempts explicitly marked invalid as clean evidence) are retained with original hashes and renamed history copies.
- First unfiltered takeover run:527/529, only overflow refusal/restoration failed, no engine diagnostics. It exposed the Label minimum-size issue. Full report/raw log remain.
- Initial whole-head Pillow NEAREST output differed at sample ties from the independent exact integer-center rule. Initial failing oracle traceback retained. Builder now explicitly implements the integer rule; no pixel tolerance or test threshold was weakened.
- Intermediate530/530 repaired eye-only run and602/602 first whole-head run remain historical, distinct from final604/604. The final suite and captures bind to final helper/package bytes.

## Integration handoff

Final selection/proof: outputs/ui-root-v02/rpg-2-star-ocean-the-second_character-ui-portraits_final-source-proof_v02_20261020-001359-5381489c.json

The proof lists31selected source/package/fixture/tool paths separately from68root evidence artifacts and49historical diagnostic copies. Do not ship certificate-filter shim, filtered pass claims, smoke scripts, generated imports/uids or the eye-onlyv01 assets. The new whole-head builder reads the specifically hash-pinned archived original kit JSON only for existing source/provenance; include that single frozen JSON. Its runtime package is `game/assets/portraits/ui-kit-v02`.

Producer host raw SHA256:
- growth_screen.gd: b31fbadeb9921fb9ae1eb6c0c68aa22f9a3522ebf9e5a597d567369fdd11d8d1
- scifi_exploration_area.gd: 87e1c999342c81ba569da282824978c19e4adea0f0c5e0b9a7a29a45060f493a
- helper: a7060bf7f2d8b00273d661179b554adbd64a39d7641b0f4faefb56f4aae0ac0e

These are PRODUCER-tree hashes, not canonical combined hashes. Parent must patch only the portrait hooks into current canonical hosts, preserving newer female-exploration/UI/audio code, rerun the actual suite unfiltered there, bind resulting combined bytes and verify staged Git blobs. Parent owns integration/ledger decisions.
