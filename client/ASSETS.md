# 跃迁山谷 · PLATFORMER · 素材清单

本项目的位图分三类：

- **AI 生成主体**：用 `local-image2` 技能（gpt-image-2.5）生成 1024×1024 原图，
  再用 `client/tools/make_assets.py` 抠底、裁边、缩放到**显示尺寸的 2 倍**入库。
- **朝向帧**：在上面的处理链末尾加一步 `Image.transpose(Image.FLIP_LEFT_RIGHT)`，
  把主体烘焙成**两帧精灵表**（引擎运行时不能翻转贴图，方向只能离线做）。
- **程序化 UI 件**：九宫格面板底板、按钮底板、落地投影、尾焰、角色柔光——
  由 `client/tools/make_assets.py` 用 PIL 直接画（九宫格要求圆弧完整落在角切片内、
  中间必须可拉伸，AI 出图保证不了；程序化画更准也更可复现）。

音效是脚本合成的短音（22050Hz / 单声道 / 16bit）。

**总量**：位图 15 张（≈410 KB）+ 音效 8 个（90 KB）= 500 KB。

## 一、位图（`client/assets/`）

| 文件 | 像素 | 入库大小 | 显示尺寸 | 用途 |
|---|---|---|---|---|
| `bg_far.png` | 1536×576 | 154 KB | 1280×640 | 视差远景：黄昏天色 + 远山剪影（裁源矩形取景，随相机 0.10 速滚动） |
| `bg_mid.png` | 1536×225 | 26 KB | 1280×250 | 视差中景：松树顶（0.20 速滚动） |
| `bg_near.png` | 1536×298 | 102 KB | 1280×331 | 视差近景：灌木与碎石（0.30 速滚动，底边贴地面线） |
| `player_sheet.png` | 144×100 | 33 KB | 36×50 | 玩家角色**两帧精灵表**（0=朝右 原图 / 1=朝左 镜像） |
| `drone_sheet.png` | 176×76 | 28 KB | 44×38 | 巡逻兵**两帧精灵表**（0=朝右 / 1=朝左；贴图本身左右对称，朝向靠尾焰标出） |
| `shard.png` | 56×72 | 7 KB | 28×36 | 晶片＝金币（可收集物） |
| `tile_ground.png` | 128×128 | 45 KB | 64×64 | 地形砖块（顶面带苔藓草沿，平台与地面段平铺） |
| `flag.png` | 80×128 | 10 KB | 40×64 | 出口旗（关底目标，踩到即通关） |
| `ui_board.png` | 96×96 | 1 KB | 任意 | **九宫格面板底板**：HUD 面板 / 底部提示条 / 结算面板 |
| `ui_button.png` | 64×48 | 0.4 KB | 任意 | 按钮底板（常态） |
| `ui_button_hover.png` | 64×48 | 0.4 KB | 任意 | 按钮底板（悬停） |
| `ui_button_primary.png` | 64×48 | 0.5 KB | 任意 | 按钮底板（主按钮） |
| `shadow.png` | 96×32 | 0.8 KB | 44×11 / 36×9 | 落地投影（软椭圆） |
| `flare.png` | 64×24 | 0.5 KB | 28×12 | 巡逻兵尾焰（朝向指示） |
| `glow.png` | 96×96 | 1.6 KB | 62×76 | 角色背后的柔光（把主体从背景里托出来） |

处理链：生成 1024×1024 → 黑底洪泛抠 alpha → 裁到内容边界 → 边缘柔化 →
缩放到显示尺寸 2 倍 → PNG 量化（背景 128 色）。

脚本都入库、可复现：

```powershell
pwsh -File client/tools/gen_assets.ps1     # 生成原图到 build/raw/（不入库）
python client/tools/make_assets.py          # 后处理 → client/assets/
```

## 二、朝向帧规则（引擎限制 → 离线烘焙）

引擎运行时转不了图：`Canvas.BlitImage` 只有源矩形 (sx,sy,sw,sh)，**没有旋转、
没有水平翻转**；`Gui.SpriteBatch` 的每精灵同样只有 dx,dy,dw,dh,sx,sy,sw,sh,tint。
所以"角色朝哪边"只能烘焙进素材，运行时按状态取帧。

