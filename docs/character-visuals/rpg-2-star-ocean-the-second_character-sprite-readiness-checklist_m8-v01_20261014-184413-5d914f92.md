# 《世界之间》角色精灵制作就绪检查清单（逐变体）v0.1

**状态：事实清单，不批准任何素材。** 本文由脚本从视觉注册表与资产清单只读生成，未改动注册表、现有美术、进度计数或 Game Bible。所有「美术验收」均为 **pending**；只有用户可以验收（见[入库检查清单](rpg-2-star-ocean-the-second_character-visuals_asset-intake-checklist_m8-design_20261014-162946-c4e7a19d.md) 第 9 节）。

- 机器可读版：`game/data/character-visuals/rpg-2-star-ocean-the-second_character-sprite-readiness-checklist_m8-v01_20261014-184413-53da3710.json`
- 生成／校验脚本：`tools/rpg-2-star-ocean-the-second_character-sprite-readiness_build-and-check_m8-v01_20261014-184413-c8e6c511.py`（`--write` 重新生成；无参数为校验模式）
- 注册表：`game/data/character-visuals/rpg-2-star-ocean-the-second_character-visual-registry_m8-v01_20261014-134810-2a5d1b3c.json`（sha256-text-lf-v1 `732753892b57d394…`）
- 资产清单：`outputs/rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json`（sha256-text-lf-v1 `04a8379778f98675…`）
- 哈希算法：二进制文件（PNG）用 `sha256-bytes`（原始字节）；文本文件（JSON/Markdown）用 `sha256-text-lf-v1`（仅把 CRLF 换成 LF 后计算 SHA-256，LF 与 CRLF 检出结果相同；含 NUL 或非 UTF-8 的文件拒绝按文本处理）。
- 规格：[俯视视觉规格](rpg-2-star-ocean-the-second_character-visual-spec_topdown-v01_20261014-135700-17a0c9d4.md)；发型锚点来源：核心 17 个变体取自 `rpg-2-star-ocean-the-second_core-cast_hairstyle-manifest_v02_20261013-161317-4f5a6c7d.md`（用户批准的发型参考），其余 35 名取自 `rpg-2-star-ocean-the-second_remaining-companions_character-sheet-manifest_v01_20261013-194808-b6d7ee1d.md`。

## 范围与汇总

- **52 个视觉变体 / 51 名角色**（主角男女为同一角色的两种外观）。MVP：51 名角色都需要游戏内视觉身份；可玩内容为科技区。
- 来源立绘：approved 9 / concept 43（注册表现值，本文不改）。
- 就绪状态：未开始 45；有 32×48 占位帧（已被否定为画质基线） 5；有未登记的 32×48 占位清单 2。
- 美术验收（runtime-sprite）：已验收 0 / 待定 52；MVP 战斗动作已验收 0/5；显示图已验收 0/52。
- 正式生产帧（经用户美术验收）：0/52。另检测到 1 份清单声明 `frame_counts`（`game/assets/characters/walk-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-manifest_m8-w01_20261015-024345-e80ccf73.json`），其中 1 份未标 `art_approved=true`，只是待人工评审的试点帧，不是正式生产帧；相关变体入库阶段未自动推导，需按入库检查清单人工复核。其余 51/52 个变体处于入库阶段 0。
- 用户批准的静态待机基准帧：1 个变体（`protagonist-female`）。只批准单张静态视觉基准，不算任何闸门通过，不计入上面的美术验收或探索精灵数。
- 战斗动作 MVP 必需（资产清单 scope=MVP）：`protagonist-male`、`protagonist-female`、`liang-xu`、`ji-cheng`、`zhao-ling`；其余 47 名战斗组在资产清单中为 Full 范围，不属 MVP。
- 路径核对：缺失 0 个；已引用但未纳入 git 0 个（详见末节）。

## 闸门定义（每个变体相同）

| 闸门 | 通过条件 | 依据 |
|---|---|---|
| G0 来源立绘 | 立绘文件存在；`approval` 只记录注册表现值，approved/concept 由用户决定，本清单不改写 | 注册表 `source_portrait` |
| G1 四方向 | `south`/`west`/`north`/`east` 四向正式帧齐全；西向独立绘制，若为东向镜像须标 `mirrored_east` 并经用户接受 | 规格「四朝向」、入库 §5 |
| G2 探索动画 | 每方向待机＋行走，帧数按清单 `frame_counts` 声明且经用户批准（20=占位现状、48=试点提案，均未批准）；循环接回相位 1 | 入库 §1、§3、§6 |
| G2c 战斗动画 | 仅 MVP 可玩五形象必需：待机、移动、攻击、防御、闪避、受击、倒下、个人技能 | 规格「可玩五形象连贯」、资产清单 |
| G3 比例 | 城市显示高度 48 逻辑像素（用户已批准）；每变体唯一 `master`/`scale`/`cell_size`/`ground_pin`（数值待试点） | 入库 §3、§7 |
| G4 QA | 入库 §4 自动元数据检查全过；1280×720 `canvas_items` 城市实机截图回执；人工身份／方向／alpha 复核 | 入库 §4、§8、§9 阶段 1–3 |
| G5 美术验收 | 用户书面回执文件；任何哈希变化即作废 | 入库 §9 阶段 4（仅用户） |
| 显示图 | 游戏内展示图（独立于精灵验收） | 注册表 `runtime_display`、资产清单 `display.*` |

批量门槛：须先有一个变体四方向待机与行走达到阶段 4、且用户批准正式帧数，才可批量制作其余变体。下列所有闸门方框均未勾选，因为没有任何一项已获验收。

