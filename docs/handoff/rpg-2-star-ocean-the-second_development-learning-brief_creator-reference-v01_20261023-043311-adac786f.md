# Agent Efficiency, PC Game Creation & AI Skill Stack — Research Brief

**Prepared for:** ChatGPT, as a learning and context document. **Compiled:** 20 October 2026.

**Purpose:** load this as context (project knowledge, uploaded file, or direct paste), then use it as the reference for planning, advice, and execution on three topics: running AI agents efficiently, building a PC game with open asset libraries, and choosing skills and tools for ChatGPT and Claude.

**How to use this file**
- Read Parts 1–3 once to build the model.
- Use the tables as lookups.
- Every non-obvious claim carries a source link; verify before committing money or licensing.
- Product facts are dated **October 2026**. Anything that moves monthly (model names, feature availability) is marked **[volatile]**.

---

## Contents

1. **Part 1 — Optimizing agent efficiency, workflow, and output**
2. **Part 2 — Creating PC games and finding asset libraries**
3. **Part 3 — Skills, tools, and setup for ChatGPT and Claude**
4. **Appendix A** — Source list
5. **Appendix B** — The 12 rules

---

# Part 1 — Optimizing Agent Efficiency, Workflow, and Output

## 1.1 The core idea: context is a budget

An agent's quality is capped by what is in its context window and how much of that is signal. Anthropic frames this as **context engineering**: "finding the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."

Why it matters:
- **Context rot.** As token count rises, recall precision falls. This is measured, not folklore — see the Chroma "context rot" study. Longer context is a gradient, not a cliff, but accuracy degrades.
- **Attention budget.** Transformer attention is quadratic in sequence length; every token competes for attention. Irrelevant tokens are not free.
- **Context anxiety.** Long-running agents begin rushing or prematurely declaring victory as their context fills. Anthropic observed this in coding agents and found that **full resets with a structured handoff artifact can beat incremental compaction** for long tasks.

**Operating rules**
1. Keep the system prompt at the **"right altitude"**: specific enough to steer, general enough not to be brittle. Avoid hard-coded if/else; avoid vague platitudes.
2. Give **canonical examples**, not an exhaustive edge-case list.
3. Prefer **just-in-time retrieval** (paths, queries, links) over pre-loading.
4. **Clear consumed tool results** from deep history.
5. Treat every added instruction as a tax on attention.

## 1.2 Techniques for long-horizon work

| Technique | Mechanism | Best for | Cost / risk |
|---|---|---|---|
| **Compaction** | Summarize near the limit, restart with summary + last few files | Long back-and-forth | Loses subtle detail; one summarizer call |
| **Full reset + handoff artifact** | Wipe context, pass a structured state file | Very long builds, "context anxiety" | Requires a good state schema |
| **Structured notes / memory file** | Agent maintains NOTES.md, todo, decisions log | Multi-hour, milestone-driven work | Discipline + a little overhead |
| **Sub-agents** | Isolated context per task, returns a 1–2k token digest | Parallel research, breadth | Coordination cost; token spend |
| **Tool-result clearing** | Drop raw outputs once consumed | Any tool-heavy run | Minimal |
| **Just-in-time retrieval** | Load only when needed | Large repos/datasets | Slower than pre-computed retrieval |

Anthropic's harness work (March 2026) adds a sharper claim: for long application builds, a **planner → generator → evaluator** loop with **sprint contracts** (agreed definition of done before each sprint) produced a working app where a solo agent produced something non-functional. The trade-off was real: 6 hours and ~$200 versus 20 minutes and ~$9. The lesson is not "always use the harness" — it is *match scaffolding to task difficulty, then simplify as models improve.*

## 1.3 Workflow patterns

| Pattern | Shape | Use when | Avoid when |
|---|---|---|---|
| **Single call** | Prompt → answer | One-pass task | Multi-step, tool-using |
| **ReAct** | Think → Act → Observe → repeat | Unknown terrain, dynamic | Predictable pipelines |
| **Plan-and-execute** | Plan, then execute | Well-understood multi-step | Environment shifts mid-task |
| **Router** | Classify → specialist | Mixed task types | One dominant type |
| **Orchestrator–worker** | Lead delegates to workers | Parallelizable breadth | Tightly coupled steps |
| **Generator–evaluator** | One makes, a separate one judges | Quality-critical output | Cheap, low-stakes tasks |
| **Reflection** | Generate → critique → revise | Writing, design | Latency-sensitive |
| **Human checkpoint** | Approval before irreversible action | Money, publishing, deletion | High-volume low-risk |

**Design principle:** start with the simplest workflow that passes your evals. Add agency only when the evals demand it. Most "agent" failures are over-engineering, not under-engineering.

## 1.4 Why separate generation from evaluation

A repeatedly reproduced finding: **agents are poor judges of their own work.** They praise mediocre output. Two fixes work better than asking for self-critique:
1. **A separate evaluator** with its own rubric and, ideally, its own context.
2. **External verification** — run the test, render the page, open the file, execute the query.

Anthropic's harness used Playwright to actually test the running app rather than asking the generator whether it worked. That is the pattern to copy: **verify with tools, not with self-report.**

## 1.5 Prompt and instruction design

A reliable system-prompt skeleton:

