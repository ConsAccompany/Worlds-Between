extends Node

signal language_changed

const STRINGS := {
	"zh": {
		"title": "界间行者",
		"subtitle": "探索世界 · 结识伙伴",
		"start": "开始探索",
		"setup_title": "创建主角",
		"setup_name": "姓名",
		"setup_gender": "外观",
		"setup_male": "男性外观", "setup_female": "女性外观",
		"setup_help": "18 岁，结束一年训练，即将首次探索地表。可按自己的节奏招募伙伴。",
		"setup_controls": "操作：地图选目的地；WASD 移动；E 交互；接触敌人进入战斗。",
		"setup_skip": "跳过指引并出发", "setup_start": "开始探索", "setup_back": "返回菜单",
		"language": "语言：中文",
		"quit": "退出",
		"room_title": "工程原型 · 地下社区",
		"room_help": "WASD / 方向键移动 · Esc 返回主菜单",
		"back": "返回主菜单",
		"map_title": "世界地图 · 科技板块",
		"map_help": "点击目的地进入场景 · 普通旅行不推进日期",
		"map_back": "主菜单",
		"area_city": "科技城市片区",
		"area_outskirts": "城外通道",
		"area_ruins": "旧文明遗址",
		"area_city_hint": "街道与公共设施 · 可与维修员交谈",
		"area_outskirts_hint": "开阔路线 · 可绕过巡逻机械",
		"area_ruins_hint": "前文明设施 · 小心自动防卫机",
		"area_help": "WASD 移动 · E 交互 · Esc 地图",
		"area_back": "世界地图",
		"npc_city": "维修员：这里的旧设备还能继续使用。",
		"npc_outskirts": "巡路者：走北侧就能绕开巡逻机械。",
		"npc_ruins": "勘察员：遗址记录需要仔细核对。",
		"npc_prompt": "靠近人物或标记按 E 交互",
		"enemy_label": "自动机械",
		"battle_title": "即时战斗 · %s",
		"battle_help": "A/D 移动 · J 攻击 · K 闪避 · L 防御 · Q 个人技 · R 职业技 · Tab 换人 · P 暂停 · T 自动",
		"battle_attack": "攻击",
		"battle_dodge": "闪避",
		"battle_guard": "防御",
		"battle_hp": "生命",
		"battle_energy": "能量",
		"battle_enemy_hp": "敌人生命",
		"battle_telegraph": "敌人蓄力中！",
		"battle_ready": "靠近敌人并攻击。闪避消耗 12 能量；防御受击消耗 6 能量。",
		"battle_far": "距离过远",
		"battle_hit": "命中敌人",
		"battle_no_energy": "能量不足",
		"battle_dodge_feedback": "闪避成功",
		"battle_guard_feedback": "防御减伤",
		"battle_hurt": "受到攻击",
		"battle_win": "战斗胜利",
		"battle_loss": "战斗失败",
		"battle_win_note": "战后生命与能量各增加上限的 20%，最多回满。",
		"battle_loss_note": "队伍倒下，返回主菜单。",
		"battle_continue": "继续探索",
		"battle_menu": "返回主菜单",
		"enemy_patrol": "巡逻机械",
		"enemy_sentry": "自动防卫机",
		"member_hero": "旅人",
		"member_liang": "梁序",
		"member_zhao": "赵铃",
		"member_ji": "纪澄",
		"recruit_prompt": "靠近人物按 E 交谈",
		"recruit_invite": "邀请入队",
		"recruit_later": "暂不邀请",
		"recruit_full": "当前队伍已满（最多 5 人）。",
		"recruit_joined": "%s 已加入队伍。",
		"recruit_liang": "梁序：训练结束了。若你愿意，我仍能同行，帮你判断情势。",
		"recruit_zhao": "赵铃：这座中继站正在失去信号。修好它以后，我想看看更远的地方。",
		"recruit_ji_locked": "纪澄：先看看遗址中央的记录台，再谈同行的事。",
		"recruit_ji": "纪澄：资料不完整，正好需要有人一起验证。要同行吗？",
		"relic_prompt": "靠近记录台按 E 调查",
		"relic_marker": "记录台",
		"relic_done": "已协助纪澄核对一条旧记录。现在可以邀请她同行。",
		"battle_pause_title": "暂停指令 · 当前操纵：%s",
		"battle_resume": "继续战斗",
		"battle_skill_use": "使用技能",
		"battle_target": "指令对象：%s",
		"battle_focus": "集中攻击",
		"battle_defend": "优先防御",
		"battle_skill_order": "优先技能",
		"battle_default": "按 AI 策略",
		"ai_policy_balanced": "AI：平衡",
		"ai_policy_aggressive": "AI：进攻",
		"ai_policy_cautious": "AI：谨慎",
		"battle_auto_on": "全自动：开",
		"battle_auto_off": "全自动：关",
		"battle_skill_hero": "临场理解",
		"battle_skill_liang": "战术校准",
		"battle_skill_zhao": "回声测距",
		"battle_skill_ji": "断层回读",
		"battle_skill_used": "%s 使用了 %s。",
		"battle_member_down": "%s 倒下了。",
		"battle_party_status": "队伍：%s",
		"growth_title": "角色成长与职业",
		"growth_open": "角色与职业",
		"growth_back": "返回地图",
		"growth_pending": "达到十级关口：请选择职业去向",
		"growth_level": "等级 %d · XP %d/%d · JP %d",
		"growth_aptitudes": "天分  武 %d · 变 %d · 学 %d · 灵 %d  （60 可入职）",
		"growth_job": "当前：%s · 第 %d 阶",
		"growth_stay": "留任当前职业",
		"growth_promote": "晋升当前系列",
		"growth_switch": "转入 %s",
		"growth_upgrade": "升级技能 %s · %d JP",
		"growth_skill": "职业技能：%s",
		"growth_personal": "个人技能 %s Lv%d · 升级 %d JP",
		"save_title": "存档与读取", "save_open": "存档", "save_load_open": "读取游戏",
		"save_back": "返回", "save_manual_slot": "手动栏 %d", "save_write": "保存到此栏",
		"save_load": "读取", "save_empty": "空栏位", "save_auto": "自动记录",
		"save_before_battle": "开战前", "save_after_battle": "胜利后", "save_manual_note": "手动保存", "save_party_talk": "同行交流", "save_field_assist": "伙伴实地协助",
		"save_summary": "%s · Lv%d · %d 人 · %s",
		"save_ok": "已保存至 %s", "save_failed": "存档失败", "save_load_failed": "读取失败或存档不兼容",
		"save_version_old": "旧版存档 · 无法读取", "save_no_records": "暂无自动记录",
		"growth_rewards": "战斗奖励：%d XP / %d JP；候补获得 25%%",
		"growth_locked": "天分未达到 60",
		"growth_done": "职业选择已完成",
		"job_skill_sword_slash": "破锋斩", "job_skill_sword_arc": "回旋剑势",
		"job_skill_firearms_shot": "精准射击", "job_skill_firearms_burst": "连发压制",
		"job_skill_tactics_mark": "战术标记", "job_skill_tactics_rally": "全队整备",
		"job_skill_relics_echo": "遗物共鸣", "job_skill_relics_delay": "时序迟滞",
		"bypass_notice": "已绕过敌人，抵达另一侧。",
		"field_log": "实地日志",
		"field_log_hint": "任意顺序探索三处地点；完成勘察、核对中继与遗址记录、观察机械，最后回城汇报。每地还有两处可选痕迹，可带当地伙伴回终端解读。",
		"field_log_count": "地点 %d/3 · 勘察 %d/3 · 中继 %s · 记录 %s · 机械 %s",
		"field_assist_log": "伙伴实地协助 %d/3（可选）",
		"field_trace_log": "现场痕迹 %d/6（可选）",
		"field_trace_marker": "痕迹",
		"field_trace_found": "记录了现场痕迹。可带当地伙伴回终端解读。",
		"field_trace_need": "需要先查看附近两处现场痕迹，再让 %s 解读。",
		"field_trace_city_0": "城市痕迹：旧路牌保留了双重编号，标记落在维修线与储能线的交会处。",
		"field_trace_city_1": "城市痕迹：清晨的巡检印章叠在前一日配额表上，时间栏未同步。",
		"field_trace_outskirts_0": "城外痕迹：废弃导管表面有新的探测划痕，声音却从更深处传来。",
		"field_trace_outskirts_1": "城外痕迹：地面维护标记偏离旧导管，指向尚在工作的地下线。",
		"field_trace_ruins_0": "遗址痕迹：墙缝里有三种修补填料，磨损程度互不相同。",
		"field_trace_ruins_1": "遗址痕迹：最外层固定件使用现行规格，不能与旧层归为同一年代。",
		"field_assist_marker_city": "配额总表", "field_assist_marker_outskirts": "回声节点", "field_assist_marker_ruins": "地层面板",
		"field_assist_need": "需要 %s 同行才能解析。先邀请对方，之后随时可以回来。",
		"field_assist_use": "运用个人专长", "field_assist_close": "关闭", "field_assist_recorded": "已记录",
		"field_assist_ready_city": "梁序可以用战术校准，对照配额表里的重复编号。",
		"field_assist_ready_outskirts": "赵铃可以用回声测距，判断哪条线路仍在工作。",
		"field_assist_ready_ruins": "纪澄可以用断层回读，辨认面板经历过的修复顺序。",
		"field_assist_result_city": "梁序发现同一编号被用于维修和储能；批准记录却缺失了。",
		"field_assist_result_outskirts": "赵铃确认回声来自废弃导管，现行线路藏在其下方。",
		"field_assist_result_ruins": "纪澄辨出三次不同时期的修补；最后一次使用了现行材料。",
		"field_assist_reward": "%s 获得 4 JP，默契 +2。观察已收录在实地日志。",
		"survey_marker": "实地勘察入口", "survey_prompt": "靠近勘察入口按 E 进入",
		"survey_log": "实地勘察：城市 %s · 城外 %s · 遗址 %s",
		"survey_progress": "线索 %d/6 · 本地勘察 %s",
		"survey_help": "WASD 移动 · E 查看线索/门/终端 · Esc 返回",
		"survey_next": "深入", "survey_leave": "返回地表", "survey_previous": "返回外层",
		"survey_terminal": "研判终端", "survey_locked": "先查看此处六条线索，再作判断。",
		"survey_link_title": "证据关联", "survey_link_instruction": "选择两条有关联的线索。已找到 %d/3 组。",
		"survey_link_wrong": "这两条线索暂时无法形成可核查的关联。请再比较。",
		"survey_link_found": "这组关联已记录。", "survey_link_continue": "进入最终研判",
		"survey_notes": "线索笔记", "survey_notes_back": "返回研判", "survey_notes_previous": "上一条", "survey_notes_next": "下一条",
		"survey_retry": "这项判断缺少证据支持。可以重新对照线索。",
		"survey_completed": "此处勘察已完成。资料仍可重新查看。",
		"survey_close": "继续探索", "save_survey_note": "勘察记录",
		"survey_reward": "勘察奖励：上场角色各获 8 JP，候补各获 2 JP。",
		"talk_open": "同行交流", "talk_title": "旅途中的交流", "talk_help": "完成调查并邀请伙伴后，对话会逐步开放；随时可以回来重听。",
		"talk_empty": "还没有可聊的话题。继续探索并邀请伙伴。", "talk_back": "返回地图",
		"talk_next": "继续", "talk_finish": "结束交流", "talk_topics": "话题列表", "talk_seen": "已听过", "talk_bond": "默契 %d",
		"run_time": "本次探索 %02d:%02d",
		"field_yes": "完成", "field_no": "待办",
		"relay_marker": "中继站", "relay_prompt": "靠近中继站按 E 调查",
		"relay_done": "中继站的故障来自一段被重复改写的线路图。赵铃已记下异常。",
		"relay_record": "中继站记录：维护图纸被多次改写；原始线路用途仍未确认。",
		"archive_record": "遗址记录：前文明资料残缺，其中一条能源调度记录与现行网络的编号相同。",
		"machine_record": "机械记录：已观察到自动机械的行动模式。",
		"report_marker": "实地汇报", "report_prompt": "靠近汇报台按 E 查看进度",
		"report_locked": "仍需完成实地日志中的调查项目。",
		"report_ready": "资料已齐备。靠近汇报台按 E 提交。",
		"report_title": "科技板块试玩完成",
		"report_summary": "%s 已走访三处地点、完成三处实地勘察、核对两份记录，并观察了自动机械。同行伙伴：%d/3。",
		"report_continue": "继续自由探索", "report_map": "返回世界地图",
		"report_note": "这份资料揭示了新的问题。完整故事将在后续章节展开。",
		"report_receipt": "本地试玩记录已保存。",
	},
	"en": {
		"title": "Worlds Between",
		"subtitle": "Explore worlds · Meet companions",
		"start": "Start exploring",
		"setup_title": "Create your traveler",
		"setup_name": "Name",
		"setup_gender": "Appearance",
		"setup_male": "Masculine", "setup_female": "Feminine",
		"setup_help": "At 18, you have finished a year of training and are ready to explore the surface. Recruit companions at your own pace.",
		"setup_controls": "Controls: choose a map destination; move with WASD; press E to interact; contact an enemy to fight.",
		"setup_skip": "Skip guide and depart", "setup_start": "Start exploring", "setup_back": "Main menu",
		"language": "Language: English",
		"quit": "Quit",
		"room_title": "Foundation prototype · Underground community",
		"room_help": "WASD / arrows to move · Esc for menu",
		"back": "Back to menu",
		"map_title": "World map · Science region",
		"map_help": "Click a destination · Ordinary travel does not advance the calendar",
		"map_back": "Main menu",
		"area_city": "Science city district",
		"area_outskirts": "Outer passage",
		"area_ruins": "Old civilization ruins",
		"area_city_hint": "Streets and public works · Talk to a technician",
		"area_outskirts_hint": "Open routes · Bypass a patrol machine",
		"area_ruins_hint": "Pre-reset facility · Watch for automated defense",
		"area_help": "WASD move · E interact · Esc map",
		"area_back": "World map",
		"npc_city": "Technician: These old devices still work well.",
		"npc_outskirts": "Path watcher: Take the north route past the patrol.",
		"npc_ruins": "Surveyor: The ruin records need careful checking.",
		"npc_prompt": "Press E near a person or marker to interact",
		"enemy_label": "Automated machine",
		"battle_title": "Real-time battle · %s",
		"battle_help": "A/D move · J attack · K dodge · L guard · Q personal · R job · Tab swap · P pause · T auto",
		"battle_attack": "Attack",
		"battle_dodge": "Dodge",
		"battle_guard": "Guard",
		"battle_hp": "HP",
		"battle_energy": "Energy",
		"battle_enemy_hp": "Enemy HP",
		"battle_telegraph": "Enemy winding up!",
		"battle_ready": "Close in and attack. Dodge costs 12 energy; guarding a hit costs 6.",
		"battle_far": "Too far away",
		"battle_hit": "Hit the enemy",
		"battle_no_energy": "Not enough energy",
		"battle_dodge_feedback": "Dodged the attack",
		"battle_guard_feedback": "Guard reduced damage",
		"battle_hurt": "Took a hit",
		"battle_win": "Victory",
		"battle_loss": "Defeat",
		"battle_win_note": "After battle, HP and energy each gain 20% of their maximum, capped at full.",
		"battle_loss_note": "Your party fell. Returning to the main menu.",
		"battle_continue": "Keep exploring",
		"battle_menu": "Main menu",
		"enemy_patrol": "Patrol machine",
		"enemy_sentry": "Defense machine",
		"member_hero": "Traveler",
		"member_liang": "Liang Xu",
		"member_zhao": "Zhao Ling",
		"member_ji": "Ji Cheng",
		"recruit_prompt": "Approach someone and press E to talk",
		"recruit_invite": "Invite to party",
		"recruit_later": "Maybe later",
		"recruit_full": "The active party is full (maximum 5).",
		"recruit_joined": "%s joined your party.",
		"recruit_liang": "Liang Xu: Your training is over. I can still travel with you and help assess what we find.",
		"recruit_zhao": "Zhao Ling: This relay is losing signal. Once it's fixed, I want to see what lies farther away.",
		"recruit_ji_locked": "Ji Cheng: Examine the records console in the center first. Then we can talk about traveling together.",
		"recruit_ji": "Ji Cheng: These records are incomplete. I'd welcome help checking them. Shall we travel together?",
		"relic_prompt": "Approach the records console and press E",
		"relic_marker": "Records",
		"relic_done": "You helped Ji Cheng verify an old record. You can now invite her.",
		"battle_pause_title": "Paused · Controlling: %s",
		"battle_resume": "Resume battle",
		"battle_skill_use": "Use skill",
		"battle_target": "Order target: %s",
		"battle_focus": "Focus attacks",
		"battle_defend": "Defend first",
		"battle_skill_order": "Use skill first",
		"battle_default": "Follow AI policy",
		"ai_policy_balanced": "AI: Balanced",
		"ai_policy_aggressive": "AI: Attack",
		"ai_policy_cautious": "AI: Cautious",
		"battle_auto_on": "Full auto: on",
		"battle_auto_off": "Full auto: off",
		"battle_skill_hero": "Situational Insight",
		"battle_skill_liang": "Tactical Calibration",
		"battle_skill_zhao": "Echo Ranging",
		"battle_skill_ji": "Fault-Line Recall",
		"battle_skill_used": "%s used %s.",
		"battle_member_down": "%s fell.",
		"battle_party_status": "Party: %s",
		"growth_title": "Character Growth & Jobs",
		"growth_open": "Characters & Jobs",
		"growth_back": "Back to map",
		"growth_pending": "Level 10 threshold: choose a job path",
		"growth_level": "Level %d · XP %d/%d · JP %d",
		"growth_aptitudes": "Aptitudes  Martial %d · Adaptive %d · Scholarly %d · Spiritual %d  (60 required)",
		"growth_job": "Current: %s · Stage %d",
		"growth_stay": "Stay in current job",
		"growth_promote": "Promote in current series",
		"growth_switch": "Switch to %s",
		"growth_upgrade": "Upgrade %s · %d JP",
		"growth_skill": "Job skills: %s",
		"growth_personal": "Personal %s Lv%d · upgrade %d JP",
		"save_title": "Save & Load", "save_open": "Save", "save_load_open": "Load Game",
		"save_back": "Back", "save_manual_slot": "Manual slot %d", "save_write": "Save here",
		"save_load": "Load", "save_empty": "Empty slot", "save_auto": "Autosave",
		"save_before_battle": "Before battle", "save_after_battle": "After victory", "save_manual_note": "Manual save", "save_party_talk": "Party talk", "save_field_assist": "Companion fieldwork",
		"save_summary": "%s · Lv%d · %d party · %s",
		"save_ok": "Saved to %s", "save_failed": "Save failed", "save_load_failed": "Load failed or incompatible save",
		"save_version_old": "Old save · cannot load", "save_no_records": "No autosaves yet",
		"growth_rewards": "Battle rewards: %d XP / %d JP; reserves earn 25%%",
		"growth_locked": "Aptitude below 60",
		"growth_done": "Job choice complete",
		"job_skill_sword_slash": "Edge Break", "job_skill_sword_arc": "Sword Arc",
		"job_skill_firearms_shot": "Precision Shot", "job_skill_firearms_burst": "Suppressive Burst",
		"job_skill_tactics_mark": "Tactical Mark", "job_skill_tactics_rally": "Team Rally",
		"job_skill_relics_echo": "Relic Echo", "job_skill_relics_delay": "Time Delay",
		"bypass_notice": "You bypassed the enemy and reached the far side.",
		"field_log": "Field log",
		"field_log_hint": "Explore all three places in any order. Complete the surveys, check the relay and ruin records, observe a machine, then report in the city. Each place also has two optional traces to interpret with its local companion.",
		"field_log_count": "Places %d/3 · Surveys %d/3 · Relay %s · Records %s · Machine %s",
		"field_assist_log": "Companion fieldwork %d/3 (optional)",
		"field_trace_log": "Field traces %d/6 (optional)",
		"field_trace_marker": "Trace",
		"field_trace_found": "A field trace was recorded. Return to the terminal with the local companion to interpret it.",
		"field_trace_need": "Inspect both nearby traces before %s can interpret them.",
		"field_trace_city_0": "City trace: an old sign keeps two numbers at the junction of a repair line and a storage line.",
		"field_trace_city_1": "City trace: a dawn inspection stamp overlaps the previous day's quota sheet; its time field was not updated.",
		"field_trace_outskirts_0": "Outskirts trace: a discarded conduit has fresh sensor scratches, but the echo comes from deeper below.",
		"field_trace_outskirts_1": "Outskirts trace: a ground marker diverges from the old conduit toward a line still in use.",
		"field_trace_ruins_0": "Ruin trace: three repair fillers in a wall seam show different degrees of wear.",
		"field_trace_ruins_1": "Ruin trace: the outermost fastener uses a current specification and cannot date to the oldest layer.",
		"field_assist_marker_city": "Allocation ledger", "field_assist_marker_outskirts": "Echo node", "field_assist_marker_ruins": "Strata panel",
		"field_assist_need": "Bring %s to examine this. You can invite them and return anytime.",
		"field_assist_use": "Use personal skill", "field_assist_close": "Close", "field_assist_recorded": "Recorded",
		"field_assist_ready_city": "Liang Xu can use Tactical Calibration to compare duplicate ledger IDs.",
		"field_assist_ready_outskirts": "Zhao Ling can use Echo Ranging to find the live conduit.",
		"field_assist_ready_ruins": "Ji Cheng can use Fault-Line Recall to order the panel's repairs.",
		"field_assist_result_city": "One ID serves repair and energy storage; its approval record is missing.",
		"field_assist_result_outskirts": "The echo came from an old conduit. The live line lies beneath it.",
		"field_assist_result_ruins": "Three repairs span different eras. The last used present-day material.",
		"field_assist_reward": "%s gained 4 JP and 2 bond. This finding is in the field log.",
		"survey_marker": "Field survey", "survey_prompt": "Approach the survey entrance and press E",
		"survey_log": "Field surveys: City %s · Outskirts %s · Ruins %s",
		"survey_progress": "Clues %d/6 · Survey %s",
		"survey_help": "WASD move · E inspect clues, doors and console · Esc back",
		"survey_next": "Go deeper", "survey_leave": "Return outside", "survey_previous": "Outer room",
		"survey_terminal": "Analysis console", "survey_locked": "Inspect all six clues here before deciding.",
		"survey_link_title": "Connect evidence", "survey_link_instruction": "Select two related clues. Links found: %d/3.",
		"survey_link_wrong": "These clues do not yet form a testable connection. Compare them again.",
		"survey_link_found": "This link is already recorded.", "survey_link_continue": "Make final judgment",
		"survey_notes": "Clue notes", "survey_notes_back": "Back to analysis", "survey_notes_previous": "Previous", "survey_notes_next": "Next",
		"survey_retry": "The evidence does not support that conclusion. Compare the clues again.",
		"survey_completed": "Survey complete. You can still review the evidence.",
		"survey_close": "Keep exploring", "save_survey_note": "Survey record",
		"survey_reward": "Survey reward: 8 JP for each active member, 2 JP for each reserve.",
		"talk_open": "Party talk", "talk_title": "Conversations on the road", "talk_help": "Topics open as you investigate and invite companions. You can replay them anytime.",
		"talk_empty": "No topics yet. Keep exploring and invite companions.", "talk_back": "World map",
		"talk_next": "Continue", "talk_finish": "Finish talk", "talk_topics": "Topics", "talk_seen": "Heard", "talk_bond": "Bond %d",
		"run_time": "Run time %02d:%02d",
		"field_yes": "Done", "field_no": "Open",
		"relay_marker": "Relay", "relay_prompt": "Approach the relay and press E",
		"relay_done": "The relay fault points to a circuit plan rewritten several times. Zhao Ling notes the anomaly.",
		"relay_record": "Relay record: the maintenance plan was repeatedly revised. Its original purpose is unknown.",
		"archive_record": "Ruin record: a fragmented energy dispatch entry shares an identifier with the current network.",
		"machine_record": "Machine record: an automated machine's behavior has been observed.",
		"report_marker": "Field report", "report_prompt": "Approach the report desk and press E",
		"report_locked": "The field log still has unfinished investigations.",
		"report_ready": "The evidence is ready. Press E at the report desk to submit it.",
		"report_title": "Science region demo complete",
		"report_summary": "%s visited three places, completed three surveys, checked two records, and observed a machine. Companions: %d/3.",
		"report_continue": "Continue exploring", "report_map": "World map",
		"report_note": "The evidence raises further questions. The full story will develop in later chapters.",
		"report_receipt": "Local playtest record saved.",
	},
}

