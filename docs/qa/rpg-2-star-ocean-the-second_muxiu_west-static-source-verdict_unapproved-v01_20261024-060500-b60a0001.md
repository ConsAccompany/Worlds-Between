# Muxiu west static — independently verified source, UNAPPROVED

Canonical task: `content.char.muxiu.static-west`. Claude produced the source through the authorized durable adapter; Hermes independently checked it and coordinates integration. Base: `f556e74e`. Recorded 2026-10-24 UTC. SHA-256 means raw bytes, no text normalization. Source completion requires this package and QA note to be committed; no provider exit or review is creator approval.

## Deliverable and source contract

New original west-facing static, not the old 32x48 placeholder: 80x112 canvas, opaque rows8..103, pivot40,104, display scale0.5, 48 logical pixels. PNG plus editable layered PXO and ORA, palette and manifest. Thirteen visible functional layers, hidden guides, 33 used colours, binary alpha and clear borders. Reuses the pinned Muxiu south palette, Lin/Jiang/male native serializers and frozen gates; redraws the west profile. Existing south dependency is done and unchanged. Identity reference is Bible character-06 and the existing UNAPPROVED portrait: moss-green short cloak, brown hair/braid, cream shirt, whistle, rope bracelet. Sea of Stars is direction approval only.

Final author: `tools/rpg-2-star-ocean-the-second_muxiu_west-static-author_unapproved-v01r2_20261024-055724-17c9961a.py`. Final checker: `tools/rpg-2-star-ocean-the-second_muxiu_west-static-source-check_v01_20261024-055724-17c9961a.py`. The checker does not import a Muxiu author; it reuses only the established ORA compositor. No animations, other direction, runtime default, UI adoption, human playtest or art acceptance is delivered.

## Independent checks on installed revision r2

Commands run from repo with `../tooling/venv/bin/python`, UTF-8:

1. Final author `-X utf8 -I <author> check`: rc0, `MUXIU_WEST_V01R2_ALL_OK`, deterministic in-memory rebuild and five installed files match. Hard failures empty. Full coordinator log retained in `outputs/muxiu-w01/hermes60-source-r2/author-check.log`.
2. `-X utf8 -I <checker> --root . --out outputs/muxiu-w01/hermes60-source-r2`: rc0,50/50, failures empty. Native PXO/ORA composition and hashes, source size/pivot/height, palette,13 genuine layers, anchor contributions, west-facing profile and negative controls pass. Mirrored west, south, mirrored south and squashed south are rejected; corrupt hashes, altered pixels and visible guides are detected. West versus Lin west silhouette difference473 texels exceeds the unchanged400 threshold; final isolated texels16 satisfies unchanged24 limit. Placeholder search returns no Muxiu matches; this absence is disclosed rather than treated as visual quality evidence.
3. Existing v03 orchestration `pixelorama hermes60-pxl-r2`, then `compare hermes60-compare-r2 hermes60-pxl-r2`: both native processes rc0, source hashes unchanged, both native exports80x112 and exactly equal authored RGBA. Native PNG encoding differs, so equality is pixel equality, not PNG file equality. Full export/application logs retained.
4. Same orchestration `fit hermes60-fit-r2`: existing generic static source-fit script, Xvfb, Dummy audio, checked runner110s deadline. Inner rc0, `JIANG37_SOURCE_FIT_PASS captures=4`, checked runner PASS, no script/parser/runtime diagnostic markers. Four separate640x360 logical captures: EN/ZH city and ruins. These are deterministic test-only overlays, not normal actor adoption or low-light/night proof.
5. Checked Godot runner `--timeout 60 --expect M1_SMOKE_OK --log outputs/muxiu-w01/hermes60-source-r2/m1-smoke.runner.log -- ../tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64 --headless --audio-driver Dummy --path game --script res://tests/m1_smoke.gd`: rc0, M1_SMOKE_OK, checked PASS. Protected baseline5185 tracked game/relevant south-source files independently hash-exact after implementation.

Proof: `outputs/muxiu-w01/hermes60-source-r2/rpg-2-star-ocean-the-second_muxiu_west-independent-source-proof_v01_20261024-055724-17c9961a.json`.

## Visual observation, not approval

