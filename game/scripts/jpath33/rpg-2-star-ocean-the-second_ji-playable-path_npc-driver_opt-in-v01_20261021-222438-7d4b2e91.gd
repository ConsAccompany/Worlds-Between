extends "res://scripts/lpath30/rpg-2-star-ocean-the-second_liang-playable-path_npc-driver_opt-in-v01_20261021-202247-ca439d91.gd"

# Ji Cheng (纪澄) field-NPC driver (opt-in, default OFF; art/motion UNAPPROVED). Reuses the zpath27/lpath30 driver instance
# behaviour unchanged (four-direction idle/walk, phase-aware stop bridges, frame_ms clock, state()) and the lpath30
# actor-parameterized validation (_prepare_actor). Only the actor, the frozen jexplore31 package paths and a separate
# per-actor cache differ. The node only picks textures for the existing scifi.ruins recruit Sprite2D; it never moves it,
# adds no wandering AI and no follower.

const JI_ACTOR := "ji-cheng"
const JI_REGISTRY_PATH := "res://data/jexplore31/rpg-2-star-ocean-the-second_ji-cheng_explore-sprite-set-registry_unapproved-jexplore31-v01_20261021-210451-9469bb52.json"
const JI_SUPPLEMENT_PATH := "res://data/jexplore31/rpg-2-star-ocean-the-second_ji-cheng_explore-stop-transition-supplemental_unapproved-jexplore31-v01_20261021-210451-4c66ed97.json"

static var _ji_prepared := {}


static func clear_ji_cache() -> void:
	_ji_prepared.clear()


# Whole-package validation for Ji; cached per (registry, supplement) separately from the Zhao and Liang caches.
static func prepare_ji_package(registry: String, supplement: String) -> Dictionary:
	var key := registry + "|" + supplement
	if not _ji_prepared.has(key):
		_ji_prepared[key] = _prepare_actor(JI_ACTOR, registry, supplement)
	return _ji_prepared[key]


# Returns the driver now drawing the Ji recruit NPC, or null (other member, or package refused whole: legacy texture).
static func attach_ji_npc(target: Sprite2D, member_id: String, registry: String, supplement: String) -> Node:
	if member_id != JI_ACTOR or target == null:
		return null
	var prepared := prepare_ji_package(registry, supplement)
	if not prepared["ok"]:
		return null
	var driver = new()
	driver.name = "JiFieldNpcDriver"
	driver.sprite = target
	driver.actor_id = JI_ACTOR
	driver.sprite_set = prepared["set"]
	driver.bridges = prepared["bridges"]
	driver.frame_ms = prepared["frame_ms"]
	driver.facing = "south"
	var density: int = prepared["set"]["density"]
	var frame_size: Vector2 = prepared["set"]["frame_size"]
	var pivot: Vector2 = prepared["set"]["pivot"]
	# Presentation only, same convention as zpath27/lpath30: Sprite2D.position and z_index are never touched.
	target.scale = Vector2.ONE / float(density)
	target.offset = frame_size * 0.5 - pivot + Vector2(0.0, FLOOR_DROP_LOGICAL * density)
	target.add_child(driver)
	driver._apply()
	return driver
