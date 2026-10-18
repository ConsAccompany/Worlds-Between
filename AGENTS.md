# Worlds Between working rules

Read [the operating workflow](docs/workflow.md) before starting a batch. Its linked operating registry assigns the current primary task, supporting tasks and integration checkout. Read the latest creator decisions and the canonical production ledger; historical plan text does not override them.

## Ownership and execution

- Codex coordinates and inspects; Claude normally implements code/native assets; the creator decides artistic acceptance and scope. The creator explicitly authorizes **Codex to implement, test and integrate during Claude quota gaps**. Reassign the task and continue useful work without waiting for quota.
- One accountable owner per task. Run one primary completion task and at most two supporting tasks with disjoint write scopes. Finish existing work before opening additional candidates. Delegate to agents only when the current user instructions or an applicable skill authorize delegation.
- Each task needs an output, dependencies, completion conditions, evidence and a bounded next action. Technical parameters are implementation decisions; ask the creator only for essential creative/scope decisions and continue independent work meanwhile.
- Use the registry's single integration checkout. Preserve the dirty primary checkout and unrelated partial work. Producers do not edit the shared ledger, Git index or published dashboard. The integration coordinator stages explicit verified paths; never use blanket staging or reset another checkout.

## Evidence and completion

- A successful process exit is insufficient: `SCRIPT_ERROR`, parser/runtime exceptions, missing required checks or missing evidence fail the gate. Test expected behavior independently, including exact timing boundaries and malformed input; do not skip boundaries or weaken thresholds to obtain a pass.
- Bind evidence to the tested source revision and asset hashes. Declare text hash normalization. Record limitations and failed checks honestly. Recheck the combined normal game path after integration.
- Check the staged Git bytes of hash-bound files, not only working files; scoped checkout attributes must preserve the declared bytes. Historical CRLF snapshots must not be silently normalized.
- Gate dependent native commands explicitly. In PowerShell, inspect `$LASTEXITCODE` after each test/build/commit before the next mutation; a later successful command must not hide an earlier failure. Keep validation and publication separate when inspecting the result requires judgment.
- Production, playable readiness, inspection and creator approval are separate states. Update the canonical ledger through its CLI after verified work. Do not change scoring/denominators or award points per version, screenshot, test count, report or repeated review. Pending creator review does not erase completed production credit.
- Actual gameplay captures support visual review. Concept images, test fixtures, opt-in candidates and static approvals are not full runtime art/motion approval. Keep fixtures labeled, approval scope explicit, and existing defaults unless separately authorized.
- Finish one representative character set and one complete scene production path before scaling further asset batches. Use reusable style/source contracts and actual normal-speed motion review, not metric-only tuning loops.

## Accounts, schedules and assets

- Before each new Claude session verify signed-in Max through `claude.ai`/`firstParty`, with `ANTHROPIC_API_KEY` absent. Honor the latest recorded reset; stop inference on actual quota exhaustion. The one-time promotional credit allowance is closed: no cloud credits, API billing, extra paid usage, purchases, auto-reload or paid fallback.
- All schedules are canceled. Do not recreate schedules without fresh user authorization. Coalesce any authorized wakeup with active work; never duplicate or interrupt workers.
- Save each requested generated image separately. Generated assets, captures, exports and manifests use lowercase `[project-slug]_[subject]_[purpose]_[variant]_[YYYYMMDD-HHMMSS]-[unique-id].[ext]`; keep directories short for Windows. Preserve editable native sources and provenance.
- Canon remains the science US/Canada MVP, NYC/Catskills, 2537-05-25 start, 51 identities/52 variants, no persistent companion followers and simple whole-hour travel. Consult the Bible for full canon; do not revive superseded precision travel rules.

## Windows execution

Use explicit UTF-8 for file/subprocess text and extended-length paths when needed. Keep directory names short; preserve descriptive asset filenames. Check each command result before dependent work.
