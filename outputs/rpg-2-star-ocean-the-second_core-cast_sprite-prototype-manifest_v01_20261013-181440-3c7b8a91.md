# 核心角色像素精灵原型 v0.1

依据已批准的角色发型画像，使用内置 imagegen 制作。每个角色、每类用途各自独立成图；主角男女版本分别成图。所有文件为透明背景、约 21:9 的视觉原型，尚非可直接导入游戏的逐帧动画或固定网格图集。

| 角色 | 俯视探索方向原型 | 横向战斗动作原型 |
|---|---|---|
| 主角·男 | [探索方向](./rpg-2-star-ocean-the-second_protagonist-male_exploration-directions_prototype-v01_20261013-181440-d4e92b09.png) | [战斗动作](./rpg-2-star-ocean-the-second_protagonist-male_combat-poses_prototype-v01_20261013-181440-7dee3381.png) |
| 主角·女 | [探索方向](./rpg-2-star-ocean-the-second_protagonist-female_exploration-directions_prototype-v01_20261013-181440-61f32ddf.png) | [战斗动作](./rpg-2-star-ocean-the-second_protagonist-female_combat-poses_prototype-v01_20261013-181440-fd0e187b.png) |
| 梁序 | [探索方向](./rpg-2-star-ocean-the-second_liang-xu_exploration-directions_prototype-v01_20261013-181440-fcd1a74c.png)；[补充右向侧身](./rpg-2-star-ocean-the-second_liang-xu_exploration-right-profile_prototype-v01_20261013-181440-633cdb7c.png) | [战斗动作](./rpg-2-star-ocean-the-second_liang-xu_combat-poses_prototype-v01_20261013-181440-6fbbeca6.png) |
| 阿荻 | [探索方向](./rpg-2-star-ocean-the-second_adi_exploration-directions_prototype-v01_20261013-181440-1f1095a1.png) | [战斗动作](./rpg-2-star-ocean-the-second_adi_combat-poses_prototype-v01_20261013-181440-a0d03971.png) |
| 娜丽娅 | [探索方向](./rpg-2-star-ocean-the-second_nalia_exploration-directions_prototype-v01_20261013-181440-a6abaaa0.png) | [战斗动作](./rpg-2-star-ocean-the-second_nalia_combat-poses_prototype-v01_20261013-181440-fd463120.png) |
| 夜澜 | [探索方向](./rpg-2-star-ocean-the-second_yelan_exploration-directions_prototype-v01_20261013-181440-03102b06.png) | [战斗动作](./rpg-2-star-ocean-the-second_yelan_combat-poses_prototype-v01_20261013-181440-88b541f3.png) |

## 视觉内容

- 探索图：同一角色的正面、背面和两个侧身视角，强调发型、服装和背面标识；梁序的原方向图中两个侧身朝向重复，故另附独立的右向侧身。各探索图的左右侧身排列尚未统一。
- 战斗图：同一角色从左至右的待机、水平跑动、基础攻击、防御和个人技能姿态；遵守横向移动、无跳跃的战斗设定。
- 主角两版共享地下社区徽记、茶绿色围巾与背包；阿荻的双辫、娜丽娅的不对称短发、夜澜的平直短发、梁序的灰白盘发保持清晰差别。

## 交付边界与制作规格草案

这些图用于确定游戏内角色轮廓、配色、姿态语言。图中人物像素尺寸和格线尚未统一，不能直接视作可播放的游戏动画。正式制作需为每个方向和动作建立固定尺寸、统一锚点与逐帧序列，并在实际游戏画面缩放下检查可读性。建议以探索角色格约 `64×96 px`、战斗角色格约 `128×128 px` 起步试验；这两个尺寸是待验证的制作草案。

## 生成提示词摘要

以各角色已批准画像为严格参考，保留身份、发型、配色、服装和关键道具；透明 21:9 画布；探索图为四方向整身像素精灵原型，战斗图为侧面五种地面动作姿态；要求清晰硬边像素块、人物之间留空、无场景与文字。梁序补充图要求单人右向侧身。