## 逐变体清单

### 01. `protagonist-male` · 主角·男（protagonist · 主角 · 地下社区）

- 身份／发型锚点（注册表原文）：「蓬松层次短发」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_male_20261013-153316-5b7c19e2.png` · 存在
- 就绪状态：有 32×48 占位帧（已被否定为画质基线） · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.protagonist-male` stage=production checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：south、west、north、east；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 four_direction_native_walk_integrated / pending_motion_and_art_approval；占位 待机 4 + 行走 16；正式帧数未批准）
  - 占位清单：`game/assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-male_native-animation-manifest_m8-v01_20261014-141005-29a4674f.json` · 存在
  - 注册表未引用的相关清单：`game/assets/characters/native-prototypes/rpg-2-star-ocean-the-second_protagonist-male_native-idle-manifest_m8-v01_20261014-135316-9a83ccae.json`
- [ ] G2c 战斗动画（MVP 必需；注册表 sideview_8_action_prototype_integrated / pending_art_approval；原型 8 动作 20 帧；资产清单 `playable-combat.protagonist-male` checked=false）
  - 原型清单：`game/assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-male_sideview-combat-manifest_m8-prototype_20261014-142325-8655f25a.json` · 存在
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=production checked=false

### 02. `protagonist-female` · 主角·女（protagonist · 主角 · 地下社区）

- 身份／发型锚点（注册表原文）：「高束长马尾」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_female_20261013-153316-8fa4d0c3.png` · 存在
- 就绪状态：有 32×48 占位帧（已被否定为画质基线） · 入库阶段 未自动推导（有声明 `frame_counts` 的清单，需人工复核；不表示已越过阶段 0）
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.protagonist-female` stage=production checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：south、west、north、east；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 four_direction_native_walk_integrated / pending_motion_and_art_approval；占位 待机 4 + 行走 16；正式帧数未批准）
  - 声明 `frame_counts` 的清单：`game/assets/characters/walk-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-manifest_m8-w01_20261015-024345-e80ccf73.json`（未批准试点帧，非正式生产帧）
  - 占位清单：`game/assets/characters/native-animation/rpg-2-star-ocean-the-second_protagonist-female_native-animation-manifest_m8-prototype_20261014-140955-d7d64ca7.json` · 存在
  - 注册表未引用的相关清单：`game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-pixelorama-pilot-manifest_m8-v01_20261014-211454-868681b7.json`
  - 注册表未引用的相关清单：`game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-quantized-downscale-manifest_m8-v01_20261014-212322-aa446773.json`
  - 注册表未引用的相关清单：`game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-refinement-candidates-manifest_m8-v01_20261014-231100-08c301fd.json`
  - 注册表未引用的相关清单：`game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v2-polish-manifest_m8-v02_20261014-233300-d4a8a850.json`
  - 注册表未引用的相关清单：`game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v3-polish-manifest_m8-v03_20261014-234700-b47e2c10.json`
  - 注册表未引用的相关清单：`game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v4-structural-manifest_m8-v04_20261015-001500-0c9d3a74.json`
  - 注册表未引用的相关清单：`game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v5-lowerbody-hair-manifest_m8-v05_20261015-004000-f41a7d92.json`
  - 注册表未引用的相关清单：`game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v6-value-separation-manifest_m8-v06_20261015-010000-c2e9081b.json`
  - 注册表未引用的相关清单：`game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v7-slate-coat-manifest_m8-v07_20261015-015010-ed510f85.json`
  - 注册表未引用的相关清单：`game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-manifest_m8-v08_20261015-021600-2d6c5eff.json`
  - 注册表未引用的相关清单：`game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-editable-manifest_m8-v08_20261015-080907-270b2256.json`
  - 注册表未引用的相关清单：`game/assets/characters/walk-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-manifest_m8-w01_20261015-024345-e80ccf73.json`
  - 注册表未引用的相关清单：`game/assets/characters/walk-pilots-v2/rpg-2-star-ocean-the-second_protagonist-female_south-locomotion-v2-manifest_m8-w02_20261015-030458-eb352ac8.json`
  - 用户批准的静态基准帧（2026-10-14，用户回复「够了，可作为静止帧基准」）：south idle 单帧 selout v8 cloth-leather，48 逻辑像素；只是静态视觉基准，本闸门仍为 pending。决定记录：`docs/character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md`
    - 源图：`game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png`（sha256-bytes `ccf9d2a293e7f1b9…`）；清单：`game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-manifest_m8-v08_20261015-021600-2d6c5eff.json`（sha256-text-lf-v1 `3ba35811bf4d55b0…`）
    - 用户看过的 1280×720 实机截图：`outputs/rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-idle-selout-v8-h48_m8-v08_20261015-022215-e2203167.png`、`outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-idle-selout-v8-h48_m8-v08_20261015-022215-e2203167.png`；同次暗场景：`outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v8-h48_m8-v08_20261015-022215-e2203167.png`
    - QA 报告：`outputs/rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v8-visual-qa-report_m8-v08_20261015-022215-e2203167.json`；QA 说明：`docs/qa/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8_visual-qa-note_m8-v08_20261015-021600-c1694107.md`
    - 不批准：探索动画、其他朝向、替换运行时精灵、runtime-sprite 验收、场景画质闸门、人工试玩。
