# Complete heroine path: front/back source and normal win/loss integration

## Scope and owners

Creator priority: one complete playable heroine before roster batches. Claude authored front/back limb articulation; DeepSeek extended the existing read-only source checker and copied negative fixtures; Codex independently inspected, pinned the runtime package and checked the combined actual game flow. No new orchestration platform or per-version scoring.

## Delivered

The existing Chinese one-click playable launcher now uses hsea-front17 through the existing config and distance driver. Four-direction exploration/start/stop/repress/reversal, normal encounter with all29 combat poses loaded, natural attack victory/rewards/return/after-battle reload, and natural defeat/menu/pre-battle retry are usable in the same game. The check command shares asset preparation with play; no manual package setup is required. Saves use isolated profiles; normal game defaults and real user saves are unchanged.

Source package outputs/hsea-front17/src-v01-20261021-022403: 52 idle/walk PNGs,16 legacy bridge PNGs,192 phase-stop PNGs, two13-frame front/back native PXOs and four48-frame phase PXOs. All4 idles,24 side walk,96 side phase and8 side legacy PNG bytes are protected. Allowed24 front/back walks and8 legacy samples changed; source rebuild matches all268 files exactly. Independent parser confirms26 front pose and192 phase compositions. The native editor export is pixel-exact but emitted shader ERROR diagnostics; clean GUI SaveAs/reopen is NOT established.

Runtime changes are confined to a new exact package profile, coordinator-owned allowed phase directions and the existing opt-in playable config. Old two-direction profiles remain strict. Model/speed140/cadence/inclusive120ms/physical movement are unchanged. No generic scene, AI, damage, rewards, collisions or save rules were changed.

## Root evidence

- outputs/hsea-front17-root/*independent-source-check*: original producer directory checked read-only; all structural gates passed. Source/transition source hash bound, all28 protected pose,96 side phase and8 legacy bytes intact. Root repeated author reconstruction after copying to canonical checkout:268/268 byte-identical.
- outputs/hsea-front17-root/*checker-fixtures*: root rerun9 copied cases passes; protected idle/side walk/side phase, missing front phase, corrupted native export, bad hash, traversal and malformed JSON all refuse without traceback or input mutation. Synthetic marker-pixel fixtures are NOT art or gameplay evidence.
- outputs/hsea-front17-root/*four-direction-phase-boundaries*:880 predicates for all48 outgoing phases and sample boundaries; old side-only package449 predicates remains passing. Existing two-profile acceptance/refusal runner passes both prior profiles plus restored byte tampering and wrong revision refusal.
- outputs/heroine-path16/*combined-root-proof*v16_20261021-022802-beb07777.json: real windowed EN104/ZH104 checks, 250-frame1280x720/30fps normal1x movies. Both97-entry normal-input/encounter/combat traces exactly equal the prior stop15 flow (source presentation changes only).
- outputs/heroine-path16/*combined-root-proof*v16_20261021-022848-39d62eab.json: natural defeat and retry EN90/ZH90 checks. Normal enemy attacks cause HP0; authored hit and final defeat frame observed; no XP/JP or victory autosave on loss; menu returns and pre-battle save reloads with restored health, uncleared enemy and source-bound driver. No synthetic HP/damage/finish injection.
- Root viewed separate actual north/south frames extracted from the normal-speed movie under outputs/hsea-front17-root, plus browser playback at rate1. These samples establish visible runtime evidence, not complete fluidity or art acceptance. Other NPCs/enemies remain placeholders.

## Workflow implementation

Existing package builder, runtime driver, isolated launcher, checked runner, source checker and normal-input recorder were extended rather than replaced. The one entry supports play, controls and check --scenario victory|defeat --movie. AVI recording retains exact frames and removes per-frame PNG writes; this batch EN12.797s/ZH12.250s engine wall time for victory, EN10.750s/ZH11.860s for natural defeat (no defeat movie requested). These are measured run times, not a projected project-wide saving.

Reusable native prop catalog: outputs/science-prop-kit/rpg-2-star-ocean-the-second_science-prop-kit_existing-native-catalog_v01_20261021-022234-4e609fc4.json. Ten existing props from three approved rooms are indexed by semantic purpose with source PNG/ORA/author/runtime raw hashes, canvas and opaque bounds. Runtime/source bytes and native merged exports match. No art duplicated, resized, repainted or newly approved. Workflow and registry now direct later scene work to this existing kit.

## Failures retained and corrected

The first prop-catalog check failed because JSON decoded bounds as lists while Pillow returned tuples. Converted the computed bounds to lists; no image/hash comparison weakened. Initial front17 combined run refused the unimported source-bound driver; added the existing bounded asset-preparation step to the shared check entry, then reran both languages successfully. Earlier defeat probe broke during the transient null scene handoff; the same bounded menu wait now requires a non-null ready menu. The retained traces show the null handoff at frame877, followed by the proper menu. Failed logs remain. Short game shutdown still reports2 ObjectDB leak warnings; not relabeled clean shutdown.

## Limits and progress

Shoulders/upper sleeves remain torso-bound; some north scarf/belt pixels can move with the cut-out arm; scarf can widen1px, toe-off lifts the boot rather than peeling the heel, west remains mirrored. Two interim stop samples do not by themselves prove smoothness. Complete authored motion, native GUI reliability and default adoption remain separate acceptance/production gates. Existing all8 combat-action technical evidence is retained; this new victory flow exercises attack, loss exercises hit/defeat, and does not pretend to trigger every action.

Production54.5% ->54.5%(+0.0pp), inspection16.7% ->16.7%(+0.0pp), creator approval7.8% ->7.8%(+0.0pp). Existing source production credit is retained; no additional points per revision/report/test. Ordinary-game DEFAULT integration is still pending, so its two2-point tasks remain in_progress. Full accepted runtime sprites0/52, environments5/12, human playtests0/2; formal acceptance false. The concrete deliverable is a complete runnable opt-in heroine path with win and loss recovery, not final art acceptance.