var language := "zh"
var hero_name := ""
var hero_appearance := "male"
var current_destination_id := "scifi.city"
var hero_state := {"hp": 100, "max_hp": 100, "energy": 60, "max_energy": 60}
var member_states: Dictionary = {}
var active_party_ids: Array[String] = ["hero"]
var recruited_members: Dictionary = {}
var party_talk_seen: Dictionary = {}
var party_bonds: Dictionary = {}
var field_insights: Dictionary = {}
var field_traces: Dictionary = {}
var ji_records_checked := false
var relay_checked := false
var areas_visited: Dictionary = {}
var machine_observed := false
var demo_completed := false
var play_time_seconds := 0.0
var playtest_events: Array = []
var wrong_pair_attempts: Dictionary = {}
var wrong_judgment_attempts: Dictionary = {}
var playtest_receipt_path := ""
var run_active := false
var survey_clues: Dictionary = {}
var survey_links: Dictionary = {}
var survey_solved: Dictionary = {}
var current_annex_room := 1
var annex_surface_return_position := Vector2(558, 143)
var resume_annex_pending := false
var resume_annex_position := Vector2(84, 238)
var show_initial_guide := false
var battle_enemy_id := ""
var battle_return_position := Vector2(82, 260)
var enemy_cleared_for_return := false
var returning_from_battle := false
var battle_transition_started_usec := 0
var last_battle_transition_ms := 0.0
var growth_return_scene := "res://scenes/scifi_world_map.tscn"
var save_screen_mode := "load"
var save_return_scene := "res://scenes/scifi_world_map.tscn"
var save_return_position := Vector2(82, 260)
var resume_area_pending := false
var resume_area_position := Vector2(82, 260)
var loaded_scene_kind := "map"

