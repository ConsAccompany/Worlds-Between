# 52 人来源画像内部审查画廊

**用途：** 在 Godot 640×360 画面里逐张检查来源人物设定图。此画廊是独立内部工具，未加入主菜单、招募、剧情或战斗，也**不改变任何探索/战斗精灵的验收状态**。

- [独立场景](../../game/scenes/rpg-2-star-ocean-the-second_character-source-gallery_m8-v01_20261014-144020-907ab4d1.tscn)；[场景脚本](../../game/scripts/rpg-2-star-ocean-the-second_character-source-gallery_m8-v01_20261014-144020-907ab4d1.gd)。在 Godot 编辑器中单独运行该场景即可审查，左右方向键或画面按钮逐张切换，Esc 退出。
- 数据只读地来自现有 [52 项视觉注册表](../../game/data/character-visuals/rpg-2-star-ocean-the-second_character-visual-registry_m8-v01_20261014-134810-2a5d1b3c.json)。画面顶部持续显示“来源已批准 9 · 概念 43”；每项再显示其具体 `approved` 或 `concept` 状态；底部注明“游戏内精灵未因此验收”。
- 来源 PNG 在仓库根目录 `outputs/` 中，画廊从本地文件按需加载当前一张。鼠标悬停图像可见源文件路径；这要求在完整项目检出中运行，不作为导出游戏功能。

## 定向检查

[检查脚本](../../game/tests/rpg-2-star-ocean-the-second_character-source-gallery_visual-check_m8-v01_20261014-144300-1e74bc90.gd) 在 Godot 4.7.2 无头模式逐张加载 52 项，核对纹理不为空、存在可绘制像素、可见图像容器尺寸 608×238、条目状态与画面标签一致。实际文件为 **9 张已批准来源画像、43 张概念图，缺失 0 张**；上一张/下一张按钮也通过检查。

非无头模式另保存三张**各自独立**的 640×360 引擎截图：

- [主角概念图](../../outputs/rpg-2-star-ocean-the-second_character-source-gallery_in-engine-review_m8-v02_20261014-144400-782bf513/rpg-2-star-ocean-the-second_character-source-gallery_in-engine-protagonist-concept_m8-v01_20261014-144204-f32f9a58.png)
- [蒋岚已批准来源画像](../../outputs/rpg-2-star-ocean-the-second_character-source-gallery_in-engine-review_m8-v02_20261014-144400-782bf513/rpg-2-star-ocean-the-second_character-source-gallery_in-engine-approved-source_m8-v01_20261014-144204-c13ddeee.png)
- [余音概念图](../../outputs/rpg-2-star-ocean-the-second_character-source-gallery_in-engine-review_m8-v02_20261014-144400-782bf513/rpg-2-star-ocean-the-second_character-source-gallery_in-engine-final-companion-concept_m8-v01_20261014-144204-a1bb5a2b.png)

[捕获清单](../../outputs/rpg-2-star-ocean-the-second_character-source-gallery_in-engine-review_m8-v02_20261014-144400-782bf513/rpg-2-star-ocean-the-second_character-source-gallery_visual-check-manifest_m8-v01_20261014-144204-37aa0ee7.json)明确写明 `runtime_sprites_accepted_by_this_test: 0`。三种样本的整张设定图都以保留纵横比的方式置于单一图像框内，没有拼贴或另造一张人物组合图。

## 局限

画廊检验的是来源图可以在引擎中逐张查看，不验证四方向探索动作、战斗图、人物身份审美或图片内容是否最终批准。画面尺寸较小，适合浏览与发现明显问题；细部美术审批仍需查看原始 PNG。来源图存放在 `game/` 项目目录之外，因此导出包不会自动包含它们，这与“内部审查工具”的定位一致。
