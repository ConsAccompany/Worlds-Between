extends SceneTree
func sha256(bytes: PackedByteArray) -> String:
    var ctx := HashingContext.new()
    ctx.start(HashingContext.HASH_SHA256)
    ctx.update(bytes)
    return ctx.finish().hex_encode()
func _initialize() -> void:
    call_deferred("_run")
func _run() -> void:
    var png := "res://assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png"
    var pxo := "res://assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-editable_unapproved-v01_20261018-090713-99e861ce.pxo"
    assert(FileAccess.file_exists(png))
    assert(FileAccess.get_sha256(png) == "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd")
    var raw := Image.load_from_file(ProjectSettings.globalize_path(png))
    assert(raw != null)
    raw.convert(Image.FORMAT_RGBA8)
    assert(sha256(raw.get_data()) == "2f2e742e3611e662c33f2a3fb2590f69ac2792b276a6c3fc5d5c2ff500d306ae")
    var texture := load(png) as Texture2D
    assert(texture != null)
    var imported := texture.get_image()
    imported.convert(Image.FORMAT_RGBA8)
    assert(sha256(imported.get_data()) == "748e411b01ec04716c34dbaa774d9cfa77b8e1b0249a74f3614a34e19b9ab531")
    var zip := ZIPReader.new()
    assert(zip.open(pxo) == OK)
    var data_size := zip.read_file("data.json").size()
    zip.close()
    assert(zip.open(ProjectSettings.globalize_path(pxo)) == OK)
    assert(zip.read_file("data.json").size() == data_size)
    zip.close()
    print("PACK_RAW_PNG_PLUGIN "+JSON.stringify({"rawPngSha256":FileAccess.get_sha256(png),"rawPngBytes":FileAccess.get_file_as_bytes(png).size(),"rawRgbaSha256":sha256(raw.get_data()),"resourceRgbaSha256":sha256(imported.get_data()),"resourceUnchanged":true,"globalizedImageLoad":true,"zipResAndGlobalized":true,"pxoDataJsonBytes":data_size}))
    var script_path := "res://scripts/growth_screen.gd"
    assert(FileAccess.file_exists(script_path))
    assert(FileAccess.get_sha256(script_path) == "2c4dca616acf3027a171ca8f5c53307e3edb7f8113b76622ac33c46dceded91f")
    var raw_script := FileAccess.get_file_as_string(script_path)
    assert(sha256(raw_script.replace("\r\n", "\n").to_utf8_buffer()) == "2c4dca616acf3027a171ca8f5c53307e3edb7f8113b76622ac33c46dceded91f")
    var gdscript := load(script_path) as GDScript
    assert(gdscript != null)
    var remap_path := script_path + ".remap"
    var remap := FileAccess.get_file_as_string(remap_path) if FileAccess.file_exists(remap_path) else ""
    assert(FileAccess.file_exists("res://scripts/growth_screen.gdc"))
    assert(remap.contains("res://scripts/growth_screen.gdc"))
    assert(gdscript.can_instantiate())
    assert(gdscript.get_source_code().is_empty())
    var manifest_path := "res://assets/ui/battle-skin-v01/rpg-2-star-ocean-the-second_battle-ui_asset-manifest_skin-v01_20261019-171056-ca4652ec.json"
    assert(FileAccess.file_exists(manifest_path))
    assert(FileAccess.get_sha256(manifest_path) == "545c0e25368a15061ee9b1cb8fca3f4c796907d43eecbcaa0c6e35bed221a504")
    root.size = Vector2i(640,360)
    var app := root.get_node("AppState")
    app.begin_new_run()
    app.hero_appearance = "female"
    var scene := load("res://scenes/growth_screen.tscn") as PackedScene
    assert(scene != null)
    var screen := scene.instantiate()
    root.add_child(screen)
    current_scene = screen
    await process_frame
    await process_frame
    assert(screen.title_label != null and not screen.title_label.text.is_empty())
    assert(screen.back_button != null and screen.member_buttons.size() == 5)
    print("PACK_HELPER_DIAG "+JSON.stringify({"managementStatus":screen.management_ui_skin_status,"managementError":screen.management_ui_skin.last_error if screen.management_ui_skin != null else "not installed","mvpStatus":screen.mvp_display_portraits.status if screen.mvp_display_portraits != null else "not installed","mvpRefusal":screen.mvp_display_portraits.refusal_reason if screen.mvp_display_portraits != null else "not installed"}))
    assert(screen.management_ui_skin_status == "applied")
    assert(screen.mvp_display_portraits != null and screen.mvp_display_portraits.visible)
    assert(screen.mvp_display_portraits.get_active_variant() == "protagonist-female")
    var selector := load("res://scripts/audio/rpg-2-star-ocean-the-second_themed-music_selector_v01_20261019-212037-7f3c2a26.gd") as GDScript
    var stream: AudioStreamWAV = selector.select("city",1)
    assert(stream != null)
    var wav_path := "res://assets/music/themed-v01/rpg-2-star-ocean-the-second_city-dawn-inquiry_audio_v01_20261019-212037-7f3c2a26.wav"
    assert(FileAccess.file_exists(wav_path))
    print("PACK_COMPLETE_RAW_BOUNDARY "+JSON.stringify({"rawScriptSha256":FileAccess.get_sha256(script_path),"rawScriptCharacters":raw_script.length(),"scriptResourcePath":gdscript.resource_path,"scriptResourceSourceLength":gdscript.get_source_code().length(),"scriptRemapPresent":not remap.is_empty(),"scriptRemapText":remap,"rawUiManifestSha256":FileAccess.get_sha256(manifest_path),"growthSceneInstantiated":true,"growthTitle":screen.title_label.text,"memberButtonCount":screen.member_buttons.size(),"managementApplied":screen.management_ui_skin.applied,"mvpPortraitStatus":screen.mvp_display_portraits.status,"mvpPortraitSize":str(screen.mvp_display_portraits.get_texture_size()),"themedMusicCitySelected":true,"rawWavSha256":FileAccess.get_sha256(wav_path),"musicPcmBytes":stream.data.size(),"musicMixRate":stream.mix_rate}))
    screen.management_ui_skin.revert()
    screen.queue_free()
    await process_frame
    print("PACK_COMPLETE_RAW_BOUNDARY_PROBE_OK")
    quit(0)
