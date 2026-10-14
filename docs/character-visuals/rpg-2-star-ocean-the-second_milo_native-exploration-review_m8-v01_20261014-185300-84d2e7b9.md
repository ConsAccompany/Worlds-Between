# 米洛 · 原生探索动作样板审查

**状态：制作完成的候选，未获游戏内精灵验收。** 米洛 / Milo 是科技板块第 04 位主线伙伴，31 岁的医疗工作者。核对了[视觉注册表](../../game/data/character-visuals/rpg-2-star-ocean-the-second_character-visual-registry_m8-v01_20261014-134810-2a5d1b3c.json)、[人物档案](../../outputs/rpg-2-star-ocean-the-second_core-cast_character-bible_v01_20261012-234158-cc7e91a4.md)与[已批准的发型来源图](../../outputs/rpg-2-star-ocean-the-second_milo_character-sheet_hairstyle-v02_20261013-161317-f1651dc0.png)。来源画像已批准，但这套新精灵仍需单独验收。

## 设计落点

- 极短深色圆寸在头顶做锯齿短发轮廓，人物右鬓使用明显的银色发片。西向可见银色侧面；东向远侧银色发片大多被遮住，东西帧并非镜像。
- 白灰短医袍与深海军蓝内衣形成明暗分区；衣摆、白色高领、绿色袖口腕带和方形医药箱在四个朝向保持身份一致。药箱有绿色十字，随行走轻微摆动。
- 每张原生透明 PNG 为 32×48；四方向各 1 张待机、4 张行走，共 **20 张独立文件**。固定锚点 `(16,44)`，所有相位的靴底到 y=44，头部不因步态上下跳动。

## 交付与尺寸检查

- [逐帧清单](../../game/assets/characters/native-animation/rpg-2-star-ocean-the-second_milo_native-exploration-manifest_m8-v01_20261014-185020-1976baf4.json)列出 action、direction、phase、路径、尺寸、锚点及逐文件 SHA-256。
- [可重运行的绘制脚本](../../game/assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_milo_native-exploration-generator_m8-v01_20261014-185020-c4b17e8a.py)按最终 32×48 像素逐笔绘制，不缩小 21:9 来源画像。脚本成功重跑；检查 20 个 RGBA 文件、透明四角、共同脚底、第 44 行接地及每方向 5 个不同相位。
- 以下是**五张独立** 640×360 游戏尺度检查图。每张只放一位米洛于科技城候选背景，以 1:1 逻辑像素合成，人物锚点位于 `(320,240)`。这不是 Godot 引擎截图，也不替代游戏内实际移动检查。

  - [朝南待机](../../outputs/rpg-2-star-ocean-the-second_milo_game-scale-south-idle_m8-v01_20261014-185020-461c056e.png)
  - [朝西待机](../../outputs/rpg-2-star-ocean-the-second_milo_game-scale-west-idle_m8-v01_20261014-185020-dbffc1d0.png)
  - [朝北待机](../../outputs/rpg-2-star-ocean-the-second_milo_game-scale-north-idle_m8-v01_20261014-185020-3909a58b.png)
  - [朝东待机](../../outputs/rpg-2-star-ocean-the-second_milo_game-scale-east-idle_m8-v01_20261014-185020-9074bf6c.png)
  - [朝南行走相位 2](../../outputs/rpg-2-star-ocean-the-second_milo_game-scale-south-walk-phase-02_m8-v01_20261014-185020-4ec43298.png)

## 待审风险

在 640×360 暖色石砖上，白色医袍和深色轮廓可见，但银色鬓角与药箱的十字只有少量像素。需要在 Godot 可玩场景里与其他角色并排测试、关掉姓名标签，重点看西向与北向轮廓、四相位脚底稳定和腕带是否被袖口遮住。此批不修改注册表、可玩场景或任何美术验收勾选。
