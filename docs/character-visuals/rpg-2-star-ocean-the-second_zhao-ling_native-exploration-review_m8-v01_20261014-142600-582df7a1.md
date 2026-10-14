# 赵铃原生探索精灵：四方向待机与行走样板

**状态：制作样板，尚未验收。** 角色设定画像仍标记为 `concept`。本批只制作探索动作，不计入战斗动画或已验收的 52 个探索形象。

## 角色依据

- 角色档案：赵铃 / Zhao Ling，26 岁，科技板块的城市无线电修理员；用浅显方式解释复杂信息；个人技能为「回声测距」。
- 外观依据：[角色画像](../../outputs/rpg-2-star-ocean-the-second_zhao-ling_character-sheet_v01_20261013-193120-54215370.png)：不对称短发，湖蓝头戴耳机，右后方天线，深灰维修服，斜跨背带、维修终端与工具包。
- 对照 [俯视探索规格](./rpg-2-star-ocean-the-second_character-visual-spec_topdown-v01_20261014-135700-17a0c9d4.md)：直接在 32×48 画布上组织像素；没有缩小画像，也没有左右翻转代替侧面绘制。

## 本批文件

- [20 帧清单](../../game/assets/characters/native-animation/rpg-2-star-ocean-the-second_zhao-ling_native-exploration-manifest_m8-v01_20261014-142000-b123903c.json)：南、西、北、东各 1 张待机和 4 张行走帧；每张 PNG 均为独立文件。
- [可重现绘制脚本](../../game/assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_zhao-ling_native-exploration-generator_m8-v01_20261014-142000-a7e81d3c.py)。
- [640×360 原尺寸示例](../../outputs/rpg-2-star-ocean-the-second_zhao-ling_scene-scale-idle-south-masonry_m8-v01_20261014-142400-73b1cc9a.png)：单人叠在简化暖石地面，用于尺寸与对比度预检；**不是 Godot 实景截图**。
- 独立放大审查图：南、西、北、东各一张，`outputs/rpg-2-star-ocean-the-second_zhao-ling_pixel-review-idle-*`。放大图使用最近邻，仅用于查看原生像素，没有进入游戏素材。

## 核对结果

| 检查 | 结果 |
|---|---|
| 帧数与格式 | 20 张独立 32×48 透明 RGBA PNG；四方向各 5 张。 |
| 足底 | 所有帧的最后非透明行是 y=44，世界锚点固定为 `(16,44)`；无纵向头部跳动。 |
| 边界 | 四角透明，横向有效像素始终离画布边缘至少 1 像素；手持终端摆动不裁边。 |
| 动作差异 | 每方向 5 帧像素散列全不同；行走相对待机约 122–212 像素变化，腿、袖、终端分别移动。 |
| 发型身份 | 南面长侧分发片覆盖左脸；背面短发和双耳杯形成独有轮廓；两侧耳杯和天线的位置分别绘制，不是镜像。 |
| 色数 | 待机方向各 17–19 个 RGBA 色值，保留头发、湖蓝配件与深灰服装的分层。 |

## 尚待验收

在 Godot 科技城和郊外场景的真实 640×360 画面中，检查四方向连续行走、背景分离、脚底与遮挡、与主角及其他科技区伙伴同屏的辨识度。再由人工审美审查确认发片、耳机、天线、终端不会在连续播放时抖动或被遮住。在这两步之前，注册表和资产清单保持未验收。
