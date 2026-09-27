"""チャンネルアイコン（800x800）とバナー（2560x1440）を作る"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from PIL import Image, ImageDraw  # noqa: E402

from engine.core import PAL, MapBase, font  # noqa: E402

OUT = os.path.dirname(__file__)


def icon():
    im = Image.new("RGB", (800, 800), PAL["ink"])
    d = ImageDraw.Draw(im)
    d.ellipse([40, 40, 760, 760], outline=PAL["gold"], width=18)
    # 地球の経緯線
    for k in (0.35, 0.7):
        w = 300 * k
        d.ellipse([400 - w, 110, 400 + w, 690], outline=(70, 85, 120), width=6)
    for y in (250, 400, 550):
        d.line([(130, y), (670, y)], fill=(70, 85, 120), width=6)
    d.text((400, 330), "世界史", font=font("black", 150), fill=PAL["white"], anchor="mm",
           stroke_width=10, stroke_fill=PAL["ink"])
    d.text((400, 510), "ずかん", font=font("black", 170), fill=PAL["gold"], anchor="mm",
           stroke_width=10, stroke_fill=PAL["ink"])
    im.save(os.path.join(OUT, "icon_800.png"))


def banner():
    W, H = 2560, 1440
    m = MapBase()
    lon0, lat0, lon1, lat1 = -12, 58, 46, 27
    x0, y0 = m.bxy(lon0, lat0)
    x1, y1 = m.bxy(lon1, lat1)
    cw = x1 - x0
    ch = cw * H / W
    cy = (y0 + y1) / 2
    im = m.img.crop((int(x0), int(cy - ch / 2), int(x1), int(cy + ch / 2))).resize((W, H), Image.LANCZOS)
    im = im.convert("RGBA")
    ov = Image.new("RGBA", (W, H), (*PAL["ink"], 95))
    im.alpha_composite(ov)
    d = ImageDraw.Draw(im)
    # 全端末で表示される安全領域 1546x423 に文字を収める
    cx, cy = W // 2, H // 2
    d.text((cx, cy - 70), "世界史ずかん", font=font("black", 170), fill=PAL["white"], anchor="mm",
           stroke_width=12, stroke_fill=PAL["ink"])
    d.text((cx, cy + 95), "教科書の世界史を、地図と図解で60秒に。", font=font("black", 62),
           fill=PAL["gold"], anchor="mm", stroke_width=8, stroke_fill=PAL["ink"])
    d.text((cx, cy + 180), "受験版 × 教養版で配信中", font=font("bold", 48), fill=PAL["white"], anchor="mm",
           stroke_width=6, stroke_fill=PAL["ink"])
    im.convert("RGB").save(os.path.join(OUT, "banner_2560x1440.png"))


if __name__ == "__main__":
    icon()
    banner()