- [ ] G2c 战斗动画（MVP 必需；注册表 sideview_8_action_prototype_integrated / pending_art_approval；原型 8 动作 20 帧；资产清单 `playable-combat.protagonist-female` checked=false）
  - 原型清单：`game/assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_protagonist-female_sideview-combat-manifest_m8-prototype_20261014-143059-e2500154.json` · 存在
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 03. `liang-xu` · 梁序（main · 伙伴 #1 · 科技）

- 身份／发型锚点（注册表原文）：「灰白挑染盘发」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_liang-xu_character-sheet_v01_20261013-153556-c7630671.png` · 存在
- 就绪状态：有 32×48 占位帧（已被否定为画质基线） · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.liang-xu` stage=production checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：south、west、north、east；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 four_direction_native_walk_authored / pending_motion_and_art_approval；占位 待机 4 + 行走 16；正式帧数未批准）
  - 占位清单：`game/assets/characters/native-animation/rpg-2-star-ocean-the-second_liang-xu_native-animation-manifest_m8-v01_20261014-181000-c09d742e.json` · 存在
  - 注册表未引用的相关清单：`game/assets/characters/directional-prototypes/rpg-2-star-ocean-the-second_liang-xu_native-idle-manifest_m8-v03_20261014-180100-9d804f2a.json`
  - 注册表未引用的相关清单：`game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_liang-xu_exploration-direction-concepts-manifest_m8-v01_20261014-154500-fae9103a.json`
- [ ] G2c 战斗动画（MVP 必需；注册表 sideview_8_action_prototype_integrated / pending_art_approval；原型 8 动作 20 帧；资产清单 `playable-combat.liang-xu` checked=false）
  - 原型清单：`game/assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-combat-manifest_m8-prototype_20261014-143736-ddc3e7f9.json` · 存在
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 integrated_npc_prototype / pending_art_approval；资产清单 stage=production checked=false

### 04. `jiang-lan` · 蒋岚（main · 伙伴 #2 · 科技）

- 身份／发型锚点（注册表原文）：「剃短两侧与后脑、上梳立体发束、橙色细挑染」
- 来源立绘：**approved** · `outputs/rpg-2-star-ocean-the-second_jiang-lan_character-sheet_hairstyle-v02_20261013-161317-c21bd255.png` · 存在
- 就绪状态：有未登记的 32×48 占位清单 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.jiang-lan` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
  - 注册表未引用的相关清单：`game/assets/characters/native-animation/rpg-2-star-ocean-the-second_jiang-lan_native-exploration-manifest_m8-prototype_20261014-144703-dbe4b4c6.json`
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 05. `lin-que` · 林阙（main · 伙伴 #3 · 科技）

- 身份／发型锚点（注册表原文）：「深蓝色碎层短发」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_lin-que_character-sheet_v01_20261013-153556-88b92720.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.lin-que` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 06. `milo` · 米洛（main · 伙伴 #4 · 科技）

- 身份／发型锚点（注册表原文）：「极短圆寸、鬓角银色发片」
- 来源立绘：**approved** · `outputs/rpg-2-star-ocean-the-second_milo_character-sheet_hairstyle-v02_20261013-161317-f1651dc0.png` · 存在
- 就绪状态：有未登记的 32×48 占位清单 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.milo` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
  - 注册表未引用的相关清单：`game/assets/characters/native-animation/rpg-2-star-ocean-the-second_milo_native-exploration-manifest_m8-v01_20261014-185020-1976baf4.json`
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 07. `adi` · 阿荻（main · 伙伴 #5 · 自然）

- 身份／发型锚点（注册表原文）：「头顶环编、背后两条粗长辫」
- 来源立绘：**approved** · `outputs/rpg-2-star-ocean-the-second_adi_character-sheet_hairstyle-v02_20261013-161317-72861851.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.adi` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 08. `muxiu` · 牧修（main · 伙伴 #6 · 自然）

- 身份／发型锚点（注册表原文）：「单条及背长辫」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_muxiu_character-sheet_v01_20261013-153818-25247999.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.muxiu` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 09. `yanke` · 岩柯（main · 伙伴 #7 · 自然）

- 身份／发型锚点（注册表原文）：「短卷发与浓胡须」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_yanke_character-sheet_v01_20261013-153818-244380f3.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.yanke` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 10. `sangguo` · 桑果（main · 伙伴 #8 · 自然）

- 身份／发型锚点（注册表原文）：「蓬松短发与野花发饰」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_sangguo_character-sheet_v01_20261013-153818-40fbffff.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.sangguo` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 11. `nalia` · 娜丽娅（main · 伙伴 #9 · 奇幻）

- 身份／发型锚点（注册表原文）：「齐颌不对称直发、单侧红金细辫」
- 来源立绘：**approved** · `outputs/rpg-2-star-ocean-the-second_nalia_character-sheet_hairstyle-v02_20261013-161317-1a57ee29.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.nalia` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 12. `isai` · 伊赛（main · 伙伴 #10 · 奇幻）

- 身份／发型锚点（注册表原文）：「及背直发、中分、两条饰珠细辫」
- 来源立绘：**approved** · `outputs/rpg-2-star-ocean-the-second_isai_character-sheet_hairstyle-v02_20261013-161317-b40ff401.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.isai` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 13. `sain` · 赛恩（main · 伙伴 #11 · 奇幻）

