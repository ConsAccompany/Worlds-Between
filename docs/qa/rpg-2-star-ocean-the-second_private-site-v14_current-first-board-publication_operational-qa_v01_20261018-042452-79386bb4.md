# Private Site v14: current-candidates-first board publication (operational QA)

Date: 2026-10-18 04:25 local. This is an operational record only. It accepts no art, changes no gate, and the counters are unchanged: 40.8%, M2 10/12, scenes 3/12, sprites 0/52, playtests 0/2, formal acceptance false.

## Deployment (as reported by root)

- **Deployed source:** private Site source revision `a7e04d00be4d7ee666a3af4792fa4ac27f3dac0c`.
- **Deployment:** `appgdep_6ad47ea356f48191813a55d06ba4616c`, status succeeded.
- **Live UI check:** root inspected the live UI and saw:
  - the current-candidates board appears **before** the collapsed history of nine older previews;
  - 3/3 current images load;
  - 40.8% and scenes 3/12 are unchanged.
- **Follow-up closed:** this closes the follow-up named in the 7370739 handoff, where the Site did not yet consume the repository Bible's current-candidates presentation.

## Public-safe proof

`outputs/rpg-2-star-ocean-the-second_cloud-tracker_current-first-v14-live-proof_v01_20261018-041100-695c8b0e.png`, sha256 `ef40d4f080e8653d92aeb0ebe44149126cd323c17616191a05836d829790f759`.

Claude inspected the image. It shows the production tab with:
- the open-decisions list;
- the **当前候选 / Current candidates** panel: "3 项 · 均未批准 / 3 items · none approved", "3 / 3 张可从 GitHub 查看 / on GitHub", images pinned to GitHub commit `7370739`;
- the bilingual text "40.8%, M2 10/12, scenes 3/12, sprites 0/52 and playtests 0/2 do not change";
- three current cards with their unapproved and art-not-accepted badges: world map v03r2, Yonkers room 1 v03, battle heroine static v12.

The collapsed history section is below the visible area, so the "nine historical previews" figure is root's live observation, not something this image shows. The image contains no account, credential, budget or session data.

## Not included

- Private Site source, deployment logs, controller or session logs, account and budget files.
- No Site URL is recorded here.
