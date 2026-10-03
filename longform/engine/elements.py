"""図解・地図アニメ用の演出要素（横型ステージ 1920x816 用）

x, y を取る図解要素はステージ内の座標（左上が 0,0）。地図要素は経度・緯度。
"""
import math

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from .core import (El, PAL, STAGE_H, STAGE_Y, W, clamp, draw_markup, ease_back, ease_io, ease_out, font,
                   markup_w, text_w, with_alpha)


def _label(d, x, y, txt, f, col=PAL["ink"], a=1.0, anchor="lm", stroke=6):
    d.text((x, y), txt, font=f, fill=with_alpha(col, a), anchor=anchor,
           stroke_width=stroke, stroke_fill=with_alpha(PAL["white"], a))


def _fade_img(im, a):
    if a >= 0.999:
        return im
    im = im.copy()
    im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return im


# ================================================================= 地図の上の要素
class MapLabel(El):
    """海・地域名などの地図上の文字"""
    sfx = None

    def __init__(self, lon, lat, text, size=40, col=PAL["teal"], serif=True, **kw):
        super().__init__(**kw)
        self.lon, self.lat, self.text, self.size, self.col, self.serif = lon, lat, text, size, col, serif

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        x, y = fr.xy(self.lon, self.lat)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        f = font("serif" if self.serif else "black", self.size)
        if sum(self.col) > 600:  # 明るい文字は暗い縁取りで（衛星写真風の地図用）
            d.text((x, y), self.text, font=f, fill=with_alpha(self.col, a), anchor="mm", stroke_width=5,
                   stroke_fill=(10, 14, 24, int(200 * a)))
        else:
            _label(d, x, y, self.text, f, self.col, a, anchor="mm", stroke=5)
        fr.comp(L)


class Marker(El):
    """地点マーカー（波紋＋ラベル）"""

    def __init__(self, lon, lat, text, col=PAL["red"], side="r", sub=None, size=44, **kw):
        super().__init__(**kw)
        self.lon, self.lat, self.text, self.col, self.side, self.sub = lon, lat, text, col, side, sub
        self.size = size

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        x, y = fr.xy(self.lon, self.lat)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        for k in range(2):
            ph = ((lt * 0.8 + k * 0.5) % 1.0)
            r = 12 + ph * 40
            d.ellipse([x - r, y - r, x + r, y + r], outline=with_alpha(self.col, a * (1 - ph) * 0.8), width=4)
        s = ease_back(lt / 0.3)
        r = 13 * s
        d.ellipse([x - r, y - r, x + r, y + r], fill=with_alpha(self.col, a),
                  outline=with_alpha(PAL["white"], a), width=4)
        f = font("black", self.size)
        fs = font("bold", int(self.size * 0.62))
        ta = a * clamp((lt - 0.1) / 0.25)
        dx = (1 - ease_out((lt - 0.1) / 0.3)) * 20
        off = self.size * 0.95
        if self.side == "r":
            _label(d, x + 26 + dx, y, self.text, f, self.col, ta, "lm", 6)
            if self.sub:
                _label(d, x + 28 + dx, y + off, self.sub, fs, PAL["ink"], ta, "lm", 5)
        elif self.side == "l":
            _label(d, x - 26 - dx, y, self.text, f, self.col, ta, "rm", 6)
            if self.sub:
                _label(d, x - 28 - dx, y + off, self.sub, fs, PAL["ink"], ta, "rm", 5)
        elif self.side == "t":
            _label(d, x, y - 28 - dx, self.text, f, self.col, ta, "mb", 6)
            if self.sub:
                _label(d, x, y - 28 - off * 1.1 - dx, self.sub, fs, PAL["ink"], ta, "mb", 5)
        else:
            _label(d, x, y + 28 + dx, self.text, f, self.col, ta, "mt", 6)
            if self.sub:
                _label(d, x, y + 28 + off * 1.15 + dx, self.sub, fs, PAL["ink"], ta, "mt", 5)
        fr.comp(L)


class Dot(El):
    """小さな点（ポリスの分布など）。ラベルなし"""
    sfx = None

    def __init__(self, pts, col=PAL["red"], r=7, dt=0.04, **kw):
        super().__init__(**kw)
        self.pts, self.col, self.r, self.dt = pts, col, r, dt

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        for i, (lo, la) in enumerate(self.pts):
            k = ease_back((lt - i * self.dt) / 0.25)
            if k <= 1e-3:
                continue
            x, y = fr.xy(lo, la)
            r = self.r * clamp(k, 0, 1.3)
            d.ellipse([x - r, y - r, x + r, y + r], fill=with_alpha(self.col, a),
                      outline=with_alpha(PAL["white"], a), width=2)
        fr.comp(L)


class Glow(El):
    """地域を強調する楕円の光"""
    sfx = None

    def __init__(self, lon, lat, rx, ry, col=PAL["gold"], **kw):
        super().__init__(**kw)
        self.lon, self.lat, self.rx, self.ry, self.col = lon, lat, rx, ry, col

    def draw(self, fr, lt):
        a = self.alpha(fr.t) * (0.75 + 0.25 * math.sin(lt * 4))
        x, y = fr.xy(self.lon, self.lat)
        z = fr.zoom()
        rx, ry = self.rx * z * ease_out(lt / 0.5), self.ry * z * ease_out(lt / 0.5)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=with_alpha(self.col, 0.18 * a),
                  outline=with_alpha(self.col, 0.9 * a), width=5)
        fr.comp(L)


def _smooth_closed(pts, n=8):
    """閉じた多角形を Catmull-Rom でなめらかにする"""
    out = []
    m = len(pts)
    for i in range(m):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % m], pts[(i + 2) % m]
        for s in range(n):
            t = s / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t
                                    + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    return out


