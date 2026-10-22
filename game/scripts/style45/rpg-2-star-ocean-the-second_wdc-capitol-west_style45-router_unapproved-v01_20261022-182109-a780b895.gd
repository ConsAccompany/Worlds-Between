extends "res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v13_20261018-135539-63201688.gd"

# Washington, D.C. ruins (scifi.ruins): STYLE45 common-style candidate router (UNAPPROVED; art not accepted, not a default).
# Off unless `-- --wdc-common-style45` is given. Without it, _ready() and _v12_path() hand straight to the v13
# selector, so every existing flag, override and the sdef35 default policy behave exactly as before.
# With the flag and AppState.current_destination_id == "scifi.ruins", v13 (and through it v12r2/v12r1/v12) is forced
# on for this _ready() only (v13_override is restored afterwards), and the base, the foreground and the four Y-sorted
# textures come from game/assets/environments/style45/. The walk mask stays the original v12 rt-walk file; camera,
# movement, interactions, dialogue, save, battle and return are the selector's own code. Cmdline args persist, so the
# flag also applies when the scene reloads on a real battle return.
# Art: generated style43 reference NEAREST-sampled to 640x360 and cut by the old binary masks (generated raster, no
# hand pixel art); old v13 rt-base pixels sit hidden under foreground coverage; silhouette alignment is unproven.
# Source: tools/rpg-2-star-ocean-the-second_wdc-capitol-west_style45-source-assembly_v01_20261022-182109-a780b895.py
# To remove: point game/scenes/scifi_exploration_area.tscn back at the v13 selector.

const STYLE45_FLAG := "--wdc-common-style45"
const STYLE45_TEXTURES := {
	"rt-base": "res://assets/environments/style45/rpg-2-star-ocean-the-second_wdc-capitol-west_style45-rt-base_unapproved-v01_20261022-182109-a780b895.png",
	"rt-ys-mast": "res://assets/environments/style45/rpg-2-star-ocean-the-second_wdc-capitol-west_style45-rt-ys-mast_unapproved-v01_20261022-182109-a780b895.png",
	"rt-ys-tripod": "res://assets/environments/style45/rpg-2-star-ocean-the-second_wdc-capitol-west_style45-rt-ys-tripod_unapproved-v01_20261022-182109-a780b895.png",
	"rt-ys-beacon": "res://assets/environments/style45/rpg-2-star-ocean-the-second_wdc-capitol-west_style45-rt-ys-beacon_unapproved-v01_20261022-182109-a780b895.png",
	"rt-ys-elm": "res://assets/environments/style45/rpg-2-star-ocean-the-second_wdc-capitol-west_style45-rt-ys-elm_unapproved-v01_20261022-182109-a780b895.png",
	"rt-fg": "res://assets/environments/style45/rpg-2-star-ocean-the-second_wdc-capitol-west_style45-rt-fg_unapproved-v01_20261022-182109-a780b895.png",
}

var style45_active := false


func _ready() -> void:
	if not (OS.get_cmdline_user_args().has(STYLE45_FLAG) and AppState.current_destination_id == "scifi.ruins"):
		super()
		return
	style45_active = true
	var saved := v13_override
	v13_override = 1
	super()
	v13_override = saved
	style45_active = v13_active


func _v12_path(purpose: String) -> String:
	if style45_active and STYLE45_TEXTURES.has(purpose):
		return String(STYLE45_TEXTURES[purpose])
	return super(purpose)
