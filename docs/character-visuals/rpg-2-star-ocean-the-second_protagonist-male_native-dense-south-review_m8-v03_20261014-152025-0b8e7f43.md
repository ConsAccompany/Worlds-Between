# M8 男主高密度原生像素图：单张质量实验（未通过美术验收）

**交付物：**[唯一南向待机 PNG](../../game/assets/characters/high-density-prototypes/rpg-2-star-ocean-the-second_protagonist-male_native-dense-south-idle_m8-v03_20261014-151556-75c4d0a1.png)、[可重复绘制脚本](../../game/assets/characters/high-density-prototypes/rpg-2-star-ocean-the-second_protagonist-male_native-dense-south-generator_m8-v03_20261014-151556-8f4ca128.py)、[实际 Godot 城市 1280×720 截图](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-male-native-dense-character-quality-h52-canvas-items-with-liang_m8-v02_20261014-151759-295c7825.png)和[渲染收据](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-male-native-dense-character-quality-h52-canvas-items-with-liang_m8-v02_20261014-151759-295c7825.json)。这是独立手绘的程序化像素簇；脚本不读取、缩放或描摹现有 32×48 精灵及高分辨率概念图。只制作一张图，没有动画或拼图。

## 技术结果

- PNG 为 `192×224` RGBA，强可见边界 x=54–152、y=56–208，源图可见身高约 `152` 像素；脚点 `(96,208)`，全透明背景、无半透明边、强像素不触碰画布边。头发、茶绿色围巾、浅色内衫、棕灰外套、旅行背包和菱形徽记由不同色组逐层绘制。
- 画质检查脚本在固定城市脚点 `(340,253)`、临时 `canvas_items` 模式下把这张图显示为约 `52` 逻辑像素，即 `104` 个 1280×720 物理像素。独立的 40×14 软阴影由检查脚本放在脚下；梁序当前 32×48 图在同一地面 y 值右侧，用于现场尺度参照。游戏场景、角色注册表及项目设置没有被这次实验改写。
- 截图和收据实际尺寸均验证为 `1280×720`；无 alpha 画布边缘裁切。Godot 检查脚本退出码为 0。PNG SHA-256：`DE2BAD5BE165C67FAFE2B7AC9935540508FD893D8D3E5987422EECB75AFA46C9`。

## 目视结论

在 52 逻辑像素时，蓬松短发外轮廓、茶绿围巾、外套和背包仍能被认出；人物比旧 32×48 图更有存在感，脚底与街面接触正确。然而眼睛、胸前徽记、皮带扣和衣料纹理多数合并成暗色小块；比例显得偏宽、偏卡通，与科技城高细节背景及[同尺度高分辨率女主概念候选](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-character-quality-h52-canvas-items-with-liang_m8-v02_20261014-151401-81330838.png)相比，细节密度和质感仍有明显差距。**这次原生像素方案不能作为达到目标画质的成品标准。**

主要技术原因是源图 152 像素身高被压到 104 个物理像素；收据缩放率约 `0.342` 逻辑倍数、`0.684` 物理倍数，每个源像素无法稳定对应一个屏幕像素，人工设计的细节簇被不规则丢弃。若最终城市身高选在约 48–52 逻辑像素，下一轮原生像素试样应考虑可见身体约 `96–104` 源像素、物理 `1:1` 采样，或改用经过人工清理透明边缘和逐帧一致性的高分辨率角色绘制。两者都还需要真实城市验收。此单张南向图不能证明四方向、待机/行走动画、角色间比例或与战斗图的连贯性。
