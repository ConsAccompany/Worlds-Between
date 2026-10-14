extends RefCounted
class_name BattleRules


static func recover_after_battle(member: Dictionary) -> Dictionary:
	var recovered := member.duplicate(true)
	var max_hp: int = maxi(1, int(recovered.get("max_hp", 1)))
	var max_energy: int = maxi(1, int(recovered.get("max_energy", 1)))
	var hp: int = int(recovered.get("hp", 0))
	var energy: int = int(recovered.get("energy", 0))
	if hp <= 0:
		recovered["hp"] = maxi(1, ceili(float(max_hp) * 0.10))
		recovered["energy"] = maxi(1, ceili(float(max_energy) * 0.10))
	else:
		recovered["hp"] = mini(max_hp, hp + ceili(float(max_hp) * 0.20))
		recovered["energy"] = mini(max_energy, energy + ceili(float(max_energy) * 0.20))
	return recovered
