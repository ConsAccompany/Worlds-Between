extends SceneTree
# Separate-profile preview entry (run it with APPDATA/LOCALAPPDATA pointed at a dedicated profile directory, as the
# zpath27/lpath30 launchers do). Ji remains the real recruitable companion at scifi.ruins (records console first), not the
# hero; the Ji default stays OFF until separate creator authorization.
const Config = preload("res://scripts/jpath33/rpg-2-star-ocean-the-second_ji-playable-path_config_opt-in-v01_20261021-222438-7d4b2e91.gd")
func _initialize() -> void:
 call_deferred("run")
func argument(prefix: String, fallback: String) -> String:
 for value in OS.get_cmdline_user_args():
  if value.begins_with(prefix): return value.trim_prefix(prefix)
 return fallback
func refuse(reason: String) -> void:
 Config.rollback()
 print("JPATH33_PLAYABLE_REFUSED ",reason)
 quit(1)
func run() -> void:
 var profile := OS.get_environment("WB_JPATH33_PROFILE").replace("\\", "/").trim_suffix("/")
 var user_dir := ProjectSettings.globalize_path("user://").replace("\\", "/")
 if profile == "" or not profile.contains("/work/jpath33-preview-profiles/") or not user_dir.begins_with(profile + "/"):
  refuse("dedicated jpath33 preview profile required; ordinary saves are protected");return
 var language:=argument("--jpath33-language=","en")
 var appearance:=argument("--jpath33-appearance=","male")
 var result: Dictionary=Config.configure(root.get_node_or_null("AppState"),language,appearance)
 if not result.get("ok",false):
  refuse(result.get("error","package rejected"));return
 if change_scene_to_file(result.scene)!=OK:
  refuse("exploration scene did not open");return
 for i in 600:
  await process_frame
  if current_scene!=null and current_scene.is_node_ready():
   if Config.npc_attached(current_scene):
    print("JPATH33_PLAYABLE_READY language=%s appearance=%s"%[language,appearance])
    return
   current_scene.hide()
   refuse("Ji recruit NPC package did not attach");return
 refuse("exploration readiness deadline")
