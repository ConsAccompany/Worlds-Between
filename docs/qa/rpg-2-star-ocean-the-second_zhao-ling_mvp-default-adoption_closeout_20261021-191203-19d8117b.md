# Zhao MVP ordinary default adoption

Creator explicitly authorized: “先设为 MVP 默认，精修后置（推荐）”. Scope is ordinary default use only; final character art, full motion and human playtests remain separate.

## Delivered

- `DEFAULT_ADOPTED=true`; the existing single Zhao policy activates the stationary Yonkers field NPC and separate companion combat set without preview host overrides. Hero defaults, mechanics, party assignment, saves and no-follower rule are preserved.
- Reused the existing real-input runner with explicit `ordinary-default` and hero appearance options. This branch never calls `configure()`: it starts an ordinary fresh AppState run and selects the destination as a declared setup fixture, leaving all presenter/member/index overrides empty and enabled_override=-1.
- EN male and ZH female: 55/55 normal recruit, combat actions, natural victory/return and actual autosave reload checks each.
- ZH female defeat/retry:45/45 from a declared valid1HP/0energy save fixture; subsequent damage/result are engine-caused. This does not establish healthy-party defeat or Save/Load UI coverage.
- Existing malformed/disable/explicit-index/rollback checks:15/15 per hero appearance. Rollback returns to the newly authorized ordinary default, not the old disabled default.
-155 flow checks +30 boundary checks pass.171 source/runtime character files remain byte-identical. Codex viewed the actual ZH female battle screenshot; no final art/fluidity acceptance is inferred.

## Evidence and limitations

Root proof: outputs/zpath27/adopt-20261021-190923-68fdb2b0/rpg-2-star-ocean-the-second_zhao-ling_default-adoption_root-proof_20261021-191114-4ee445f3.json

The proof binds exact working source SHA256, normal-input reports and captured image hashes. New captures are native640x360. Fixture exit ObjectDB warnings remain; successful runs contain no parser/script/runtime diagnostic errors. Earlier30fps MovieMaker attack-observation failure and60fps recording stall remain documented separately; these real-time ordinary-default runs do not reuse their results. The root evidence checker initially hit the Windows long-path limit on a screenshot; an extended-length read fixed that helper without altering source/evidence.

Only existing production task IDs `content.char.zhao-ling.runtime-integration` and `content.combat.zhao-ling.combat-integration` become complete after source integration. No new points, denominator changes, inspection credit, full-sprite approval or human-play credit are created. Before/after meters are recorded by the canonical task recorder in the Bible.