class Region(El):
    """勢力範囲（陸地だけを塗る）。poly は (経度, 緯度) の列"""
    sfx = None

    def __init__(self, poly, col=PAL["red"], label=None, label_at=None, label_size=46, opacity=0.38, **kw):
        super().__init__(**kw)
        self.poly, self.col, self.label, self.label_at = poly, col, label, label_at
        self.label_size, self.opacity = label_size, opacity

    def draw(self, fr, lt):
        a = self.alpha(fr.t) * ease_out(lt / 0.7)
        pts = _smooth_closed([fr.xy(lo, la) for lo, la in self.poly])
        pts = [(x, y - STAGE_Y) for x, y in pts]
        fill = Image.new("L", (W, STAGE_H), 0)
        d = ImageDraw.Draw(fill)
        d.polygon(pts, fill=int(255 * self.opacity))
        edge = Image.new("L", (W, STAGE_H), 0)
        ImageDraw.Draw(edge).line(pts + [pts[0]], fill=235, width=5, joint="curve")
        alpha = ImageChops.lighter(fill, edge)
        alpha = ImageChops.multiply(alpha, fr.v.map.land_mask(fr.cam))
        if a < 0.999:
            alpha = alpha.point(lambda v: int(v * a))
        col = Image.new("RGBA", (W, STAGE_H), (*self.col, 255))
        col.putalpha(alpha)
        fr.canvas.alpha_composite(col, (0, STAGE_Y))
        if self.label:
            la = a * clamp((lt - 0.3) / 0.3)
            x, y = fr.xy(*self.label_at)
            L = fr.layer()
            for i, line in enumerate(self.label.split("/")):
                _label(ImageDraw.Draw(L), x, y + i * self.label_size * 1.15, line,
                       font("black", self.label_size), self.col, la, "mm", 7)
            fr.comp(L)


class Arrow(El):
    """経路が伸びていく矢印（民族移動・遠征など）"""
    sfx = "whoosh"

    def __init__(self, path, col=PAL["red"], width=14, draw_dur=1.4, label=None, label_at=0.5, label_dx=30,
                 label_dy=0, label_anchor="lm", dashed=False, **kw):
        super().__init__(**kw)
        self.path, self.col, self.width, self.draw_dur = path, col, width, draw_dur
        self.label, self.label_at, self.label_dx, self.label_dy = label, label_at, label_dx, label_dy
        self.label_anchor, self.dashed = label_anchor, dashed

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        pts = [fr.xy(lo, la) for lo, la in self.path]
        sm = []
        for i in range(len(pts) - 1):
            p0, p1 = pts[max(0, i - 1)], pts[i]
            p2, p3 = pts[i + 1], pts[min(len(pts) - 1, i + 2)]
            for s in range(12):
                t = s / 12
                t2, t3 = t * t, t * t * t
                sm.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t
                                       + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                       + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
        sm.append(pts[-1])
        seg = [math.dist(sm[i], sm[i + 1]) for i in range(len(sm) - 1)]
        total = sum(seg)
        want = total * ease_io(lt / self.draw_dur)
        out, acc = [sm[0]], 0.0
        for i, sl in enumerate(seg):
            if acc + sl >= want:
                r = (want - acc) / sl if sl else 0
                out.append((sm[i][0] + (sm[i + 1][0] - sm[i][0]) * r, sm[i][1] + (sm[i + 1][1] - sm[i][1]) * r))
                break
            out.append(sm[i + 1])
            acc += sl
        L = fr.layer()
        d = ImageDraw.Draw(L)
        if len(out) >= 2:
            d.line(out, fill=with_alpha(PAL["white"], a), width=self.width + 8, joint="curve")
            d.line(out, fill=with_alpha(self.col, a), width=self.width, joint="curve")
            (x0, y0), (x1, y1) = out[-2], out[-1]
            if math.dist((x0, y0), (x1, y1)) < 0.5 and len(out) > 2:
                x0, y0 = out[-3]
            ang = math.atan2(y1 - y0, x1 - x0)
            hl, hw = self.width * 2.6, self.width * 1.9
            tip = (x1 + math.cos(ang) * hl * 0.6, y1 + math.sin(ang) * hl * 0.6)
            left = (x1 + math.cos(ang + math.pi / 2) * hw, y1 + math.sin(ang + math.pi / 2) * hw)
            right = (x1 + math.cos(ang - math.pi / 2) * hw, y1 + math.sin(ang - math.pi / 2) * hw)
            d.polygon([tip, left, right], fill=with_alpha(self.col, a), outline=with_alpha(PAL["white"], a))
        if self.label and lt > self.draw_dur * 0.5:
            idx = min(len(sm) - 1, int(len(sm) * self.label_at))
            lx, ly = sm[idx]
            la = a * clamp((lt - self.draw_dur * 0.5) / 0.3)
            _label(d, lx + self.label_dx, ly + self.label_dy, self.label, font("black", 40), self.col, la,
                   self.label_anchor, 7)
        fr.comp(L)


# ================================================================= カード・文字
def _panel(w, h, title, lines, col, title_size=40, body_size=38, align="c"):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 10, w - 1, h - 1], radius=22, fill=(0, 0, 0, 55))
    d.rounded_rectangle([0, 0, w - 7, h - 11], radius=22, fill=(*PAL["white"], 250), outline=col, width=5)
    y = 22
    if title:
        th = 26 + title_size + 14
        d.rounded_rectangle([0, 0, w - 7, th], radius=22, fill=col)
        d.rectangle([0, 36, w - 7, th], fill=col)
        d.text(((w - 7) / 2, th / 2 + 2), title, font=font("black", title_size), fill=PAL["white"], anchor="mm")
        y = th + 22
    fb = font("black", body_size)
    for line in lines:
        lw = markup_w(line, fb)
        x = (w - 7) / 2 - lw / 2 if align == "c" else 30
        draw_markup(d, x, y, line, fb, PAL["ink"], PAL["red"], anchor="lt")
        y += int(body_size * 1.5)
    return im


class Card(El):
    """ポップアップする解説カード（x,y はステージ内座標・中心）"""

    def __init__(self, x, y, w, title, lines, col=PAL["ink"], body_size=38, title_size=40, align="c", **kw):
        super().__init__(**kw)
        h = (26 + title_size + 14 + 22 if title else 22) + int(body_size * 1.5) * len(lines) + 22
        self.x, self.y = x, y
        self.img = _panel(w, h, title, lines, col, title_size, body_size, align)

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        s = 0.6 + 0.4 * ease_back(lt / 0.35)
        im = self.img
        if abs(s - 1) > 0.003:
            im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
        im = _fade_img(im, a)
        fr.canvas.alpha_composite(im, (int(self.x - im.width / 2), int(STAGE_Y + self.y - im.height / 2)))


