# Working toward finished game deliverables

Effective 2026-10-18, following the creator's workflow redesign and explicit authorization for Codex implementation during Claude quota gaps.

## Sources of truth

| Record | Purpose |
| --- | --- |
| [Production ledger](../outputs/rpg-2-star-ocean-the-second_production-completion_task-ledger_v01_20261018-140533-3de52073.json) and its declared CLI | Frozen work baseline, owners, evidence and separate production/inspection/approval meters |
| [Operating registry](coordination/rpg-2-star-ocean-the-second_workflow-operating_registry-v01_20261018-211617-6d390c24.json) | Current task contracts, write scopes, worktrees and blockers; carries no completion points |
| [Implementation plan](implementation-plan.md), [current progress summary](progress.md), Bible/inventory files linked by the ledger | Scope and readable summaries; latest confirmed creator decisions supersede historical notes |
| Ignored local account controller under `work/claude-cycle/` | Subscription/reset/account state only; never commit or publish |

The registry is an operating queue, not a second progress system. The dashboard and compact panel consume verified canonical data. Generate summaries from those records and show the tested source revision. Label the old mixed delivery/acceptance percentage as historical; do not compare it as a gain/loss against production completion.

## Batch loop

1. **Orient once:** read current decisions, ledger, registry, relevant source/QA and Git status. Preserve dirty work. Confirm the task is useful and not already active elsewhere.
2. **Select:** one primary finishable deliverable, plus at most two disjoint supporting tasks. Assign one owner, output, dependencies, file scope, completion conditions and next action. Choose the smallest useful completion boundary; do not add scoring milestones retrospectively.
3. **Build:** Claude normally implements; Codex takes over bounded coding/testing/integration when Max is unavailable. Quota is an ownership transition, not a project-wide blocker. Keep the creator out of routine implementation parameters.
4. **Finish first:** near session/context/quota limits, stop starting work. Stabilize the current task and preserve exact files, failures, evidence and next commands. A partial deliverable stays in progress.
5. **Inspect:** check source-bound results independently. Use the normal game path, exact-time expectations, invalid inputs, fallback behavior and targeted unaffected-path checks. Capture actual bilingual gameplay where relevant. Any `SCRIPT_ERROR` fails even if exit code is zero. Disclose threshold changes and resolve the underlying defect instead of narrowing the test around it.
6. **Integrate serially:** the coordinator reviews explicit diffs, merges selected verified work into the designated integration checkout, runs the relevant combined checks and updates the ledger through its CLI. Reconcile stale producer bases without resetting their partial work.
7. **Publish and close:** refresh the Bible/fallback from verified commits, check live, then report completed/integrated/revised/blocked/next. No filler closeouts for unchanged polling or repeated audits.

The coordinator records producer/technical-check transfers with the existing ledger CLI: `reassign --task <id> --owner codex|claude|deepseek --reason-en "<reason>"`. It audits the hash chain, moves any existing revision bucket with its parent, and preserves every score/status/evidence field. Never hand-edit owners or reassign creator approvals, creative reviews or operations. The operating registry mirrors the actual assignment after the ledger transition.

### Command and snapshot gates

For dependent native commands in PowerShell, stop on each nonzero `$LASTEXITCODE` before running the next build, commit or push. A final process exit can otherwise conceal an earlier Python assertion or failed validation. Do not combine validation with publication unless the intermediate result is explicitly checked; inspect diagnostic markers and required predicates in addition to exit status.

New SceneTree probes use the [bounded checked runner](../tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py) with a finite deadline, unique log and expected success marker. It terminates its owned normal process tree on compiler/runtime diagnostics even if the caller event loop stays alive. This prevents waiting through a long command timeout after a failed inner script load. It is a test-process controller, not a security sandbox for intentionally detached children.

For raw-hash evidence, compare every frozen file with its staged Git blob before publishing. Working-file hashes alone miss checkout/filter conversion. Use scoped attributes for the exact source/report snapshots, preserve historical CRLF when that is what was tested, and state any normalization. Recognizing CRLF as a line ending must retain other whitespace checks. A failed hash gate requires correction and disclosure, not a silently rewritten report.

## Completion and handoff contract

For every completed task, retain: task ID and owner; base/tested/integrated revisions; outputs and editable sources; hashes (with explicit LF normalization when applicable); actual commands/results and failed checks; inspection verdict; limitations; remaining creator decision if any. Use the existing ledger evidence paths and QA notes rather than inventing a second receipt platform.

Track these states separately:

- **Produced:** defined code or content deliverable exists and meets its production criterion.
- **Integrated/readiness:** it loads and behaves in the intended game path; list remaining blockers. No new readiness percentage is introduced by this workflow.
- **Inspected:** technical/visual/content checks have actually been performed and have a recorded verdict.
- **Approved:** the creator explicitly accepts the stated artistic scope, or completes a required human playthrough. Automated runs cannot supply this state.

