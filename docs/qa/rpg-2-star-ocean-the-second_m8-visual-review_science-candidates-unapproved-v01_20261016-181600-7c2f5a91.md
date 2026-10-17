# M8 visual review — science candidate set (unapproved)

Reviewed at the game's 640×360 presentation scale on 2026-10-16. This is Codex visual judgment of captured Godot frames, not creator acceptance. The completion meter and art counters do not change.

## New York City Hall Park v04

Capture: `outputs/nyc-chp-v04_20261016-172144-eb092a52/rpg-2-star-ocean-the-second_nyc-city-hall-park_godot-render-640x360-axis-test-npc_unapproved-v04_20261016-172144-eb092a52.png`.

The central path, City Hall silhouette, fountain, surrounding streets, planted beds, and visitors remain readable at 640×360. The fountain and pavement have more internal pixel structure than earlier candidates. The scene currently reads as a compact formal garden with a generic City Hall facade. The fountain appears much simpler than the historic Jacob Wrey Mould fountain; the park's distinctive central promenade and gardens are supported by [NYC Parks' history](https://nycgovparks.org/about/history/before-they-were-parks/manhattan). For the next candidate, prioritize the landmark's silhouette and ornamental fountain shape over more small flowers or pavement noise. The facades, mature trees, and visitor clothing should show a consistent 2537 science-civilization visual language. Keep all new figures explicitly test-only until identity and scene art review.

Against the creator's [Wandering Sword quality reference](https://store.steampowered.com/app/1876890/Wandering_Sword/), the present shot has readable authored pixels but less depth from lighting, material changes and overlapping architectural layers. That comparison concerns finish and density; preserve this project's approved top-down exploration camera and its own setting.

A 2026-10-16 image edit of the v04 Godot capture was visually rejected as a transfer reference. It preserved the broad path/fountain/City Hall arrangement, but added an elevated viaduct, aircraft and cupola ornament, changed the protagonist and visitors, and replaced authored pixel clusters with continuous generated detail. None of those changes has been approved for this landmark. The image remains only in the tool's internal generated-image store; it is not a project asset or runtime candidate. Continue from the actual v04 capture and the site-specific silhouette/fountain notes above.

## Washington Capitol west grounds v08

Captures: `outputs/wdc-cw-v08_20261016-155827-6cf49486/rpg-2-star-ocean-the-second_wdc-capitol-west_godot-640x360-entry_unapproved-v08_20261016-155827-6cf49486.png` and `...vista_unapproved-v08_20261016-155827-6cf49486.png` in the same folder.

The Capitol dome, west steps, terraces, central path, survey equipment, and patrol machine are identifiable. The path has convincing broken pavement and the immediate foreground has dense overgrowth. The building reads mostly intact because its centerline, dome, facade rhythm, and west terraces are uniformly clean. The creator approved a recognizable but partly collapsed, vegetation-invaded Capitol in an abandoned city. In the next pass, concentrate damage on one or two distinct facade sections and let vegetation visibly interrupt masonry or architectural edges; adding more loose rubble to the foreground alone will not communicate structural collapse. Increase contrast between the survey camp and the patrol machine: the dark craft at right presently competes with the building, while small survey objects at left are hard to read at gameplay scale. [Architect of the Capitol's grounds overview](https://www.aoc.gov/explore-capitol-campus/buildings-grounds) and [west terrace reference](https://www.aoc.gov/explore-capitol-campus/buildings-grounds/capitol-grounds/olmsted-terrace) provide the site-specific architectural landmarks. Do not replace pixel authored layers with a continuous-color concept image.

## Global map art v02

Captures: `outputs/rpg-2-star-ocean-the-second_global-map-art_us-northeast-zh-640x360-candidate_candidate-unapproved-v02_20261016-172153-ab9459d4.png` and `outputs/rpg-2-star-ocean-the-second_global-map-art_us-great-lakes-card-chicago-air-zh-640x360-candidate_candidate-unapproved-v02_20261016-172153-ab9459d4.png`.

The Northeast coast, Great Lakes, mode, whole-hour travel duration, and route card are legible. At 640×360 the New York and Yonkers label boxes visually crowd one another; the large Chicago route card leaves little geographic context, and its flight line is nearly lost under the overlay. Prioritize marker hierarchy, label collision handling, and route visibility during preview. The map does not need more geographic micro-detail before those interaction problems are solved. This is a functional art candidate, not an accepted world-map style.

## Female protagonist battle static v10

Capture: `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-ruins-640_unapproved-v10_20261016-162819-de44e59a.png`.

The owner approved only the 0.65 battle display proportion. In the four-person 640×360 frame, the teal scarf and forward-facing profile differentiate the heroine, but her far arm, rear coat and pack/bedroll shapes merge into the party silhouettes. The party as a whole has simpler shading and surface detail than the ruin arena. Refine the heroine's readable arm-to-torso gap and distinct back-silhouette first, then review the full team against a battle background at native gameplay size. Do not start a full attack animation batch from this static frame yet.

## Publication and acceptance

The private Game Bible Site displayed commit `a87ac16` and 35.8% on this review. Its character preview gallery still presents older battle v08 and Liang Xu v01 candidates. New captures above exist locally and are not a cross-device review packet until deliberately synced and added to the private gallery. Show each candidate with a clear **unapproved / nonruntime** caption. Art counters remain runtime sprites **0/52**, scene visuals **0/11**, and human post-art playtests **0/2**.

Recommended cross-device review order once verified images are selectively synced:

1. **NYC City Hall Park v04:** “Walkable 640×360 scene candidate. Landmark composition and fountain still need refinement; unapproved and not integrated.” Use the axis capture above.
2. **Washington Capitol west v08:** “Walkable 640×360 ruins candidate. The building is recognizable, but structural damage and survey-camp clarity need work; unapproved and not integrated.” Use the entry capture above.
3. **Global map v02:** “640×360 interactive-map art candidate. Labels and the Chicago route preview need legibility work; unapproved and not integrated.” Use the Northeast and Chicago captures above as two separate pictures.
4. **Female battle static v10:** “Four-person 640×360 battle proportion candidate. Only display scale was approved; character art and animation remain unapproved.” Use the party capture above.

Do not overwrite older review evidence in place; add these as dated candidate records. Each separate picture needs an independent caption and an immutable commit-pinned image URL. The private audience must remain unchanged.
