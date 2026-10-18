# Female protagonist four-direction idle loops — produced candidate, unapproved

Task: `content.char.protagonist-female.idle-anim` (fixed 2-point production milestone).

## Scope and art basis

Four 80×112 exploration idle loops use the exact south seloutv8, north, west and east static cells as their first and rest frames. Only the south static has creator approval. All north/west/east art and all idle motion remain unapproved. Pivot(40,104), body rows8–103 and scale0.5 preserve48 logical pixels. No locomotion, combat, default adoption, registry change or full-character completion is claimed.

Each4.8second cycle has **8 unique RGBA poses across12 timed phases**. The four rest phases are byte-identical to their direction's static. Inhale begins with a local coat/chest fold and contour adjustment; shoulder lift follows, then free hair/cloth tips lag. Exhale reverses that order. Authored maximum movement is1 source pixel=0.5 logical pixel; nearest rendering at native640 can quantize that to1 screen pixel. No whole-sprite bob, head translation, skeleton shear, parameter sweep or added gear. Head/pack and all source rows78–111 remain fixed. Directional accessory asymmetry is retained; the west scarf is occluded, so its visible coat tip follows instead of animating the canister band.

An explicit separate `seam-underlay` role restores original static texels at3–5 newly enclosed single-pixel holes found during source-mask inspection. Final48 cells introduce zero new such holes. No timing, amplitude or static frame changed to make that check pass.

## Editable native source

**Primary source: four genuine multiframe Pixelorama PXOs**,12 frames×8 layers (7 visible roles plus hidden locked guide), native fps1 with authored frame durations totaling4.8seconds. Roles are fixed-body, seam-underlay, chest-breath, shoulder-breath, scarf-free-tip, coat-free-tip, pony-free-tip and guides. The existing inspected v06 animated container serializer is reused with exact RGBA cels; no v06 motion controller/art is adopted.

**Supplemental interchange:48 separate layered ORAs**, one per direction/phase. ORA itself is not an animation format; timing lives in the manifest and PXO. Every ORA cell archive is checked against source. Twelve critical ORAs (rest0,crest4,lag7 for each direction) were independently reopened/exported by native Pixelorama. All4 PXOs/12frames/7 visible roles exported exactly, as did all12 critical ORAs. Fresh isolated APPDATA/LOCALAPPDATA were used; no existing user editor was selected or stopped. Native GUI Save As remains unverified.

The strict diagnostic checker is deliberately **34/46**, not46/46: source gates30/30 and primary PXO native gates4/4 pass; supplemental ORA diagnostic-clean gates0/12 fail. Every exported ORA pixel is exact, but Pixelorama emits UI get_child/ancestor/cleanup diagnostics. A fresh hidden windowed run and a grace-exit run reproduce them. Crucially, the unchanged committed WEST ORA control reproduces the same problem. This is a reasoned primary-format scope choice, not a relaxed pixel check. The initial strict30/42 failure report, final34/46 report, verbatim diagnostics and unchanged-WEST control are preserved. See the separate ORA diagnostic supplement; earlier WEST/EAST native export evidence does not establish clean GUI opening/saving.

## Actual normal-speed playback

Godot's actual `AnimatedSprite2D` clock plays the12 timed frames. `play(direction)` deliberately changes south→north→west→east,5.2seconds per direction, without manual frame setting. The ordinary bright-city and dark-room2 scenes instantiate and render in a source-only harness at the shared ground pin. Default hero is hidden only within that harness.

The final deliverable contains two separate640×360 normal1x MP4s: bright English30fps(624frames/1924 mechanical checks) and dark Chinese60fps(1248frames/3796checks), each20.8seconds. Every captured process frame is consecutive and has an asserted1/fps simulation delta. A startup smoothing issue in bright30 was found by the first proof check (four early deltas differed); the harness now warms up before starting native playback and asserts every recorded delta. Original art/timing is unchanged. Recording uses fixed simulation fps and normal video playback rate1; it is not a hardware performance benchmark.

All source-frame hashes and raw capture-frame hashes are retained in reports. Raw624+1248 PNG sequences remain in ignored temporary run directories and are not committed. Twelve separate critical PNGs are included: SOUTH/WEST rest/crest/lag from bright30 and NORTH/EAST rest/crest/lag from dark60. MP4 is lossy H.264; critical PNGs are the exact rendered evidence.

## Visual inspection and limits

Root opened the first actual bright30 movie in a browser:640×360,20.8seconds,readyState4,pausedfalse,playbackRate1 at5.97seconds. Root separately viewed six SOUTH/WEST rest/crest/lag PNGs: planted silhouette/feet stable and local movement subtle, without observable whole-body bob in those sampled poses. Root accepted a produced idle-loop candidate for source review only. This is sampled playback plus critical-pose inspection, **not a continuous-motion quality certification or creator fluidity/art/full-set approval**. Final movies are regenerated after the seam-underlay and clock-start corrections. Root also viewed final dark NORTH rest/crest and EAST rest/lag640 PNGs: static silhouettes, planted feet and local cloth changes remain consistent. The verdict remains produced candidate only, with no art/fluidity approval.

The portable final evidence checker verifies all five tool-source hashes, protected game source against the base Git commit, source/helper/artifact hashes, native results including retained failures, captured reports, video metadata and selected PNGs. It prints package integrity success while explicitly preserving ORA diagnostic-clean failures. No test count is presented as proof of smoothness.

Accepted environments3/12, complete accepted sprites0/52 and human post-art playtests0/2 stay unchanged. No progress ledger or Site is edited by this producer task.
