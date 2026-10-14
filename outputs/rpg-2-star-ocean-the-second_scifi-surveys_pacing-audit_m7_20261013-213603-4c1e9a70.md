# M7 science-region pacing audit

Date: 2026-10-13. This is a content and geometry audit, not a timed human playthrough.

## What is playable

- Three freely ordered destinations, each with a two-room survey, three recruit options, two optional machine encounters, and a city report endpoint.
- Each survey has six clues, three evidence pairs to establish, and one final judgment. All text and pair explanations are available in Chinese and English.
- Wrong pairs and judgments can be retried. Pair progress, clues, judgments, and position survive save/load.

## Mechanical lower bound

Survey rooms place clues at `(163,165)`, `(320,165)`, and `(477,165)`. At `140 px/s`, a direct path through the three clues to the next door is approximately 575 px; the corresponding inner-room path to the terminal and exit is approximately 885 px. Across the three destinations, these six room paths total approximately 4,380 px, or **31 seconds of uninterrupted movement**. This excludes surface routes, interaction range, menus, reading, choosing links, battle, and player hesitation.

The survey content source currently contains approximately **1,093 Chinese Han characters and 814 English word tokens**. The English token count includes data keys and identifiers, so it overstates player-facing prose. These are rough source counts, not a reading-speed measurement.

## Decision

The geometry and text alone cannot establish the planned 25–35 minute duration. The nine evidence pairs add reasoning to the existing exploration loop without slowing movement. M7 remains in progress until a fresh, uninterrupted start-to-report run is timed in the actual game, followed by a second run with a different destination and recruit order. Record total time, time spent in each destination, wrong pair attempts, optional fights, and any point where instructions are unclear. Add meaningful content only in response to those observations.
