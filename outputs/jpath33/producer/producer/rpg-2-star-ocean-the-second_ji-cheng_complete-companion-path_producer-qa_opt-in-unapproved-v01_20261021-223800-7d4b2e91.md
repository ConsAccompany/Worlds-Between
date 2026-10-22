# Ji Cheng complete companion path — jpath33 producer QA (opt-in, default OFF, UNAPPROVED)

Producer: Claude (primary, bounded). Base `759f2b9ffc1d2e236f5ab15dca3350b20e7943bb`, branch `codex/jpath33`, worktree `work/needle33/cl-jpath`. Nothing is committed or pushed. The shared ledger, Bible, registry and index were not touched.

**State:** I finished the implementation and ran the targeted smoke checks. Ji's default stays **OFF** (`DEFAULT_ADOPTED := false`). Ji's art and motion are **UNAPPROVED**. This is not a human playtest and it does not ask the creator to adopt the default.

## What was built
- `game/scripts/jpath33/…_config_opt-in-v01_20261021-222438-7d4b2e91.gd` is a copy of lpath30 with Ji's member id, `DESTINATION=scifi.ruins` and the exact Ji-only `jcombat32` index. Its `npc_attached` checks `field_npc`, because the ruins scene keeps its recruit NPC there.
- `…_npc-driver_…gd` extends the lpath30 driver and reuses `_prepare_actor`. It has its own Ji cache and points at the frozen `jexplore31` registry and supplemental files. It only sets textures, scale and offset. It never changes position or z.
- `…_entry_…gd` follows the lpath30 separate-profile guard. It requires `WB_JPATH33_PROFILE` to contain `/work/jpath33-preview-profiles/` and requires `user://` to be inside that profile.
- Host changes are registration only, one line each:
  - `scifi_exploration_area.gd`: added `FIELD_NPC_PRESENTERS["ji-cheng"]`.
  - `battle_arena.gd`: appended Ji to `COMPANION_COMBAT_POLICIES`, keeping Zhao and Liang in their existing order.
  - Two comment lines were updated.
  - There are no mechanic, stat, AI, input, save-schema, story or collision changes. `game/data` is unchanged.
- `.gitattributes` now has `-text` rules for jpath33 paths, matching the existing lpath30 rules, so the LF bytes behind the hashes are preserved.

## Evidence
Text hashes are `sha256-text-lf-v1`. All files are LF, so raw and text hashes are equal.

| File | sha256 |
|---|---|
| config | 90826c1c3f25531f0ae5d1eafa8fb40971f584d5b6fc3b6badaa0124d661625e |
| driver | 003ce85b39ba492703bd3b8c29f95c70deac47c29bbe3a5014d27bb0b7ce5ad6 |
| entry | 91f5d770ff84ee2453f1e99ad6cb7dee3d264d9e97d823418d6d67a2ba0df779 |
| battle_arena.gd | c9c01b86589caffe57b63c33c1d8428f2ed7b414e700ceaac046089ed70ff543 |
| scifi_exploration_area.gd | a8e147f11e1487e8ddec57bc068ca10b96451636e99f7187b6362ec50e3e3f70 |
| flow `tools/…ji-playable-path_real-input-flow…gd` | 3fbdb0ae4b40ed4af9c8c1a4f3f1cbf991a016751d3af22f2323c93a49ef420c |
| runner `.py` | 9c991befcf947b86341a6273c64664fb5ac537a2d6fc111d747150949017fb60 |
| boundary `tools/…ji-playable-path_boundary-check…gd` | 76876f9d469e9a89a536d148bac0e1bb1c0b224bde7a0ae2782a0a910c7ef248 |
| jcombat32 index (unchanged) | 9677d8e3… |
| jexplore31 registry (unchanged) | e5b8fbef… |
| jexplore31 supplement (unchanged) | 80f177bf… |

### Real-input runs
All runs went through the reused checked runner: `tools/…godot_checked-runner_v01…py`, with a deadline and diagnostic stop. Each run used its own APPDATA profile under `work/jpath33-profiles/`.

| Run (`outputs/jpath33/…`) | Lang / fps | Scenario | Result |
|---|---|---|---|
| `rif-20261021-223005-3787b10c` | EN / 60 | victory | 60/60 PASS, 16 captures at 640×360 |
| `rif-20261021-223029-3aa9988e` | ZH / 30, `--write-movie` | victory | 60/60 PASS, 16 captures |
| `rif-20261021-223029-563d15a0` | EN / 60 | defeat-boundary | 49/49 PASS, 14 captures |
| `rif-20261021-223029-ace6c124` | EN / 60 | ordinary-default (Ji OFF) | 7/7 PASS: static Ji NPC, no driver |