const DESTINATIONS := ["scifi.city", "scifi.outskirts", "scifi.ruins"]
const DESTINATION_KEYS := {
	"scifi.city": "area_city",
	"scifi.outskirts": "area_outskirts",
	"scifi.ruins": "area_ruins",
}
const PARTY_CAPACITY := 5
const MEMBER_DEFS := {
	"hero": {"name_key": "member_hero", "job_series": "sword", "aptitudes": [60, 60, 60, 60], "max_hp": 100, "max_energy": 60, "attack_damage": 19, "attack_range": 61.0, "skill_key": "battle_skill_hero", "color": Color("#5eb6af")},
	"liang-xu": {"name_key": "member_liang", "job_series": "tactics", "aptitudes": [48, 67, 94, 42], "max_hp": 95, "max_energy": 70, "attack_damage": 16, "attack_range": 65.0, "skill_key": "battle_skill_liang", "color": Color("#a6b4b8")},
	"zhao-ling": {"name_key": "member_zhao", "job_series": "firearms", "aptitudes": [51, 84, 68, 40], "max_hp": 82, "max_energy": 75, "attack_damage": 14, "attack_range": 164.0, "skill_key": "battle_skill_zhao", "color": Color("#69bbce")},
	"ji-cheng": {"name_key": "member_ji", "job_series": "relics", "aptitudes": [41, 67, 79, 83], "max_hp": 80, "max_energy": 80, "attack_damage": 12, "attack_range": 100.0, "skill_key": "battle_skill_ji", "color": Color("#6da78b")},
}


