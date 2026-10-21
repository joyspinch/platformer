# 素材处理链：AI 原图 → 抠底 / 裁边 / 缩放 → 入库 client/assets/。
#
# 用法（在仓库根 platformer/ 下）：
#     python client/tools/make_assets.py
#
# 两类素材：
#   1) 位图主体（玩家 / 巡逻兵 / 晶片 / 地形 / 旗子 / 三层背景）——
#      来自 build/raw/ 里 image2 生成的 1024x1024 原图（不入库），
#      抠黑底 → 裁内容边界 → 边缘柔化 → 缩放到「显示尺寸 x2」入库。
#   2) 朝向帧 —— 玩家与巡逻兵各出一张**两帧精灵表**（左帧=原图朝右，
#      右帧=水平镜像朝左）。引擎运行时不能翻转贴图（Canvas.BlitImage
#      只有源矩形，没有旋转/镜像），所以方向只能离线烘焙。
#   3) UI 底板与投影 —— 九宫格面板底板、按钮底板、落地投影都是
#      **程序化生成**（不是 AI 生成）：九宫格要求四角的圆弧与内框
#      完整落在角切片内、中间必须能拉伸，AI 出图保证不了这一点，
#      程序化画反而更准也更可复现。
#
# 入库目录：client/assets/（构建时拷到 exe 旁，运行时磁盘优先）。
import math
import os
from collections import deque

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))       # platformer/
RAW = os.path.join(ROOT, "build", "raw")
if not os.path.isdir(RAW):
    RAW = os.path.join(ROOT, "build", "assets_raw")
OUT = os.path.join(ROOT, "client", "assets")

# ---- 色板（与 client/src/PlatformerPalette.zan 同一套语义色） ----------
C_BOARD_TOP = (0x27, 0x2D, 0x38)
C_BOARD_BOTTOM = (0x18, 0x1C, 0x24)
C_BOARD_EDGE = (0xC9, 0x8A, 0x3C)     # 暖橙金外框
C_BOARD_INNER = (0x46, 0x50, 0x60)    # 内框线
C_RIVET = (0xE6, 0xB3, 0x68)          # 角铆钉

C_BTN_TOP = (0x33, 0x3B, 0x47)
C_BTN_BOTTOM = (0x27, 0x2E, 0x38)
C_BTN_EDGE = (0x56, 0x61, 0x6F)
C_BTN_HOVER_TOP = (0x41, 0x4B, 0x59)
C_BTN_HOVER_BOTTOM = (0x33, 0x3C, 0x48)
C_BTN_HOVER_EDGE = (0xE0, 0xA8, 0x5C)
C_BTN_PRIMARY_TOP = (0xE8, 0x9A, 0x45)
C_BTN_PRIMARY_BOTTOM = (0xC8, 0x7B, 0x2C)
C_BTN_PRIMARY_EDGE = (0x7E, 0x4A, 0x19)

# 九宫格角切片边长（像素）。角切片之外的像素会被拉伸，
# 因此所有圆弧与装饰都必须落在角切片内。
BOARD_CORNER = 16
BUTTON_CORNER = 14


# ---------------------------------------------------------------- 通用工具


def key_out_black(img, thresh=26):
    """把与画布边界连通的近黑像素抠成透明（洪泛，不动内部暗部）。"""
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    seen = bytearray(w * h)
    q = deque()

    def is_bg(x, y):
        r, g, b, a = px[x, y]
        return a > 0 and r <= thresh and g <= thresh and b <= thresh

    for x in range(w):
        for y in (0, h - 1):
            if is_bg(x, y):
                q.append((x, y))
                seen[y * w + x] = 1
    for y in range(h):
        for x in (0, w - 1):
            if is_bg(x, y) and not seen[y * w + x]:
                q.append((x, y))
                seen[y * w + x] = 1

    while q:
        x, y = q.popleft()
        r, g, b, _ = px[x, y]
        px[x, y] = (r, g, b, 0)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx]:
                if is_bg(nx, ny):
                    seen[ny * w + nx] = 1
                    q.append((nx, ny))
    return img


