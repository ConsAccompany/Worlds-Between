extends SceneTree
# Separate-profile preview entry. Zhao remains the real recruitable companion, not the hero.
const Config = preload("res://scripts/zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd")
func _initialize() -> void:
 call_deferred("run")
func argument(prefix: String, fallback: String) -> String:
 for value in OS.get_cmdline_user_args():
  if value.begins_with(prefix): return value.trim_prefix(prefix)
 return fallback
func refuse(reason: String) -> void:
 Config.rollback()
 print("ZPATH27_PLAYABLE_REFUSED ",reason)
 quit(1)
func run() -> void:
 var language:=argument("--zpath27-language=","en")
 var appearance:=argument("--zpath27-appearance=","male")
 var result: Dictionary=Config.configure(root.get_node_or_null("AppState"),language,appearance)
 if not result.get("ok",false):
  refuse(result.get("error","package rejected"));return
 if change_scene_to_file(result.scene)!=OK:
  refuse("exploration scene did not open");return
 for i in 600:
  await process_frame
  if current_scene!=null and current_scene.is_node_ready():
   if Config.npc_attached(current_scene):
    print("ZPATH27_PLAYABLE_READY language=%s appearance=%s"%[language,appearance])
    return
   current_scene.hide()
   refuse("Zhao field NPC package did not attach");return
 refuse("exploration readiness deadline")