func _ready() -> void:
	_install_default_controls()


func _process(delta: float) -> void:
	if run_active and get_tree().current_scene != null and get_tree().current_scene.name != "MainMenu":
		play_time_seconds += delta


func text_for(key: String) -> String:
	return STRINGS[language].get(key, key)


func destination_name(destination_id: String) -> String:
	return text_for(DESTINATION_KEYS.get(destination_id, "area_city"))


func select_destination(destination_id: String) -> bool:
	if not DESTINATIONS.has(destination_id):
		return false
	current_destination_id = destination_id
	enemy_cleared_for_return = false
	returning_from_battle = false
	return true


func begin_new_run() -> void:
	hero_state = {"hp": 100, "max_hp": 100, "energy": 60, "max_energy": 60, "level": 1, "xp": 0, "jp": 0, "pending_job_choices": 0, "job_series": "sword", "job_stage": 1, "job_records": {"sword": {"stage": 1, "skills": {"sword_slash": 1}}}, "personal_skill_rank": 1, "aptitudes": [60, 60, 60, 60], "ai_policy": "balanced"}
	member_states.clear()
	active_party_ids = ["hero"]
	recruited_members.clear()
	party_talk_seen.clear()
	party_bonds.clear()
	field_insights.clear()
	field_traces.clear()
	ji_records_checked = false
	hero_name = ""
	hero_appearance = "male"
	relay_checked = false
	areas_visited.clear()
	machine_observed = false
	demo_completed = false
	play_time_seconds = 0.0
	playtest_events.clear()
	wrong_pair_attempts.clear()
	wrong_judgment_attempts.clear()
	playtest_receipt_path = ""
	run_active = true
	record_playtest_event("run_start")
	survey_clues.clear()
	survey_links.clear()
	survey_solved.clear()
	current_annex_room = 1
	annex_surface_return_position = Vector2(558, 143)
	resume_annex_pending = false
	show_initial_guide = false
	battle_enemy_id = ""
	enemy_cleared_for_return = false
	returning_from_battle = false
	current_destination_id = "scifi.city"
	growth_return_scene = "res://scenes/scifi_world_map.tscn"
	resume_area_pending = false
	loaded_scene_kind = "map"