- 身份／发型锚点（注册表原文）：「银白色蓬松中短发」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_sain_character-sheet_v01_20261013-154105-0ed8e534.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.sain` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 14. `daga` · 达伽（main · 伙伴 #12 · 奇幻）

- 身份／发型锚点（注册表原文）：「极短寸头与山纹侧边」
- 来源立绘：**approved** · `outputs/rpg-2-star-ocean-the-second_daga_character-sheet_hairstyle-v02_20261013-161317-9aafbee7.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.daga` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 15. `chenxian` · 晨弦（main · 伙伴 #13 · 魔法）

- 身份／发型锚点（注册表原文）：「整齐披肩发、后脑金扣」
- 来源立绘：**approved** · `outputs/rpg-2-star-ocean-the-second_chenxian_character-sheet_hairstyle-v02_20261013-161317-c0ab77ae.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.chenxian` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 16. `yelan` · 夜澜（main · 伙伴 #14 · 魔法）

- 身份／发型锚点（注册表原文）：「齐颌几何直发与整齐平刘海」
- 来源立绘：**approved** · `outputs/rpg-2-star-ocean-the-second_yelan_character-sheet_hairstyle-v02_20261013-161317-2d69b5da.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.yelan` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 17. `luowen` · 洛纹（main · 伙伴 #15 · 魔法）

- 身份／发型锚点（注册表原文）：「单侧剃短、另一侧斜长刘海的短发」
- 来源立绘：**approved** · `outputs/rpg-2-star-ocean-the-second_luowen_character-sheet_hairstyle-v02_20261013-161317-4182bff0.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.luowen` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 18. `ji-cheng` · 纪澄（side · 伙伴 #16 · 科技）

- 身份／发型锚点（注册表原文）：「沉静的旧资料修复师，乐于承认「无法判断」。耳后剃短、头顶齐肩银黑直发；墨绿夹克与折叠放大镜是识别点。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_ji-cheng_character-sheet_v01_20261013-190436-dcea1a37.png` · 存在
- 就绪状态：有 32×48 占位帧（已被否定为画质基线） · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.ji-cheng` stage=production checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：south、west、north、east；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 four_direction_native_walk_authored / pending_motion_and_art_approval；占位 待机 4 + 行走 16；正式帧数未批准）
  - 占位清单：`game/assets/characters/native-animation/rpg-2-star-ocean-the-second_ji-cheng_native-exploration-manifest_m8-prototype_20261014-142157-a4836b01.json` · 存在
- [ ] G2c 战斗动画（MVP 必需；注册表 sideview_8_action_prototype_integrated / pending_art_approval；原型 8 动作 20 帧；资产清单 `playable-combat.ji-cheng` checked=false）
  - 原型清单：`game/assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_ji-cheng_sideview-combat-manifest_m8-prototype_20261014-144815-54f4a48b.json` · 存在
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 integrated_npc_prototype / pending_art_approval；资产清单 stage=production checked=false

### 19. `zhou-he` · 周赫（side · 伙伴 #17 · 科技）

- 身份／发型锚点（注册表原文）：「精于合同与物流，讨厌用人情掩盖账目。光头、细框眼镜和折角铜色账簿构成独立轮廓。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_zhou-he_character-sheet_v01_20261013-190819-c2a519a0.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.zhou-he` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 20. `aiti` · 艾缇（side · 伙伴 #18 · 科技）

- 身份／发型锚点（注册表原文）：「年轻的公共系统审查员，语言直接，尊重不愿被量化的人。浅金色紧贴头皮的短卷发、黄色袖章和透明信息片。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_aiti_character-sheet_v01_20261013-190819-3366d67b.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.aiti` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 21. `ye-qiao` · 叶乔（side · 伙伴 #19 · 自然）

- 身份／发型锚点（注册表原文）：「建屋匠，务实而幽默，修缮比更换更令她自豪。灰褐色短辫贴头盘绕，木尺挂在宽腰带。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_ye-qiao_character-sheet_v01_20261013-190819-ad98572d.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.ye-qiao` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 22. `mi-yi` · 米漪（side · 伙伴 #20 · 自然）

- 身份／发型锚点（注册表原文）：「河道测绘人，话少但愿意分享自己走过的错误路线。浅褐色长直发编成低位鱼骨辫，蓝灰测绳横跨肩头。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_mi-yi_character-sheet_v01_20261013-190819-fe5c8d41.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.mi-yi` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 23. `luo-qi` · 罗栖（side · 伙伴 #21 · 自然）

- 身份／发型锚点（注册表原文）：「野地食材与药剂的老手，温和却对配方真实性毫不妥协。浓密白眉、短白胡须、平顶草帽和多层布包。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_luo-qi_character-sheet_v01_20261013-192354-9e32de79.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.luo-qi` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 24. `avila` · 阿维拉（side · 伙伴 #22 · 奇幻）

- 身份／发型锚点（注册表原文）：「有潮汐血统的巡岸人，平时完全是人类外貌；擅长听见水流变化，态度爽朗。深青色齐耳卷发、长叉枪和海盐白披巾。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_avila_character-sheet_v01_20261013-192354-1326eefe.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.avila` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 25. `kern` · 克恩（side · 伙伴 #23 · 奇幻）

- 身份／发型锚点（注册表原文）：「骨纹血统的石雕师，看着强硬，做事却非常细。极短红棕发、无胡须、石灰色宽围裙和裂纹锤。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_kern_character-sheet_v01_20261013-192354-db79abc8.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.kern` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 26. `lairui` · 莱芮（side · 伙伴 #24 · 奇幻）

- 身份／发型锚点（注册表原文）：「与夜鸟神话相关的远行信使，爱把旅途见闻讲成笑话。黑色双侧短羽形发夹、铜色眼睛和灰紫轻弓。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_lairui_character-sheet_v01_20261013-192354-3d9211d5.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.lairui` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 27. `mi-luo` · 弥罗（side · 伙伴 #25 · 魔法）

- 身份／发型锚点（注册表原文）：「研究光暗两源的抄写员，擅长把争论拆成可检验的问题。半长黑发有一道白色中分，左右肩各一条不同色书带。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_mi-luo_character-sheet_v01_20261013-192811-8d27196f.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.mi-luo` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 28. `heya` · 赫娅（side · 伙伴 #26 · 魔法）