class Stamp(El):
    """ハンコ風の強調（例：未解読）"""
    sfx = "stamp"

    def __init__(self, x, y, text, col=PAL["red"], size=64, angle=-12, **kw):
        super().__init__(**kw)
        f = font("black", size)
        tw = int(text_w(text, f))
        im = Image.new("RGBA", (tw + 64, size + 64), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([6, 6, im.width - 6, im.height - 6], radius=14, fill=(*PAL["white"], 200),
                            outline=col, width=8)
        d.text((im.width / 2, im.height / 2), text, font=f, fill=col, anchor="mm")
        self.img = im.rotate(angle, expand=True, resample=Image.BICUBIC)
        self.x, self.y = x, y

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        k = ease_out(lt / 0.18)
        s = 2.2 - 1.2 * k
        im = self.img.resize((int(self.img.width * s), int(self.img.height * s)), Image.BILINEAR)
        im = _fade_img(im, a * clamp(lt / 0.1))
        fr.canvas.alpha_composite(im, (int(self.x - im.width / 2), int(STAGE_Y + self.y - im.height / 2)))


class Caption(El):
    """ステージ上部の見出し（図解のタイトル）"""
    sfx = None

    def __init__(self, text, sub=None, x=W / 2, y=62, size=54, col=PAL["ink"], **kw):
        super().__init__(**kw)
        self.text, self.sub, self.x, self.y, self.size, self.col = text, sub, x, y, size, col

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        f = font("black", self.size)
        lw = markup_w(self.text, f)
        draw_markup(d, self.x - lw / 2, STAGE_Y + self.y, self.text, f, self.col, PAL["red"], a, "lm", 7)
        if self.sub:
            _label(d, self.x, STAGE_Y + self.y + self.size * 0.95, self.sub, font("bold", int(self.size * 0.6)),
                   PAL["dim"], a, "mm", 5)
        fr.comp(L)


class TitleHook(El):
    """冒頭のつかみ。1コマ目から見える大見出し（左側のパネル）"""
    sfx = None

    def __init__(self, kicker, lines, sub=None, x=60, y=150, w=860, **kw):
        super().__init__(**kw)
        self.kicker, self.lines, self.sub, self.x, self.y, self.w = kicker, lines, sub, x, y, w

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        x0, y0 = self.x, STAGE_Y + self.y
        h = 150 + 124 * len(self.lines) + (70 if self.sub else 0)
        d.rounded_rectangle([x0 + 8, y0 + 10, x0 + self.w + 8, y0 + h + 10], radius=28, fill=(0, 0, 0, int(60 * a)))
        d.rounded_rectangle([x0, y0, x0 + self.w, y0 + h], radius=28, fill=with_alpha((250, 243, 225), a * 0.96),
                            outline=with_alpha(PAL["ink"], a), width=6)
        fk = font("black", 38)
        kw_ = text_w(self.kicker, fk)
        d.rounded_rectangle([x0 + 40, y0 + 40, x0 + 40 + kw_ + 56, y0 + 104], radius=32,
                            fill=with_alpha(PAL["red"], a))
        d.text((x0 + 68, y0 + 72), self.kicker, font=fk, fill=with_alpha(PAL["white"], a), anchor="lm")
        f = font("black", 96)
        y = y0 + 150
        for line in self.lines:
            draw_markup(d, x0 + 44, y, line, f, PAL["ink"], PAL["red"], a, "lt", 6)
            y += 124
        if self.sub:
            d.text((x0 + 48, y + 10), self.sub, font=font("bold", 38), fill=with_alpha(PAL["dim"], a), anchor="lt")
        fr.comp(L)


class ChapterBanner(El):
    """章の切り替わりで左上に出る控えめな見出し"""
    sfx = "chapter"

    def __init__(self, no, title, **kw):
        super().__init__(**kw)
        self.no, self.title = no, title

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        k = ease_out(lt / 0.45)
        fn, ft = font("black", 34), font("serif", 62)
        w = max(text_w(self.no, fn), text_w(self.title, ft)) + 90
        x0 = -w + (w + 40) * k
        y0 = STAGE_Y + 36
        L = fr.layer()
        d = ImageDraw.Draw(L)
        d.rounded_rectangle([x0 + 6, y0 + 8, x0 + w + 6, y0 + 150], radius=18, fill=(0, 0, 0, int(60 * a)))
        d.rounded_rectangle([x0, y0, x0 + w, y0 + 142], radius=18, fill=with_alpha(PAL["ink"], a * 0.95))
        d.rectangle([x0, y0, x0 + 14, y0 + 142], fill=with_alpha(PAL["gold"], a))
        d.text((x0 + 44, y0 + 36), self.no, font=fn, fill=with_alpha(PAL["gold"], a), anchor="lm")
        d.text((x0 + 44, y0 + 98), self.title, font=ft, fill=with_alpha(PAL["white"], a), anchor="lm")
        fr.comp(L)


# ================================================================= 図解
class Labyrinth(El):
    """クレタの迷宮（古典的な迷路の簡略図）"""
    sfx = None

    def __init__(self, x, y, r, col=PAL["gold"], **kw):
        super().__init__(**kw)
        self.x, self.y, self.r, self.col = x, y, r, col

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        cx, cy = self.x, STAGE_Y + self.y
        d.ellipse([cx - self.r - 30, cy - self.r - 30, cx + self.r + 30, cy + self.r + 30],
                  fill=with_alpha((250, 243, 225), a * 0.9), outline=with_alpha(PAL["ink"], a), width=5)
        rot = lt * 8
        n = 6
        for i in range(n):
            r = self.r * (i + 1) / n * ease_out((lt - i * 0.05) / 0.5)
            if r <= 2:
                continue
            gap = 30 + (i * 67) % 90
            start = (i * 97 + rot * (1 if i % 2 else -1)) % 360
            d.arc([cx - r, cy - r, cx + r, cy + r], start + gap / 2, start + 360 - gap / 2,
                  fill=with_alpha(self.col, a), width=12)
        d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=with_alpha(PAL["red"], a))
        fr.comp(L)


