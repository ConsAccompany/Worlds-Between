# 女主角高精度探索像素样稿：朝南

**状态：仅供美术方向审查，未批准，未替换运行时角色。** 本轮只制作一张静止、朝南的单人样稿；尚无其他方向或行走动画。

## 交付与依据

- [透明角色源图](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png)：1145×1374 RGBA，单人全身。
- [Godot 城市 640×360、角色可见高度 72px](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-character-quality-h72_m8-v02_20261014-150122-ea26a69d.png)；[引擎捕获数据](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-character-quality-h72_m8-v02_20261014-150122-ea26a69d.json)。另有 [68px](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-character-quality-h68_m8-v02_20261014-145941-5f63ab3e.png) 和 [76px](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-character-quality-h76_m8-v02_20261014-150038-420e22c7.png) 对照，均为单独的实机截图，并非合成拼贴。
- 身份参考：[已建立的女主角设定图](../../outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_female_20261013-153316-8fa4d0c3.png)。她的高侧马尾、茶绿色围巾与睡袋、旧棕色冒险外套、社区菱形徽章得到保留。

## 生成说明

使用内置 imagegen，以原设定图作身份参考，要求单人、透明背景、朝南、略俯视的完整探索姿态；高精度手绘像素簇、彩色轮廓、分层材质与暖光冷影，同时保持高侧马尾、茶绿围巾、背包睡袋和社区徽章。禁止背景、文字、额外角色、拼图或多姿态。输出按项目资产命名规则复制进仓库；未使用角色设定图的现成裁切代替探索图。

## 比例与透明度复核

- 透明角落为 `(0,0,0,0)`；alpha≥64 的主体边界为 `x269–860, y47–1328`，画布边界没有主体像素。边缘有低 alpha 像素，缩小时需继续留意暗晕。
- 实机图把源图脚点 `(638,1328)` 放在城市场景 `(340,253)`，主体可见高度 72 逻辑像素，缩放率约 `0.0562`。单独的柔和椭圆接地影不会写入角色 PNG。
- 72px 下高侧马尾、脸、茶绿围巾和整体装束可辨，人物与精细城市背景的质感比旧 32×48 样稿更接近。菱形徽章和细小五官仍弱；68px 更弱，76px 略清楚但超出本次 60–72px 的比较带。
- 源图是正面偏三分之四的姿态，俯视程度仍需与最终城市相机统一。未检验动画、四向一致性、亮暗区域或与男主在同一镜头的并列身高。源图大量高分辨率细节在 72px 与最近邻采样下不可见，正式生产应先确定目标角色尺寸和采样方式。

结论：可作为高精度方向的审查样本；**不计入正式角色资产完成数**。
