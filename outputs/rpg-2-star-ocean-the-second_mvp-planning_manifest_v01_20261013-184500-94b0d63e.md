# RPG MVP planning assets

Created 2026-10-13. The in-app side panel is at <http://127.0.0.1:18724/> while the local widget server is running.

| Purpose | File |
|---|---|
| Full MVP plan and acceptance criteria | `rpg-2-star-ocean-the-second_mvp-implementation-plan_v01_20261013-183550-0f7c4d21.md` |
| Durable step status, evidence, and blockers | `rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json` |
| Right-side panel display | `rpg-2-star-ocean-the-second_mvp-progress_widget_v01_20261013-183804-531ac0f2.html` |
| Local server (in `../work/`) | `rpg-2-star-ocean-the-second_mvp-widget-server_v01_20261013-183804-8e4d90a7.js` |

## Progress protocol

The plan is authoritative for scope and acceptance. At the start of each step, set its JSON status to `in_progress`; after implementation, set `review` while checking the acceptance criteria. Mark `done` only after recording concrete evidence in that step's `evidence` array. Set `currentStep` to the next incomplete step and update `updatedAt`. The widget reads the JSON every eight seconds, so the same panel follows the whole project.

The widget is a local view; the JSON file is the lasting progress record. If the local server is no longer running, restart the Node script above and reopen <http://127.0.0.1:18724/> in the Codex side panel.