- **ZH movie:** `work/jpath33-profiles/20261021-223029-3aa9988e/rpg-2-star-ocean-the-second_ji-playable-path_actual-input-normal-30fps_20261021-223029-3aa9988e.avi`, 35,936,300 bytes. It was recorded at the original speed and not encoded; MP4 encoding is left to root. The folder is ignored by git.
- **Route:** fresh `scifi.ruins` run, then:
  1. WASD to Ji, then E. The dialogue opens with **Invite disabled**, because `ji_records_checked` is false. A Later click closes it.
  2. WASD to the records console at 320,250, then E sets `ji_records_checked` through the real handler.
  3. WASD back to Ji, then E, then a click on Invite. Ji is recruited, the NPC is hidden, there is no follower, and the game writes its own autosave.
  4. Walk into the sentry, which opens the normal battle with one pre-battle autosave.
  5. A moves the hero aside, then Tab switches control to Ji.
  6. Q (skill), L (guard), K (dodge), R (job-skill attempt), then D/J until a natural victory.
  7. Click the result button, return to the ruins, then reload the after-battle autosave.
- **Ji actions seen in victory runs:** idle, move, skill, guard, dodge, attack.
- **Defeat-boundary run:** after the real recruitment, a DECLARED save checkpoint puts hero and Ji at 1 HP / 0 energy. The defeat is caused by the engine. The run returns to the main menu, the pre-battle autosave loads for a retry, and Ji is still recruited.
- **Fixtures (declared):** `configure()` starts a fresh preview run at `scifi.ruins` with no forced recruit and no records bypass. Reload uses `AppState.load_save` on the autosave the game wrote, not the Save/Load UI.

### Boundary check
`outputs/jpath33/producer/…boundary-check-log…223207-24451815.log`: **39/39 PASS**.
- **Defaults:** Ji is OFF; Zhao and Liang are still on.
- **Default-off behaviour:** the ruins NPC gets no driver, and a battle loads only the Zhao and Liang models.
- **Refusals:** `configure()` refuses each of these and leaves state exactly as it was (full snapshot compared):
  - bad locale or bad appearance
  - missing registry, or a registry with no Ji entry
  - missing or malformed supplement
  - an index that lists only Liang, an index that lists two members, or a missing index
- **Successful configure:** fresh ruins run, records still unchecked, solo party, no host override set.
- **Enabled battle:** separate Zhao, Liang and Ji models, with Ji bound to exactly slot 3.
- **Member pairs:** each pair (member, that member's own index) loads that member only. The pair (Ji, Liang's index) loads nothing. The generic override suppresses every companion.
- **Rollback:** restores the Ji knob, and Zhao and Liang stay on.

The first boundary run, `…223157-585d32ef.log`, **FAILED** on two GDScript type-inference parse errors. The checked runner caught them. I fixed them, kept that log, and re-ran.

### Entry guard
- Run without a dedicated profile: prints `JPATH33_PLAYABLE_REFUSED … ordinary saves are protected`, exit 1.
- Run with `fr`: refused, exit 1.
- Run with a dedicated profile under `work/jpath33-preview-profiles/`: prints `JPATH33_PLAYABLE_READY language=zh`. The preview then keeps running until it is closed. My 60 s shell timeout killed it, and the kill produced engine teardown messages (`BUG: Unreferenced static string`, RID leaks). Those messages come from the kill, not from a script error. There was no separate receipt for this probe.

## Limitations (stated honestly)
- **Job skill (R) depends on timing.** It fired in the ZH 30 fps run (energy spent) but not in the EN 60 fps run (energy unchanged at level 1). The run records this as information, not as a pass condition. I did not investigate further because that would mean probing mechanics.
- **First EN run's runner hash differs.** That run used the runner before a cosmetic rename of its summary print (`LIANG_RIF_RUN`→`JI_RIF_RUN`), so its receipt carries the older runner hash. The flow harness hash, 3fbdb0ae…, is the same in all four runs.
- **Headless boundary run:** it ends with a warning that 12 ObjectDB instances were leaked at exit.
- **Import cleanup:** a fresh-worktree `--import` was needed. Afterwards I restored the 1305/447 `.import` files that changed only in line endings, and removed the untracked `.uid`/`.import` sidecars it generated, so a later run will import again. I kept the jpath33 `.gd.uid` files.
- **Not done:** the job/growth screen route and a root combined canonical-path recheck are not in this producer batch. That recheck is root's job.

## Default adoption (prepared, NOT applied)
`outputs/jpath33/producer/…default-adoption_prepared-patch-not-applied…patch` is a one-line change, `DEFAULT_ADOPTED := false` → `true`. It passes `git apply --check`. It needs separate creator authorization before anyone applies it.
