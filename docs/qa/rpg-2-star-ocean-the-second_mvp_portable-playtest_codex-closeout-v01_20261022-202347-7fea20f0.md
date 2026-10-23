# Current-default portable developer playtest bundle

Task `current-portable-developer-playtest-bundle`; base/game source `d5f204373c17c62e45e92dea14c3a2e85c525062`. This rebuild delivers the current creator-authorized MVP defaults together in a runnable Windows bundle. It does not create another content/version scoring bucket.

## Delivered

- ZIP contains the unchanged installed Godot 4.7.2 GUI/console runtime pair, current exported game PCK, double-click normal/diagnostic launchers, source/hash manifest, engine MIT and embedded third-party notices, and a reviewed Chinese/English quickstart.
- No editor/project installation is needed to launch. This is explicitly a **developer runtime + PCK bundle**, not a native release EXE export. Windows export templates are not installed; no templates, engines or paid services were purchased/downloaded for this task.
- Game source comes from a clean archive of the pinned commit, never uncommitted primary/canonical game edits. All 3001 protected canonical tracked game files excluding import files remain raw-byte identical to the pre-task snapshot.
- The approximately251MB ZIP and binaries are LOCAL under ignored `work/p54-c1425087/`. They are not committed to GitHub; tools, guide, manifests, reports, logs and actual captures are published. The local verifier receipt identifies the exact ZIP/launcher location and digest. Do not present these local paths as a public download.

## Direct verification

[Final build report](../../outputs/play54/producer/rpg-2-star-ocean-the-second_play54_build-report_v01_20261022-203718-2fd4b10c.json) and [independent extracted-bundle receipt](../../outputs/play54/root/20261022-203846-c1425087/rpg-2-star-ocean-the-second_mvp_portable-verification_v01_20261022-203846-c1425087.json).

1. Clean imported archive, current preset and existing raw-input export hook: export and diagnostic gates pass. Pinned4917 archived game files are hash-listed.447 existing `.import` rewrites are proven exact CRLF/LF-only conversions against pinned Git blobs and archive hashes; importer options/content are unchanged. Git archive itself honors Windows text EOL attributes; archive raw hashes are not falsely called raw Git blob hashes.1101 newly generated `.import`/`.uid` metadata files are listed with raw hashes. No other generated/modified source files are allowed. A separate negative test changes an importer type and proves refusal; it touches only a disposable task fixture.
2. Installed runtime hashes match the two shipped binaries exactly. Embedded engine license/copyright APIs produce nonempty notices with a success marker. All files except the manifest itself are size/hash-bound in that manifest; the independent verifier also compares the extracted manifest to the build manifest.
3. Producer smoke passes direct console+PCK from an empty working directory and both real launchers from a copied directory with spaces. No art/pilot flags, scene overrides or source-project path are passed. Normal launcher preserves normal user-data behavior; TEST processes use isolated profiles.
4. Codex copies the final ZIP to a separate short directory, verifies ZIP digest/CRC, extracts every listed file and checks every size/hash. Normal launcher boots again from an empty working directory. An external bounded probe runs only the bundled console runtime and PCK, without a source project; packed project metadata exists.
5. **94/94 checks**,20 separate actual native640x360 captures: EN/ZH menu, NYC, Yonkers, Washington exterior, Washington records room2, Chicago, sentry battle, patrol battle, growth and save. All four ordinary common-style scene defaults load. Zhao/Ji field drivers and hero/three-companion combat sets plus both enemy animation textures are present. No diagnostics are filtered; exit0 alone is not accepted.
6. Codex visually inspected14 captures: both languages of NYC/Washington exterior/records/Chicago, plus ZH Yonkers and sentry, EN patrol/menu/save/growth. Current scene plates, labels, actors and enemy textures render in those frames. This is a resource/entry check, not artistic acceptance or an animation-fluidity judgment.

All probes use explicit scene/party setup fixtures. Recruitment is injected for combat rendering; this is **not** an end-to-end campaign/recruitment/battle-return/save-write/load test. The save screen renders, but this task does not claim a new persisted save roundtrip. Audio uses Dummy for windowed tests; no new listening assessment. Human post-art timed plays remain0/2; final approval remainsfalse.

## Failures and corrections retained

Claude produced the builder/license tool and ran bounded export attempts; its480-second task deadline interrupted the unfinished third attempt. No quota exhaustion or credit error was reported. DeepSeek produced the short bilingual draft; Codex checked controls and edited the final guide, tightened source validation, fixed Windows path handling, completed builds and independently checked the extracted PCK.

Early producer checks rejected447 sidecar byte changes and then1101 generated sidecars. Their logs/reports remain. Root's first stricter guard also rejected archive-CRLF versus Git-blob-LF bytes; the corrected guard recognizes only those exact forms and still rejects importer content changes. Later assembly failed on legacy Windows long paths; extended file I/O corrected copying, and a short contained workspace corrected `.cmd` launch. The first packed probe incorrectly expected Godot's consumed `--main-pack` option in exposed process arguments; it failed immediately and is retained. The corrected probe requires packed project metadata, while the independent runner binds the actual command and PCK digest. Final build/packed runs pass; earlier failures are not relabeled as passes.

## Ji Cheng gate disposition

The previously queued `qa.char.ji-cheng.runtime-set-check` is not credited. Its criterion requires every frame/anchor/direction/slip check to pass. Existing source evidence explicitly discloses in-place front/back moving-source foot slip; this task does not retest or claim to fix it. The ordinary field role is a stationary recruit NPC, not a persistent follower or controlled exploration hero. MVP default use was separately authorized; moving-source refinement is deferred. See [existing source closeout](rpg-2-star-ocean-the-second_ji-cheng_exploration-source_codex-closeout_unapproved-v01_20261021-212415-382d3721.md). Keep the all-pass task blocked pending the required future evidence rather than repeatedly re-auditing or weakening it.

## Progress and next boundary

Production **60.3% ->60.3%(+0.0pp)**; inspection **21.6% ->21.6%(+0.0pp)**; creator approval **7.8% ->7.8%(+0.0pp)**. Coding111/111,content635/1881,inspection44/204,creator19/244; frozen1183 tasks unchanged. Rebuilding already-produced content into a current runnable delivery earns no duplicate production or final-regression points. All six legacy category meters are recomputed separately, with no acceptance claim.

Next useful boundary: a bounded automated science-route journey against this packaged build, using normal menu/interaction paths through recruitment, report, save/quit/reload and real battle return. Keep it separate from final-art-dependent M9 and the two creator playthroughs. Defer cosmetic character/scene iterations.