- 身份／发型锚点（注册表原文）：「诊疗师，重视病人对自身身体的决定权，笑容克制但有耐心。赤褐色盘辫低置颈后，灰白医巾与暗红急救袋。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_heya_character-sheet_v01_20261013-192811-6cbcb12e.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.heya` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 29. `wu-li` · 乌礼（side · 伙伴 #27 · 魔法）

- 身份／发型锚点（注册表原文）：「剧场音效师，喜欢模仿别人的口音却很认真地征求同意。紫黑色自然卷高蓬发、细铃和无面具的便装。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_wu-li_character-sheet_v01_20261013-192811-13444778.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.wu-li` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 30. `huan-7` · 环七（side · 伙伴 #28 · 星外）

- 身份／发型锚点（注册表原文）：「城市口述史保管机器人，面对人类「回忆会变」这件事既困惑又着迷。圆环形单眼头部、青铜躯壳和可展开的录音翼片。」 — 机器人，无发型，头部外廓即锚点
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_huan-7_character-sheet_v01_20261013-192811-58229613.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.huan-7` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 31. `suiya` · 穗芽（side · 伙伴 #29 · 星外）

- 身份／发型锚点（注册表原文）：「维护人造植物景观与种子档案的机器人；星球上没有活体植株，它照料的是仿生材料与历史资料。透明叶片状头冠、奶白机身和绿色液囊。」 — 机器人，无发型，头部外廓即锚点
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_suiya_character-sheet_v01_20261013-193120-f4dbe48d.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.suiya` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 32. `zhongdu` · 钟渡（side · 伙伴 #30 · 星外）

- 身份／发型锚点（注册表原文）：「公共交通调度机器人，说话以路线开头，逐渐学会人们也会为了陪伴绕路。方形站牌头、黄铜钟摆胸灯和蓝白短披布。」 — 机器人，无发型，头部外廓即锚点
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_zhongdu_character-sheet_v01_20261013-193120-12c4826e.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.zhongdu` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 33. `zhao-ling` · 赵铃（situational · 伙伴 #31 · 科技）

- 身份／发型锚点（注册表原文）：「城市无线电修理员，热衷把复杂信息讲清楚。湖蓝耳机、整齐的侧分短发和便携天线。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_zhao-ling_character-sheet_v01_20261013-193120-54215370.png` · 存在
- 就绪状态：有 32×48 占位帧（已被否定为画质基线） · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.zhao-ling` stage=production checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：south、west、north、east；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 four_direction_native_walk_authored / pending_motion_and_art_approval；占位 待机 4 + 行走 16；正式帧数未批准）
  - 占位清单：`game/assets/characters/native-animation/rpg-2-star-ocean-the-second_zhao-ling_native-exploration-manifest_m8-v01_20261014-142000-b123903c.json` · 存在
- [ ] G2c 战斗动画（MVP 必需；注册表 sideview_8_action_prototype_integrated / pending_art_approval；原型 8 动作 20 帧；资产清单 `playable-combat.zhao-ling` checked=false）
  - 原型清单：`game/assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_zhao-ling_sideview-combat-manifest_m8-prototype_20261014-144336-7d0dd6cc.json` · 存在
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 integrated_npc_prototype / pending_art_approval；资产清单 stage=production checked=false

### 34. `pei-zhi` · 裴支（situational · 伙伴 #32 · 科技）

- 身份／发型锚点（注册表原文）：「旧设备修理铺老板，修理时会耐心解释原理。红褐色平头、焊接面罩常挂在颈后、蓝色绝缘手套。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_pei-zhi_character-sheet_v01_20261013-193120-0397bc6c.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.pei-zhi` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 35. `an-suo` · 安索（situational · 伙伴 #33 · 科技）

- 身份／发型锚点（注册表原文）：「公共运输签约员，讲究准时也善于应对意外。灰色一字胡、无帽短发、带孔票夹。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_an-suo_character-sheet_v01_20261013-193428-86708847.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.an-suo` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 36. `su-yan` · 苏砚（situational · 伙伴 #34 · 科技）

- 身份／发型锚点（注册表原文）：「街区志愿救护员，性格急但手很稳。两侧剃短、上方紫灰色小卷、腕部红白灯带。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_su-yan_character-sheet_v01_20261013-193428-bc523491.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.su-yan` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 37. `tao-yu` · 陶榆（situational · 伙伴 #35 · 自然）

- 身份／发型锚点（注册表原文）：「木桥匠，踏实、爱唱走调的工作歌。短而密的黑卷发，右肩木纹护片与可拆工具锤。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_tao-yu_character-sheet_v01_20261013-193428-61dd58a2.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.tao-yu` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 38. `ruan-tian` · 阮田（situational · 伙伴 #36 · 自然）

- 身份／发型锚点（注册表原文）：「照护驮兽的年轻人，和陌生人说话会先观察表情。两侧各一簇短辫、橘棕披肩、骨制小铃。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_ruan-tian_character-sheet_v01_20261013-193428-ce87ebee.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.ruan-tian` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 39. `bu-he` · 布禾（situational · 伙伴 #37 · 自然）