func member_name(member_id: String) -> String:
	if member_id == "hero" and hero_name != "":
		return hero_name
	return text_for(String(MEMBER_DEFS.get(member_id, MEMBER_DEFS["hero"])["name_key"]))


func field_log_text() -> String:
	var state := text_for("field_yes")
	var open := text_for("field_no")
	return text_for("field_log_count") % [areas_visited.size(), survey_solved.size(), state if relay_checked else open, state if ji_records_checked else open, state if machine_observed else open]


func field_assist_log_text() -> String:
	return text_for("field_assist_log") % field_insights.size()


func field_trace_log_text() -> String:
	return text_for("field_trace_log") % field_traces.size()


func field_trace_count(destination_id: String) -> int:
	return int(field_traces.has(destination_id + ":0")) + int(field_traces.has(destination_id + ":1"))


func discover_field_trace(destination_id: String, index: int) -> bool:
	if not DESTINATIONS.has(destination_id) or index not in [0, 1]:
		return false
	var key := "%s:%d" % [destination_id, index]
	if field_traces.has(key):
		return false
	field_traces[key] = true
	record_playtest_event("field_trace", destination_id)
	return true


func complete_field_assist(destination_id: String, member_id: String) -> bool:
	var assistants := {"scifi.city": "liang-xu", "scifi.outskirts": "zhao-ling", "scifi.ruins": "ji-cheng"}
	if assistants.get(destination_id, "") != member_id or not recruited_members.has(member_id) or field_insights.has(destination_id) or field_trace_count(destination_id) < 2:
		return false
	field_insights[destination_id] = true
	member_state(member_id)["jp"] = int(member_state(member_id).get("jp", 0)) + 4
	party_bonds[member_id] = mini(100, int(party_bonds.get(member_id, 0)) + 2)
	record_playtest_event("field_assist", destination_id)
	return true


func survey_log_text() -> String:
	var state := text_for("field_yes")
	var open := text_for("field_no")
	return text_for("survey_log") % [state if survey_solved.has("scifi.city") else open, state if survey_solved.has("scifi.outskirts") else open, state if survey_solved.has("scifi.ruins") else open]


func play_time_text() -> String:
	var total := maxi(0, int(play_time_seconds))
	return text_for("run_time") % [total / 60, total % 60]


func record_playtest_event(event_type: String, destination_id: String = "") -> void:
	if run_active:
		playtest_events.append({"type": event_type, "destination": destination_id, "atSeconds": snappedf(play_time_seconds, 0.1)})


func playtest_time_by_destination() -> Dictionary:
	var totals := {"scifi.city": 0.0, "scifi.outskirts": 0.0, "scifi.ruins": 0.0, "map_and_setup": 0.0}
	var active := "map_and_setup"
	var previous := 0.0
	for event in playtest_events:
		if typeof(event) != TYPE_DICTIONARY or event.get("type", "") != "location":
			continue
		var at_seconds := clampf(float(event.get("atSeconds", previous)), previous, play_time_seconds)
		totals[active] += at_seconds - previous
		var destination := String(event.get("destination", ""))
		active = destination if DESTINATIONS.has(destination) else "map_and_setup"
		previous = at_seconds
	totals[active] += maxf(0.0, play_time_seconds - previous)
	for key in totals:
		totals[key] = snappedf(totals[key], 0.1)
	return totals


func record_playtest_mistake(kind: String, destination_id: String) -> void:
	if not DESTINATIONS.has(destination_id):
		return
	var counts: Dictionary = wrong_pair_attempts if kind == "pair" else wrong_judgment_attempts
	counts[destination_id] = int(counts.get(destination_id, 0)) + 1


