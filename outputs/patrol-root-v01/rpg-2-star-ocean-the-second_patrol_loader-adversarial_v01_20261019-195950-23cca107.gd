extends SceneTree
const PKG := "res://assets/enemies/patrol-anim-v01/rpg-2-star-ocean-the-second_patrol_battle-animation-runtime-package_v01_20261019-194007-a4b10a85.json"
const LD := "res://assets/enemies/patrol-anim-v01/rpg-2-star-ocean-the-second_patrol_battle-animation-loader_v01_20261019-194007-a4b10a85.gd"
func _initialize():
    call_deferred("run")
func run():
    var loader = load(LD)
    var cases = {}
    cases["validAccepted"] = not loader.load_package(PKG).is_empty()
    cases["existingJsonTraversalRejected"] = loader.load_package(PKG.replace("patrol-anim-v01/", "patrol-anim-v01/../patrol-anim-v01/")).is_empty()
    cases["existingJsonDoubleSlashRejected"] = loader.load_package(PKG.replace("patrol-anim-v01/", "patrol-anim-v01//")).is_empty()
    var base = JSON.parse_string(FileAccess.get_file_as_string(PKG))
    var temp = "res://assets/enemies/patrol-anim-v01/" + get_script().resource_path.get_file().replace(".gd", ".json")
    for kind in ["wrongHashRejected", "missingHashRejected", "existingStripTraversalRejected"]:
        var data = base.duplicate(true)
        if kind == "wrongHashRejected":
            data["strip_sha256"] = "0".repeat(64)
        elif kind == "missingHashRejected":
            data.erase("strip_sha256")
        else:
            data["strip"] = String(base["strip"]).replace("patrol-anim-v01/", "patrol-anim-v01/../patrol-anim-v01/")
        var f = FileAccess.open(temp, FileAccess.WRITE)
        f.store_string(JSON.stringify(data))
        f.close()
        cases[kind] = loader.load_package(temp).is_empty()
        DirAccess.remove_absolute(ProjectSettings.globalize_path(temp))
    print("PATROL_LOADER_ADVERSARIAL ", JSON.stringify(cases))
    var okay = not cases.values().has(false)
    print("PATROL_LOADER_ADVERSARIAL_PASS" if okay else "PATROL_LOADER_ADVERSARIAL_FAIL")
    quit(0 if okay else 1)
