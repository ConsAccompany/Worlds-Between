# 女主角单图程序化移动：MVP 动画替代方案复核

**结论：可暂作内部操作占位，不能作为当前高精度美术方向的 MVP 行走动画基准。** 人物造型稳定，但在城市道路上明显像滑行；没有接入正式运行时。

## 实机证据

- [8 帧城市动态预览](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_procedural-walk_city-motion-review_m8-concept_20261014-160400-90e5b17d.gif)
- [8 张独立 1280×720 Godot 截图与逐帧脚点数据](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_procedural-walk_city-visual-manifest_m8-concept_20261014-160214-53cb1dfa.json)；例如[第 1 帧](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_procedural-walk-phase-01_city-visual_m8-concept_20261014-160214-53cb1dfa.png)与[第 8 帧](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_procedural-walk-phase-08_city-visual_m8-concept_20261014-160214-53cb1dfa.png)
- [仅用于视觉测试的 Godot 脚本](../../game/tests/rpg-2-star-ocean-the-second_protagonist-female_procedural-walk-visual-capture_m8-concept_20261014-160000-51d69ac2.gd)
- 对照：[独立生成的四相行走预览](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_south-walk-cycle_city-motion-review-v02_m8-concept_20261014-155300-6cab85de.gif)和[连续性审查](rpg-2-star-ocean-the-second_protagonist-female_south-walk-cycle-continuity-review_m8-concept-v02_20261014-155600-2c7f9a80.md)

测试只使用[女主角南向静止透明图](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png)，没有编辑 PNG。人物高度固定为已选的 48 逻辑像素。临时场景以 640×360 逻辑画布、`canvas_items` 输出 1280×720；8 帧每帧向右移动 6 逻辑像素，每帧停 0.09 秒，垂直起伏最多 0.9 像素，旋转在 ±0.7° 内，接地影按起伏轻微缩放与变淡。GIF 经过调色板量化，颜色与像素边缘以独立 PNG 为准。

相较于独立生成的四相图，这个方案完全保留高侧马尾、围巾方向、护膝所在腿、脸与背包的体积，不会在切帧时换装。问题是**两只靴子与双臂的形状完全不变**：角色跨过脚下铺砖时，脚底同速平移，细微上下起伏更接近轻跳，阴影节奏无法让它读成迈步。四相生成图有左右腿交替，但护具换腿、躯干横跳约 4.3 逻辑像素；同样不达标。

建议将单图程序化移动仅保留为内部交互占位。正式 MVP 动画需要固定角色的头脸、发型、徽章、背包和左右护具图层，制作可控的左右脚接触与过渡帧，再在同一街面检查真实移动；仅靠整张图平移、摆动和阴影不能满足本项目已确定的高精度角色标准。