def trim(img):
    bbox = img.getchannel("A").getbbox()
    if bbox is None:
        return img
    return img.crop(bbox)


def soften_fringe(img, lo=26, hi=90):
    """边缘半透明化：紧贴透明区的暗像素按亮度渐隐，去掉黑边光晕。"""
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    out = img.copy()
    opx = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            m = max(r, g, b)
            if m > hi:
                continue
            near = False
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3] == 0:
                    near = True
                    break
            if near:
                k = (m - lo) / float(hi - lo)
                if k < 0:
                    k = 0.0
                opx[x, y] = (r, g, b, int(a * k))
    return out


def save(img, name, colors=0):
    if colors:
        img = img.quantize(colors=colors, method=Image.FASTOCTREE)
    img.save(os.path.join(OUT, name), optimize=True)
    size = os.path.getsize(os.path.join(OUT, name))
    print("%-22s %-12s %6.1f KB" % (name, str(img.size), size / 1024.0))


def raw(name):
    if not name.endswith(".png"):
        name = name + ".png"
    return Image.open(os.path.join(RAW, name))


def sprite(name, out_name, size, colors=0):
    img = key_out_black(raw(name))
    img = trim(img)
    img = soften_fringe(img)
    img = img.resize(size, Image.LANCZOS)
    save(img, out_name, colors)


def band(name, out_name, rows, scale, colors=0):
    """背景层：裁一条横向带 → 放大 → 保住 alpha。"""
    img = key_out_black(raw(name))
    img = img.crop((0, rows[0], 1024, rows[1]))
    w = int(1024 * scale)
    h = int((rows[1] - rows[0]) * scale)
    img = img.resize((w, h), Image.LANCZOS)
    save(img, out_name, colors)


# ------------------------------------------------------------ 朝向精灵表


def facing_sheet(name, out_name, frame_size):
    """两帧精灵表：第 0 帧 = 原图（朝右），第 1 帧 = 水平镜像（朝左）。

    取帧规则（写进 ASSETS.md，断言用例按它钉住）：
        帧索引 = 0 → 朝右，1 → 朝左
        源矩形 = (索引 * 帧宽, 0, 帧宽, 帧高)
    镜像帧同样走一遍抠底/柔化（镜像本身不脏，但入库口径统一）。
    """
    img = key_out_black(raw(name))
    img = trim(img)
    img = soften_fringe(img)
    img = img.resize(frame_size, Image.LANCZOS)
    fw, fh = frame_size
    sheet = Image.new("RGBA", (fw * 2, fh), (0, 0, 0, 0))
    sheet.paste(img, (0, 0))
    sheet.paste(img.transpose(Image.FLIP_LEFT_RIGHT), (fw, 0))
    # 镜像帧再柔化一次：两帧的边缘口径保持一致。
    sheet = soften_fringe(sheet)
    save(sheet, out_name)


# ------------------------------------------------------- 程序化 UI 底板


def rounded_gradient(size, radius, top, bottom):
    """竖向渐变 + 圆角遮罩（外接圆角矩形以外的像素全透明）。"""
    w, h = size
    grad = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(grad)
    for y in range(h):
        t = y / float(max(1, h - 1))
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c + (255,))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1],
                                           radius=radius, fill=255)
    grad.putalpha(mask)
    return grad


def make_board(out_name, size=96, radius=14):
    """面板底板（九宫格源）：外金框 + 内灰线 + 四角铆钉。

    所有圆弧都落在 BOARD_CORNER 角切片内，中间是纯渐变（可拉伸）。
    """
    img = rounded_gradient((size, size), radius, C_BOARD_TOP, C_BOARD_BOTTOM)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius,
                        outline=C_BOARD_EDGE + (255,), width=2)
    inner = 6
    d.rounded_rectangle([inner, inner, size - 1 - inner, size - 1 - inner],
                        radius=max(2, radius - inner),
                        outline=C_BOARD_INNER + (255,), width=1)
    rivet = 13
    for cx, cy in ((rivet, rivet), (size - 1 - rivet, rivet),
                   (rivet, size - 1 - rivet), (size - 1 - rivet, size - 1 - rivet)):
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=C_RIVET + (255,))
    save(img, out_name)


