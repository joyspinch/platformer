# 跃迁山谷 · PLATFORMER

> 横版重力跳跃闯关：跑、跳、二段跳、踩巡逻兵、捡晶片、插旗过关，三关打通进结算。

用 [Zan](https://github.com/joyspinch/zan-lang) 语言写的独立游戏项目（仓库根自带 git 仓库）。完整设计与实现说明见 [`PROJECT.md`](PROJECT.md)。

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

| 关卡 | 名字 | 宽 | 特点 |
|---|---|---|---|
| 1 | 苔谷浅滩 | 2400 | 两处缺口 + 8 块浮空平台，4 个巡逻兵 |
| 2 | 熔痕裂谷 | 2600 | 四处缺口，平台更碎，7 个巡逻兵 |
| 3 | 霜夜尖塔 | 2800 | 缺口与高台交替，10 个巡逻兵 |

## 构建

需要 [zan-lang](https://github.com/joyspinch/zan-lang) 仓库（`zanc` 编译器、公共包与 stdlib 都在里面）：

```powershell
git clone https://github.com/joyspinch/zan-lang.git
$env:ZAN_HOME = 'D:/path/to/zan-lang'   # 指到刚克隆的 zan-lang 仓库根

pwsh -File client/tools/build.ps1
```

产物：`build/platformer/Platformer.exe`（运行目录要带上它旁边的 `assets/` 与 `skins/`）。

## 运行

```powershell
cd build/platformer
.\Platformer.exe
```

## 测试

```powershell
pwsh -File client/tools/test.ps1
```

## 目录结构

```
platformer/
client/
  src/      # 游戏源码（.zan 源码 + HTML 界面设计稿）
  assets/   # 位图 / 音频素材
  data/     # 数值表与数据文件
  tests/    # 玩法断言用例
  tools/    # 构建与测试脚本
PROJECT.md
```

## 素材与授权

- 素材清单与授权说明见 [`client/ASSETS.md`](client/ASSETS.md)。

## 许可

本仓库暂未附带 `LICENSE` 文件，开源许可待作者选定后补充。依赖的 zan-lang 仓库采用 ZCSL（Zan Community Source License 1.0）。

## 更多文档

- [`PROJECT.md`](PROJECT.md) —— 完整设计与实现说明
- [`client/ASSETS.md`](client/ASSETS.md) —— 素材清单