func write_playtest_receipt() -> String:
	var directory := SaveStore.root_path.path_join("playtests")
	if DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(directory)) != OK:
		return ""
	var stamp := Time.get_datetime_string_from_system().replace("-", "").replace(":", "").replace("T", "-")
	var filename := "rpg-2-star-ocean-the-second_scifi-region_playtest-receipt_m7_%s-%08x.json" % [stamp, randi()]
	var path := directory.path_join(filename)
	var receipt := {
		"schemaVersion": 1,
		"project": "rpg-2-star-ocean-the-second",
		"milestone": "M7",
		"recordedAt": Time.get_datetime_string_from_system(),
		"durationSeconds": snappedf(play_time_seconds, 0.1),
		"timeByDestinationSeconds": playtest_time_by_destination(),
		"language": language,
		"events": playtest_events.duplicate(true),
		"wrongEvidencePairs": wrong_pair_attempts.duplicate(true),
		"wrongJudgments": wrong_judgment_attempts.duplicate(true),
		"recruited": recruited_members.keys(),
		"surveysCompleted": survey_solved.keys(),
		"conversationsHeard": party_talk_seen.keys(),
		"fieldAssists": field_insights.keys(),
		"fieldTraces": field_traces.keys(),
		"reportCompleted": demo_completed,
	}
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return ""
	file.store_string(JSON.stringify(receipt, "\t"))
	file.flush()
	file.close()
	playtest_receipt_path = ProjectSettings.globalize_path(path)
	print("PLAYTEST_RECEIPT " + playtest_receipt_path)
	return playtest_receipt_path


func can_submit_report() -> bool:
	return areas_visited.size() == DESTINATIONS.size() and survey_solved.size() == DESTINATIONS.size() and relay_checked and ji_records_checked and machine_observed


func member_state(member_id: String) -> Dictionary:
	return hero_state if member_id == "hero" else member_states.get(member_id, {})


func recruit_member(member_id: String) -> bool:
	if not MEMBER_DEFS.has(member_id) or member_id == "hero" or recruited_members.has(member_id):
		return false
	if active_party_ids.size() >= PARTY_CAPACITY:
		return false
	if member_id == "ji-cheng" and not ji_records_checked:
		return false
	var definition: Dictionary = MEMBER_DEFS[member_id]
	var level := maxi(1, int(hero_state.get("level", 1)))
	var stage := mini(2, 1 + (level - 1) / 10)
	member_states[member_id] = {
		"hp": int(definition["max_hp"]), "max_hp": int(definition["max_hp"]),
		"energy": int(definition["max_energy"]), "max_energy": int(definition["max_energy"]),
		"level": level, "xp": 0, "jp": 0, "pending_job_choices": 0,
		"job_series": definition["job_series"], "job_stage": stage,
		"job_records": {definition["job_series"]: {"stage": stage, "skills": {String(GrowthRules.SERIES[definition["job_series"]]["skills"][0]): 1, String(GrowthRules.SERIES[definition["job_series"]]["skills"][stage - 1]): 1}}},
		"personal_skill_rank": mini(3, 1 + (level - 1) / 20),
		"ai_policy": "balanced",
		"learned_skill_ids": ["basic", "advanced"] if stage > 1 else ["basic"],
		"aptitudes": definition["aptitudes"].duplicate(),
	}
	recruited_members[member_id] = true
	record_playtest_event("recruit", member_id)
	party_bonds[member_id] = int(party_bonds.get(member_id, 0))
	active_party_ids.append(member_id)
	return true


func record_party_talk(topic_id: String, participants: Array) -> bool:
	if party_talk_seen.has(topic_id):
		return false
	for member_id in participants:
		if not recruited_members.has(member_id):
			return false
	party_talk_seen[topic_id] = true
	record_playtest_event("conversation", topic_id)
	for member_id in participants:
		party_bonds[member_id] = mini(100, int(party_bonds.get(member_id, 0)) + 3)
	write_auto_save("map", Vector2.ZERO, "party_talk")
	return true


func award_battle_rewards(enemy_id: String) -> Dictionary:
	var xp := 26 if enemy_id == "patrol" else 44
	var jp := 12 if enemy_id == "patrol" else 20
	for member_id in active_party_ids:
		_grant_growth(member_state(member_id), xp, jp)
	for member_id in member_states:
		if not active_party_ids.has(member_id):
			_grant_growth(member_states[member_id], ceili(float(xp) * 0.25), ceili(float(jp) * 0.25))
	return {"xp": xp, "jp": jp}


func award_survey_jp() -> void:
	for member_id in active_party_ids:
		var state := member_state(member_id)
		state["jp"] = int(state.get("jp", 0)) + 8
	for member_id in member_states:
		if not active_party_ids.has(member_id):
			member_states[member_id]["jp"] = int(member_states[member_id].get("jp", 0)) + 2


func _grant_growth(member: Dictionary, xp: int, jp: int) -> void:
	member["xp"] = int(member.get("xp", 0)) + xp
	member["jp"] = int(member.get("jp", 0)) + jp
	_process_levels(member)


func _process_levels(member: Dictionary) -> void:
	while int(member.get("pending_job_choices", 0)) == 0 and int(member["xp"]) >= GrowthRules.xp_to_next(int(member["level"])):
		member["xp"] = int(member["xp"]) - GrowthRules.xp_to_next(int(member["level"]))
		member["level"] = int(member["level"]) + 1
		member["max_hp"] = int(member["max_hp"]) + 3
		member["max_energy"] = int(member["max_energy"]) + 2
		member["hp"] = member["max_hp"]
		member["energy"] = member["max_energy"]
		if int(member["level"]) % 10 == 0:
			member["pending_job_choices"] = 1


func has_pending_job_choice() -> bool:
	for member_id in active_party_ids:
		if int(member_state(member_id).get("pending_job_choices", 0)) > 0:
			return true
	return false


func choose_job(member_id: String, action: String, target_series: String = "") -> bool:
	var member := member_state(member_id)
	if member.is_empty() or int(member.get("pending_job_choices", 0)) < 1:
		return false
	var current: String = member["job_series"]
	var records: Dictionary = member["job_records"]
	match action:
		"stay":
			pass
		"promote":
			if int(member["job_stage"]) >= 2:
				return false
			member["job_stage"] = int(member["job_stage"]) + 1
			var record: Dictionary = records[current]
			record["stage"] = member["job_stage"]
			record["skills"][GrowthRules.current_skill_id(member)] = 1
		"switch":
			if target_series == current or not GrowthRules.can_enter(member, target_series):
				return false
			if not records.has(target_series):
				records[target_series] = {"stage": 1, "skills": {String(GrowthRules.SERIES[target_series]["skills"][0]): 1}}
			member["job_series"] = target_series
			member["job_stage"] = int(records[target_series]["stage"])
		_:
			return false
	member["pending_job_choices"] = int(member["pending_job_choices"]) - 1
	_process_levels(member)
	return true


