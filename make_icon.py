#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""生成应用图标 folder_plus.ico：蓝色文件夹 + 右下角绿色加号。

要点：
- 每个尺寸独立绘制（4x 超采样后 LANCZOS 降采样），边缘锐利；
- 用 build_ico() 手工拼 ICO 二进制（ICONDIR + 目录项 + PNG 负载），
  把 9 个尺寸全部嵌进去。不能用 PIL 的 save(sizes=..., append_images=...)：
  该写法在此环境只写首帧（曾只存 16px），Windows 放大显示就会糊；
- 校验方式：解析 ICO 目录确认帧数，别只信 PIL 的 seek。
依赖：Pillow（仅生成图标时用，主程序不需要）。
"""
from PIL import Image, ImageDraw

SIZES = [16, 20, 24, 32, 40, 48, 64, 128, 256]
MASTER = 256
SS = 4  # 超采样倍数


def draw_at(S: int, bold: bool = False) -> Image.Image:
    """在 S x S 画布上绘制（S 为超采样后的尺寸）。"""
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    c_tab = (25, 103, 210, 255)     # 背舌深蓝
    c_body = (47, 128, 237, 255)    # 主体蓝
    c_green = (21, 156, 71, 255)    # 深绿（对蓝底对比强）
    c_white = (255, 255, 255, 255)

    # ---- 文件夹 ----
    m = int(S * 0.05)
    tab_h = int(S * 0.14)
    body_top = int(S * 0.27)
    body_bot = S - m
    l, r = m, S - m
    rad = int(S * 0.09)

    d.rounded_rectangle([l, body_top - tab_h, int(S * 0.46), body_top + rad],
                        radius=rad, fill=c_tab)
    d.rounded_rectangle([l, body_top, r, body_bot], radius=rad, fill=c_body)

    # ---- 右下角加号（徽标不溢出边界）----
    cx, cy = int(S * 0.735), int(S * 0.735)
    r_badge = int(S * 0.245)
    d.ellipse([cx - r_badge, cy - r_badge, cx + r_badge, cy + r_badge],
              fill=c_green)
    t = int(S * 0.085)           # 笔画宽度（细，避免像医院十字）
    arm = int(S * 0.155)         # 臂半长（略长，更像“加号”）
    rr = max(1, t // 2)          # 圆头
    d.rounded_rectangle([cx - t // 2, cy - arm, cx + t // 2, cy + arm],
                        radius=rr, fill=c_white)
    d.rounded_rectangle([cx - arm, cy - t // 2, cx + arm, cy + t // 2],
                        radius=rr, fill=c_white)

    return img


def render(size: int) -> Image.Image:
    """返回指定尺寸的高质量图标（超采样母版降采样）。"""
    big = draw_at(size * SS)
    return big.resize((size, size), Image.LANCZOS)


def build_ico(path: str, images):
    """手工拼 ICO：每个尺寸作为独立 PNG 帧嵌入（Win10/11 支持），
    避免 PIL 只保留单帧导致小尺寸被放大而糊。"""
    import struct
    import io
    pngs = []
    for im in images:
        b = io.BytesIO()
        im.save(b, format="PNG")
        pngs.append(b.getvalue())
    n = len(images)
    header = struct.pack("<HHH", 0, 1, n)
    offset = 6 + 16 * n
    entries, data = b"", b""
    for im, png in zip(images, pngs):
        w, h = im.size
        wb = 0 if w >= 256 else w
        hb = 0 if h >= 256 else h
        entries += struct.pack("<BBBBHHII", wb, hb, 0, 0, 1, 32, len(png), offset)
        data += png
        offset += len(png)
    with open(path, "wb") as f:
        f.write(header + entries + data)


def main():
    out = "folder_plus.ico"
    images = [render(s) for s in SIZES]           # 每个尺寸独立高质量渲染
    build_ico(out, images)
    print("已生成", out, "尺寸:", SIZES)

    # 校验：读回 ICO，打印实际帧
    im = Image.open(out)
    seen = []
    try:
        i = 0
        while True:
            im.seek(i)
            seen.append(im.size)
            i += 1
    except EOFError:
        pass
    print("ICO 实际帧数:", len(seen), "帧:", seen)

    # 预览：导出真实帧（16/32 用最近邻放大，看真实像素）
    for want, name, scale in [(256, "_v256.png", 1), (32, "_v32.png", 4),
                              (16, "_v16.png", 8)]:
        for i, sz in enumerate(seen):
            if sz[0] == want:
                im.seek(i)
                fr = im.convert("RGBA")
                fr.resize((want * scale, want * scale), Image.NEAREST).save(name)
                break
    print("预览导出: _v256.png / _v32.png / _v16.png")


if __name__ == "__main__":
    main()
