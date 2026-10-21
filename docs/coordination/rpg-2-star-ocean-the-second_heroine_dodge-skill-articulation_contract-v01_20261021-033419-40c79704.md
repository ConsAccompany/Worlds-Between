# Heroine dodge and skill articulation

Base dedf44ddb83e29d3864da4dca9a6b9fe1e6673cf. Production54.6%, inspection17.6%, creator7.8%. One primary: stronger authored dodge and skill body poses, not parameter grids or generic concept art. Preserve current face identity, palette,136x144 cells,pivot64,136,binary alpha,logical0.5,battle display0.65; all other22 poses and exact8 action sequences/ticks/loop semantics remain unchanged. No gameplay changes. Default use already authorized, art acceptance separate.

Claude owns new native author/source outputs under outputs/hero-sea-motion-v04 and one new author tool only. DeepSeek owns one reusable selective-revision packer and its bounded negative tests only. Neither changes game scripts, shared checkers, existing immutable packages, ledger, Git or Site. Codex integrates serially, verifies native/source equality and actual bilingual1x normal-default gameplay before replacing current source. Do not mutate package files during active gameplay validators.

Visible goals: dodge should read as a backward evasive crouch/weight shift rather than idle sliding; skill should show torso/shoulder/hip participation and a deliberate wind-up/release/recover. Keep head/face readable and do not let hair, knees or boots detach. Keep current duration budgets; no extra damage or root motion from asset authoring. Skill is Situational Insight, a self-buff, not a direct attack; avoid an exaggerated impact burst that promises a hit.

Shared revision manifest schema (all paths relative to the producer root; raw SHA256):

{
  "schema": "worlds-between.heroine-combat-pose-revision/1",
  "baselineIndex": "game/data/heroine-sea-combat-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-index_v01_20261020-201338-38ecfcb0.json",
  "baselineIndexSha256": "1abb5b67b3bf59c02b3c747068789a01509812aee97c105b9f5c15c7a60ffa49",
  "cell": [
    136,
    144
  ],
  "pivot": [
    64,
    136
  ],
  "tickRate": 30,
  "overrides": {
    "dodge-a": {
      "png": "<repo-relative>",
      "sha256": "<raw PNG SHA256>",
      "pxo": "<repo-relative>",
      "pxoSha256": "<raw>",
      "ora": "<repo-relative>",
      "oraSha256": "<raw>"
    },
    "dodge-b": {
      "png": "<repo-relative>",
      "sha256": "<raw PNG SHA256>",
      "pxo": "<repo-relative>",
      "pxoSha256": "<raw>",
      "ora": "<repo-relative>",
      "oraSha256": "<raw>"
    },
    "skill-tel-a": {
      "png": "<repo-relative>",
      "sha256": "<raw PNG SHA256>",
      "pxo": "<repo-relative>",
      "pxoSha256": "<raw>",
      "ora": "<repo-relative>",
      "oraSha256": "<raw>"
    },
    "skill-tel-b": {
      "png": "<repo-relative>",
      "sha256": "<raw PNG SHA256>",
      "pxo": "<repo-relative>",
      "pxoSha256": "<raw>",
      "ora": "<repo-relative>",
      "oraSha256": "<raw>"
    },
    "skill-strike": {
      "png": "<repo-relative>",
      "sha256": "<raw PNG SHA256>",
      "pxo": "<repo-relative>",
      "pxoSha256": "<raw>",
      "ora": "<repo-relative>",
      "oraSha256": "<raw>"
    },
    "skill-contact": {
      "png": "<repo-relative>",
      "sha256": "<raw PNG SHA256>",
      "pxo": "<repo-relative>",
      "pxoSha256": "<raw>",
      "ora": "<repo-relative>",
      "oraSha256": "<raw>"
    },
    "skill-recover": {
      "png": "<repo-relative>",
      "sha256": "<raw PNG SHA256>",
      "pxo": "<repo-relative>",
      "pxoSha256": "<raw>",
      "ora": "<repo-relative>",
      "oraSha256": "<raw>"
    }
  },
  "artApproved": false
}

Baseline manifests/sheet/provenance and all v01-v03 inputs are read-only. Exact other-cell equality, decode equality for seven source PNGs, full action equality, binary alpha/palette/bounds, honest native CLI diagnostics and unchanged rules are required. Preserve failures. No points per version; this is polish to an already-produced8-action set. Native GUI reliability and full artistic fluidity remain separate.