```
<role>Who the agent is, what it optimizes for. Two sentences.</role>

<goal>The concrete outcome. Define "done" as a testable condition.</goal>

<context>Only what's needed. Point to retrievable sources.</context>

<tools>
- name: when to use it, when NOT to, what it returns
</tools>

<rules>
- Hard constraints
- Escalation: when to ask, when to stop
</rules>

<output>Exact schema, length, tone, plus one example.</output>
```

High-yield techniques:
- **Explicit done-criteria.** Most bad outputs are undefined success.
- **Output schemas / structured outputs.** Eliminates parser failures.
- **2–5 canonical examples**, including one hard case.
- **One negative example** of the failure you keep seeing.
- **Pre-mortem prompt:** "List the three ways this answer is most likely wrong, then check them."
- **Stop conditions:** max iterations, token budget, "if blocked twice, report and stop."
- **Scope restatement:** "Restate the task in one line before starting."

## 1.6 Tool design

Tools are the contract with the world, and most agent failures are tool failures.

- **Narrow and unambiguous.** If a human engineer can't pick the right tool, the model can't either.
- **No overlapping tools.** Two similar tools cause decision paralysis.
- **Token-efficient returns.** Return the minimum; truncate with a pointer to the full result.
- **Actionable errors:** "File not found: X. Files in dir: [...]" beats "Error 404."
- **Idempotent writes** where possible; destructive actions explicit and confirmed.
- **Readable names and parameters.** `search_orders(customer_id, since)` > `q(a,b)`.
- **MCP (Model Context Protocol)** is the de facto standard for connecting tools and data. One server works across Claude, ChatGPT, Codex, and IDEs.

## 1.7 Efficiency levers

| Lever | Typical effect | Notes |
|---|---|---|
| **Prompt caching** | Reads cost about **0.1×** base input (Anthropic and OpenAI); writes cost 1.25× (5-min) or 2× (1-hour) | Order context most-stable-first: tools → system → references → history → input. One timestamp before the breakpoint invalidates everything after it |
| **Model cascade** | RouteLLM reports >2× cost cut; FrugalGPT up to 98% at GPT-4-level quality | Cheap model triages; strong model for hard cases |
| **Parallel tool calls** | Wall-clock speedup | Independent reads in one turn |
| **Batch API** | ~50% discount | Offline, non-latency-critical |
| **Tool search / deferred loading** | −85% context in Anthropic's test (77k → 8.7k tokens); MCP-eval accuracy 49% → 74% | Load tool definitions on demand instead of all at once |
| **Programmatic tool calling** | −37% tokens on complex research (43.6k → 27.3k); 19 fewer inference passes on a 20-call workflow | Keep intermediate results out of context |
| **Sub-agent isolation** | Bounded context per worker | Watch total spend (often 3–10× a solo agent) |
| **Answer caching** | Avoid repeat work | Hash the normalized request |

Track per task: **tokens, cost, wall-clock, success rate, retries, human interventions, cache hit rate** (target >70–90% on stable agents).

## 1.8 Output quality: evals are the whole game

1. **Golden set** — 20–100 real tasks with known-good outputs or rubrics.
2. **Automatic scoring** where possible: schema validity, exact match, unit tests, retrieval hit rate.
3. **LLM-as-judge** for subjective quality — with a rubric, a reference answer, and position swapping to reduce bias.
4. **Regression-test every prompt change.** Prompts are code.
5. **Ground everything** — citations, quote spans, tool-derived evidence.
6. **Verify before returning** — run it, read it, open it.
7. **Log failures** with full traces; build a failure taxonomy.
8. **Measure consistency, not just averages.** At 75% per-trial success, **pass^3 is only ~42%**. Report both pass@k (any success) and pass^k (all succeed).
9. **Grade outcomes, not paths.** Agents find valid routes you didn't anticipate.
10. **Fix the grader before blaming the model.** Anthropic moved Opus 4.5 from 42% to 95% on CORE-Bench by correcting rigid grading and ambiguous specs.

| Metric | What it catches |
|---|---|
| Task success rate | Overall capability |
| Pass@k on golden set | Consistency |
| Tokens per task | Bloat |
| Cost per success | Efficiency |
| Tool error rate | Bad tool design |
| Human-intervention rate | Autonomy gaps |
| Time to first useful output | UX |
| Hallucination rate (sampled) | Grounding |

## 1.9 Multi-agent: when it helps, when it hurts

**Helps:** parallelizable breadth (research, audits), isolated context per worker, adversarial review.
**Hurts:** tightly coupled steps, small tasks, one-voice output, tight budgets.

Practical rules:
- One clear deliverable and return format per sub-agent.
- The lead sees **digests**, not transcripts.
- **Structured handoffs** (JSON), not prose.
- **Cap depth and fan-out.** Anthropic's early agents spawned 50 sub-agents for simple queries until effort-scaling rules were added.
- Log a **run tree** so you can see where tokens went.
- **Economics:** agents use ~4× chat tokens; multi-agent systems ~15×. Token usage alone explained ~80% of performance variance on BrowseComp, and Anthropic's research orchestrator beat a single agent by **90.2%** at ~15× the tokens. Multi-agent is a deliberate spend — worth it only when the task value clears the bill.

## 1.10 Failure modes

| Failure | Symptom | Fix |
|---|---|---|
| Context rot / anxiety | Forgets decisions; rushes to finish | Compaction, resets, notes, smaller scope |
| Tool thrash | Repeated wrong tool calls | Better descriptions, fewer tools |
| Loops | Same action repeated | Iteration caps, progress checks |
| Premature stop | "Done" without verification | Done-criteria + verify step |
| Hallucinated success | Claims tests pass; they don't | Run the test, read the output |
| Silent truncation | Misses data past a limit | Pagination, "N of M" reporting |
| Scope creep | Expands beyond ask | Restate scope, confirm |
| Cost blowup | 10× expected spend | Routing, caps, batch |
| Sycophancy | Agrees with a wrong premise | Ask for disconfirming evidence |

