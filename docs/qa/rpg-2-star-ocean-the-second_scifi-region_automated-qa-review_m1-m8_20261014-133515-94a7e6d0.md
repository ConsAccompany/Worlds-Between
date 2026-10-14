# 《世界之间》M1–M8 QA 记录（2026-10-14）

检查工作区：`parallel/qa-readiness`，起点为当时的 `origin/main`。运行环境：Windows、Godot `4.7.2.stable`、`--headless`。Godot 先成功完成资源导入；下列 smoke 逐项运行，保存测试位于各自的 `user://test-saves/` 子目录。**这不是在玩家窗口中完成的真人试玩，也不是 M8 画质审查。**

| 检查 | 进程退出码 | 控制台结果 |
|---|---:|---|
| `m1_smoke.gd` | 0 | `M1_SMOKE_OK` |
| `m2_smoke.gd` | 0 | `M2_SMOKE_OK` |
| `m3_smoke.gd` | 0 | `M3_SMOKE_OK` |
| `m4_smoke.gd` | 0 | `M4_SMOKE_OK`；退出时 `2 ObjectDB instances were leaked` 警告 |
| `m5_smoke.gd` | 0 | `M5_SMOKE_OK` |
| `m6_smoke.gd` | 0 | `M6_SMOKE_OK` |
| `m6_restart_smoke.gd` | 0 | `M6_RESTART_OK`；同一退出警告 |
| `m7_smoke.gd` | 0 | `M7_SMOKE_OK`；两条自动路线及回执模式通过 |
| 新增 `m8_city_reentry_smoke.gd`（当前 main 城市代码） | 0 | `M8_CITY_REENTRY_OK`；同一退出警告 |

新增测试覆盖城市**暂不邀请→回地图→切换语言→回城市→邀请→手动存档→读档**，并检查双语热点文字、梁序的角色形象和姓名是否随招募状态出现／消失。这些是状态与 UI 字符串检查，不证明标记在实际画面中容易辨识。第一次编写时直接调用 `write_manual_save` 而未设置场景返回路径，测试自身失败；改为通过城市的真实存档入口后通过，故没有把此视为产品缺陷。

已审阅远端 `origin/codex/city-walkable-boundaries` 的 `m8_city_integration_smoke.gd` 与 `m8_city_navigation_smoke.gd`：前者覆盖两种主角形象、足底锚点、城市六处热点行走、梁序招募、合法与旧位置存档恢复、回地图；后者覆盖路面连通性、障碍、滑动碰撞和大范围旧坐标修复。新增测试避开了上述几项的重复实现。因为 QA 工作区从 main 派生，**这两个分支测试尚未在本工作区执行**；统筹者整合城市分支与 Agent A 修改后，应同新测试一起重跑。

## 当前未关闭的验收项

1. 两条 **25–35 分钟真人新档**路线没有完成回执；按[现场路线表](rpg-2-star-ocean-the-second_scifi-region_human-playtest-routes_m7-m8_20261014-133240-51d0c8a7.md)执行后记录真实时间与反馈。
2. 城市正常窗口中的主角／梁序比例、站地、遮挡、热点可读性、双语文字裁切和目标画质，需要逐张审查引擎实际画面。自动状态测试不能勾选美术验收。
3. 合并后的 M8 integration/navigation/reentry 三项检查需要在单一整合版本重跑；通过后仍需前两项人工判断。
4. Godot 退出时偶发 `2 ObjectDB instances were leaked` 警告，目前未影响上述测试退出码；如在正常试玩中出现资源增长或卡顿，再单独定位。
