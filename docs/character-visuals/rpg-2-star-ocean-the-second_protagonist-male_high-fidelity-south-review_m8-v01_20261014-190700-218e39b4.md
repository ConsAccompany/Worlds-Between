# 男主角高清探索形象 · 朝南单张样板

**状态：视觉方向候选，未批准；没有替换可玩精灵。** 本轮依据[男主角来源设定图](../../outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_male_20261013-153316-5b7c19e2.png)制作一张独立透明 PNG。视觉注册表将该来源画像列为 `concept`，因此新样板也不能视为已批准角色形象。

## 文件与制作方式

- [单人 PNG 源图](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-male_high-fidelity-south-exploration_m8-concept_20261014-185706-6bbf80c1.png)：1024×1536 RGBA，全身朝南一人、无文字或多姿势拼版。使用内置 imagegen 工具，以来源画像作为身份参照；保留蓬松层次短发、茶绿围巾、棕色旅行外套、卷起的蓝绿铺盖与菱形社区徽记。
- [Godot 尺寸检查脚本](../../game/tests/rpg-2-star-ocean-the-second_protagonist-male_high-fidelity-city-scale-check_m8-v01_20261014-190000-639d1e74.gd)：独立运行，在 640×360 科技城候选背景上放置一位男主角；源图缩放 0.05，视觉主体约 70 逻辑像素高，足底约 `(320,239)`。没有修改主菜单、探索场景或角色注册表。
- [实际 Godot 640×360 截图](../../outputs/rpg-2-star-ocean-the-second_protagonist-male_high-fidelity-city-game-scale_m8-concept_20261014-190400-1f9c784d.png)

运行环境为 Godot 4.7.2 Compatibility；检查脚本输出 `HIGH_FIDELITY_CITY_SCALE_OK size=640x360`。图像使用最近邻采样，未用于正式游戏。

## 图像生成提示要点

向 imagegen 提供男主角角色设定图，要求：只生成一位成年初期男性的朝南全身探索形象；用高细节 HD-2D 像素绘画与清晰像素簇表现，而非简单 32×48 方块人；保留短发层次、围巾、外套、背包卷铺盖和徽记；透明背景，不要场景、光晕、阴影、界面、文字或其他角色。第一张生成图的半透明暗晕明显；之后做一次背景清理编辑，并再次从原始身份图生成。当前 PNG 为再次生成的候选。

## 640×360 观察与限制

- **较旧 32×48 样板更接近精致背景的材质密度**，外套、裤靴和茶绿围巾形成可辨色块。短发仍有蓬松外轮廓，但在约 70 像素高时层次细节大幅损失；胸前小徽记基本不能独立辨认。
- 源图的 RGBA 四角透明，主体高不透明像素范围约 x=250–785、y=73–1470；但几乎整张画布仍有少量低透明度暗晕像素。放在城市背景上较不明显，源 PNG **不是干净的角色剪影 alpha**，需清理后才能考虑正式接入。
- 1024×1536 的细节缩到约 70 像素时会丢失大量像素笔触；仍需与女性主角、队友并排检查，确认人物尺寸和画面语言一致。

**判定：** 保留为一张南向视觉方向样板供审查；不得据此量产其余方向、替换运行素材或增加资产验收计数。
