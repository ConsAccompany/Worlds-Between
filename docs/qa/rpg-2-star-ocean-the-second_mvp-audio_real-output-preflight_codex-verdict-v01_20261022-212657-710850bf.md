# Packed MVP audio: real-output technical preflight, listening incomplete

Task `review.content.audio` remains **not complete**. Its frozen criterion is Codex listening to music/sounds in game and recording a verdict. This session can inspect actual rendered PCM, but has no verified listening input; playing/exporting audio is not hearing it. No subjective quality verdict or point is awarded.

Base `f1d2faca0a353cc2d916351eaac69ee8897850bc`; unchanged game source `d5f204373c17c62e45e92dea14c3a2e85c525062`; shipped native PCK SHA-256 `bded12fa9ea7b9db7d12c1078be7d5cfb5e3c72afab5582d70fdfd8c05bd98fe`. All4917 tracked game files remain byte-exact; existing Windows bundle is current. No default audio/art flags changed.

## Work actually performed

Claude supplied a bounded read-only source review (113.703s): no reproducible default-path blocker found; its unverified raw-WAV packaging suspicion was **not accepted as a bug**. The actual themed run loads a50.526s stereo24000Hz city track, contrasting with default8s mono22050Hz ambience. The selector's raw-WAV/hash-validation path succeeds against the shipped PCK; raw WAV export is already handled by the existing raw-input addon.

DeepSeek delivered an unexecuted external scene fixture, then reached its301.062s task deadline (not quota/credit depletion). Codex inspected, repaired and ran it. Fresh isolated profiles, actual city-scene music player, actual GameSettings master-gain path, actual GameAudioCues service with its enable override confined to the test fixture. Editor host runs the exact release PCK with a labeled external SceneTree fixture; this is **not release-EXE external-script support or ordinary-input gameplay**.

Two checked windowed Movie Maker runs capture the final offline Master mix: default city ambience and opt-in themed city music. Each replays matched music from0 at100% and50%, mutes Master while music continues, restores100%, stops music, and plays11 SFX one at a time. Per-cue spacing is max(27frames, actual stream duration rounded up +6frames). Exact voice/resource identity is checked, followed by1s isolated silence. See [official Movie Maker documentation](https://docs.godotengine.org/en/4.7/tutorials/animation/creating_movies.html): offline audio recording is distinct from listening while recording.

Final captures: default `20261022-213747-7b703b9e` and themed `20261022-213747-50466a99`. Both pass bounded checked-runner gates with no script/parser/runtime diagnostics. Independent decoded PCM checks:8/8 each;11/11 cue-to-asset bindings each.100%->50% RMS ratios **0.503272** and **0.500326**. Both Master0% windows are exact zeros; all11 isolated cue windows contain nonzero PCM; no full-scale clipping; final quiet windows exact zero. These establish rendered output and controls, not musical quality, real-time physical-device behavior or approval.

Uncompressed source PCM is decoded using the installed FFmpeg/FFprobe without sample-rate/channel changes, widened from16-bit to32-bit integer WAV without amplification. Decoder `-xerror` succeeds; retained warning is only `Guessed Channel Layout: stereo`. Movie Maker AVI's root RIFF length declaration is70bytes smaller than actual file length; the first custom strict RIFF parser rejected it. No container-validity claim is made. FFmpeg decodes all PCM with no error. Original AVI is local/ignored and hash-bound; final extracted WAVs are committed.

## Material failures retained / corrections

- Producer constant `.size()` was not a GDScript constant expression; first run failed to parse and checked runner stopped promptly. Exact failed source/log retained. Corrected to arithmetic constants.
- Producer initially rejected Movie Maker's `Dummy` audio driver. Actual movie-mode metadata showed the expected offline driver. The false guard was removed while preserving active-movie, non-headless, valid Master and no pre-gain-capture guards; actual PCM, not driver name/playing flag, supplies output evidence. Failed attempt retained.
- First recorded schedule used a fixed0.45s cue spacing, overlapping authored0.56–0.98s clips; its `_playing_voice` could report an earlier cue. Exact-zero final-silence check failed and results remain failed. Corrected the fixture to wait actual duration +6frames, bind the requested event's exact cached stream, then measure a full separate silence phase. Thresholds were not relaxed. No game defect or audio-asset revision was needed.
- Initial custom AVI parser failed on the recorded RIFF length mismatch. Its source/full error retained, then replaced by the installed media decoder. No arbitrary file-length acceptance was inserted into that parser.

## Limitations and queue

Only **city contexts** default/themed plus11 direct-dispatch SFX are covered; other music contexts, whole-track loops, musical mood, balance by ear and physical speaker audition remain unreviewed. The heal sound is presentation-only, not evidence of a healing mechanic. No native movement, battle-input, artistic/default-use or human M9 claim. Prior technical tests are not presented as fresh work.

Ledger `review.content.audio`: blocked for the unmet listening criterion; Codex still owns it. Do not repeatedly recapture this same preflight or request creator approval for it. Continue missing production: Lin Que's complete required four-direction native exploration source package, using existing approved style direction and established reusable pipeline, retaining concept/unapproved identity-source status and no default adoption.

Production **60.3% ->60.3%(+0.0pp)**; performed inspection **21.6% ->21.6%(+0.0pp)**; creator approval **7.8% ->7.8%(+0.0pp)**. No frozen points/denominators changed; formal acceptance false. Evidence: `outputs/audio57/root/rpg-2-star-ocean-the-second_audio57_technical-closeout-proof_v01_20261022-212657-710850bf.json` and its linked final PCM verdicts/source snapshots/logs.