Hermes loaded the final enlarged r2 static and actual ZH ruins fit capture through native image input. A left-facing profile, green capelet with cream motifs, dark front-hanging braid, tan whistle and near wrist bracelet are visible enlarged. The stance is stiff and narrow, boots overlap in profile and the braid reads as a dark straight strip rather than clearly separated plait segments. At actual48px scale the silhouette and facing can be seen, but small identity details are not independently legible and moss clothing blends with vegetation. Fit sprite is at screen(400,280), separately labeled test only; the nearby playable heroine is not Muxiu. The earlier city capture inspection was revision r1 and is not substituted for final r2. No visual-review or human gate is closed.

## Retained failures and permission gates

- Draft1 preview failed with30 isolated texels above unchanged24. Draft author, content-named preview and failed log remain. Draft never installed source. An initial diagnostic helper lacked NumPy under system Python; its failed version and replacement version remain.
- Revision r1 built, then independent source check failed49/50: Lin west silhouette difference380 below unchanged400. Coordinator independently reproduced that failure in `outputs/muxiu-w01/hermes60-source/`. Source was repaired, not the threshold. All r1 author/checker/logs/previews remain. Earlier native/fit evidence is r1 only.
- Revision r2 stages fresh under `outputs/muxiu-w01/stage-r2`. Four changed installed files were replaced only using authorized `python3 tools/wb_safe_replace.py SOURCE DESTINATION`; all four original backups and before/after hashes were independently verified. Palette bytes did not change. Backup receipts/paths are in the checkpoint below. No lost original bitmap is claimed.
- Genuine provider Bash gates denied compound discovery, backup creation, shell redirected scratch author and a filtered check command. Exact commands and actual error responses are preserved in the checkpoint and hashed raw local provider transcript. They are technical tool gates, not missing overwrite consent. No permission bypass or settings edit was used. Original authors were retained rather than edited after denied backup creation; fresh author revision was written to a different path.
- Provider job `3efb2367b73641b1b5cabc2772cd5047` finished rc1, classification `max_turns`, scope confirmed; it did not supply a normal success closeout or QA note. Hermes independently verifies the installed source boundary. Exact stdout/stderr paths and hashes are recorded below. No second provider was launched.
- Pixelorama application-clean FAIL: four shader diagnostics per format; ORA also reports child-index/control errors and ObjectDB/resource/RID shutdown leaks. Exact native export passes separately. GUI save/reopen reliability is unverified for this package. This does not close application diagnostics or artistic acceptance.
- Two coordinator metadata extractors failed before writing (`AttributeError: str object has no attribute get`); robust message-shape filtering corrected the export. No source bytes changed.

Checkpoint: `outputs/muxiu-w01/rpg-2-star-ocean-the-second_muxiu_west-independent-checkpoint_unapproved-v01_20261024-060500-b60a0001.json`, SHA-256 `1e6b12e904479c03538761c1d50d467e9ee2bd2aa554c7d59a96e63dfed9631e`.

## Installed source raw hashes

Under `game/assets/characters/muxiu-native-v01/west/`:

- static PNG ending `74e5c117.png`: `0eb36b3bfed70b1ffcf0a20401e7948e683e317d4ca3db6fa6a4f06e6d2d8ec0`
- editable PXO ending `7b8925b9.pxo`: `8fb88fe3ea8430cc7d4971731579106324cc5cb9aa7ab159ceb9ec4d4265f4ca`
- editable ORA ending `73a0748b.ora`: `4eb224d6e2b1fedd66045d1c06ffb435d16a2f1d532d7bf83ff86635f24b35e9`
- palette ending `adb333d7.json`: `dd8ff4213df8f14a73842a6142ef82c3a8eb799388b360777b5a561f1ecbd6fc`
- manifest ending `a2f2ac0f.json`: `c92fb90c2f6a54b778856329f1c60b6db269070244e38c897bee5f7a13dc4772`

## Closure boundary

Production before61.7%, inspection21.6%, creator approval7.8%; final values are recorded by canonical CLI after verified source commit. Only the existing west production task can close; no new points/baseline/inspection/approval changes. Overall operational verdict remains partial because provider hit its turn limit and native application cleanliness still fails, even if committed source satisfies the production criterion. Defaults, all pauses and unrelated dirty work are unchanged. Next: preserve this source boundary and failed checks, then only the next explicitly assigned unpaused task; do not automatically start another direction or resume Milo west.
