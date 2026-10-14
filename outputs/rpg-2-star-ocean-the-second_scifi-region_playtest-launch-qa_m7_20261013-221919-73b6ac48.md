# M7 local playtest launch check

Checked on 2026-10-13 at the local game bible on port 18726.

- Before launch, the status endpoint returned `idle`, and no Godot GUI process for this project was running.
- Clicking **开始新档试玩** changed status to `running` and opened the bundled Godot GUI executable with `--path` pointed at this project's `game` directory. Windows reported a visible `Worlds Between (DEBUG)` window.
- The test window was closed without submitting the city report. Status changed to `no_report`; the panel showed the same outcome and remained ready for another launch.
- The receipt list remained empty. This check is not a completed or timed playthrough.
- The older panel on port 18725 showed a disabled launch button and a working link to the current panel on port 18726.

Remaining M7 acceptance: complete two fresh, differently ordered human playthroughs, inspect their recorded duration and friction, then tune content or usability as needed.