class Polis(El):
    """ポリスの模式図：集住 → アクロポリス＋アゴラ（cx,cy はステージ内の中心、s は拡大率）"""
    sfx = "whoosh"

    def __init__(self, cx=W / 2, cy=430, s=0.8, **kw):
        super().__init__(**kw)
        self.cx, self.cy, self.s = cx, cy, s

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        S = self.s
        cx, cy = self.cx, STAGE_Y + self.cy
        P = lambda x, y: (cx + x * S, cy + y * S)
        k_wall = ease_out((lt - 1.4) / 0.6)
        if k_wall > 0:
            d.ellipse([*P(-560, -380), *P(560, 380)], outline=with_alpha(PAL["coast"], a * k_wall), width=10)
        hill = [P(-330, -40), P(-200, -250), P(-60, -300), P(80, -250), P(190, -40)]
        d.polygon(hill, fill=with_alpha((196, 176, 132), a), outline=with_alpha(PAL["coast"], a), width=5)
        k_t = ease_back((lt - 0.2) / 0.4)
        if k_t > 0:
            q = clamp(k_t, 0, 1.2)
            tx, ty = -65, -300
            T = lambda x, y: P(tx + x * q, ty + y * q)
            d.polygon([T(-110, -20), T(110, -20), T(0, -80)], fill=with_alpha(PAL["white"], a),
                      outline=with_alpha(PAL["ink"], a), width=4)
            for i in range(6):
                x = -90 + i * 36
                d.rectangle([*T(x - 8, -20), *T(x + 8, 50)], fill=with_alpha(PAL["white"], a),
                            outline=with_alpha(PAL["ink"], a), width=3)
            d.rectangle([*T(-110, 50), *T(110, 62)], fill=with_alpha(PAL["ink"], a))
        k_ag = ease_back((lt - 0.5) / 0.4)
        ax, ay = 250, 150
        if k_ag > 0:
            q = clamp(k_ag, 0, 1.2)
            d.rounded_rectangle([*P(ax - 160 * q, ay - 100 * q), *P(ax + 160 * q, ay + 100 * q)], radius=18,
                                fill=with_alpha((250, 238, 205), a), outline=with_alpha(PAL["gold"], a), width=6)
            for i in range(9):
                px = ax - 100 * q + (i % 5) * 50 * q + (i // 5) * 25 * q
                py = ay - 20 * q + (i // 5) * 55 * q + math.sin(lt * 3 + i) * 5
                x, y = P(px, py)
                d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=with_alpha(PAL["ink"], a))
        villages = [(-700, -380), (700, -360), (-720, 330), (700, 330), (0, 470), (-760, 0), (760, -20)]
        homes = [(-380, -60), (330, -150), (-280, 130), (440, -20), (-60, 230), (-420, 60), (280, -260)]
        k_m = ease_io(lt / 1.4)
        for (vx, vy), (hx, hy) in zip(villages, homes):
            x, y = P(vx + (hx - vx) * k_m, vy + (hy - vy) * k_m)
            r = 26 * S
            d.polygon([(x - r, y), (x + r, y), (x, y - r)], fill=with_alpha(PAL["red"], a))
            d.rectangle([x - r * 0.78, y, x + r * 0.78, y + r * 1.08], fill=with_alpha((225, 120, 90), a))
            if k_m < 0.98:
                d.line([(x, y), P(hx, hy)], fill=with_alpha(PAL["red"], a * (1 - k_m) * 0.6), width=4)
        la = a * clamp((lt - 0.6) / 0.3)
        x, y = P(-65, -420)
        _label(d, x, y, "アクロポリス", font("black", 50), PAL["ink"], la, "mm", 7)
        _label(d, x, y + 50, "丘の上の城山・神殿", font("bold", 30), PAL["ink"], la, "mm", 5)
        lb = a * clamp((lt - 0.8) / 0.3)
        x, y = P(ax + 330, ay)
        _label(d, x, y - 26, "アゴラ（広場）", font("black", 50), PAL["gold"], lb, "lm", 7)
        _label(d, x, y + 26, "市場・話し合いの場", font("bold", 30), PAL["ink"], lb, "lm", 5)
        lc = a * clamp((1.0 - k_m) * 3)
        _label(d, cx, cy + 380 * S + 36, "集住（シノイキスモス）", font("black", 46), PAL["red"], lc, "mm", 6)
        fr.comp(L)


class PyramidTier(El):
    """身分ピラミッドの1段（i=0 が頂点）。段ごとに at を変えて順に出す"""

    def __init__(self, i, n, name, desc, col, cx=560, top=140, height=640, base_w=860, **kw):
        super().__init__(**kw)
        self.i, self.n, self.name, self.desc, self.col = i, n, name, desc, col
        self.cx, self.top, self.height, self.base_w = cx, top, height, base_w

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        k = ease_back(lt / 0.35)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        th = self.height / self.n
        wid = lambda y: 120 + (y - self.top) / self.height * (self.base_w - 120)
        y0 = self.top + self.i * th + 5
        y1 = self.top + (self.i + 1) * th - 5
        dy = (1 - clamp(k)) * 50
        cx = self.cx
        pts = [(cx - wid(y0) / 2, STAGE_Y + y0 + dy), (cx + wid(y0) / 2, STAGE_Y + y0 + dy),
               (cx + wid(y1) / 2, STAGE_Y + y1 + dy), (cx - wid(y1) / 2, STAGE_Y + y1 + dy)]
        d.polygon(pts, fill=with_alpha(self.col, a), outline=with_alpha(PAL["white"], a), width=5)
        my = STAGE_Y + (y0 + y1) / 2 + dy
        size = 44 if self.i else 34
        d.text((cx, my - 20), self.name, font=font("black", size), fill=with_alpha(PAL["white"], a), anchor="mm",
               stroke_width=5, stroke_fill=with_alpha(PAL["ink"], a))
        d.text((cx, my + 28), self.desc, font=font("bold", 28 if self.i else 22), fill=with_alpha(PAL["white"], a),
               anchor="mm", stroke_width=4, stroke_fill=with_alpha(PAL["ink"], a))
        fr.comp(L)


class Step(El):
    """改革の階段の1段（i=0 が一番下、右上へのぼる）"""

    def __init__(self, i, year, name, desc, col=PAL["teal"], n=4, name_size=40, w=620, **kw):
        super().__init__(**kw)
        self.i, self.year, self.name, self.desc, self.col, self.n = i, year, name, desc, col, n
        self.name_size, self.w = name_size, w

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        k = ease_back(lt / 0.35)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        w, h = self.w, 150
        span = (W - 120 - w) / max(1, self.n - 1)
        x0 = 60 + self.i * span - (1 - clamp(k)) * 60
        rise = (STAGE_H - 170 - h) / max(1, self.n - 1)
        y1 = STAGE_Y + STAGE_H - 40 - self.i * rise
        y0 = y1 - h
        d.rounded_rectangle([x0 + 6, y0 + 8, x0 + w + 6, y1 + 8], radius=18, fill=(0, 0, 0, int(50 * a)))
        d.rounded_rectangle([x0, y0, x0 + w, y1], radius=18, fill=with_alpha(PAL["white"], a),
                            outline=with_alpha(self.col, a), width=5)
        d.rounded_rectangle([x0, y0, x0 + 150, y1], radius=18, fill=with_alpha(self.col, a))
        d.rectangle([x0 + 130, y0, x0 + 150, y1], fill=with_alpha(self.col, a))
        d.text((x0 + 75, (y0 + y1) / 2), self.year, font=font("black", 36), fill=with_alpha(PAL["white"], a),
               anchor="mm")
        d.text((x0 + 172, y0 + 46), self.name, font=font("black", self.name_size), fill=with_alpha(PAL["ink"], a),
               anchor="lm")
        draw_markup(d, x0 + 174, y0 + 110, self.desc, font("bold", 30), PAL["dim"], PAL["red"], a, "lm")
        fr.comp(L)


class Phalanx(El):
    """重装歩兵の密集隊形（丸盾と槍が横から進む）"""
    sfx = "whoosh"

    def __init__(self, x=960, y=500, s=0.85, label=True, **kw):
        super().__init__(**kw)
        self.x, self.y, self.s, self.label = x, y, s, label

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        S = self.s
        k = ease_out(lt / 1.0)
        base_x = self.x - 520 * S - (1 - k) * 700
        for row in range(3):
            for col in range(8):
                x = base_x + (col * 130 + row * 40) * S
                y = STAGE_Y + self.y + (row * 95 - 60) * S
                if not -80 < x < W + 80:
                    continue
                d.line([(x + 10 * S, y - 150 * S), (x + 20 * S, y + 60 * S)], fill=with_alpha(PAL["coast"], a),
                       width=6)
                d.polygon([(x + 8 * S, y - 170 * S), (x + 18 * S, y - 150 * S), (x + 2 * S, y - 150 * S)],
                          fill=with_alpha(PAL["dim"], a))
                d.ellipse([x - 55 * S, y - 55 * S, x + 55 * S, y + 55 * S], fill=with_alpha(PAL["gold"], a),
                          outline=with_alpha(PAL["ink"], a), width=5)
                d.ellipse([x - 22 * S, y - 22 * S, x + 22 * S, y + 22 * S], fill=with_alpha(PAL["red"], a))
        if self.label:
            la = a * clamp((lt - 0.6) / 0.3)
            _label(d, self.x, STAGE_Y + self.y - 290 * S, "重装歩兵の密集隊形（ファランクス）", font("black", 46),
                   PAL["ink"], la, "mm", 7)
        fr.comp(L)


class Ostracon(El):
    """陶片追放の陶片（実在するテミストクレスの陶片がモチーフ）"""

    def __init__(self, x, y, s=0.8, name="ΘΕΜΙΣΤΟΚΛΗΣ", caption="「テミストクレス」と刻まれた陶片", **kw):
        super().__init__(**kw)
        self.x, self.y, self.s, self.name, self.caption = x, y, s, name, caption

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        s = self.s * (0.6 + 0.4 * ease_back(lt / 0.35))
        L = fr.layer()
        d = ImageDraw.Draw(L)
        cx, cy = self.x, STAGE_Y + self.y
        shape = [(-260, -120), (-120, -175), (90, -150), (250, -90), (275, 40), (180, 150), (-40, 170),
                 (-210, 120), (-285, 10)]
        pts = [(cx + px * s, cy + py * s) for px, py in shape]
        d.polygon([(px + 10, py + 12) for px, py in pts], fill=(0, 0, 0, int(60 * a)))
        d.polygon(pts, fill=with_alpha((196, 110, 70), a), outline=with_alpha((120, 60, 35), a), width=5)
        n = int(len(self.name) * clamp((lt - 0.3) / 1.0))
        d.text((cx, cy), self.name[:n], font=font("bold", max(8, int(50 * s))), fill=with_alpha((40, 25, 20), a),
               anchor="mm")
        if self.caption:
            _label(d, cx, cy + 200 * self.s, self.caption, font("bold", 30), PAL["ink"], a * clamp((lt - 1.0) / 0.3),
                   "mm", 5)
        fr.comp(L)


class Trireme(El):
    """三段櫂船（3段のオールが動く）"""
    sfx = "whoosh"

    def __init__(self, x=960, y=470, s=0.95, label=True, **kw):
        super().__init__(**kw)
        self.x, self.y, self.s, self.label = x, y, s, label

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        S = self.s
        cx = self.x + (1 - ease_out(lt / 1.2)) * -1100
        cy = STAGE_Y + self.y + math.sin(lt * 2) * 6
        for i in range(4):
            yy = STAGE_Y + self.y + (90 + i * 45) * S
            pts = [(x, yy + math.sin(x / 40 + lt * 3 + i) * 8) for x in range(0, W + 20, 20)]
            d.line(pts, fill=with_alpha((120, 170, 180), a * (0.8 - i * 0.15)), width=5)
        for tier in range(3):
            for i in range(11):
                ox = cx + (-330 + i * 62 + tier * 14) * S
                oy = cy + (10 + tier * 18) * S
                ang = math.radians(110 + 22 * math.sin(lt * 5 + i * 0.2 + tier))
                ln = (120 + tier * 20) * S
                d.line([(ox, oy), (ox + math.cos(ang) * ln * 0.45, oy + math.sin(ang) * ln)],
                       fill=with_alpha((110, 80, 50), a), width=5)
        P = lambda x, y: (cx + x * S, cy + y * S)
        hull = [P(-420, -40), P(360, -40), P(470, 20), P(360, 40), P(-360, 40), P(-440, -90)]
        d.polygon(hull, fill=with_alpha((120, 70, 45), a), outline=with_alpha(PAL["ink"], a), width=5)
        d.rectangle([*P(-400, -20), *P(380, -4)], fill=with_alpha(PAL["gold"], a))
        d.ellipse([*P(330, -34), *P(360, -14)], fill=with_alpha(PAL["white"], a), outline=with_alpha(PAL["ink"], a),
                  width=3)
        d.line([P(-20, -40), P(-20, -300)], fill=with_alpha((110, 80, 50), a), width=9)
        d.polygon([P(-170, -280), P(130, -280), P(110, -110), P(-150, -110)],
                  fill=with_alpha((245, 235, 210), a), outline=with_alpha(PAL["coast"], a), width=4)
        d.ellipse([*P(-60, -235), *P(20, -155)], outline=with_alpha(PAL["red"], a), width=7)
        if self.label:
            la = a * clamp((lt - 0.6) / 0.3)
            _label(d, W / 2, STAGE_Y + 60, "三段櫂船（さんだんかいせん）", font("black", 48), PAL["ink"], la, "mm", 7)
            _label(d, W / 2, STAGE_Y + 118, "こぎ手は財産のない市民＝無産市民", font("bold", 36), PAL["red"], la, "mm", 5)
        fr.comp(L)


ASSEMBLY_ROWS = [("成年男性市民", PAL["teal"]), ("女性", PAL["red"]), ("奴隷", PAL["dim"]), ("在留外人", PAL["gold"])]


def _person(d, x, y, col, a, s=1.0):
    d.ellipse([x - 20 * s, y - 62 * s, x + 20 * s, y - 22 * s], fill=with_alpha(col, a))
    d.rounded_rectangle([x - 30 * s, y - 16 * s, x + 30 * s, y + 50 * s], radius=int(18 * s), fill=with_alpha(col, a))


class Assembly(El):
    """民会に参加できる人・できない人"""

    def __init__(self, x0=560, **kw):
        super().__init__(**kw)
        self.x0 = x0

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        _label(d, self.x0 + 480, STAGE_Y + 70, "民会に参加できるのは？", font("black", 50), PAL["ink"], a, "mm", 7)
        for r, (name, col) in enumerate(ASSEMBLY_ROWS):
            k = ease_back((lt - r * 0.12) / 0.35)
            if k <= 1e-3:
                continue
            y = STAGE_Y + 210 + r * 160
            ra = a * clamp(k)
            _label(d, self.x0, y, name, font("black", 40), col, ra, "lm", 6)
            for i in range(6):
                _person(d, self.x0 + 330 + i * 90, y + 4, col, ra, clamp(k, 0, 1.1) * 0.9)
        fr.comp(L)


class AssemblyCross(El):
    """女性・奴隷・在留外人に✕（参政権なし）"""
    sfx = "stamp"

    def __init__(self, x0=560, **kw):
        super().__init__(**kw)
        self.x0 = x0

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        k = ease_out(lt / 0.25)
        for r in (1, 2, 3):
            y = STAGE_Y + 210 + r * 160
            d.rounded_rectangle([self.x0 - 30, y - 72, self.x0 + 1000, y + 62], radius=18,
                                fill=(236, 226, 200, int(150 * a * k)))
            s = 44 * (2 - k)
            cx = self.x0 + 930
            d.line([(cx - s, y - s), (cx + s, y + s)], fill=with_alpha(PAL["red"], a * k), width=14)
            d.line([(cx - s, y + s), (cx + s, y - s)], fill=with_alpha(PAL["red"], a * k), width=14)
        y = STAGE_Y + 210
        d.ellipse([self.x0 + 885, y - 45, self.x0 + 975, y + 45], outline=with_alpha(PAL["teal"], a * k), width=12)
        fr.comp(L)


class Temple(El):
    """パルテノン神殿（簡略図）"""

    def __init__(self, x, y, s=1.0, **kw):
        super().__init__(**kw)
        self.x, self.y, self.s = x, y, s

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        k = ease_back(lt / 0.4)
        s = self.s * clamp(k, 0, 1.15)
        if s <= 0.02:
            return
        L = fr.layer()
        d = ImageDraw.Draw(L)
        cx, cy = self.x, STAGE_Y + self.y
        ink, marble = with_alpha(PAL["ink"], a), with_alpha(PAL["white"], a)
        d.polygon([(cx - 250 * s, cy - 130 * s), (cx + 250 * s, cy - 130 * s), (cx, cy - 230 * s)],
                  fill=marble, outline=ink, width=6)
        d.rectangle([cx - 260 * s, cy - 130 * s, cx + 260 * s, cy - 100 * s], fill=marble, outline=ink, width=5)
        for i in range(8):
            x = cx - 220 * s + i * 440 / 7 * s
            d.rectangle([x - 17 * s, cy - 100 * s, x + 17 * s, cy + 90 * s], fill=marble, outline=ink, width=4)
        for j in range(3):
            w = 270 + j * 20
            d.rectangle([cx - w * s, cy + (90 + j * 20) * s, cx + w * s, cy + (110 + j * 20) * s],
                        fill=marble, outline=ink, width=4)
        fr.comp(L)


class Coins(El):
    """同盟の資金（コインが流れこむ）"""
    sfx = None

    def __init__(self, x0, y0, x1, y1, n=10, **kw):
        super().__init__(**kw)
        self.p0, self.p1, self.n = (x0, y0), (x1, y1), n

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        for i in range(self.n):
            ph = (lt * 0.7 + i / self.n) % 1.0
            x = lerp_(self.p0[0], self.p1[0], ph)
            y = lerp_(self.p0[1], self.p1[1], ph) - math.sin(ph * math.pi) * 120 + STAGE_Y
            ca = a * clamp(ph * 5) * clamp((1 - ph) * 5)
            d.ellipse([x - 24, y - 24, x + 24, y + 24], fill=with_alpha(PAL["gold"], ca),
                      outline=with_alpha((140, 100, 10), ca), width=4)
            d.text((x, y), "¤", font=font("black", 30), fill=with_alpha((140, 100, 10), ca), anchor="mm")
        fr.comp(L)


def lerp_(a, b, t):
    return a + (b - a) * t


class Table(El):
    """比較表（行が順番に出る）。heads=[列見出し...]、rows=[(行名, 値1, 値2, ...)]"""

    def __init__(self, heads, rows, row_dt=0.6, title=None, x0=120, x1=W - 120, top=40, row_h=112, name_w=240,
                 cols=None, **kw):
        super().__init__(**kw)
        self.heads, self.rows, self.row_dt, self.title = heads, rows, row_dt, title
        self.x0, self.x1, self.top, self.row_h, self.name_w = x0, x1, top, row_h, name_w
        self.cols = cols or [PAL["teal"], PAL["red"], PAL["gold"]]

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        x0, x1 = self.x0, self.x1
        y = STAGE_Y + self.top
        if self.title:
            d.rounded_rectangle([x0, y, x1, y + 76], radius=16, fill=with_alpha(PAL["ink"], a))
            d.text(((x0 + x1) / 2, y + 38), self.title, font=font("black", 44), fill=with_alpha(PAL["gold"], a),
                   anchor="mm")
            y += 90
        nc = len(self.heads)
        cw = (x1 - x0 - self.name_w) / nc
        cx = lambda i: (x0 + self.name_w + i * cw, x0 + self.name_w + (i + 1) * cw)
        for i, h in enumerate(self.heads):
            xa, xb = cx(i)
            d.rounded_rectangle([xa + 6, y, xb - 6, y + 70], radius=14, fill=with_alpha(self.cols[i], a))
            d.text(((xa + xb) / 2, y + 35), h, font=font("black", 42), fill=with_alpha(PAL["white"], a), anchor="mm")
        y += 84
        rh = self.row_h
        for r, row in enumerate(self.rows):
            k = ease_out((lt - 0.2 - r * self.row_dt) / 0.3)
            if k <= 1e-3:
                break
            ra = a * k
            yy = y + (1 - k) * 20
            d.rounded_rectangle([x0, yy, x1, yy + rh - 12], radius=14, fill=with_alpha(PAL["white"], ra * 0.95))
            d.text((x0 + self.name_w / 2, yy + (rh - 12) / 2), row[0], font=font("black", 36),
                   fill=with_alpha(PAL["dim"], ra), anchor="mm")
            for i, v in enumerate(row[1:]):
                xa, xb = cx(i)
                lines = v.split("/")
                fv = font("black", 38 if len(lines) == 1 else 32)
                ty = yy + (rh - 12) / 2 - (len(lines) - 1) * 21
                for line in lines:
                    lw = markup_w(line, fv)
                    draw_markup(d, (xa + xb) / 2 - lw / 2, ty, line, fv, PAL["ink"], PAL["red"], ra, "lm")
                    ty += 42
            y += rh
        fr.comp(L)


class Summary(El):
    """最後の総まとめ：年表の上に出来事が順番に並ぶ"""
    sfx = None
    ROWS = (110, 220, 330)

    def __init__(self, items, rng=(-2000, -250), breaks=None, title="総まとめ",
                 ticks=(-2000, -1200, -800, -500, -338, -272), **kw):
        """items=[(年, ラベル, 色, 上下(0=上/1=下), 段(0=軸に近い), 出るタイミング 秒 or 'c1+0.5', 横ずれpx)]"""
        super().__init__(**kw)
        self.items, self.rng, self.breaks, self.title, self.ticks = items, rng, breaks, title, ticks

    def resolve(self, when):
        self.items = [(*it[:5], when(it[5]), *it[6:]) for it in self.items]

    def draw(self, fr, lt):
        from .core import tl_scale
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        X = tl_scale(self.breaks or [(self.rng[0], 0), (self.rng[1], 1)], 120, W - 120)
        ay = STAGE_Y + 470
        d.line([(90, ay), (W - 70, ay)], fill=with_alpha(PAL["ink"], a), width=8)
        d.polygon([(W - 60, ay), (W - 90, ay - 18), (W - 90, ay + 18)], fill=with_alpha(PAL["ink"], a))
        _label(d, W / 2, STAGE_Y + 50, self.title, font("black", 50), PAL["ink"], a, "mm", 7)
        f = font("black", 32)
        for it in self.items:
            yr, text, col, lane, row, at = it[:6]
            dx = it[6] if len(it) > 6 else 0
            k = ease_back((lt - at) / 0.35)
            if k <= 1e-3:
                continue
            ka = a * clamp(k)
            x = X(yr)
            ty = ay + (self.ROWS[row] if lane else -self.ROWS[row])
            lines = text.split("/")
            bw = max(text_w(s, f) for s in lines) + 36
            bh = 44 * len(lines) + 16
            by = ty - bh / 2 + (1 - clamp(k)) * (20 if lane else -20)
            bx = min(max(x + dx - bw / 2, 20), W - 20 - bw)
            d.line([(x, ay), (x, ty)], fill=with_alpha(col, ka), width=4)
            d.ellipse([x - 12, ay - 12, x + 12, ay + 12], fill=with_alpha(col, ka), outline=with_alpha(PAL["white"], ka),
                      width=4)
            d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=14, fill=with_alpha(PAL["white"], ka),
                                outline=with_alpha(col, ka), width=4)
            for i, s in enumerate(lines):
                d.text((bx + bw / 2, by + 30 + i * 44), s, font=f, fill=with_alpha(PAL["ink"], ka), anchor="mm")
        for yr in self.ticks:
            _label(d, X(yr), ay + 34, f"前{-yr}", font("bold", 24), PAL["dim"], a, "mm", 5)
        fr.comp(L)