Production credit remains while awaiting review. Revisions use the ledger's defined revision mechanism; another version does not earn another bucket of points. Reopen a revision when it fails. Changes to scope or weights need a separately explained baseline change, never a silent percentage adjustment.

## Asset production and review

- Before authoring, write a short style/source contract: source identity and approval status, native size, gameplay display scale, palette/light/material language, pivots/layers/export requirements, normal scene selector and protected interaction geometry.
- Maintain a reusable material/prop kit and one representative character pipeline. Complete the female protagonist's required exploration/combat set and use the accepted NYC public-facilities room 2 as an environment production reference before scaling batches. Existing approved rooms remain accepted; a reusable kit does not imply other scenes are approved.
- Give each revision a short observable defect list and protected properties. After two unsuccessful passes on the same problem, change the method rather than generate another cosmetic version. Judge motion at normal speed through start/run/stop/re-press/reversal and combat anticipation/contact/recovery in bright/dark contexts.
- Separate native source/export equality, application diagnostics, and GUI save/reopen evidence. An exact export with exit0 does not establish clean application behavior. Preserve failed diagnostic checks and compare an unchanged control; label any primary-format production credit and supplemental-format limitation explicitly. Never report all native checks passed when errors remain, or claim GUI reliability from a CLI export.
- Present only inspected candidates to the creator: show the actual gameplay visual, a working link if inline display fails, exact approval scope and a brief change list. Batch related decisions when helpful. Keep working on independent tasks while approval waits.

## Worktrees, quota and communication

The operating registry names one integration checkout; current producer checkouts are not competing main branches. Only the coordinator changes its shared ledger/index. Legacy worktrees stay protected until explicitly reconciled. Keep generated output directories short while retaining unique descriptive filenames.

Before each new Claude session, verify Max/firstParty authentication and no API key, then honor the latest actual reset in the ignored local controller. Stop on depletion; transfer tasks to Codex where useful. Cloud-credit authorization is closed permanently. Schedules remain canceled unless the creator authorizes a new schedule. No promises of automatic resumption without an active authorized schedule.

At the end of a substantive batch report only: completed and integrated outputs, remaining real blockers/creator decisions, current separate meters, and the next task. Use concise progress updates during long work; quiet checks do not constitute production.

## Minimal operational measures

Use task start/finish/revision timestamps and existing evidence to report completed integrated deliverables, task age, active task count, repeated revisions and periods blocked on account availability. Categorize time only when actually measured (production/testing/coordination/waiting); otherwise say unknown. Do not invent historical hours, count scheduled wakeups as work, or build a new monitoring service. Review these measures when choosing the next batch, not on every polling tick.

### Windows private Site packaging

After a successful source build, use the official source helper with credentials only on hidden stdin. The current Windows environment needs Git\bin and the bundled Node\bin on the helper process PATH for Bash and packaging Node; do not change system PATH. If the package-manager shim fails before compilation, run the existing project framework build directly with the verified Node executable and gate its exit before packaging unchanged inputs. For the Bash/tar archive argument use an absolute MSYS `/c/...` path (a `C:/...` colon is interpreted as a tar remote). Verify the resulting ordinary Windows archive path before passing it to private publication. Preserve source SHA, audience, errors and proof; never put credentials in files, argv or output.

## Dual-provider dispatch policy (creator-authorized 2026-10-19)

Run Claude Max and DeepSeek V4.1 Flash concurrently on disjoint useful scopes when both are available. Claude leads complex gameplay changes, the representative character motion and difficult visual implementation. DeepSeek takes bounded code/content production, package corrections and deterministic validation suited to its demonstrated results. Use observed task results and account state to adjust assignments; neither model approves its own work. Codex coordinates, inspects and serially integrates.

On actual Claude quota exhaustion, capture its exact reset message, stop Claude inference, schedule one alarm for that reset and continue DeepSeek alone. At the alarm, coalesce with active work, verify Max/claude.ai/firstParty and no API key, then resume Claude alongside DeepSeek. No routine repeated polling, premature inference, Claude cloud credits or paid fallback.

On DeepSeek insufficient credit, stop all project production, including Codex and both providers, save the handoff and cancel pending resumption. Never top up, purchase credits, enable paid fallback or substitute another DeepSeek billing route. Check the signed-in account balance before new batches, record its currency and any display delay in the ignored account controller, and retain provider exhaustion errors. Existing DeepSeek account credit is authorized; this does not reopen the closed Claude promotional-cloud allowance. Account balances and reset logs stay local.

Assign bounded completion contracts and preserve the one-primary/two-supporting limit. Transfer producer/technical-check owners through the ledger CLI, now accepting `deepseek`, without changing points, production status or creative approval. An alarm is a resumption mechanism, not production evidence.