- 身份／发型锚点（注册表原文）：「社区炊事师，手快、记得每个人的口味。乌黑齐肩直发包在方布巾里，铜锅盖背在肩后。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_bu-he_character-sheet_v01_20261013-193838-3a285ca4.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.bu-he` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 40. `han-ze` · 韩泽（situational · 伙伴 #38 · 自然）

- 身份／发型锚点（注册表原文）：「沿路交换工具与粮食的经纪人，乐于让双方知道彼此的真实需求。深棕短莫霍克发、草绳卷轴、旧式秤砣。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_han-ze_character-sheet_v01_20261013-193838-dd9d7fbc.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.han-ze` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 41. `xida` · 席妲（situational · 伙伴 #39 · 奇幻）

- 身份／发型锚点（注册表原文）：「出自日轮传说血统的灯塔看守人，外貌平常，目光敏锐。麦金色极短发、浅色长耳坠、方形提灯。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_xida_character-sheet_v01_20261013-193838-dd1fdcbe.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.xida` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 42. `gu-lin` · 顾鳞（situational · 伙伴 #40 · 奇幻）

- 身份／发型锚点（注册表原文）：「有蛇类神话血统的年轻练习者，努力摆脱别人对血统的固定期待。黑发齐耳并在左侧编一根细辫，绿色腕绳。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_gu-lin_character-sheet_v01_20261013-193838-16710012.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.gu-lin` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 43. `ruima` · 瑞玛（situational · 伙伴 #41 · 奇幻）

- 身份／发型锚点（注册表原文）：「与狼传说有关的动物照护员，坦率但并不冲动。银灰色低束发、厚毛边短外套、双音呼哨。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_ruima_character-sheet_v01_20261013-194328-964e67e2.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.ruima` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 44. `tao-li` · 陶粒（situational · 伙伴 #42 · 奇幻）

- 身份／发型锚点（注册表原文）：「研究古老血统器物的收藏修复师，宁愿标明「来历不明」也不编造传奇。光亮额头、短白发圈和沉重的布纹箱。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_tao-li_character-sheet_v01_20261013-194328-081482e6.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.tao-li` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 45. `lin-yan` · 霖砚（situational · 伙伴 #43 · 魔法）

- 身份／发型锚点（注册表原文）：「在光暗两种治疗方法之间做实证记录的医师，不把不同意见当成敌意。蓝黑色低马尾、两色药袋。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_lin-yan_character-sheet_v01_20261013-194328-ff31ae19.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.lin-yan` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 46. `he-huai` · 何槐（situational · 伙伴 #44 · 魔法）

- 身份／发型锚点（注册表原文）：「社区照明维护者，喜欢听年轻人质疑旧规矩。银白色齐颈波浪发、琥珀镜片和小圆灯。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_he-huai_character-sheet_v01_20261013-194328-4451b802.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.he-huai` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 47. `xuan-ya` · 玄芽（situational · 伙伴 #45 · 魔法）

- 身份／发型锚点（注册表原文）：「专门照看私人物件保存室的暗系术者，温和、守口如瓶。墨紫色双短髻、黑银钥匙扣。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_xuan-ya_character-sheet_v01_20261013-194543-be791613.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.xuan-ya` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 48. `que-zhi` · 雀枝（situational · 伙伴 #46 · 魔法）

- 身份／发型锚点（注册表原文）：「魔法材料协议协调员，擅长让不同源系共同受益。深栗色圆弧刘海、左右不同色的袖套与双页合同。」
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_que-zhi_character-sheet_v01_20261013-194543-4ac30749.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.que-zhi` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 49. `menling` · 门铃（situational · 伙伴 #47 · 星外）

- 身份／发型锚点（注册表原文）：「公共建筑维修机器人，见面先确认门是否好开，随后才想到问访客感受。门拱形头盔、黄铜铰链手臂、白色工具箱。」 — 机器人，无发型，头部外廓即锚点
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_menling_character-sheet_v01_20261013-194543-6c4dc2bc.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.menling` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 50. `lingbing` · 零饼（situational · 伙伴 #48 · 星外）

- 身份／发型锚点（注册表原文）：「市场摊位机器人，把顾客的闲聊也当作有价值的交易体验。扁圆饼状显示头、可折叠小柜台、蓝色轮足。」 — 机器人，无发型，头部外廓即锚点
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_lingbing_character-sheet_v01_20261013-194543-e84188a0.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.lingbing` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 51. `lengjing` · 棱镜（situational · 伙伴 #49 · 星外）