def make_button(out_name, top, bottom, edge, size=(64, 48), radius=10):
    """按钮底板（九宫格源）：渐变面 + 2px 描边。"""
    img = rounded_gradient(size, radius, top, bottom)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius,
                        outline=edge + (255,), width=2)
    save(img, out_name)


def make_shadow(out_name, size=(96, 32), peak=200):
    """落地投影：软边椭圆（中心最实，边缘淡出），纯黑带蓝调。"""
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    rx = w / 2.0
    ry = h / 2.0
    for y in range(h):
        for x in range(w):
            dx = (x - cx) / rx
            dy = (y - cy) / ry
            d = math.sqrt(dx * dx + dy * dy)
            if d >= 1.0:
                continue
            a = (1.0 - d) ** 1.6
            px[x, y] = (8, 10, 18, int(peak * a))
    save(img, out_name)


def make_flare(out_name, size=(64, 24), peak=215):
    """尾焰：横向软椭圆（暖橙）。巡逻兵贴图左右对称，靠它标出前进方向。"""
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    rx = w / 2.0
    ry = h / 2.0
    for y in range(h):
        for x in range(w):
            dx = (x - cx) / rx
            dy = (y - cy) / ry
            d = math.sqrt(dx * dx + dy * dy)
            if d >= 1.0:
                continue
            a = (1.0 - d) ** 1.4
            px[x, y] = (0xFF, 0xC4, 0x6B, int(peak * a))
    save(img, out_name)


def make_glow(out_name, size=(96, 96), peak=64):
    """角色背后的柔光：径向暖光，把主体从背景里托出来。"""
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = img.load()
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    rx = w / 2.0
    ry = h / 2.0
    for y in range(h):
        for x in range(w):
            dx = (x - cx) / rx
            dy = (y - cy) / ry
            d = math.sqrt(dx * dx + dy * dy)
            if d >= 1.0:
                continue
            a = (1.0 - d) ** 2.0
            px[x, y] = (0xFF, 0xE0, 0xB0, int(peak * a))
    save(img, out_name)


# ------------------------------------------------------------------ 主流程


def main():
    os.makedirs(OUT, exist_ok=True)

    # --- 背景三层（视差）：同一套取景口径，源图横向 1.5 倍放大 ---
    band("bg_far", "bg_far.png", (267, 651), 1.5, colors=128)
    band("bg_mid", "bg_mid.png", (500, 650), 1.5, colors=128)
    band("bg_near", "bg_near.png", (778, 977), 1.5, colors=128)

    # --- 主体位图：显示尺寸的 2 倍 ---
    sprite("shard", "shard.png", (56, 72))
    sprite("tile_ground", "tile_ground.png", (128, 128))
    sprite("flag", "flag.png", (80, 128))

    # --- 朝向精灵表（两帧：右 / 左） ---
    facing_sheet("player", "player_sheet.png", (72, 100))
    facing_sheet("drone", "drone_sheet.png", (88, 76))

    # --- 程序化 UI 底板与投影 ---
    make_board("ui_board.png")
    make_button("ui_button.png", C_BTN_TOP, C_BTN_BOTTOM, C_BTN_EDGE)
    make_button("ui_button_hover.png", C_BTN_HOVER_TOP, C_BTN_HOVER_BOTTOM,
                C_BTN_HOVER_EDGE)
    make_button("ui_button_primary.png", C_BTN_PRIMARY_TOP, C_BTN_PRIMARY_BOTTOM,
                C_BTN_PRIMARY_EDGE)
    make_shadow("shadow.png")
    make_flare("flare.png")
    make_glow("glow.png")

    # --- 清理上一版被替换掉的素材 ---
    for dead in ("player.png", "drone.png", "hud_panel.png"):
        p = os.path.join(OUT, dead)
        if os.path.exists(p):
            os.remove(p)
            print("removed  " + dead)

    total = sum(os.path.getsize(os.path.join(OUT, f))
                for f in os.listdir(OUT) if f.endswith(".png"))
    print("total png: %.1f KB" % (total / 1024.0))


if __name__ == "__main__":
    main()