## 1.11 Build checklist

- [ ] Success defined as a testable condition
- [ ] Golden set + scoring harness
- [ ] System prompt sectioned, right altitude
- [ ] ≤10 well-described, non-overlapping tools
- [ ] Structured output schema enforced
- [ ] Verification step before final answer
- [ ] Compaction/notes for runs > 30 turns
- [ ] Iteration, token, and time caps
- [ ] Tracing + cost logging
- [ ] Human checkpoint on irreversible actions
- [ ] Regression run on every prompt change

---

# Part 2 — Creating PC Games & Asset Libraries

## 2.1 Engines (state as of October 2026)

| Engine | Current | Best for | License | Watch out |
|---|---|---|---|---|
| **Godot 4** | 4.6.1 (4.6 stable Jan 2026) | 2D, stylized 3D, solo devs | MIT, free, no royalties | Smaller 3D ecosystem; console export via third parties (e.g. W4 Games) |
| **Unity 6** | 6.3 LTS / 6.4 | 2D/3D, PC + mobile, huge store | Personal free under **$200k** revenue/funding; Pro **~$2,310/seat/yr**; Runtime Fee canceled Sept 2024; no royalties | Seat costs; URP/HDRP churn; terms have changed before |
| **Unreal Engine 5** | UE 5.7+ | High-fidelity 3D, cinematics | Free under **$1M lifetime gross per product**; 5% above; 0% on Epic Games Store sales | Heavy; 5% stacks on Steam's 30% cut |
| **GameMaker** | Current release | 2D action/platformers | Free IDE; **~$99.99 one-off** commercial licence; Enterprise sub for consoles | 2D only |
| **Bevy** | 0.18 | Rust/ECS enthusiasts | MIT/Apache | No editor; immature tooling |
| **Ren'Py** | Current release | Visual novels | Free (MIT-style) | Niche |

**Defaults:** first PC game + 2D → **Godot 4**. Max tutorials/assets/hiring → **Unity 6**. 3D showcase → **Unreal 5**. Jam → **Godot** or **GameMaker**.

**Licensing specifics worth memorizing**
- **Godot:** MIT. No royalties, no revenue share, ever. Console exports (Switch/PlayStation/Xbox) require third-party porting services.
- **Unity:** Runtime Fee **canceled in September 2024**. Pricing is now seats + revenue thresholds. Personal is free under **$200k**; Pro is roughly **$2,310/seat/yr**. Confirm current terms before budgeting.
- **Unreal:** royalty only above **$1M lifetime gross per product**, at **5%**; **0%** on Epic Games Store sales. Non-game commercial use above $1M needs seats at **$1,850/seat/yr**.
- **Royalty math:** $2M Steam gross → ~$1.4M net after Valve's 30%. UE5's 5% applies to the $1M above the threshold = ~$50k, about 3.5% of net. Unity with 2 Pro seats ≈ $4,620/yr. Godot = $0.

## 2.2 Idea → Steam pipeline

1. **Concept** — one-sentence pitch, core loop, target player, "X meets Y" comparables.
2. **Prototype (days–weeks)** — prove the loop is fun with placeholder art. Kill fast if it isn't.
3. **Vertical slice (weeks)** — one polished 10-minute segment at final quality. This is your proof and your trailer.
4. **Production** — build to the slice's quality bar. Scope to what you can finish.
5. **Playtesting** — 5 real playtesters beat 50 opinions. Watch, don't explain.
6. **Polish** — juice, settings, accessibility, localization hooks.
7. **Steam page early** — 6+ months out. Wishlists compound.
8. **Demo + festivals** — Steam Next Fest, genre showcases, press kit.
9. **Launch** — review copies, streamer keys, launch discount, day-one patch.
10. **Post-launch** — patches, roadmap, community, sales events.

**Scope:** a first commercial PC game should be finishable in 6–18 months by 1–3 people. Cut features, not polish.

## 2.3 Toolchain

| Need | Free | Paid / pro |
|---|---|---|
| 3D | Blender | Maya, 3ds Max, ZBrush |
| 2D / pixel | Krita, GIMP, Piskel, LibreSprite | Aseprite (~$20), Photoshop, Clip Studio |
| Vector / UI | Inkscape, Figma free tier | **Affinity suite (now free under Canva)** |
| Texturing | Material Maker, ArmorPaint | Substance 3D Indie (~$20/mo) |
| Audio edit | Audacity, Ardour | Reaper ($60), Pro Tools |
| Music | LMMS, MuseScore | FL Studio, Ableton |
| Game audio | — | FMOD (free indie tier), Wwise (free under budget) |
| Animation | Blender, Mixamo | Cascadeur, Maya |
| Version control | Git + Git LFS | Perforce |
| CI | GitHub Actions + GameCI | Custom |
| Planning | Trello, Notion, Obsidian | Jira, Linear |

## 2.4 Asset libraries

**License shorthand:** CC0 = public domain, no credit needed. CC-BY = credit required. MIT = permissive code license. RF = royalty-free, but read the EULA.

### 3D models & characters