func upgrade_job_skill(member_id: String, skill_id: String) -> bool:
	var member := member_state(member_id)
	if member.is_empty():
		return false
	var series_id: String = member["job_series"]
	var skills: Array = GrowthRules.SERIES[series_id]["skills"]
	if not skills.has(skill_id) or skills.find(skill_id) >= int(member["job_stage"]):
		return false
	var record: Dictionary = member["job_records"][series_id]
	var rank := int(record["skills"].get(skill_id, 0))
	var cost := GrowthRules.jp_cost(member, series_id, rank + 1)
	if cost < 0 or int(member["jp"]) < cost:
		return false
	member["jp"] = int(member["jp"]) - cost
	record["skills"][skill_id] = rank + 1
	return true


func upgrade_personal_skill(member_id: String) -> bool:
	var member := member_state(member_id)
	if member.is_empty() or not MEMBER_DEFS.has(member_id):
		return false
	var rank := int(member.get("personal_skill_rank", 1))
	var home_series: String = MEMBER_DEFS[member_id]["job_series"]
	var cost := GrowthRules.jp_cost(member, home_series, rank + 1)
	if cost < 0 or int(member.get("jp", 0)) < cost:
		return false
	member["jp"] = int(member["jp"]) - cost
	member["personal_skill_rank"] = rank + 1
	return true


func begin_battle(enemy_id: String, return_position: Vector2) -> bool:
	if not ["patrol", "sentry"].has(enemy_id):
		return false
	battle_enemy_id = enemy_id
	record_playtest_event("battle_start", current_destination_id)
	battle_return_position = return_position
	battle_transition_started_usec = Time.get_ticks_usec()
	return true


func make_snapshot(scene_kind: String, position: Vector2, note: String) -> Dictionary:
	return {
		"scene": scene_kind,
		"position": [position.x, position.y],
		"destination": current_destination_id,
		"enemyCleared": enemy_cleared_for_return,
		"hero": hero_state.duplicate(true),
		"heroName": hero_name,
		"heroAppearance": hero_appearance,
		"members": member_states.duplicate(true),
		"activeParty": active_party_ids.duplicate(),
		"recruited": recruited_members.duplicate(true),
		"partyTalkSeen": party_talk_seen.duplicate(true),
		"partyBonds": party_bonds.duplicate(true),
		"fieldInsights": field_insights.duplicate(true),
		"fieldTraces": field_traces.duplicate(true),
		"jiRecordsChecked": ji_records_checked,
		"relayChecked": relay_checked,
		"areasVisited": areas_visited.duplicate(true),
		"machineObserved": machine_observed,
		"demoCompleted": demo_completed,
		"playTimeSeconds": play_time_seconds,
		"playtestEvents": playtest_events.duplicate(true),
		"wrongPairAttempts": wrong_pair_attempts.duplicate(true),
		"wrongJudgmentAttempts": wrong_judgment_attempts.duplicate(true),
		"surveyClues": survey_clues.duplicate(true),
		"surveyLinks": survey_links.duplicate(true),
		"surveySolved": survey_solved.duplicate(true),
		"annexRoom": current_annex_room,
		"annexSurfaceReturnPosition": [annex_surface_return_position.x, annex_surface_return_position.y],
		"language": language,
		"note": note,
	}


func write_manual_save(slot: int) -> String:
	var kind := "annex" if save_return_scene.ends_with("survey_annex.tscn") else ("area" if save_return_scene.ends_with("scifi_exploration_area.tscn") else "map")
	return SaveStore.write_entry("manual", slot, make_snapshot(kind, save_return_position, "manual_note"))


func write_auto_save(scene_kind: String, position: Vector2, note: String) -> String:
	return SaveStore.write_entry("auto", 0, make_snapshot(scene_kind, position, note))


func load_save(id: String) -> bool:
	var entry := SaveStore.read_entry(id)
	if entry.is_empty() or int(entry.get("schemaVersion", -1)) != SaveStore.SCHEMA_VERSION:
		return false
	var snapshot: Dictionary = entry["snapshot"]
	if not _valid_snapshot(snapshot):
		return false
	var party: Array[String] = []
	for member_id in snapshot["activeParty"]:
		party.append(String(member_id))
	hero_state = snapshot["hero"].duplicate(true)
	hero_name = String(snapshot.get("heroName", ""))
	hero_appearance = String(snapshot.get("heroAppearance", "male"))
	member_states = snapshot["members"].duplicate(true)
	active_party_ids = party
	recruited_members = snapshot["recruited"].duplicate(true)
	party_talk_seen = snapshot.get("partyTalkSeen", {}).duplicate(true)
	party_bonds = snapshot.get("partyBonds", {}).duplicate(true)
	field_insights = snapshot.get("fieldInsights", {}).duplicate(true)
	field_traces = snapshot.get("fieldTraces", {}).duplicate(true)
	for member_id in recruited_members:
		if not party_bonds.has(member_id):
			party_bonds[member_id] = 0
	ji_records_checked = bool(snapshot["jiRecordsChecked"])
	relay_checked = bool(snapshot.get("relayChecked", false))
	areas_visited = snapshot.get("areasVisited", {}).duplicate(true)
	machine_observed = bool(snapshot.get("machineObserved", false))
	demo_completed = bool(snapshot.get("demoCompleted", false))
	play_time_seconds = float(snapshot.get("playTimeSeconds", 0.0))
	playtest_events = snapshot.get("playtestEvents", []).duplicate(true)
	wrong_pair_attempts = snapshot.get("wrongPairAttempts", {}).duplicate(true)
	wrong_judgment_attempts = snapshot.get("wrongJudgmentAttempts", {}).duplicate(true)
	playtest_receipt_path = ""
	run_active = true
	survey_clues = snapshot.get("surveyClues", {}).duplicate(true)
	survey_links = snapshot.get("surveyLinks", {}).duplicate(true)
	survey_solved = snapshot.get("surveySolved", {}).duplicate(true)
	current_annex_room = int(snapshot.get("annexRoom", 1))
	var surface_position: Array = snapshot.get("annexSurfaceReturnPosition", [558.0, 143.0])
	annex_surface_return_position = Vector2(float(surface_position[0]), float(surface_position[1]))
	show_initial_guide = false
	current_destination_id = String(snapshot["destination"])
	language = String(snapshot["language"])
	enemy_cleared_for_return = bool(snapshot["enemyCleared"])
	loaded_scene_kind = String(snapshot["scene"])
	resume_area_position = Vector2(float(snapshot["position"][0]), float(snapshot["position"][1]))
	resume_area_pending = loaded_scene_kind == "area"
	resume_annex_position = resume_area_position
	resume_annex_pending = loaded_scene_kind == "annex"
	returning_from_battle = false
	battle_enemy_id = ""
	battle_return_position = resume_area_position
	language_changed.emit()
	return true


func loaded_scene_path() -> String:
	var path := "res://scenes/scifi_world_map.tscn"
	if loaded_scene_kind == "area":
		path = "res://scenes/scifi_exploration_area.tscn"
	elif loaded_scene_kind == "annex":
		path = "res://scenes/survey_annex.tscn"
	if has_pending_job_choice():
		growth_return_scene = path
		return "res://scenes/growth_screen.tscn"
	return path


