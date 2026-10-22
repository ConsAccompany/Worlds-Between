extends SceneTree
# Separate-profile preview entry (run it with APPDATA/LOCALAPPDATA pointed at a dedicated profile directory, as the
# zpath27 launcher does). Liang remains the real recruitable companion at scifi.city, not the hero; ordinary MVP default use is creator-authorized.
const Config = preload("res://scripts/lpath30/rpg-2-star-ocean-the-second_liang-playable-path_config_opt-in-v01_20261021-202247-ca439d91.gd")
func _initialize() -> void:
 call_deferred("run")
func argument(prefix: String, fallback: String) -> String:
 for value in OS.get_cmdline_user_args():
  if value.begins_with(prefix): return value.trim_prefix(prefix)
 return fallback
func refuse(reason: String) -> void:
 Config.rollback()
 print("LPATH30_PLAYABLE_REFUSED ",reason)
 quit(1)
func run() -> void:
 var profile := OS.get_environment("WB_LPATH30_PROFILE").replace("\\", "/").trim_suffix("/")
 var user_dir := ProjectSettings.globalize_path("user://").replace("\\", "/")
 if profile == "" or not profile.contains("/work/lpath30-preview-profiles/") or not user_dir.begins_with(profile + "/"):
  refuse("dedicated lpath30 preview profile required; ordinary saves are protected");return
 var language:=argument("--lpath30-language=","en")
 var appearance:=argument("--lpath30-appearance=","male")
 var result: Dictionary=Config.configure(root.get_node_or_null("AppState"),language,appearance)
 if not result.get("ok",false):
  refuse(result.get("error","package rejected"));return
 if change_scene_to_file(result.scene)!=OK:
  refuse("exploration scene did not open");return
 for i in 600:
  await process_frame
  if current_scene!=null and current_scene.is_node_ready():
   if Config.npc_attached(current_scene):
    print("LPATH30_PLAYABLE_READY language=%s appearance=%s"%[language,appearance])
    return
   current_scene.hide()
   refuse("Liang recruit NPC package did not attach");return
 refuse("exploration readiness deadline")