| 主体 | 精灵表 | 帧宽×帧高（源图像素） | 显示尺寸 | 帧索引 → 含义 |
|---|---|---|---|---|
| 玩家 | `player_sheet.png` | 72×100 | 36×50 | `0` = 朝右（原图），`1` = 朝左（镜像） |
| 巡逻兵 | `drone_sheet.png` | 88×76 | 44×38 | `0` = 朝右（原图），`1` = 朝左（镜像） |

取帧规则（唯一真源在 `client/src/PlatformerFacing.zan`）：

```
帧索引   = facingRight ? 0 : 1
源矩形   = (帧索引 * 帧宽, 0, 帧宽, 帧高)      ← 源图像素，不是显示像素
```

- 帧索引由 `PlatformerFacing.PlayerFrame(facingRight)` /
  `PlatformerFacing.DroneFrame(facingRight)` 给出（纯函数，断言用例按它钉住）。
- 源矩形左边界由 `PlayerSrcX()` / `DroneSrcX()` 给出，运行时用
  `Canvas.BlitImage` 的源矩形裁帧。
- 镜像帧同样走一遍抠底与边缘柔化（镜像本身不脏，但入库口径统一）。
- 巡逻兵贴图左右对称，镜像几乎看不出差别，所以画面上另加**尾焰**
  （`flare.png`）标出前进方向。

## 三、九宫格规则（引擎没有 border-image）

九宫格自己切：`PlatformerPaint.NineSlice` 用 `Canvas.BlitImage` 的源矩形把底板
裁成 9 块拼起来（四角原样、上下左右边拉伸、中间平铺）。

| 底板 | 角切片边长（源图像素） | 用在哪 |
|---|---|---|
| `ui_board.png` | 16 | HUD 面板（440×86）、底部提示条、结算面板（560×380） |
| `ui_button*.png` | 14 | 画布上的按钮（180×48 / 88×34） |

角切片之外的像素会被拉伸，因此所有圆弧与装饰必须落在角切片内——这也是 UI 件
用程序化生成而不是 AI 出图的原因。

## 四、皮肤包（`client/assets/skins/platformer/skin.css`）

设置浮层用标准库控件（Panel/Flex/Label/Button），外观由**皮肤包**决定：

- 令牌（`:root`）：暖橙金 `--primary`、石板灰 `--bg-secondary` / `--bg-tertiary`、
  米白 `--text-primary`、暖石板 `--border-primary`、圆角 `--radius-*` 与
  `--border-radius-*`（后者才进 Theme）等。
- 规则：`button`（含 `:hover` / `:active` / `button.primary`）、`label`、
  `panel.card`（设置浮层那张卡）。
- 构建拷到 `build/platformer/skins/platformer/`（exe 同级），
  启动时 `host.App().UseSkin("platformer")` 应用（在默认皮肤之后）。

## 五、音效（`client/assets/sfx/`）

| 文件 | 时长 | 触发时机 | 合成方式 |
|---|---|---|---|
| `jump.wav` | 0.18s | 起跳（地面跳与二段跳同一音） | 方波 420→900Hz 上滑 |
| `land.wav` | 0.12s | 从空中落到平台顶 | 220→120Hz 正弦 + 噪声 |
| `shard.wav` | 0.20s | 拾取晶片 | 1180Hz + 1760Hz 双正弦 |
| `stomp.wav` | 0.16s | 踩扁巡逻兵 | 噪声爆 + 520→160Hz 方波 |
| `hurt.wav` | 0.26s | 撞到巡逻兵扣血 | 方波 520→190Hz 下行 |
| `die.wav` | 0.55s | 坠亡扣命 | 锯齿 700→120Hz 长滑音 |
| `clear.wav` | 0.26s | 通关一关 | 660/880/1320Hz 上行三音 |
| `over.wav` | 0.34s | 结算（三关通关或命用尽） | 660/520/330Hz 下行三音 |

音效由公共包 `Game.Foundation.SfxBank` 加载（磁盘优先 + 内嵌兜底 + 限频），
没有音频设备时静默失效、游戏照常跑。设置浮层里可以关掉音效。

## 六、授权与来源

- 全部位图：本项目用 AI 生成 + 脚本后处理自制，**未取用任何第三方游戏素材**。
- 全部音效：脚本合成，无采样库来源。
- 玩法结构（横版重力跳跃、巡逻兵、收集物、视差分层）参考横版平台跳跃这一**通用玩法类型**，
  不复制任何具体作品的代码或素材。
