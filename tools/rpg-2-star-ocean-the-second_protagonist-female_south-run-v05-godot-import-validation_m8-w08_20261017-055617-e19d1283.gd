extends SceneTree

# v05: a copy of the v04 import validation tool (tools/...south-run-v04-godot-import-validation_m8-w07_20261017-015826-2a8e4f71.gd,
# untouched), pointed at the v05 asset folder.
# (v04:) a copy of the v03 import validation tool (tools/...south-locomotion-compact-v03-godot-import-validation_m8-w06_20261017-012243-d2169050.gd,
# untouched), pointed at the v04 asset folder.  (v03:) Started as a copy of the v02 import validation tool.
# TEST-ONLY Godot import validation for the UNAPPROVED / NONRUNTIME female SOUTH RUN motion pilot v05 (m8-w08, test-only).
# The asset folder ships with an empty .gdignore so the shared working tree imports nothing (no .import / .uid side
# effects for other sessions).  This tool is run in an ISOLATED COPY of game/ (under %LOCALAPPDATA%\Temp) where that
# .gdignore was removed and `--headless --import` was run first:
#   Godot --headless --path <copy>/game --import
#   Godot --headless --path <copy>/game -s <absolute path of this file>
# Gates (exit 1): every pilot PNG has a .import with compress/mode=0 (lossless), mipmaps/generate=false; the project's
# default canvas texture filter is Nearest (0); the imported texture has no mipmaps; versus the PNG file (RGBA8) its
# alpha is identical everywhere and RGB identical on every opaque texel (Godot's default
# process/fix_alpha_border only rewrites the RGB of alpha-0 texels, which is counted and reported).  Prints RUN_V05_IMPORT PASS.
const ASSET_DIR := "res://assets/characters/run-v05-unapproved/"


func _initialize() -> void:
	var fails := []
	var n := 0
	var n_transparent_rgb := 0
	var n_fix_alpha := 0
	var filt := int(ProjectSettings.get_setting("rendering/textures/canvas_textures/default_texture_filter", -1))
	if filt != 0:
		fails.append("default_texture_filter is %d, not 0 (Nearest)" % filt)
	var dir := DirAccess.open(ASSET_DIR)
	if dir == null:
		fails.append("asset dir missing")
	else:
		for f in dir.get_files():
			if not f.ends_with(".png"):
				continue
			n += 1
			var p := ASSET_DIR + f
			var imp := ConfigFile.new()
			if imp.load(p + ".import") != OK:
				fails.append("no .import for " + f)
				continue
			if int(imp.get_value("params", "compress/mode", -1)) != 0:
				fails.append("compress/mode != 0 (lossless) for " + f)
			if bool(imp.get_value("params", "mipmaps/generate", true)):
				fails.append("mipmaps on for " + f)
			var tex := ResourceLoader.load(p) as Texture2D
			if tex == null:
				fails.append("cannot load imported texture " + f)
				continue
			var a := tex.get_image()
			if a.has_mipmaps():
				fails.append("imported image has mipmaps " + f)
			a.convert(Image.FORMAT_RGBA8)
			var b := Image.load_from_file(ProjectSettings.globalize_path(p))
			b.convert(Image.FORMAT_RGBA8)
			# process/fix_alpha_border (Godot default: on) rewrites the RGB of fully transparent texels only; those are
			# invisible (alpha 0), so the gate is: alpha identical everywhere and RGB identical on every opaque texel
			if a.get_size() != b.get_size():
				fails.append("imported size differs for " + f)
				continue
			var bad := 0
			var transparent_rgb_changed := 0
			for y in b.get_height():
				for x in b.get_width():
					var ca := a.get_pixel(x, y)
					var cb := b.get_pixel(x, y)
					if ca.a8 != cb.a8:
						bad += 1
					elif cb.a8 > 0 and (ca.r8 != cb.r8 or ca.g8 != cb.g8 or ca.b8 != cb.b8):
						bad += 1
					elif cb.a8 == 0 and (ca.r8 != cb.r8 or ca.g8 != cb.g8 or ca.b8 != cb.b8):
						transparent_rgb_changed += 1
			if bad:
				fails.append("%d visible texels differ from the PNG for %s" % [bad, f])
			n_transparent_rgb += transparent_rgb_changed
			if bool(imp.get_value("params", "process/fix_alpha_border", false)):
				n_fix_alpha += 1
	if fails.is_empty():
		print("RUN_V05_IMPORT PASS %d PNGs imported lossless (compress/mode 0), no mipmaps, alpha + every opaque texel identical; default canvas filter Nearest; fix_alpha_border on for %d (changed RGB of %d alpha-0 texels only)" % [n, n_fix_alpha, n_transparent_rgb])
		quit(0)
	else:
		for x in fails:
			print("RUN_V05_IMPORT FAIL " + x)
		quit(1)