| Source | URL | License | Notes |
|---|---|---|---|
| Kenney | kenney.nl | CC0 | Low-poly kits, characters, props; best for prototypes |
| Quaternius | quaternius.com | CC0 | Low-poly characters, animals, nature |
| Poly Pizza | poly.pizza | CC0/CC-BY mixed | Searchable free low-poly aggregator |
| Sketchfab | sketchfab.com | Varies (filter by license) | Store closed; free CC models remain |
| Mixamo | mixamo.com | Free (Adobe account) | Rigged humanoids + animations; **no redistribution** |
| Quixel Megascans | quixel.com | **Mostly paid now**; ~800 free assets remain | Terms changed; check before relying |
| Unity Asset Store | assetstore.unity.com | Per-seat EULA | Largest commercial marketplace |
| Fab (Epic) | fab.com | CC-BY free tier, or Personal (<$100k) / Professional (>$100k) | Buying the wrong tier is an EULA breach |
| CGTrader | cgtrader.com | Varies | Marketplace; watch "editorial only" |
| TurboSquid | turbosquid.com | Varies | Marketplace; watch "editorial only" |
| Free3D | free3d.com | Varies | Often personal-use only |

### 2D sprites, tilesets, UI

| Source | URL | License | Notes |
|---|---|---|---|
| Kenney | kenney.nl | CC0 | UI packs, tilesets, platformer kits — start here |
| itch.io assets | itch.io/game-assets | Varies | Huge indie ecosystem; filter free + license |
| OpenGameArt | opengameart.org | CC0/CC-BY/GPL | Community; avoid the GPL entries |
| CraftPix | craftpix.net | Free + paid | Attribution or paid; no redistribution |
| Pixel Frog | pixelfrog-assets.itch.io | CC0 | Excellent platformer art |
| Universal LPC | github.com/LiberatedPixelCup | **CC-BY-SA** | Share-alike — be careful |
| GameDevMarket | gamedevmarket.net | Varies | Curated marketplace |
| Lospec | lospec.com | Varies | Palettes + pixel resources |
| game-icons.net | game-icons.net | CC-BY | 4,000+ SVG icons for abilities/items |

**Never** use ripped sprite sheets (Spriters Resource and similar).

### Audio

| Source | URL | License | Notes |
|---|---|---|---|
| Sonniss GDC bundles | sonniss.com/gameaudiogdc | Royalty-free | Tens of GB of pro SFX, free each GDC |
| Freesound | freesound.org | CC0/CC-BY/NC per sound | Huge; check each — some are non-commercial |
| OpenGameArt audio | opengameart.org | CC0/CC-BY | Music + SFX |
| Free Music Archive | freemusicarchive.org | CC licenses | Watch NC/ND traps |
| Incompetech | incompetech.com | CC-BY | Kevin MacLeod; attribution required |
| Pixabay audio | pixabay.com/music | Pixabay license | Free commercial use |
| ZapSplat | zapsplat.com | Free tier w/ attribution | Check terms |
| BBC Sound Effects | sound-effects.bbcrewind.co.uk | **RemArc: personal/education only** | Do not ship |

### Textures / materials / HDRIs

| Source | URL | License | Notes |
|---|---|---|---|
| Poly Haven | polyhaven.com | CC0 | HDRIs, PBR materials, models — gold standard |
| ambientCG | ambientcg.com | CC0 | PBR materials, decals |
| Quixel Megascans | quixel.com | Mostly paid; ~800 free | Photoreal; terms changed |
| Material Maker | materialmaker.org | MIT (tool) | Procedural materials |

**Skip Texture Ninja** — provenance of the source photos is unclear, which is a licensing risk.

### Animation & rigging

| Source | URL | License | Notes |
|---|---|---|---|
| Mixamo | mixamo.com | Free | Auto-rig + 2,000+ animations |
| ActorCore | actorcore.reallusion.com | Paid/free tiers | Mocap libraries |
| Cascadeur | cascadeur.com | Free/paid | Physics-assisted keyframing |
| Unity/Unreal packs | Asset Store / Fab | Varies | Locomotion, combat sets |

### Shaders & VFX

| Source | URL | License | Notes |
|---|---|---|---|
| Shadertoy | shadertoy.com | **CC-BY-NC-SA by default** | Inspiration only unless the author says otherwise |
| Unity VFX Graph samples | Unity Learn | Unity license | Production examples |
| Unreal Niagara samples | Fab / Epic docs | Unreal license | Production examples |
| Godot shader repos | github.com/topics/godot-shader | Mostly MIT | Community shaders |
| Book of Shaders | thebookofshaders.com | Free (educational) | Learning GLSL |

### Plugins & frameworks worth buying

