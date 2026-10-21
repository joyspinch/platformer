# 跃迁山谷 · PLATFORMER

横版重力跳跃闯关：跑、跳、二段跳、踩巡逻兵、捡晶片、插旗过关，三关打通进结算。

**素材清单见 `client/ASSETS.md`。**

## 玩法

| 操作 | 键 | 说明 |
|---|---|---|
| 左右移动 | `A` / `D` 或 `←` / `→` | 有加速度与摩擦，松手会减速停住 |
| 跳跃 | `空格` / `W` / `↑` | 地面起跳；**下落中再按一次 = 二段跳**（落地重置次数） |
| 设置浮层 | `Esc` | 难度（1 轻松 / 2 标准 / 3 硬核，影响重力与跑速）、音效开关 |

- **巡逻兵 Drone**：在平台面来回走。撞到扣 1 血；从上方踩到它头顶会**踩扁**它并被弹起。
- **晶片 Shard**：关卡里的金币，碰到即收集（+10 分）。
- **出口旗**：关底目标，跑到即通关本关 → 下一关；第三关通关 → 结算画面。
- **失败**：掉出屏幕底部（掉进缺口）或血量归零 → 命 -1，重生到当前关卡起点（关卡重置）；
  三条命耗尽 → 结算画面。
- **计分**：晶片 10 分 / 踩敌 25 分 / 通关一关 100 分。

## 三关

| 关卡 | 名字 | 宽 | 特点 |
|---|---|---|---|
| 1 | 苔谷浅滩 | 2400 | 两处缺口 + 8 块浮空平台，4 个巡逻兵 |
| 2 | 熔痕裂谷 | 2600 | 四处缺口，平台更碎，7 个巡逻兵 |
| 3 | 霜夜尖塔 | 2800 | 缺口与高台交替，10 个巡逻兵 |

## 画面

- 三层视差背景（远山 0.10 / 松林 0.20 / 灌木 0.30），用 `Canvas.BlitImage` **裁源矩形**取景，
  随相机按不同速度滚动（不平移两张拼接，所以没有竖缝）。
- 角色、巡逻兵、晶片、旗子、地形砖块全部是位图；HUD 面板、底部提示条与结算面板是
  **九宫格美术底板**（`ui_board.png`，`PlatformerPaint.NineSlice` 自己切 9 块）；
  画布按钮是九宫格按钮底板（三态）。
- **朝向**：引擎运行时不能翻转贴图，所以玩家与巡逻兵各用一张**两帧精灵表**
  （原图朝右 / 水平镜像朝左），按 `facingRight` 取帧；规则见 `client/ASSETS.md`。
- **主体细节**：落地投影（软椭圆）、巡逻兵尾焰（朝向指示）、角色背后的柔光、
  起跳与落地的尘土粒子。
- **UI 皮肤包**：`client/assets/skins/platformer/skin.css`（山谷黄昏：暖橙 / 苔绿 / 石板灰），
  构建拷到 `build/platformer/skins/platformer/`，启动时 `host.App().UseSkin("platformer")` 应用。
- 颜色统一在 `client/src/PlatformerPalette.zan`（同一语义只有一个出处）。
- 贴图走 `Assets.Find`（磁盘优先）→ 内嵌表兜底 → 纯色绘制兜底，缺资源也不崩。

## 音效

8 个事件音（跳跃 / 落地 / 拾取 / 踩敌 / 受伤 / 坠亡 / 通关 / 结算），由公共包
`Game.Foundation.SfxBank` 加载播放，带限频；没有声卡时静默失效。

## 存档

`%LOCALAPPDATA%/Platformer/platformer_slot0.json`（可用 `PLATFORMER_SAVE` 环境变量改目录）：

| 字段 | 含义 |
|---|---|
| `level` | 最远到达的关卡 |
| `clears` | 累计通关数 |
| `bestTime` | 最佳单关用时（毫秒） |
| `score` | 累计总分 |
| `deaths` | 累计死亡数 |
| `runs` | 局数（每启动一次 +1） |

菜单页与结算面板都会显示这些累计数据。

