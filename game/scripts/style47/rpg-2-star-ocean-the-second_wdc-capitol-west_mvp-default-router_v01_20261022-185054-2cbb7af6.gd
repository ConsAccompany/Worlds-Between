extends "res://scripts/style45/rpg-2-star-ocean-the-second_wdc-capitol-west_style45-router_unapproved-v01_20261022-182109-a780b895.gd"
# Creator-authorized ordinary MVP default; final art acceptance remains separate.
# Keep the STYLE45 native source/router immutable and retain explicit older/rollback precedence.
static func ordinary_default_requested() -> bool:
 var args:=OS.get_cmdline_user_args()
 if args.has(STYLE45_FLAG):return false
 if v13_override>=0 or r2_override>=0 or r1_override>=0 or v12_override>=0:return false
 for flag in [V13_FLAG,R2_FLAG,R1_FLAG,V12_FLAG]:
  if args.has(flag):return false
 return SceneDefaults35.default_on(SceneDefaults35.RUINS)
func _ready() -> void:
 if not ordinary_default_requested() or AppState.current_destination_id!="scifi.ruins":
  super()
  return
 style45_active=true
 var saved:=v13_override
 v13_override=1
 super()
 v13_override=saved
 style45_active=v13_active
