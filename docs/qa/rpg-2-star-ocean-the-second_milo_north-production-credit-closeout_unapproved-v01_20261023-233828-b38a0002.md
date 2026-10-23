# Milo north source integration and production credit (UNAPPROVED)

Canonical task `content.char.milo.static-north`, creator autonomous batch 38. Source commit: `70ac7793a7056bbc12a97fcad4fea75b44c6a337`, based on `9c2fc393399db331f15799eea3be5e4e4e9c96b2`. Scope: north 48-logical-pixel native static only. Existing Claude adapter source/repair was independently verified and committed by Hermes. No source or checker thresholds were changed in this batch.

Source QA: `docs/qa/rpg-2-star-ocean-the-second_milo_north-static-closeout_unapproved-v01_20261023-233700-b38a0001.md`. This integration record resolves that report's conditional commit/credit state: all five north package files, editable native sources, author, independent checker, reusable orchestration, failure backup and source-bound QA are now committed. Hermes compared all 73 staged files against exact working bytes before commit, then re-read all 73 committed blobs and verified their recorded SHA-256. No normalization was applied.

After source integration, the existing checked runner was invoked as follows:

`source ../tooling/worlds-between-env.sh && "$WB_PYTHON" tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py --timeout 60 --expect M1_SMOKE_OK --log outputs/milo-n01/logs/hermes38-m1.log -- "$GODOT" --headless --audio-driver Dummy --path game --script res://tests/m1_smoke.gd`

Result: `M1_SMOKE_OK`, `CHECKED_RUN PASS`, exit0; no diagnostics. This targeted combined normal-game smoke does not claim the outstanding full pre-playtest regression or adopt the source into runtime defaults. The separate static fit also passes and remains explicitly test-only.

The audited ledger CLI transferred only north to Hermes and set only north done after source commit. Exact comparison with the batch-start on-disk ledger showed every other task object unchanged. The frozen 1183-task baseline and weights remain intact; content completed points 663 -> 665, total 1881 unchanged. `ledger-cli check` passes.

Canonical meters (recorded by the existing Bible progress CLI):

- Production: 61.1% -> 61.2% (+0.1 percentage points).
- Inspection: 21.6% -> 21.6% (+0.0).
- Creator approval: 7.8% -> 7.8% (+0.0).

The Bible's north progress interval records final coordinator integration, not total provider/art production time; earlier interrupted authorship and repair are retained in source QA. No historical effort duration is inferred. The pre-existing unfinished west record was archived as paused, not completed, before opening north's integration record. The existing uncommitted west ownership audit is preserved as a predecessor in the canonical ledger hash chain; it grants no west score and is not new west production. All unfinished west assets/tools remain uncommitted and unchanged.

Native application diagnostic gate still FAILS: PXO four shader errors, ORA eleven errors and one warning. Exact PNG export equality is independently PASS, not clean application/GUI reliability. The adapter's permission-denied classification and denied commands remain disclosed in source QA; Hermes reran the required checks independently. No art approval, motion, full-set acceptance, default adoption or normal actor integration was awarded.

Next bounded task: resume existing `content.char.milo.static-west`, preserving its unfinished source and frozen criterion. Do not reopen north cosmetic polish or bypass human gates.