func _valid_snapshot(snapshot: Dictionary) -> bool:
	if snapshot.get("scene", "") not in ["map", "area", "annex"] or not DESTINATIONS.has(snapshot.get("destination", "")):
		return false
	var position: Variant = snapshot.get("position")
	if typeof(position) != TYPE_ARRAY or position.size() != 2:
		return false
	if typeof(snapshot.get("hero")) != TYPE_DICTIONARY or typeof(snapshot.get("members")) != TYPE_DICTIONARY or typeof(snapshot.get("activeParty")) != TYPE_ARRAY or typeof(snapshot.get("recruited")) != TYPE_DICTIONARY:
		return false
	if typeof(snapshot.get("partyTalkSeen", {})) != TYPE_DICTIONARY or typeof(snapshot.get("partyBonds", {})) != TYPE_DICTIONARY:
		return false
	var hero: Dictionary = snapshot["hero"]
	if not hero.has("level") or not hero.has("job_records") or not GrowthRules.SERIES.has(hero.get("job_series", "")):
		return false
	var party: Array = snapshot["activeParty"]
	if party.is_empty() or party.size() > PARTY_CAPACITY or party[0] != "hero":
		return false
	for member_id in party:
		if not MEMBER_DEFS.has(member_id) or (member_id != "hero" and not snapshot["members"].has(member_id)):
			return false
	for member_id in snapshot.get("partyBonds", {}).keys():
		if not MEMBER_DEFS.has(member_id) or member_id == "hero" or not snapshot["recruited"].has(member_id) or typeof(snapshot["partyBonds"][member_id]) not in [TYPE_INT, TYPE_FLOAT] or int(snapshot["partyBonds"][member_id]) < 0 or int(snapshot["partyBonds"][member_id]) > 100:
			return false
	for topic_id in snapshot.get("partyTalkSeen", {}).keys():
		if typeof(topic_id) != TYPE_STRING or snapshot["partyTalkSeen"][topic_id] != true:
			return false
	for destination_id in snapshot.get("fieldInsights", {}).keys():
		if not DESTINATIONS.has(destination_id) or snapshot["fieldInsights"][destination_id] != true:
			return false
	if typeof(snapshot.get("fieldTraces", {})) != TYPE_DICTIONARY:
		return false
	for trace_key in snapshot.get("fieldTraces", {}).keys():
		var trace_parts: PackedStringArray = String(trace_key).split(":")
		if trace_parts.size() != 2 or not DESTINATIONS.has(trace_parts[0]) or trace_parts[1] not in ["0", "1"] or snapshot["fieldTraces"][trace_key] != true:
			return false
	if snapshot.get("language", "") not in ["zh", "en"] or typeof(snapshot.get("jiRecordsChecked")) != TYPE_BOOL or typeof(snapshot.get("enemyCleared")) != TYPE_BOOL:
		return false
	if typeof(snapshot.get("relayChecked", false)) != TYPE_BOOL or typeof(snapshot.get("areasVisited", {})) != TYPE_DICTIONARY or typeof(snapshot.get("fieldInsights", {})) != TYPE_DICTIONARY or typeof(snapshot.get("machineObserved", false)) != TYPE_BOOL or typeof(snapshot.get("demoCompleted", false)) != TYPE_BOOL:
		return false
	if typeof(snapshot.get("playTimeSeconds", 0.0)) not in [TYPE_FLOAT, TYPE_INT] or float(snapshot.get("playTimeSeconds", 0.0)) < 0.0:
		return false
	if typeof(snapshot.get("playtestEvents", [])) != TYPE_ARRAY or typeof(snapshot.get("wrongPairAttempts", {})) != TYPE_DICTIONARY or typeof(snapshot.get("wrongJudgmentAttempts", {})) != TYPE_DICTIONARY:
		return false
	if typeof(snapshot.get("heroName", "")) != TYPE_STRING or snapshot.get("heroAppearance", "male") not in ["male", "female"]:
		return false
	if typeof(snapshot.get("surveyClues", {})) != TYPE_DICTIONARY or typeof(snapshot.get("surveyLinks", {})) != TYPE_DICTIONARY or typeof(snapshot.get("surveySolved", {})) != TYPE_DICTIONARY or int(snapshot.get("annexRoom", 1)) not in [1, 2]:
		return false
	var surface_position: Variant = snapshot.get("annexSurfaceReturnPosition", [558.0, 143.0])
	if typeof(surface_position) != TYPE_ARRAY or surface_position.size() != 2:
		return false
	for destination_id in snapshot.get("surveySolved", {}).keys():
		if not DESTINATIONS.has(destination_id) or snapshot["surveySolved"][destination_id] != true:
			return false
	for clue_key in snapshot.get("surveyClues", {}).keys():
		var parts: PackedStringArray = String(clue_key).split(":")
		if parts.size() != 2 or not DESTINATIONS.has(parts[0]) or not parts[1].is_valid_int() or int(parts[1]) not in [0, 1, 2, 3, 4, 5] or snapshot["surveyClues"][clue_key] != true:
			return false
	for link_key in snapshot.get("surveyLinks", {}).keys():
		var parts: PackedStringArray = String(link_key).split(":")
		if parts.size() != 2 or not DESTINATIONS.has(parts[0]) or not parts[1].is_valid_int() or int(parts[1]) not in [0, 1, 2] or snapshot["surveyLinks"][link_key] != true:
			return false
	for destination_id in snapshot.get("areasVisited", {}).keys():
		if not DESTINATIONS.has(destination_id) or snapshot["areasVisited"][destination_id] != true:
			return false
	return true


func toggle_language() -> void:
	language = "en" if language == "zh" else "zh"
	language_changed.emit()


func _install_default_controls() -> void:
	_add_key_action("move_left", KEY_A)
	_add_key_action("move_left", KEY_LEFT)
	_add_key_action("move_right", KEY_D)
	_add_key_action("move_right", KEY_RIGHT)
	_add_key_action("move_up", KEY_W)
	_add_key_action("move_up", KEY_UP)
	_add_key_action("move_down", KEY_S)
	_add_key_action("move_down", KEY_DOWN)
	_add_key_action("interact", KEY_E)
	_add_key_action("battle_attack", KEY_J)
	_add_key_action("battle_dodge", KEY_K)
	_add_key_action("battle_guard", KEY_L)
	_add_key_action("battle_switch", KEY_TAB)
	_add_key_action("battle_pause", KEY_P)
	_add_key_action("battle_auto", KEY_T)
	_add_key_action("battle_skill", KEY_Q)
	_add_key_action("battle_job_skill", KEY_R)


func _add_key_action(action: StringName, key: Key) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action)
	var event := InputEventKey.new()
	event.physical_keycode = key
	InputMap.action_add_event(action, event)