# ================================================================= 実写素材
class Photo(El):
    """実写素材（ゆっくりズーム＆パン）。layer='bg' なので実写寄りの見た目では映画風の質感がかかる

    path, credit は engine.assets.commons() / met() の戻り値をそのまま渡す
    mode='cover'：ステージ全体を埋める（風景・絵画） / mode='fit'：作品全体を見せ、余白はぼかした同じ画像
    focus=(x, y)：寄っていく先（0〜1、画像内の位置）
    work：説明欄のクレジット一覧に出す作品名（例：「ターナー『吹雪：アルプスを越えるハンニバル』」）
    side：mode='fit' のとき作品を寄せる位置（'c' 中央 / 'l' 左 / 'r' 右）。空いた側に図解を置ける
    """
    sfx = None
    layer = "bg"

    def __init__(self, path, credit, mode="cover", zoom=(1.0, 1.12), focus=(0.5, 0.5), caption=None, work=None,
                 side="c", **kw):
        super().__init__(**kw)
        self.src = Image.open(path).convert("RGB")
        self.credit, self.mode, self.zoom, self.focus, self.caption = credit, mode, zoom, focus, caption
        self.side = side
        self.credit_full = f"{work}：{credit.replace('画像：', '')}" if work else None
        self._bg = None

    def _cover(self, im, z, fx, fy, w, h):
        iw, ih = im.size
        s = max(w / iw, h / ih) * z
        cw, ch = w / s, h / s
        cx = min(max(fx * iw, cw / 2), iw - cw / 2)
        cy = min(max(fy * ih, ch / 2), ih - ch / 2)
        return im.resize((w, h), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        dur = max(0.1, self.t1 - self.t0)
        k = ease_io(clamp(lt / dur))
        z = self.zoom[0] + (self.zoom[1] - self.zoom[0]) * k
        fx = 0.5 + (self.focus[0] - 0.5) * k
        fy = 0.5 + (self.focus[1] - 0.5) * k
        if self.mode == "cover":
            im = self._cover(self.src, z, fx, fy, W, STAGE_H)
        else:
            if self._bg is None:
                bg = self._cover(self.src, 1.0, 0.5, 0.5, W // 4, STAGE_H // 4).filter(ImageFilter.GaussianBlur(6))
                self._bg = bg.resize((W, STAGE_H), Image.BILINEAR).point(lambda v: int(v * 0.4))
            im = self._bg.copy()
            iw, ih = self.src.size
            s = min((W * (0.92 if self.side == "c" else 0.5) - 40) / iw, (STAGE_H - 70) / ih) * z
            fg = self.src.resize((int(iw * s), int(ih * s)), Image.BILINEAR)
            cx = {"c": W / 2, "l": W * 0.27, "r": W * 0.73}[self.side]
            im.paste(fg, (int(cx - fg.width / 2), (STAGE_H - fg.height) // 2))
        im = im.convert("RGBA")
        if a < 0.999:
            im.putalpha(int(255 * a))
        fr.canvas.alpha_composite(im, (0, STAGE_Y))
        L = fr.layer()
        d = ImageDraw.Draw(L)
        d.text((W - 22, STAGE_Y + STAGE_H - 14), self.credit, font=font("medium", 20),
               fill=(255, 255, 255, int(200 * a)), anchor="rb", stroke_width=2, stroke_fill=(0, 0, 0, int(160 * a)))
        if self.caption:
            ca = a * clamp((lt - 0.3) / 0.4)
            f = font("serif", 40)
            tw = text_w(self.caption, f)
            y0 = STAGE_Y + STAGE_H - 96
            d.rectangle([36, y0, 36 + tw + 44, y0 + 62], fill=(10, 12, 20, int(150 * ca)))
            d.rectangle([36, y0, 43, y0 + 62], fill=with_alpha(PAL["gold"], ca))
            d.text((62, y0 + 31), self.caption, font=f, fill=(255, 250, 235, int(255 * ca)), anchor="lm")
        fr.comp(L)


class FlowArrow(El):
    """図解用のまっすぐな矢印（ステージ内座標）"""
    sfx = None

    def __init__(self, x0, y0, x1, y1, col=PAL["gold"], width=14, label=None, draw_dur=0.5, **kw):
        super().__init__(**kw)
        self.p0, self.p1, self.col, self.width, self.label, self.draw_dur = (x0, y0), (x1, y1), col, width, label, draw_dur

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        k = ease_out(lt / self.draw_dur)
        x0, y0 = self.p0[0], STAGE_Y + self.p0[1]
        x1 = x0 + (self.p1[0] - x0) * k
        y1 = y0 + (STAGE_Y + self.p1[1] - y0) * k
        L = fr.layer()
        d = ImageDraw.Draw(L)
        d.line([(x0, y0), (x1, y1)], fill=with_alpha(PAL["white"], a), width=self.width + 8)
        d.line([(x0, y0), (x1, y1)], fill=with_alpha(self.col, a), width=self.width)
        ang = math.atan2(y1 - y0, x1 - x0)
        hl, hw = self.width * 2.4, self.width * 1.8
        tip = (x1 + math.cos(ang) * hl * 0.6, y1 + math.sin(ang) * hl * 0.6)
        d.polygon([tip, (x1 + math.cos(ang + math.pi / 2) * hw, y1 + math.sin(ang + math.pi / 2) * hw),
                   (x1 + math.cos(ang - math.pi / 2) * hw, y1 + math.sin(ang - math.pi / 2) * hw)],
                  fill=with_alpha(self.col, a), outline=with_alpha(PAL["white"], a))
        if self.label and k > 0.5:
            _label(d, (x0 + x1) / 2, (y0 + y1) / 2 - 40, self.label, font("black", 36), self.col,
                   a * clamp((k - 0.5) * 2), "mm", 6)
        fr.comp(L)
