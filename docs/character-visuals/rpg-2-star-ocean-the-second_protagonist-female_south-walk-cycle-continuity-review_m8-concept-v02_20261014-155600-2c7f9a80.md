# 女主角南向四相行走连续性：定向修订结果

**结论：动作方向可探索，但本批不能作为正式循环。** 一次定向 imagegen 修订解决了围巾尾端换边，未解决护膝换腿和躯干横跳。未接入游戏运行时，未批准美术。

## 独立素材与实机证据

- 待机：[源图](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png)
- 左脚迈步：[源图](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-walk-left-stride-premium-pixel_m8-concept_20261014-152600-3cf71b09.png)
- 右脚迈步初稿：[源图](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-walk-right-stride-premium-pixel_m8-concept_20261014-153500-9a217e4c.png)
- 右脚迈步定向修订：[v2 透明源图](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-walk-right-stride-corrected-premium-pixel_m8-concept-v02_20261014-154600-e783af92.png)、[48px Godot 城市实机图](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-south-walk-right-stride-v02-character-quality-h48-canvas-items_m8-v02_20261014-155010-d0acac68.png)
- 四相播放顺序为待机→左步→待机→右步，每相 0.16 秒：[v2 动态预览](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_south-walk-cycle_city-motion-review-v02_m8-concept_20261014-155300-6cab85de.gif)、[四张独立 1280×720 Godot 帧及脚点记录](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_south-walk-cycle_city-visual-manifest_m8-concept_20261014-155156-4c9f0147.json)。[临时可复现捕获脚本](../../game/tests/rpg-2-star-ocean-the-second_protagonist-female_south-walk-cycle-visual-capture_m8-concept-v02_20261014-155100-86ab32d9.gd)只用于视觉检查。GIF 经过调色板量化，颜色和边缘质量应以 PNG 实机帧为准。

v2 修订使用右步初稿为编辑目标、待机和左步为连续性参考，仅要求围巾尾端及护膝回到既有的观看者左侧，锁定步态和其他身份细节。输出仍是单张透明角色图，没有角色表或拼图。

## 观察与限制

四相都以 48 逻辑像素可见高度放在同一城市脚点 `(340,253)`；各帧源图脚点分别为待机 `(638,1328)`、左步 `(644,1331)`、右步 v2 `(533,1338)`。右步 v2 的 alpha≥64 范围为 `(222,36)–(859,1338)`，透明边缘与接地影在城市亮色铺地上未见明显漂浮。

右步 v2 的围巾尾端已从观看者右侧移回左侧，与待机和左步一致；但**护膝依旧留在观看者右侧的后腿**，而另两帧在观看者左侧。右步的头发、脸及带扣也有细小重绘。按同脚点缩放后，躯干中段中心约在右步 `x342.5`、待机 `x338.1`，相差约 **4.3 逻辑像素**，四相切换会产生侧向跳动。原始三张源图虽均保持约 48px 高，但按不同源图分别缩放并不足以保证同一身体几何。

因此这一轮只证明：单独生成相反迈步姿态可行，**独立生成和一次自然语言局部修订仍不足以稳定做循环**。下一轮应在固定的角色轮廓、头脸/背包/徽章图层及左右腿护具归属上制作或手工校正关键帧，再以同脚点实机循环复核；不应直接批量生成全队动画。