| Need | Option |
|---|---|
| Dialogue | Yarn Spinner (free, C#), Dialogue System for Unity |
| Tweening | DOTween (Unity) |
| Behavior trees | Behavior Designer (Unity), Beehave (Godot) |
| Inventory / save | Inventory System, Easy Save (Unity) |
| Inspector | Odin Inspector (Unity) |
| Input | New Input System (Unity); built-in in Godot |
| Localization | I2 Localization (Unity) |

### AI-generated assets

Tools: Meshy, Tripo, Scenario, Layer AI, ComfyUI/Stable Diffusion, Suno/Udio.
**Caveats:** commercial terms vary by tool and plan; some stores require AI disclosure; copyright status is unsettled in several jurisdictions; style consistency is hard. Use for prototypes and filler, not hero assets, unless the license is explicitly clean.

## 2.5 License essentials

| License | Obligation | Commercial game? |
|---|---|---|
| **CC0** | None | Yes — safest |
| **CC-BY** | Credit the author | Yes, with attribution |
| **CC-BY-SA** | Share-alike may infect your project | Avoid |
| **CC-BY-NC** | No commercial use at all | **No** |
| **CC-BY-ND** | No modifications | Usually unusable |
| **GPL** | Source disclosure | Avoid in closed-source |
| **MIT / Apache** | Keep notices | Yes |
| **OFL (fonts)** | Keep licence; can't sell the font alone | Yes |
| **"Free for commercial use"** | Read the EULA; may forbid resale of the asset itself | Usually yes |
| **Royalty-free** | Pay once, no per-use fee; usually **not** redistributable standalone | Yes |
| **Engine licenses** | Separate from asset licenses | Depends on engine |

**Named traps worth memorizing**
- **Shadertoy** defaults to **CC-BY-NC-SA** — non-commercial.
- **BBC Sound Effects (RemArc)** is personal/education only.
- **Texture Ninja** has unclear provenance.
- **Fab** has revenue-tiered licences; buying Personal while above $100k is a breach.
- **"Editorial only"** stock (TurboSquid, CGTrader) can't go in a game.
- **Spriters Resource / ripped assets** — never.
- **Unity Asset Store** assets are often per-seat, not per-studio.
- **AI-generated output** has no US copyright and needs Steam disclosure.

**Pre-ship checklist**
- [ ] Every asset has a recorded source + license in a spreadsheet
- [ ] Attribution list complete (`CREDITS.md`)
- [ ] No ripped assets from commercial games
- [ ] AI assets: commercial use allowed; Steam disclosure done
- [ ] Music/SFX cleared for trailers and monetized video
- [ ] Fonts licensed for embedding
- [ ] Full asset audit ~4 weeks before launch

## 2.6 Steam specifics

- **Steam Direct fee:** $100 per app, recoupable after $1,000 adjusted gross.
- **Valve's cut:** 30% (25% above $10M, 20% above $50M).
- **Store page:** name, short + long description, tags, genres, ≥5 screenshots at 1920×1080, trailer, capsule art.
- **Public before launch:** the store page must be public **at least 2 weeks** before release; six months of wishlist building is standard practice.
- **Capsule sizes:** header 460×215, small 231×87, main 616×353, vertical 374×448, page background 1438×810, library 600×900, hero 3840×1240, logo 1280×720, library header 460×215, community 184×184 — supply 2× versions.
- **Build pipeline:** Steamworks SDK + SteamPipe (`steamcmd`), depots, beta branches.
- **Review:** store page ~1–5 business days; build review separate. Tax/bank setup takes ~30 days.
- **Steam Deck:** Verified requires readable text at 1280×800, full controller input, no compatibility warnings, and stable ~30fps via Proton. Newer **Steam Machine** and **Steam Frame** verification programs were added at GDC 2026.
- **Playtest:** a free separate app ID, no store page, invites via sign-up or keys, no reviews.
- **Demo:** separate app; 20–30 minutes ending on a hook.
- **Next Fest:** February, June, October. October 2026 ran 19–26 October; next is February 2027. One entry per title; demo live at the start; launch after.
- **Wishlists:** the best predictor of launch sales. Rough bar for Steam's "Popular Upcoming" list is **7,000–10,000**; under ~1,000 is a signal to delay.
- **AI disclosure:** rewritten January 2026 — disclose generated content (game, store page, marketing) and live generative features; ordinary AI development tools are exempt.
- **Regional pricing + a 10–15% launch discount** are standard. Launch Tuesday–Thursday. The first ~50 reviews set the store label.

## 2.7 Shipping tips

1. Finish something small first. A shipped 2-hour game beats an unshipped 40-hour one.
2. Reuse aggressively — one modular kit can carry a whole game's art.
3. Build the vertical slice early; it tells you the truth about scope.
4. Playtest with strangers.
5. Market from day one: devlog, short clips, genre communities.
6. Budget ~20% of time for polish and ~10% for launch.
7. Cut scope, not quality.
8. Ship, then iterate.

---

# Part 3 — Skills, Tools, and Setup for ChatGPT and Claude

> All product facts below are **[volatile]** and dated October 2026. Model names and feature availability change monthly.

## 3.0 Read this first: two primitives, one urgent deadline

If you remember only three things from this part:

1. **Agent Skills** are the portable unit of expertise. One `SKILL.md` folder works in Claude, ChatGPT, Codex, and Claude Code.
2. **MCP** is the portable unit of access. One server exposes the same tools to every client.
3. **Urgent, dated:** OpenAI stops accepting **new** Custom GPTs on **26 October 2026**, and Custom GPTs retire on **11 December 2026**. Migrate anything you depend on now — and expect custom Actions to be a manual rebuild.

Everything else in this part is detail hanging off those three facts.

## 3.1 The big structural story: skills are now a shared standard

**Agent Skills** started at Anthropic and became an **open standard**: a folder with a `SKILL.md` file (YAML `name` + `description`, then Markdown instructions), optionally bundling `scripts/`, `references/`, and `assets/`. Loading is by **progressive disclosure**:

1. **Discovery** — only name + description are loaded at startup (~100 tokens per skill).
2. **Activation** — full `SKILL.md` is read when a task matches.
3. **Execution** — bundled scripts/references load only when needed.

The spec lives at **agentskills.io** and is supported by a growing list of clients. **OpenAI adopted the same format** — ChatGPT skills are SKILL.md-based too, and one plugin directory serves ChatGPT and Codex.

A **plugin** (in the OpenAI sense) = skills + an MCP server + optional UI + optional lifecycle hooks. It is the packaging layer around skills, not a separate concept.

**Where skills live**

| Client | Path |
|---|---|
| Claude Code (personal) | `~/.claude/skills/` |
| Claude Code (project) | `.claude/skills/` |
| Claude.ai / Cowork | uploaded, or synced from plugins |
| ChatGPT / Codex | `$HOME/.agents/skills/` and workspace skill libraries |
| ChatGPT UI | **Plugins → Skills** tab (installed / created / shared) |

**Skill vs MCP vs sub-agent**

| Thing | Answers | Example |
|---|---|---|
| **Skill** | *How* to do it | "How we format a client report" |
| **MCP server** | *Access* to it | "Query the Postgres database" |
| **Sub-agent** | *Who* does it | "A researcher with its own context" |

Usually the right design is a **skill that uses an MCP server**, run by a sub-agent.

## 3.2 ChatGPT — current capability map [volatile]

| Capability | What it is | Power-user move |
|---|---|---|
| **GPT-6 family** (Astra / Sol / Luna) | Current model family; effort levels from Instant to Extra High | Match effort to task; don't default to max |
| **GPT-6.1 Sol** | Stronger model for Work and Codex | Use for agentic coding and long tasks |
| **Chat / Work / Codex split** | Desktop app has three modes | Chat for questions, Work for deliverables, Codex for repos |
| **Space** | Replaces Library; groups Pages, files, project work; shared collaboration | One Space per project |
| **Pages & Sites** | Living docs; Sites turns work into a shareable website/app | Publish a dashboard instead of a doc |
| **Plugins + Plugin Directory** | Packages skills + connected apps + app templates | Install few, high-value plugins |
| **Skills** | SKILL.md workflows; `skill-creator` included; Create with chat / editor / upload | Build one skill per recurring task |
| **Plugin Creator** | `@plugin-creator` builds a plugin from a description | Bundle a skill + the apps it needs |
| **Projects** | Persistent instructions + files; project-only memory option | One per domain; short instructions |
| **Memory** | Cross-chat facts; project-scoped option | Prune regularly |
| **Custom Instructions** | Global style/context; limit raised to 5,000 chars (Jul 2026) | Keep to a few lines; detail belongs in projects |
| **Deep Research** | Multi-source reports | Constrain sources and scope |
| **Codex** (desktop, cloud, CLI) | Coding agent; Code Review, Security Cloud, multi-repo | `AGENTS.md`, tests, plan before edit |
| **Dots** | Always-on agents with their own cloud computer, working between conversations | Delegate monitoring/ongoing work |
| **Scheduled tasks / automations** | Run on a schedule or app event | Daily summaries, watch tasks |
| **ChatGPT Images** | Image generation/editing | Style references, iterate |
| **Voice (GPT-Live)** | Natural turn-taking; works with plugins; Voice in Work | Hands-free drafting |
| **ChatGPT for Word/Excel/PowerPoint** | Office add-ins sharing context | Edit in place |
| **Sites** | Hosted pages/apps from Work | Internal dashboards |
| **Atlas** | **Retired 9 Aug 2026** — browser folded into the desktop app | Don't plan around it |
| **Custom GPTs** | **Retiring 11 Dec 2026** (Enterprise deferral 11 Feb 2027); **new creation ends 26 Oct 2026** | Migrate to plugins now |

**Custom GPT → Plugin migration (important)**
- Path: **My GPTs → Migrate to plugin.**
- Instructions → **skill**; knowledge files → **reference files**; connected apps → **apps**.
- **Custom actions do NOT transfer.** Rebuild them as an MCP server/app.
- Sharing does not carry over; the migrated plugin starts private.
- The selected model does not carry over.

Also retired or retiring: **Atlas** (gone Aug 2026), **Sora consumer** (shut down 2026, reports), **AgentKit Agent Builder + Evals** (wind down 30 Nov 2026 — the path is the Agents SDK or Workspace Agents), and the **DALL·E GPT** (retired Aug 2026; use ChatGPT Images).

## 3.3 Claude — current capability map [volatile]

| Capability | What it is | Power-user move |
|---|---|---|
| **Claude Fable 5.1** | Frontier model for demanding reasoning and long-horizon agentic work; $10/$50 per MTok; 1M context | Reserve for the hardest work |
| **Claude Opus 5.5** | Default recommendation for most workloads; $4/$20; 1M context | Start here |
| **Claude Sonnet 5.5** | Best speed/intelligence balance; $2/$10 | High-volume agent work |
| **Claude Haiku 5.5** | Cheapest/fastest; from $0.10/$0.50 | Classification, extraction, routing |
| **Adaptive thinking + effort** | Thinking always available; effort levels | Raise effort only when evals justify it |
| **Cowork (merged into chat)** | Agentic knowledge work in any conversation; local/cloud; scheduled tasks | Hand over whole deliverables |
| **Artifacts / Design / Slides / Docs** | Live documents, decks, designs, editable canvases | Iterate in place, not in chat |
| **Claude Code** | CLI, IDE, web; agent teams, dynamic workflows, worktrees, hooks, scheduled tasks, headless | `CLAUDE.md` + tests + plan mode |
| **Agent Skills** | SKILL.md standard; slash commands merged into skills | Install 3–5 that match your work |
| **Plugins + directory** | Bundle skills + connectors + agents; submit via developer portal (Sep 2026) | Prefer plugins over ad-hoc setup |
| **MCP connectors** | External tools/data; interactive connectors on mobile | Filesystem + one real data source |
| **Computer use** | GUI automation in Cowork / Claude Code | Sandbox + supervise |
| **Claude for Excel / PowerPoint** | Add-ins sharing conversation context; support skills | Spreadsheet/deck work in place |
| **Claude in Chrome** | Browser agent | Separate profile |
| **Memory** | Categorized entries, editable under Settings → Memory; on by default for consumer plans | Prune; exclude sensitive topics |
| **API:** prompt caching, batch, Files API, citations | Cost/latency/grounding | Cache stable prefixes |

## 3.4 Agent Skills in depth

```
my-skill/
├── SKILL.md          # required: name + description + instructions
├── scripts/          # optional: deterministic helpers
├── references/       # optional: docs loaded on demand
└── assets/           # optional: templates, fonts, images
```

**Writing a skill that actually triggers**
- The `description` must say **when** to use it, not just what it is. This is the retrieval key.
- Keep `SKILL.md` under ~500 lines; push detail into `references/`.
- Include one worked example and one "don't do this."
- Scripts should print machine-readable output and fail loudly.
- Version and test it like code.

**Where to get skills**
- Official: `github.com/anthropics/skills`
- Standard + spec: `agentskills.io`
- Curated lists: `github.com/travisvn/awesome-claude-skills`, `github.com/kenryu42/awesome-claude-skills`
- ChatGPT: **Plugins → Skills** tab (installed / created / shared), or upload a folder/zip
- Claude Code: `.claude/skills/` (project) or `~/.claude/skills/` (personal)
- Cowork/desktop: Customize section groups skills, plugins, connectors

**Safety:** uploaded skills are scanned in ChatGPT (some marked Needs Review/Blocked); Claude Enterprise offers skill/plugin security scanning. Review any third-party skill — it can contain code.

## 3.5 Claude Code power features

| Feature | What it does |
|---|---|
| `CLAUDE.md` | Project memory: conventions, commands, gotchas. Keep < 300 lines. |
| **Subagents / agent teams** | Specialized workers and parallel teams |
| **Dynamic workflows** | Orchestrate many subagents at scale |
| **Hooks** | Shell commands on events — lint, format, guardrails |
| **Skills** | Replaces slash commands; same SKILL.md format |
| **Plugins** | Bundle skills + agents + hooks + MCP |
| **Plan mode** | Read-only exploration before edits |
| **Worktrees** | Isolate parallel sessions |
| **Scheduled tasks / headless** | `claude -p` for CI and cron |
| **Checkpoints** | Roll back file changes |

## 3.6 MCP setup

High-value servers: **filesystem** (scoped), **GitHub**, **browser/Playwright**, **Postgres/SQLite** (read-only), **Drive/Notion/Slack**, **memory**.

Setup path: install the server → add to the client config → restart → verify the tool list. Claude Desktop uses `claude_desktop_config.json`; Claude Code uses `claude mcp add`; ChatGPT uses **Settings → Plugins/Connected apps** and custom MCP for plugins.

**Rules:** least privilege, scoped directories, read-only by default, review before running, never put secrets in prompts.

## 3.7 What transfers between platforms

| Transfers | Doesn't transfer |
|---|---|
| SKILL.md skills (now a shared standard) | Custom GPT Actions (retired with GPTs) |
| MCP servers | Platform-specific memory contents |
| Clear task framing + done criteria | Projects (different implementations) |
| Output schemas / JSON | Deep Research grounding behavior |
| Few-shot examples | Canvas vs Artifacts specifics |
| Eval rubrics | Model picker / effort semantics |

## 3.8 Prioritized learning path (30 days)

**Week 1 — Foundations**
- Write one reusable prompt template: role / goal / rules / output.
- Set up one Project in each platform for your top domain.
- Turn on memory; write short custom instructions; prune memory.

**Week 2 — Tools**
- Install 2 MCP servers (filesystem + one real data source).
- Build **one skill** (SKILL.md) for a task you repeat weekly.
- Try Deep Research with a constrained source list.

**Week 3 — Agents**
- Use Codex or Claude Code on a real repo; write `AGENTS.md` / `CLAUDE.md`.
- Try plan mode, then a sub-agent or agent team on a scoped task.
- Build a 10-task golden set; score the outputs.

**Week 4 — Systemize**
- Automate one recurring workflow (scheduled task or headless script).
- Assemble a personal library: prompts, skills, templates, checklists.
- Review cost and prune anything that doesn't earn its keep.

## 3.9 Highest-leverage skills (ranked)

1. **Clear task specification** — define done, constraints, format.
2. **Context curation** — supply the right 5%, nothing else.
3. **Verification habits** — never trust; check with a tool.
4. **Skill authoring** — turn repeatable work into SKILL.md.
5. **MCP setup** — connect real data safely.
6. **Eval discipline** — measure, don't vibe.
7. **Decomposition** — split until each piece is easy.
8. **Cost awareness** — cache, route, batch.
9. **Security hygiene** — least privilege, review code, no secrets.
10. **Taste** — knowing what "good" looks like.

## 3.10 Side-by-side

| Need | ChatGPT | Claude |
|---|---|---|
| Frontier reasoning | GPT-6 Astra / Pro | Fable 5.1 |
| Everyday default | GPT-6 Sol | Opus 5.5 |
| Cheap high-volume | GPT-6 Luna | Haiku 5.5 |
| Agentic coding | Codex (desktop/cloud/CLI) | Claude Code (strong) |
| Reusable procedures | Skills + Plugins | Skills + Plugins |
| Live documents | Pages / Space / Sites | Artifacts / Design / Slides / Docs |
| Deep research | Deep Research | Research + citations |
| Always-on agents | Dots | Cowork scheduled tasks |
| Office add-ins | Word, Excel, PowerPoint | Excel, PowerPoint |
| Tool ecosystem | Plugins + connected apps + MCP | Connectors/MCP (originator) |
| Images/video | ChatGPT Images (strong) | Limited |
| Long-form writing | Strong | Strong (often preferred) |

---

# Appendix A — Source list

**Agent engineering**
- Context engineering: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Building effective agents: https://www.anthropic.com/research/building-effective-agents
- Writing tools for agents: https://www.anthropic.com/engineering/writing-tools-for-agents
- Multi-agent research system: https://www.anthropic.com/engineering/multi-agent-research-system
- Harness design for long-running apps: https://www.anthropic.com/engineering/harness-design-long-running-apps
- Scaling managed agents: https://www.anthropic.com/engineering/scaling-managed-agents
- MCP spec: https://modelcontextprotocol.io
- Context rot: https://research.trychroma.com/context-rot
- Lost in the Middle: https://arxiv.org/abs/2307.03172
- ReAct: https://arxiv.org/abs/2210.03629
- Reflexion: https://arxiv.org/abs/2303.11366
- Anthropic, advanced tool use: https://www.anthropic.com/engineering/advanced-tool-use
- Anthropic, demystifying evals: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Anthropic, prompt caching: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- OpenAI, prompt caching: https://developers.openai.com/api/docs/guides/prompt-caching
- OpenAI, structured outputs: https://openai.com/index/introducing-structured-outputs-in-the-api/
- Manus, context engineering lessons: https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- RouteLLM: https://arxiv.org/abs/2406.18665
- FrugalGPT: https://arxiv.org/abs/2305.05176
- 12-Factor Agents: https://github.com/humanlayer/12-factor-agents

**Game dev**
- Godot 4.6: https://godotengine.org/download/archive/4.6-stable/
- Unity 6.3 LTS: https://docs.unity3d.com/Manual/WhatsNewUnity63.html
- Unity pricing/support: https://unity.com/releases/unity-6/support
- Unity Runtime Fee canceled: https://unity.com/blog/unity-is-canceling-the-runtime-fee
- Unreal 5.7: https://www.unrealengine.com/news/unreal-engine-5-7-is-now-available
- Unreal license: https://www.unrealengine.com/license
- GameMaker pricing: https://gamemaker.io/en/get
- Fab licensing: https://dev.epicgames.com/documentation/en-us/fab/licenses
- Steamworks: https://partner.steamgames.com
- Steam Next Fest (Oct 2026): https://partner.steamgames.com/doc/marketing/upcoming_events/nextfest/2026october
- Steam store assets: https://partner.steamgames.com/doc/store/assets
- Steam AI disclosure: https://partner.steamgames.com/doc/gettingstarted/ai

**Assets**
- Kenney https://kenney.nl · Quaternius https://quaternius.com · Poly Pizza https://poly.pizza
- Poly Haven https://polyhaven.com · ambientCG https://ambientcg.com · Texture Ninja https://texture.ninja
- Mixamo https://mixamo.com · Sketchfab https://sketchfab.com · Fab https://fab.com
- Unity Asset Store https://assetstore.unity.com · itch.io https://itch.io/game-assets
- OpenGameArt https://opengameart.org · CraftPix https://craftpix.net
- Sonniss https://sonniss.com/gameaudiogdc · Freesound https://freesound.org
- game-icons.net https://game-icons.net · Lospec https://lospec.com

**AI platforms**
- Agent Skills standard: https://agentskills.io
- Anthropic skills repo: https://github.com/anthropics/skills
- awesome-claude-skills: https://github.com/travisvn/awesome-claude-skills
- Claude docs: https://platform.claude.com/docs
- Claude release notes: https://support.claude.com/en/articles/12138966-release-notes
- Claude Code docs: https://code.claude.com/docs
- ChatGPT release notes: https://help.openai.com/en/articles/6825453-chatgpt-release-notes
- Skills in ChatGPT: https://help.openai.com/en/articles/20001066
- Plugins in ChatGPT: https://help.openai.com/en/articles/20001256
- Custom GPT retirement FAQ: https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq
- Atlas retirement: https://help.openai.com/en/articles/20001371-chatgpt-atlas-retirement
- OpenAI docs: https://platform.openai.com/docs
- OpenAI cookbook: https://cookbook.openai.com

---

# Appendix B — The 12 rules

1. Context is a budget — spend it on signal.
2. Define "done" as a testable condition.
3. The simplest workflow that passes evals wins.
4. Separate the maker from the judge.
5. Verify with tools, not self-report.
6. Tools are the product — design them like an API.
7. Evals before eloquence.
8. Sub-agents buy breadth, not magic.
9. Cache, route, batch — or pay 3×.
10. Skills are the portable unit of expertise now.
11. Ship small games; polish beats scope.
12. Read the license before you ship.
