# 女主角同源分层行走骨架：一次临时验证

**结论：分层路线值得继续，但这张单图自动拆出的样板尚不足以接入 MVP。** 它比整图平移有更明确的交替腿动作，且完全保留围巾、护膝、脸和背包身份；脚底仍滑移，手臂不摆，衣摆与大腿交界偶有裁切感。没有更改正式游戏运行时。

## 实机证据

- [8 帧城市动态预览](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_segmented-walk_city-motion-review_m8-concept_20261014-161500-85f2b96a.gif)
- [8 张独立 1280×720 Godot 截图和逐帧参数](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_segmented-walk_city-visual-manifest_m8-concept_20261014-161303-7105df38.json)，例如[第 1 帧](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_segmented-walk-phase-01_city-visual_m8-concept_20261014-161303-7105df38.png)与[第 5 帧](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_segmented-walk-phase-05_city-visual_m8-concept_20261014-161303-7105df38.png)
- 用于检查边缘的单帧放大图：[第 1 帧](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_segmented-walk-phase-01_diagnostic-3x-detail_m8-concept_20261014-161700-316dc840.png)、[第 5 帧](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_segmented-walk-phase-05_diagnostic-3x-detail_m8-concept_20261014-161700-316dc840.png)。这些只是实机帧的单独放大裁切，最终比例以原始截图为准。
- [临时 Godot 分层捕获脚本](../../game/tests/rpg-2-star-ocean-the-second_protagonist-female_segmented-walk-visual-capture_m8-concept_20261014-161200-8b3a6f12.gd)
- 对照：[整图程序化滑行](rpg-2-star-ocean-the-second_protagonist-female_procedural-walk-fallback-review_m8-concept_20261014-160600-f25d7861.md)与[独立生成四相图](rpg-2-star-ocean-the-second_protagonist-female_south-walk-cycle-continuity-review_m8-concept-v02_20261014-155600-2c7f9a80.md)

脚本仅在内存中从同一张[女主南向透明原图](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png)分出躯干、观看者左腿（保留护膝）和右腿的像素遮罩；源图文件未改。三层仍引用原图的原始颜色纹理。Godot 将两腿绕髋关节反向旋转约 ±4°、相反方向升降最多约 0.9 逻辑像素，躯干起伏最多 0.6 像素；每帧向南移动 5 像素、停 0.10 秒。画面保持 48 逻辑像素人物高度，`canvas_items` 输出 1280×720。

与整图滑行相比，步幅更能看出左右交替，围巾和护膝不会换边。与独立生成图相比，头脸、纹理、徽章和服饰完全来自同一图，不发生重画漂移。但自动多边形遮罩没有真正重绘衣摆下方的遮挡面；腿大角度时裤腿交界和腰部有硬边，尤其在放大图里明显。两只胳膊保持静止。角色下行时，当前单段刚性腿无法在身体前进的同时固定着地靴子，所以脚仍沿地面移动。GIF 调色板会改变部分细色，颜色请看 PNG。

因此，**没有证据证明此版整体优于另两种失败方案到可用于 MVP 的程度**。可把它当作制作方式的技术验证，不能视为成品动作或推广至全队。若继续此路线，至少需要：

1. 角色按南、北、东、西分层的可编辑源文件：头/发尾、躯干/衣摆、左右上臂与前臂、左右大腿、膝护具、左右小腿与靴、围巾尾、背包，以及每层被遮挡处的补画；保留统一 48px 足点与关节坐标。
2. 两段腿骨或局部变形网格、明确的左右脚着地阶段和脚掌锁定；逐帧检查衣摆、膝盖与靴子重叠顺序。手臂及围巾可以在腿部合格后再加轻摆。
3. 在亮色道路、暗色室内、不同方向和实际移动速度下复核脚滑、接缝、轮廓与伙伴身高；通过后再讨论正式运行时接入。

**粗略人工量级，需用一个完整角色验证：** 对已有扁平单图，南向分层、补画、双腿接触、循环调试约 0.5–1.5 个熟练美术／技术美术工作日；四个方向加一致性审查约 3–6 天／角色。若 51 人都需要相同质量的四向走路，约 150–300 人日，仅为探索动作、未计战斗动作与返工。若先提供真正分层的源图和共用骨架模板，后续角色才可能减少重复拆图时间。
