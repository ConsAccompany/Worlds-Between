# Heya east static — independent source-production verdict (UNAPPROVED)

Canonical task: content.char.heya.static-east. Coordinator: Hermes. Existing source producer: DeepSeek through the authorized adapter (batch155); batch157 reconciliation producer: DeepSeek through the same adapter. No artistic approval, runtime adoption or default change.

## Tested boundary

Base bfb00f33ecafcf4691d658c88fc97f4562e81969. Existing native east source is 80x112, body rows8..103 at scale0.5 =48 logical pixels, pivot40,104. It is not the32x48 placeholder. Editable layered PXO/ORA, palette, flat PNG and manifest are installed under game/assets/characters/heya-native-v01/east; deterministic staging remains outputs/heya-e155/staging/east. No source repaint or asset edit was needed in batch157.

Raw SHA256; no text normalization:
- PNG273e5e854121fa8ec92dc74e28a67be35920da6442fc20571ff053453fdf9dd4
- PXO45ab6257e31b20fb756e1d18c687d1716c73d2fa22489737ed86fd5348e2bf56
- ORA0cf8b0b465560bf6328de320f2e40f356cb5d304c3c546227de3a2ba12e8bc91
- manifest dc5e13978247c8781955785f2d5ef46a0ac0fe26ced3e03ed98ea1a871a6302d

## Independently executed checks

Project tooling Python3 -I and existing pipeline only:
1. Existing east author `check`: exit0, HEYA_EAST_V01_ALL_OK, hard_failures=[], deterministic rebuild and every stage/install comparison pass. Log outputs/heya-e157/coordinator/author.log.
2. Existing east independent source checker --root . --out outputs/heya-e157/coordinator/source: exit0,57/57, no failed predicates. Recomputes from PNG/PXO/ORA bytes; malformed hash/pixel/guide/facing/light/braid/scarf/bag/smile/dress controls retained. Log outputs/heya-e157/coordinator/source.log.
3. Existing east Pixelorama checker --out outputs/heya-e157/coordinator/native: export equality11/11. Exact per-layer/merged/flat exports and unchanged sources pass. Native application diagnostic cleanliness FAILS: custom_samplers errors4/4/4; ORA shutdown/resource/index errors also retained. Report under native/20261024-135128-8f732d84. Exit0 is NOT a clean-application verdict.
4. Existing east source-fit driver: checked90s runner, Xvfb/OpenGL3/Dummy audio, required JIANG37_SOURCE_FIT_PASS captures=4. Exit0, four640x360 city/ruins EN/ZH captures, unchanged source. Fresh outputs/heya-e155/fit-r3 and matching proof. This is a test-only overlay, not ordinary actor integration. The ruins scene is daytime despite historical 'dark' fixture wording; this batch does not establish night/dark-lighting coverage.
5. Hermes opened the native PNG and all four fresh rendered captures with vision_analyze. The sprite faces screen right with auburn hair, ivory coat, pale scarf/apron, dark-red rear-hip bag and boots; silhouette fits the visible scene without clipping. Small face/low braid details remain visually ambiguous at gameplay scale. No mature-age, detailed braid readability, stylistic excellence or human art-acceptance claim follows from metrics.
6. Adapter job fbb58fba89f840428756ccb9f89d4b5a finished: outcome exited, classification success, returncode0, scope.confirmed=true. Exact stdout /home/kel/projects/worlds-between/autonomy/provider/158-deepseek.stdout.log (SHA256 dc0d0b5c5a8b8a37d655b2dc1fde87d9881130930efb99048b3ff05027639403), stderr /home/kel/projects/worlds-between/autonomy/provider/158-deepseek.stderr.log (empty SHA256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855) inspected. finished.json.result agrees. Provider receipt artifacts independently hash-checked27/27; adapter success alone was not accepted as task evidence.

## Preserved failures and limits

Batch155 preservation FAILED: second QA edit lacked a unique pre-edit backup; author-preview.log overwrote differing content without verified backup. Intermediate QA text recovered from original backup and edit events is not retroactive compliance. Original failed log is not recoverable from its later rerun. Preserve outputs/heya-e155/coordinator/preservation-audit.json, reconstructed/failed reconstruction notes, retained-producer-failures.json, source-backups, failed draft and preview. The old producer QA's 'No backup failures' statement is superseded by this verdict and the batch157 provider addendum, not silently edited away.

Prior failed source author API/import/constant operations and identity_colours_all/upper_left_light_east draft predicates remain failures. Prior combined process-inspection python -c command was genuinely denied by the single-query guard and abandoned, not bypassed. Existing checked runner log-opening failure also remains in retained provider events; isolated runs later pass. GUI SaveAs/reopen untested for this east asset. No animation, motion, combat, save/reload, human playtest, default adoption or art review credit.

Coordinator alone changed the ledger through audited reassignment on a candidate copy then wb_safe_replace; provider's observed concurrent ledger change is fully attributed to that operation. Unique metadata-preserving backups precede coordinator metadata edits. Scoped raw-byte attributes and staged Git-blob equality are required before commit. Existing153 unrelated staged files must remain untouched.

## Completion gate and progress

Source is technically eligible for the canonical source-production criterion once this native package and QA are committed and staged bytes verified. Commit, post-source-commit M1 smoke, ledger done transition and final progress are recorded in the coordinator closeout; this precommit verdict alone does not claim them.

Starting canonical production62.6%; inspection21.6%; approval7.8%. Frozen baseline unchanged. The Bible already has an unrelated active Muxiu east progress record; it must not be finished or displaced just to record this task. Remaining actions are source integration, bounded normal-game smoke and audited ledger transition, not repaint/polish or approval.
