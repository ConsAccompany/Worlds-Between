# 女主角高精度南向行走关键帧可行性复核

**状态：单帧概念，尚非可循环动画。** 未接入运行时，未改角色登记或 Game Bible。

- [新迈步单帧透明源图](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-walk-left-stride-premium-pixel_m8-concept_20261014-152600-3cf71b09.png)
- [48 逻辑像素、1280×720 Godot 城市实机截图](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-south-walk-left-stride-character-quality-h48-canvas-items_m8-v02_20261014-152906-37f80376.png)；[同名捕获数据](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-south-walk-left-stride-character-quality-h48-canvas-items_m8-v02_20261014-152906-37f80376.json)
- 对照：[南向待机源图](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png)与[待机 48px 城市实机截图](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-character-quality-h48-canvas-items-with-liang_m8-v02_20261014-151442-b75b310e.png)

以现有女主角南、东、北三个静止概念作为 imagegen 身份参考，要求南向左腿前迈、右腿后随、手臂反向摆动、侧马尾和围巾轻微弹动。明确锁定脸、发型、服装、茶绿睡袋、社区蓝绿菱形徽章、像素质感和透明背景；输出仅一名角色的一张单独图片。

新图为 1145×1374 RGBA；alpha≥64 的主体框为 `(256,37)–(884,1331)`，画布角落透明。以前脚着地点 `(644,1331)` 对准城市 `(340,253)`，有效高度 `1294px`，缩放 `48/1294≈0.0370943`；人物最近邻采样，阴影独立。待机图对应有效高度 `1281px`、脚点 `(638,1328)`、缩放 `48/1281≈0.0374707`。这样两帧在画面里均为 48 逻辑像素高，脚点只差由姿态造成的源图位置，而城市场景落点相同。

**观察：** 迈步、单脚支撑、另一脚跟进的方向可读；高侧马尾、茶绿围巾、棕色外套和徽章在 48px 下仍保持身份。头部附近的源图宽度比待机约宽 6%，躯干附近约宽 1–2%；缩小时主要表现为约一像素的发型摆动，未看到明显身形突变。源图 alpha≥64 面积比待机少约 4%，主要来自收拢的腿部姿态。城市实机图中前脚贴地，无明显整圈暗晕。

**限制：** 单张生成图无法证明四帧循环稳定。眼睛、发束和皮带等细节有轻微重画；目前只验证待机和一次前迈之间的体积、脚点与身份。要做正式循环，应固定头、脸、胸、背包及徽章的共用像素参考和脚点规范，再补相反脚、过渡与回到待机的帧，并在真实移动中检查节奏和抖动。该图只能作为动作方向候选，不能计入完成动画。