- 身份／发型锚点（注册表原文）：「公共博物馆引导与安全机器人，坚持先疏散再处理故障；与敌对的献祭组织防卫机不同。多面棱柱头、乳白护板、细长指示臂。」 — 机器人，无发型，头部外廓即锚点
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_lengjing_character-sheet_v01_20261013-194650-4864f54c.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.lengjing` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

### 52. `yuyin` · 余音（situational · 伙伴 #50 · 星外）

- 身份／发型锚点（注册表原文）：「剧场投影机器人，能重现舞台，却仍在学习为什么观众会为虚构人物流泪。半月形发光面罩、靛色幕布披肩、投影模块。」 — 机器人，无发型，头部外廓即锚点
- 来源立绘：**concept** · `outputs/rpg-2-star-ocean-the-second_yuyin_character-sheet_v01_20261013-194650-47abe995.png` · 存在
- 就绪状态：未开始 · 入库阶段 0
- 美术验收：**pending**（仅用户；资产清单 `runtime-sprite.yuyin` stage=planned checked=false）
- [ ] G1 四方向正式帧 0/4（占位方向：无；西向绘制方式：未声明）
- [ ] G2 探索动画（注册表 not_started / pending；占位 待机 0 + 行走 0；正式帧数未批准）
- G2c 战斗动画：资产清单 scope=Full，不属 MVP（注册表 not_started）
- [ ] G3 比例 48 逻辑像素；master/scale/cell_size/ground_pin 未定
- [ ] G4 QA：自动检查未运行（无正式帧）；实机截图回执无；人工身份/方向复核 pending
- [ ] G5 用户美术验收：pending，无回执
- [ ] 显示图：注册表 not_started / pending；资产清单 stage=planned checked=false

## 待人工复核：发型锚点可能重复或含糊

以下只是 48 px 精灵尺度下的**潜在混淆提示**，不改写角色设定、发型或已批准立绘；是否需要处理由用户决定。

- 完全相同的锚点文本：无。

| 组 | 成员与注册表原文 | 关注点 | 决定 |
|---|---|---|---|
| chin-length-straight | `nalia` 娜丽娅：「齐颌不对称直发、单侧红金细辫」<br>`yelan` 夜澜：「齐颌几何直发与整齐平刘海」 | 两者锚点都以「齐颌…直发」开头；区分依赖单侧细辫与平刘海，48 px 背面需确认仍可分。 | 待人工复核 |
| single-thin-side-braid | `nalia` 娜丽娅：「齐颌不对称直发、单侧红金细辫」<br>`gu-lin` 顾鳞：「有蛇类神话血统的年轻练习者，努力摆脱别人对血统的固定期待。黑发齐耳并在左侧编一根细辫，绿色腕绳。」 | 两者都含单侧细辫，且发长均在齐颌／齐耳附近；区分依赖发色与细辫颜色。 | 待人工复核 |
| single-long-braid | `muxiu` 牧修：「单条及背长辫」<br>`mi-yi` 米漪：「河道测绘人，话少但愿意分享自己走过的错误路线。浅褐色长直发编成低位鱼骨辫，蓝灰测绳横跨肩头。」 | 单条及背长辫 vs 低位鱼骨辫：背面同为单条下垂辫，需确认长度/编法在 48 px 可见。 | 待人工复核 |
| twin-braids | `adi` 阿荻：「头顶环编、背后两条粗长辫」<br>`isai` 伊赛：「及背直发、中分、两条饰珠细辫」<br>`ruan-tian` 阮田：「照护驮兽的年轻人，和陌生人说话会先观察表情。两侧各一簇短辫、橘棕披肩、骨制小铃。」 | 均为两条辫；粗长 / 饰珠细辫 / 两侧短辫簇的差异需在北向（背面）确认。 | 待人工复核 |
| low-coiled-or-bun | `liang-xu` 梁序：「灰白挑染盘发」<br>`heya` 赫娅：「诊疗师，重视病人对自身身体的决定权，笑容克制但有耐心。赤褐色盘辫低置颈后，灰白医巾与暗红急救袋。」<br>`ye-qiao` 叶乔：「建屋匠，务实而幽默，修缮比更换更令她自豪。灰褐色短辫贴头盘绕，木尺挂在宽腰带。」<br>`xuan-ya` 玄芽：「专门照看私人物件保存室的暗系术者，温和、守口如瓶。墨紫色双短髻、黑银钥匙扣。」 | 盘发 / 颈后盘辫 / 贴头盘绕短辫 / 双短髻都是贴头团状轮廓，需核对位置与数量。 | 待人工复核 |
| very-short-crop | `milo` 米洛：「极短圆寸、鬓角银色发片」<br>`daga` 达伽：「极短寸头与山纹侧边」<br>`xida` 席妲：「出自日轮传说血统的灯塔看守人，外貌平常，目光敏锐。麦金色极短发、浅色长耳坠、方形提灯。」<br>`kern` 克恩：「骨纹血统的石雕师，看着强硬，做事却非常细。极短红棕发、无胡须、石灰色宽围裙和裂纹锤。」<br>`pei-zhi` 裴支：「旧设备修理铺老板，修理时会耐心解释原理。红褐色平头、焊接面罩常挂在颈后、蓝色绝缘手套。」 | 极短寸／圆寸／平头在 48 px 下轮廓接近；区分依赖鬓角发片、侧纹、发色。 | 待人工复核 |
| shaved-sides | `jiang-lan` 蒋岚：「剃短两侧与后脑、上梳立体发束、橙色细挑染」<br>`su-yan` 苏砚：「街区志愿救护员，性格急但手很稳。两侧剃短、上方紫灰色小卷、腕部红白灯带。」<br>`luowen` 洛纹：「单侧剃短、另一侧斜长刘海的短发」<br>`ji-cheng` 纪澄：「沉静的旧资料修复师，乐于承认「无法判断」。耳后剃短、头顶齐肩银黑直发；墨绿夹克与折叠放大镜是识别点。」<br>`han-ze` 韩泽：「沿路交换工具与粮食的经纪人，乐于让双方知道彼此的真实需求。深棕短莫霍克发、草绳卷轴、旧式秤砣。」 | 多种剃侧／剃短造型；上方发束、卷、斜刘海、齐肩直发、莫霍克需各自保留独特外廓。 | 待人工复核 |
| fluffy-short | `protagonist-male` 主角·男：「蓬松层次短发」<br>`sain` 赛恩：「银白色蓬松中短发」<br>`sangguo` 桑果：「蓬松短发与野花发饰」<br>`lin-que` 林阙：「深蓝色碎层短发」 | 蓬松／层次／碎层短发相近；主角男为可玩角色，需确认与同屏伙伴不混淆。 | 待人工复核 |
| short-curls | `yanke` 岩柯：「短卷发与浓胡须」<br>`tao-yu` 陶榆：「木桥匠，踏实、爱唱走调的工作歌。短而密的黑卷发，右肩木纹护片与可拆工具锤。」<br>`aiti` 艾缇：「年轻的公共系统审查员，语言直接，尊重不愿被量化的人。浅金色紧贴头皮的短卷发、黄色袖章和透明信息片。」<br>`wu-li` 乌礼：「剧场音效师，喜欢模仿别人的口音却很认真地征求同意。紫黑色自然卷高蓬发、细铃和无面具的便装。」 | 短卷发类；区分依赖胡须、发色、贴头程度与高蓬体量。 | 待人工复核 |
| low-tied-back | `lin-yan` 霖砚：「在光暗两种治疗方法之间做实证记录的医师，不把不同意见当成敌意。蓝黑色低马尾、两色药袋。」<br>`ruima` 瑞玛：「与狼传说有关的动物照护员，坦率但并不冲动。银灰色低束发、厚毛边短外套、双音呼哨。」 | 低马尾 vs 低束发，文字描述几乎同义；区分只剩发色（蓝黑 / 银灰）。 | 待人工复核 |
| silver-white-hair | `liang-xu` 梁序：「灰白挑染盘发」<br>`sain` 赛恩：「银白色蓬松中短发」<br>`he-huai` 何槐：「社区照明维护者，喜欢听年轻人质疑旧规矩。银白色齐颈波浪发、琥珀镜片和小圆灯。」<br>`ruima` 瑞玛：「与狼传说有关的动物照护员，坦率但并不冲动。银灰色低束发、厚毛边短外套、双音呼哨。」<br>`ji-cheng` 纪澄：「沉静的旧资料修复师，乐于承认「无法判断」。耳后剃短、头顶齐肩银黑直发；墨绿夹克与折叠放大镜是识别点。」<br>`tao-li` 陶粒：「研究古老血统器物的收藏修复师，宁愿标明「来历不明」也不编造传奇。光亮额头、短白发圈和沉重的布纹箱。」 | 银白／灰白发色集中；颜色不能作为唯一身份提示（视觉规格要求），需靠外廓区分。 | 待人工复核 |
| shoulder-length-straight | `chenxian` 晨弦：「整齐披肩发、后脑金扣」<br>`ji-cheng` 纪澄：「沉静的旧资料修复师，乐于承认「无法判断」。耳后剃短、头顶齐肩银黑直发；墨绿夹克与折叠放大镜是识别点。」<br>`bu-he` 布禾：「社区炊事师，手快、记得每个人的口味。乌黑齐肩直发包在方布巾里，铜锅盖背在肩后。」 | 披肩／齐肩直发；布禾包在布巾里、纪澄耳后剃短，需确认外廓不同。 | 待人工复核 |
| bald-or-receding | `zhou-he` 周赫：「精于合同与物流，讨厌用人情掩盖账目。光头、细框眼镜和折角铜色账簿构成独立轮廓。」<br>`tao-li` 陶粒：「研究古老血统器物的收藏修复师，宁愿标明「来历不明」也不编造传奇。光亮额头、短白发圈和沉重的布纹箱。」 | 光头 vs 光亮额头＋短白发圈；侧/背面需确认可分。 | 待人工复核 |

锚点本身含糊：

- `lairui`：锚点只描述发夹（「黑色双侧短羽形发夹」），未写发型本身。
- `an-suo`：锚点为「无帽短发」，发型描述泛化；主要识别点在一字胡与票夹。
- `luo-qi`：锚点未描述发型，只有白眉、胡须与草帽；草帽是否常驻需确认。
- 机器人变体无发型（7 个）：`huan-7`、`suiya`、`zhongdu`、`menling`、`lingbing`、`lengjing`、`yuyin`；需确认以头部外廓代替发型锚点。
- 注册表锚点字段混有性格描述（35 个，编号 16–50）：本清单原文引用，未自行抽取发型短语；生产前宜由人工确认 48 px 可见的发型／头部锚点。

## 路径核对与注册表差异

- 缺失文件：0 个。注册表与已登记清单引用的所有立绘、占位帧、清单和帧文件均存在。
- 已引用但未纳入 git：0 个（文件存在，仅工作区未跟踪；本任务不暂存）。
- 注册表未引用、按文件名发现的清单中未纳入 git：0 个（不计入上一项；只检查清单文件本身，不检查其帧文件）。
- 注册表差异：3 条（只记录，未修改注册表）。
  - liang-xu: exploration manifest id is 'liang_xu', registry visual_id is 'liang-xu'
  - jiang-lan: registry exploration is not_started but unregistered manifest exists: game/assets/characters/native-animation/rpg-2-star-ocean-the-second_jiang-lan_native-exploration-manifest_m8-prototype_20261014-144703-dbe4b4c6.json
  - milo: registry exploration is not_started but unregistered manifest exists: game/assets/characters/native-animation/rpg-2-star-ocean-the-second_milo_native-exploration-manifest_m8-v01_20261014-185020-1976baf4.json

## 注意事项

- 「有 32×48 占位帧」不等于完成任何闸门：创作者已否定该帧为正式画质基线。
- 战斗原型帧（5 个 MVP 可玩形象，每个 20 帧）已接入可玩战场；资产清单用户勾选验收 0/5。
- 本清单不推进任何计数；生成时资产清单 runtime-sprite 用户勾选 0/52（进度文档计数以其自身为准，本脚本不改写）。
