# Audio cue runtime capability

Codex implementation during Max quota depletion, explicitly authorized by creator. No Claude/account spend used.

## Delivered

One reusable AppState audio service, opt-in with `--audio-cues-pilot`, off by default. UI BaseButton press signals trigger a confirmation cue. The normal battle hooks trigger attack-contact, successful dodge, funded guard, damage hit, successful skill, victory and defeat independently of the VFX flag. Rejected dodge/out-of-range contact emits no success cue. Heal is a presentation API with no healing gameplay side effect.

Cached generatedPCM uses a local deterministic generator, no global RNG. Four recycled AudioStreamPlayers cap overlap,40ms coalescing limits repeated events, bounded0.055â€“0.25s envelopes begin/end at zero and peakbelow0.25. All voices route through existingMaster bus, respecting existingvolume/mute settings; UIservicecanplayduringpausedsettings. Sourcesareprovisionalcodedcuefixtures, notfinalaudioart.

## Checks

-42/42headless and43/43windowedchecks pass with noSCRIPT ERROR,ERRORorleak warning. Windowed check proves actualAudioStreamPlayer starts; headless explicitlydoesnotattemptaudibleplayback.
-ActualUIpressed signal and all listednormalcombat eventhooks exercised withVFXOFF; failedactioncounter checks pass.
-DefaultOFFallocatesnostreams/players; unknowncuefallback, cache/pool bounds, deterministicPCM/globalRNGunchanged, volume0mute/50restore, pauseUI andunchangedgamesnapshot checked.
-Normalcombinedcombatloader regressionpasses162checks withaudioenabled, including three600stepcombat/save traces matchingpilotOffandprefeaturebase.
-Rootreviewed actualVFXattackEN/guardZH captures separately. No audio artistic quality or human audition is claimed by these coding checks.

The source-and-check manifest binds the currentservice,AppState,arena andtest hashes with explicitLFnormalization and hashesall finalreports/logs. Task completion is codingcapability only; human/creator sound quality approval remains separate.

Independent Codex source review found no blocking defect. Four-voice recycling may truncate an older cue during dense events; this is a bounded presentation tradeoff, not a game-state change.
