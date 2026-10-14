# 女主角高精度探索图：东向、北向城市实机复核

**状态：美术概念，未批准。** 只检查静止朝向；没有替换运行时角色、制作动作帧或改变角色登记。

| 朝向 | 单人透明源图 | 1280×720 Godot 城市实机图 | alpha≥64 主体范围 | 脚点与缩放 |
| --- | --- | --- | --- | --- |
| 东 | [源图](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_east-exploration-premium-pixel_m8-concept_20261014-151550-dc168ba8.png) | [48px 实机图](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-east-character-quality-h48-canvas-items_m8-v02_20261014-152140-d8f9d694.png) | `(339,43)–(776,1328)` | 源图 `(640,1328)` → 城市 `(340,253)`；`48/1285≈0.0373541` |
| 北 | [源图](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_north-exploration-premium-pixel_m8-concept_20261014-151700-f1331de2.png) | [48px 实机图](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-north-character-quality-h48-canvas-items_m8-v02_20261014-152209-8f91b3c2.png) | `(322,41)–(868,1310)` | 源图 `(545,1310)` → 城市 `(340,253)`；`48/1269≈0.0378251` |

两次捕获均使用实际 Godot 科技城市、`canvas_items` 1280×720 输出、48 逻辑像素主体高度、人物最近邻采样和独立的柔和接地影。每张实机图旁的同名 JSON 记录了 alpha、尺寸和脚点。画布角落透明，alpha≥64 的主体没有接触图像边缘；脚底在截图中接在地面上，没有明显漂浮。测试工具的“低于旧 52–80px 比较带”提示只是旧诊断带警告，并非加载或渲染错误。

东向的高侧马尾向后伸出，侧脸、茶绿色围巾、睡袋、棕色外套与徽章位置都可辨。北向的马尾向右伸出，茶绿睡袋和飘带让背面仍能辨认是同一角色。东向在 48px 下约宽 16 逻辑像素，北向约宽 21；侧向轮廓较窄属姿态差异。头、肩、脚在两张城市截图中基本落在同一高度带。

仍需修正的细节：北向背包只见空心菱形压纹，未清楚呈现原角色设定的蓝绿色社区徽记；若徽记需要四向都可认，应在北向提高色彩对比。两张源图的深色头发边缘都有低 alpha 像素，亮色铺地上未见明显整圈暗晕，但暗色背景和移动中仍需检查。东向、北向与南向分别由独立生成，服装带扣和徽章位置需要统一到正式转面模型；西向尚未制作，不能确认四向一致性。