## 目录

    platformer/
      client/
        src/      玩法与渲染源码（11 个 .zan）
        assets/   位图 + assets/sfx/*.wav + assets/skins/platformer/skin.css
        tests/    platformer_test.zan（玩法断言用例）
        tools/    build.ps1 / test.ps1 / zanc.ps1 / make_assets.py / gen_assets.ps1
        ASSETS.md 素材清单
      build/      编译产物与一次性脚本（不入库）
      PROJECT.md  本文件

源码分层（逻辑与画面分开，玩法用例可以无头跑）：

| 文件 | 职责 |
|---|---|
| `main.zan` | GuiHost 入口：主循环、输入事件、按钮、皮肤应用、存档落盘 |
| `PlatformerGame.zan` | 玩法状态机（菜单/游戏中/结算）、事件队列、关卡推进、死亡与重生 |
| `PlatformerPlayer.zan` | 玩家物理：加速度、摩擦、重力、终端速度、二段跳、平台碰撞 |
| `PlatformerEnemy.zan` | 巡逻兵巡逻与边界折返 |
| `PlatformerCoins.zan` | 晶片（金币） |
| `PlatformerLevel.zan` | 三关地形 / 敌人 / 晶片 / 起点 / 出口旗数据 |
| `PlatformerView.zan` | 渲染：视差、地形贴图、实体位图（按朝向取帧）、HUD、菜单、结算面板 |
| `PlatformerPaint.zan` | 逻辑坐标绘制原语（贴图、裁源贴图、九宫格、文字、圆角矩形） |
| `PlatformerFacing.zan` | 朝向 → 取帧索引的纯函数（帧规则唯一真源） |
| `PlatformerPalette.zan` | 色板：所有画面颜色只有这一处出处 |
| `PlatformerFx.zan` | 画面特效：起跳 / 落地的尘土粒子 |
| `GameShell.zan` | 存档（累计数据）+ 设置（难度 / 音效）+ 设置浮层 |
| `PlatformerSnd.zan` | 音效库封装（加载 + 事件播放） |

## 编译

```powershell
pwsh -File client/tools/build.ps1 -PackageProject D:/project/zan-head
```

- `-PackageProject` 指向 **zan-lang 仓库**（公共包 `Zan.Game` / `Zan.Gui` 在它的 `packages/` 下）。
- 编译器查找顺序：`-Compiler` → `$env:ZANC` → `$env:ZAN_HOME/build/zanc.exe` →
  包仓库的 `build/zanc.exe` → 包仓库同级的 `zan*` 仓库 → PATH 上的 `zanc`。
- 产物：`build/platformer/Platformer.exe`；`assets/` 会复制到 exe 旁边（运行时磁盘优先）。

## 测试

```powershell
pwsh -File client/tools/test.ps1 -PackageProject D:/project/zan-head
```

三段全绿才算过：

1. `platformer_test_OK` —— 玩法断言用例（164 条断言：重力与落地、二段跳、加速与摩擦、
   **朝向取帧映射**、踩敌与撞敌、晶片、坠亡扣命与重生、三关推进与结算、存档读写、
   三个随机种子的完整流程）。
2. `platformer_SAVE_OK runs=1 -> runs=2` —— 存档写两遍读得到。
3. `platformer_SMOKE_OK` —— 无头冒烟跑满 180 帧自行退出。

用例源码：`client/tests/platformer_test.zan`（与 `src/` 一起编译，入口 `main.zan` 排除在外）。

## 截图验收

窗口像素抓取（`scripts/shot_window.py` 抓的是窗口真实像素，不是后端画布）：

```powershell
$out = 'build/platformer'
$env:ZAN_UI_OUT = "$out/uidrv"
$env:ZAN_UI_SCRIPT = 'client/tools/shot_face_right.script'   # 点「开始游戏」后按住 D
python D:/project/zan-lang/scripts/shot_window.py `
  "$out/Platformer.exe" "$out/ui_face_right.png" 4.2 $out
```

三个驱动脚本都在 `client/tools/`（可复现）：

| 脚本 | 产出 | 说明 |
|---|---|---|
| `shot_face_right.script` | `ui_face_right.png` | 按住 `D`，角色朝右 |
| `shot_face_left.script` | `ui_face_left.png` | 先右后左，角色朝左（松手后朝向保持） |
| `shot_settings.script` | `ui_settings.png` | `Esc` 打开设置浮层（皮肤包外观） |

脚本用引擎自带的 UiDriver 注入合成输入（**不移动系统鼠标**）；点击坐标是客户区
像素，窗口带标题栏时要加一个标题栏高度（见脚本注释）。

`PLATFORMER_DEMO=1` 是演示模式（自动向右走 + 周期起跳），给无头验收用。

## 环境变量

| 变量 | 作用 |
|---|---|
| `PLATFORMER_SMOKE=1` | 跑满 `PLATFORMER_FRAMES` 帧后自行退出（无头冒烟） |
| `PLATFORMER_FRAMES=<n>` | 冒烟帧数（默认 90） |
| `PLATFORMER_DEMO=1` | 演示模式：跳过菜单直接进关卡并自动操作 |
| `PLATFORMER_CAPTURE=<path>` | 指定帧把画布写成 `.zpx` 帧文件 |
| `PLATFORMER_SAVE=<dir>` | 存档目录（测试脚本用临时目录） |
