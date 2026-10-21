# 雪线跳跃 —— 2D 横向卷轴平台跳跃

> 本文件是 platformer 项目的落地说明。**素材清单见 `client/ASSETS.md`**，全局规格见工作区根的 `ASSET-PIPELINE.md`。

## 参考源与授权边界

- **参考**：SuperTux（GPLv2+；素材逐件许可见 `data/AUTHORS`）
- **抄什么**：抄关卡结构、瓦片化地形、雪球物理、视差背景分���、检查点与收集物。角色与关卡美术全部自研。

**红线与差异**：

- SuperTux 素材按件授权，**不可整体打包**；本项目只取规格参照，像素全部重画。
- 不抄 SuperTux 的 `images/objects/conveyor_belt/*`（CC BY-NC 4.0，禁商用）。
- 不使用关卡编辑器（.txt 脚本），关卡用本项目自有的 JSON 描述。

## 渲染路线

2D 贴图批（`Gui.SpriteBatch`）。角色 5 向 + 左右镜像，动画帧走 `DirectionalAnimator` 出 UV、绘制层自写 UV→源像素矩形桥接。

## 目录

    platformer/
      client/       src/ 源码、assets/ 素材、data/ 数据、skins/ 皮肤、tools/ 脚本、tests/ 用例
      build/        编译产物（不入库）

所有命令都在**项目根**下执行（路径相对项目根）。

## 编译

```powershell
$env:ZAN_HOME = 'D:/project/zan-lang'   # 编译器与 stdlib 同源；公共包在它的 packages/ 下
pwsh -File client/tools/build.ps1
```

ZAN_HOME 指向 zan-lang 仓库时用它的 `build/zanc.exe` 与 `stdlib/`；不设则用 PATH 上的 `zanc`。
编译时加 `--package-project $env:ZAN_HOME` 可直接吃仓库里的 `packages/`。

## 测试

```powershell
pwsh -File client/tools/test.ps1     # 无头冒烟：跑满 90 帧后自行退出
```

工作区批量冒烟：在 zan-lang 仓库侧跑 `pwsh -File scripts/smoke_all_game_projects.ps1`（一次跑完仓库外全部游戏项目）。

## 当前状态

骨架可编译可运行（90 帧无头冒烟通过）：横版卷轴、雪地物理、视差背景、收集物。

## 后续（按优先级）

1. 接入真实位图 sprite 与音效（素材见 `client/ASSETS.md`）。
2. 补玩法深度：参照源的关卡/数值/AI 三个维度逐项对齐。
3. 需要时再评估联网（`legend` 有服务端可参考）。