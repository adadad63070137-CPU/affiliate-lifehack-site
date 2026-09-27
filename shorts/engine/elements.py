"""図解・地図アニメ用の演出要素"""
import math

from PIL import Image, ImageDraw

from .core import (El, PAL, STAGE_H, STAGE_Y, W, clamp, ease_back, ease_io, ease_out, font,
                   parse_markup, text_w, with_alpha)


def _label(d, x, y, txt, f, col=PAL["ink"], a=1.0, anchor="lm", stroke=6):
    d.text((x, y), txt, font=f, fill=with_alpha(col, a), anchor=anchor,
           stroke_width=stroke, stroke_fill=with_alpha(PAL["white"], a))


class MapLabel(El):
    """海・地域名などの地図上の文字"""
    sfx = None

    def __init__(self, lon, lat, text, size=44, col=PAL["teal"], serif=True, **kw):
        super().__init__(**kw)
        self.lon, self.lat, self.text, self.size, self.col, self.serif = lon, lat, text, size, col, serif

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        x, y = fr.xy(self.lon, self.lat)
        L = fr.layer()
        _label(ImageDraw.Draw(L), x, y, self.text, font("serif" if self.serif else "black", self.size),
               self.col, a, anchor="mm", stroke=5)
        fr.comp(L)


class Marker(El):
    """地点マーカー（波紋＋ラベル）"""

    def __init__(self, lon, lat, text, col=PAL["red"], side="r", sub=None, **kw):
        super().__init__(**kw)
        self.lon, self.lat, self.text, self.col, self.side, self.sub = lon, lat, text, col, side, sub

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        x, y = fr.xy(self.lon, self.lat)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        for k in range(2):
            ph = ((lt * 0.8 + k * 0.5) % 1.0)
            r = 14 + ph * 46
            d.ellipse([x - r, y - r, x + r, y + r], outline=with_alpha(self.col, a * (1 - ph) * 0.8), width=5)
        s = ease_back(lt / 0.3)
        r = 15 * s
        d.ellipse([x - r, y - r, x + r, y + r], fill=with_alpha(self.col, a),
                  outline=with_alpha(PAL["white"], a), width=5)
        f = font("black", 50)
        ta = a * clamp((lt - 0.1) / 0.25)
        dx = (1 - ease_out((lt - 0.1) / 0.3)) * 20
        if self.side == "r":
            _label(d, x + 30 + dx, y, self.text, f, self.col, ta, "lm", 7)
            if self.sub:
                _label(d, x + 32 + dx, y + 48, self.sub, font("bold", 32), PAL["ink"], ta, "lm", 5)
        elif self.side == "l":
            _label(d, x - 30 - dx, y, self.text, f, self.col, ta, "rm", 7)
            if self.sub:
                _label(d, x - 32 - dx, y + 48, self.sub, font("bold", 32), PAL["ink"], ta, "rm", 5)
        elif self.side == "t":
            _label(d, x, y - 34 - dx, self.text, f, self.col, ta, "mb", 7)
            if self.sub:
                _label(d, x, y - 94 - dx, self.sub, font("bold", 32), PAL["ink"], ta, "mb", 5)
        else:
            _label(d, x, y + 34 + dx, self.text, f, self.col, ta, "mt", 7)
            if self.sub:
                _label(d, x, y + 94 + dx, self.sub, font("bold", 32), PAL["ink"], ta, "mt", 5)
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
        z = fr.cam[2]
        rx, ry = self.rx * z * ease_out(lt / 0.5), self.ry * z * ease_out(lt / 0.5)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=with_alpha(self.col, 0.18 * a),
                  outline=with_alpha(self.col, 0.9 * a), width=6)
        fr.comp(L)


class Arrow(El):
    """経路が伸びていく矢印（民族移動など）"""
    sfx = "whoosh"

    def __init__(self, path, col=PAL["red"], width=18, draw_dur=1.2, label=None, label_at=0.5, **kw):
        super().__init__(**kw)
        self.path, self.col, self.width, self.draw_dur = path, col, width, draw_dur
        self.label, self.label_at = label, label_at

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        pts = [fr.xy(lo, la) for lo, la in self.path]
        # 曲線化（Catmull-Rom）
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
            d.line(out, fill=with_alpha(PAL["white"], a), width=self.width + 10, joint="curve")
            d.line(out, fill=with_alpha(self.col, a), width=self.width, joint="curve")
            (x0, y0), (x1, y1) = out[-2], out[-1]
            ang = math.atan2(y1 - y0, x1 - x0)
            hl, hw = self.width * 2.6, self.width * 1.9
            tip = (x1 + math.cos(ang) * hl * 0.6, y1 + math.sin(ang) * hl * 0.6)
            left = (x1 + math.cos(ang + math.pi / 2) * hw, y1 + math.sin(ang + math.pi / 2) * hw)
            right = (x1 + math.cos(ang - math.pi / 2) * hw, y1 + math.sin(ang - math.pi / 2) * hw)
            d.polygon([tip, left, right], fill=with_alpha(self.col, a), outline=with_alpha(PAL["white"], a))
        if self.label and lt > self.draw_dur * 0.5:
            idx = int(len(sm) * self.label_at)
            lx, ly = sm[idx]
            la = a * clamp((lt - self.draw_dur * 0.5) / 0.3)
            _label(d, lx + 36, ly, self.label, font("black", 46), self.col, la, "lm", 7)
        fr.comp(L)


def _panel(w, h, title, lines, col, title_size=46, body_size=42):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6, 10, w - 1, h - 1], radius=26, fill=(0, 0, 0, 60))
    d.rounded_rectangle([0, 0, w - 7, h - 11], radius=26, fill=(*PAL["white"], 250), outline=col, width=6)
    y = 20
    if title:
        d.rounded_rectangle([0, 0, w - 7, 30 + title_size + 16], radius=26, fill=col)
        d.rectangle([0, 40, w - 7, 30 + title_size + 16], fill=col)
        d.text(((w - 7) / 2, 22), title, font=font("black", title_size), fill=PAL["white"], anchor="mt")
        y = 30 + title_size + 36
    fb = font("black", body_size)
    for line in lines:
        segs = parse_markup(line)
        lw = sum(text_w(s, fb) for s, _ in segs)
        x = (w - 7) / 2 - lw / 2
        for s, em in segs:
            d.text((x, y), s, font=fb, fill=PAL["red"] if em else PAL["ink"])
            x += text_w(s, fb)
        y += int(body_size * 1.45)
    return im


class Card(El):
    """ポップアップする解説カード（x,y はステージ内座標・中心）"""

    def __init__(self, x, y, w, title, lines, col=PAL["ink"], body_size=42, **kw):
        super().__init__(**kw)
        h = (30 + 46 + 36 if title else 20) + int(body_size * 1.45) * len(lines) + 24
        self.x, self.y = x, y
        self.img = _panel(w, h, title, lines, col, body_size=body_size)

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        s = 0.6 + 0.4 * ease_back(lt / 0.35)
        im = self.img
        if abs(s - 1) > 0.003:
            im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
        if a < 0.999:
            im = im.copy()
            im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
        fr.canvas.alpha_composite(im, (int(self.x - im.width / 2), int(STAGE_Y + self.y - im.height / 2)))


class Stamp(El):
    """ハンコ風の強調（例：未解読）"""
    sfx = "stamp"

    def __init__(self, x, y, text, col=PAL["red"], size=70, angle=-12, **kw):
        super().__init__(**kw)
        f = font("black", size)
        tw = int(text_w(text, f))
        im = Image.new("RGBA", (tw + 70, size + 70), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([6, 6, im.width - 6, im.height - 6], radius=14, outline=col, width=8)
        d.text((im.width / 2, im.height / 2), text, font=f, fill=col, anchor="mm")
        self.img = im.rotate(angle, expand=True, resample=Image.BICUBIC)
        self.x, self.y = x, y

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        k = ease_out(lt / 0.18)
        s = 2.2 - 1.2 * k
        im = self.img.resize((int(self.img.width * s), int(self.img.height * s)), Image.BILINEAR)
        im.putalpha(im.getchannel("A").point(lambda v: int(v * a * clamp(lt / 0.1))))
        fr.canvas.alpha_composite(im, (int(self.x - im.width / 2), int(STAGE_Y + self.y - im.height / 2)))


class Hook(El):
    """冒頭のつかみ（大見出し）"""
    sfx = None

    def __init__(self, kicker, lines, sub=None, col=PAL["red"], **kw):
        super().__init__(**kw)
        self.kicker, self.lines, self.sub, self.col = kicker, lines, sub, col

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        d.rectangle([0, STAGE_Y, W, STAGE_Y + STAGE_H], fill=(20, 22, 32, int(120 * a)))
        fk = font("black", 44)
        kw_ = text_w(self.kicker, fk)
        cy = STAGE_Y + 250
        d.rounded_rectangle([W / 2 - kw_ / 2 - 30, cy - 38, W / 2 + kw_ / 2 + 30, cy + 38], radius=38,
                            fill=with_alpha(self.col, a))
        d.text((W / 2, cy), self.kicker, font=fk, fill=with_alpha(PAL["white"], a), anchor="mm")
        f = font("black", 112)
        y = cy + 90
        for i, line in enumerate(self.lines):
            k = ease_back((lt - 0.08 * i) / 0.35)
            segs = parse_markup(line)
            lw = sum(text_w(s, f) for s, _ in segs)
            x = W / 2 - lw / 2
            yy = y + (1 - clamp(k)) * 40
            for s, em in segs:
                d.text((x, yy), s, font=f, fill=with_alpha(PAL["gold"] if em else PAL["white"], a * clamp(k * 1.5)),
                       stroke_width=10, stroke_fill=with_alpha(PAL["ink"], a * clamp(k * 1.5)))
                x += text_w(s, f)
            y += 140
        if self.sub:
            d.text((W / 2, y + 30), self.sub, font=font("black", 50),
                   fill=with_alpha(PAL["white"], a * clamp((lt - 0.4) / 0.3)), anchor="mt",
                   stroke_width=6, stroke_fill=with_alpha(PAL["ink"], a))
        fr.comp(L)


class Labyrinth(El):
    """クレタの迷宮（古典的な7重迷路の簡略図）"""

    def __init__(self, x, y, r, col=PAL["gold"], **kw):
        super().__init__(**kw)
        self.x, self.y, self.r, self.col = x, y, r, col

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        cx, cy = self.x, STAGE_Y + self.y
        rot = lt * 8
        n = 6
        for i in range(n):
            r = self.r * (i + 1) / n * ease_out((lt - i * 0.05) / 0.5)
            if r <= 2:
                continue
            gap = 30 + (i * 67) % 90
            start = (i * 97 + rot * (1 if i % 2 else -1)) % 360
            d.arc([cx - r, cy - r, cx + r, cy + r], start + gap / 2, start + 360 - gap / 2,
                  fill=with_alpha(self.col, a), width=14)
        d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=with_alpha(PAL["red"], a))
        fr.comp(L)


class Polis(El):
    """ポリスの模式図：集住 → アクロポリス＋アゴラ"""
    sfx = "whoosh"

    def __init__(self, labels=True, **kw):
        super().__init__(**kw)
        self.labels = labels

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        oy = STAGE_Y
        cx, cy = W / 2, oy + 520
        # 城壁
        k_wall = ease_out((lt - 1.4) / 0.6)
        if k_wall > 0:
            d.ellipse([cx - 440, cy - 330, cx + 440, cy + 330], outline=with_alpha(PAL["coast"], a * k_wall),
                      width=12)
        # 丘（アクロポリス）
        hill = [(cx - 330, cy - 40), (cx - 200, cy - 250), (cx - 60, cy - 300), (cx + 80, cy - 250),
                (cx + 190, cy - 40)]
        d.polygon(hill, fill=with_alpha((196, 176, 132), a), outline=with_alpha(PAL["coast"], a), width=6)
        # 神殿
        k_t = ease_back((lt - 0.2) / 0.4)
        if k_t > 0:
            tx, ty, s = cx - 65, cy - 300, clamp(k_t, 0, 1.2)
            d.polygon([(tx - 110 * s, ty - 20 * s), (tx + 110 * s, ty - 20 * s), (tx, ty - 80 * s)],
                      fill=with_alpha(PAL["white"], a), outline=with_alpha(PAL["ink"], a), width=5)
            for i in range(6):
                x = tx - 90 * s + i * 36 * s
                d.rectangle([x - 8 * s, ty - 20 * s, x + 8 * s, ty + 50 * s], fill=with_alpha(PAL["white"], a),
                            outline=with_alpha(PAL["ink"], a), width=3)
            d.rectangle([tx - 110 * s, ty + 50 * s, tx + 110 * s, ty + 62 * s], fill=with_alpha(PAL["ink"], a))
        # アゴラ（広場）
        k_ag = ease_back((lt - 0.5) / 0.4)
        ax, ay = cx + 170, cy + 150
        if k_ag > 0:
            s = clamp(k_ag, 0, 1.2)
            d.rounded_rectangle([ax - 140 * s, ay - 90 * s, ax + 140 * s, ay + 90 * s], radius=20,
                                fill=with_alpha((250, 238, 205), a), outline=with_alpha(PAL["gold"], a), width=7)
            for i in range(9):
                px = ax - 90 * s + (i % 5) * 45 * s + (i // 5) * 22 * s
                py = ay - 20 * s + (i // 5) * 50 * s + math.sin(lt * 3 + i) * 5
                d.ellipse([px - 11, py - 11, px + 11, py + 11], fill=with_alpha(PAL["ink"], a))
        # 集住：周りの村 → 中心へ
        villages = [(-470, -380), (460, -360), (-490, 330), (480, 330), (0, 420), (-500, 0), (500, -20)]
        homes = [(-360, -60), (300, -150), (-260, 130), (360, -40), (-80, 220), (-390, 70), (250, -250)]
        k_m = ease_io(lt / 1.4)
        for i, ((vx, vy), (tx, ty)) in enumerate(zip(villages, homes)):
            x = cx + vx + (tx - vx) * k_m
            y = cy + vy + (ty - vy) * k_m
            d.polygon([(x - 26, y), (x + 26, y), (x, y - 26)], fill=with_alpha(PAL["red"], a))
            d.rectangle([x - 20, y, x + 20, y + 28], fill=with_alpha((225, 120, 90), a))
            if k_m < 0.98:
                d.line([(x, y), (cx + tx, cy + ty)], fill=with_alpha(PAL["red"], a * (1 - k_m) * 0.6), width=4)
        if self.labels:
            la = a * clamp((lt - 0.6) / 0.3)
            _label(d, cx - 65, oy + 58, "アクロポリス", font("black", 54), PAL["ink"], la, "mm", 7)
            _label(d, cx - 65, oy + 108, "（丘の上の城山・神殿）", font("bold", 34), PAL["ink"], la, "mm", 5)
            lb = a * clamp((lt - 0.8) / 0.3)
            _label(d, ax + 20, ay - 150, "アゴラ（広場）", font("black", 52), PAL["gold"], lb, "mm", 7)
            _label(d, ax + 20, ay - 104, "市場・議論の場", font("bold", 34), PAL["ink"], lb, "mm", 5)
            lc = a * clamp((1.0 - k_m) * 3)
            _label(d, cx, oy + 930, "集住（シノイキスモス）", font("black", 46), PAL["red"], lc, "mm", 6)
        fr.comp(L)


class Table(El):
    """比較表（行が順番に出る）"""
    sfx = "pop"

    def __init__(self, heads, rows, row_dt=0.55, title="まとめ", **kw):
        super().__init__(**kw)
        self.heads, self.rows, self.row_dt, self.title = heads, rows, row_dt, title

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        x0, x1 = 40, W - 40
        c1, c2 = x0 + 190, x0 + 190 + (x1 - x0 - 190) / 2
        y = STAGE_Y + 40
        d.rounded_rectangle([x0, y, x1, y + 80], radius=18, fill=with_alpha(PAL["ink"], a))
        d.text((W / 2, y + 40), self.title, font=font("black", 50), fill=with_alpha(PAL["gold"], a), anchor="mm")
        y += 96
        fh = font("black", 44)
        cols = [PAL["teal"], PAL["red"]]
        for i, h in enumerate(self.heads):
            xa, xb = (c1, c2) if i == 0 else (c2, x1)
            d.rounded_rectangle([xa + 6, y, xb - 6, y + 76], radius=14, fill=with_alpha(cols[i], a))
            d.text(((xa + xb) / 2, y + 38), h, font=fh, fill=with_alpha(PAL["white"], a), anchor="mm")
        y += 90
        rh = 128
        for r, (name, v1, v2) in enumerate(self.rows):
            k = ease_out((lt - 0.2 - r * self.row_dt) / 0.3)
            if k <= 0:
                break
            ra = a * k
            yy = y + (1 - k) * 20
            d.rounded_rectangle([x0, yy, x1, yy + rh - 12], radius=14, fill=with_alpha(PAL["white"], ra * 0.95))
            d.text((x0 + 95, yy + (rh - 12) / 2), name, font=font("black", 40), fill=with_alpha(PAL["dim"], ra),
                   anchor="mm")
            for v, (xa, xb) in ((v1, (c1, c2)), (v2, (c2, x1))):
                lines = v.split("/")
                ty = yy + (rh - 12) / 2 - (len(lines) - 1) * 24
                for line in lines:
                    segs = parse_markup(line)
                    fv = font("black", 40 if len(lines) == 1 else 36)
                    lw = sum(text_w(s, fv) for s, _ in segs)
                    x = (xa + xb) / 2 - lw / 2
                    for s, em in segs:
                        d.text((x, ty), s, font=fv, fill=with_alpha(PAL["red"] if em else PAL["ink"], ra), anchor="lm")
                        x += text_w(s, fv)
                    ty += 48
            y += rh
        fr.comp(L)


class EndCard(El):
    """次回予告"""
    sfx = "ding"

    def __init__(self, next_no, next_title, cta="フォローで続きを見る", **kw):
        super().__init__(**kw)
        self.next_no, self.next_title, self.cta = next_no, next_title, cta

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        d.rectangle([0, STAGE_Y, W, STAGE_Y + STAGE_H], fill=(20, 22, 32, int(170 * a)))
        k = ease_back(lt / 0.4)
        cy = STAGE_Y + 330 + (1 - clamp(k)) * 40
        d.text((W / 2, cy), "NEXT", font=font("black", 60), fill=with_alpha(PAL["gold"], a), anchor="mm")
        d.text((W / 2, cy + 90), self.next_no, font=font("black", 48), fill=with_alpha(PAL["white"], a), anchor="mm")
        d.text((W / 2, cy + 200), self.next_title, font=font("black", 92), fill=with_alpha(PAL["white"], a),
               anchor="mm", stroke_width=8, stroke_fill=with_alpha(PAL["red"], a))
        k2 = ease_back((lt - 0.5) / 0.4)
        if k2 > 0:
            fw = font("black", 46)
            tw = text_w(self.cta, fw)
            bx, by = W / 2, cy + 360
            s = clamp(k2, 0, 1.1) * (1 + 0.03 * math.sin(lt * 6))
            d.rounded_rectangle([bx - (tw / 2 + 40) * s, by - 44 * s, bx + (tw / 2 + 40) * s, by + 44 * s],
                                radius=44, fill=with_alpha(PAL["red"], a))
            d.text((bx, by), self.cta, font=fw, fill=with_alpha(PAL["white"], a), anchor="mm")
        fr.comp(L)


class PyramidTier(El):
    """身分ピラミッドの1段（i=0 が頂点）。段ごとに出す"""

    def __init__(self, i, n, name, desc, col, top=120, height=720, **kw):
        super().__init__(**kw)
        self.i, self.n, self.name, self.desc, self.col = i, n, name, desc, col
        self.top, self.height = top, height

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        k = ease_back(lt / 0.35)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        th = self.height / self.n
        wid = lambda y: 140 + (y - self.top) / self.height * 820
        y0 = self.top + self.i * th + 6
        y1 = self.top + (self.i + 1) * th - 6
        dy = (1 - clamp(k)) * 50
        cx = W / 2
        pts = [(cx - wid(y0) / 2, STAGE_Y + y0 + dy), (cx + wid(y0) / 2, STAGE_Y + y0 + dy),
               (cx + wid(y1) / 2, STAGE_Y + y1 + dy), (cx - wid(y1) / 2, STAGE_Y + y1 + dy)]
        d.polygon(pts, fill=with_alpha(self.col, a), outline=with_alpha(PAL["white"], a), width=5)
        my = STAGE_Y + (y0 + y1) / 2 + dy
        size = 52 if self.i else 40
        d.text((cx, my - 22), self.name, font=font("black", size), fill=with_alpha(PAL["white"], a), anchor="mm",
               stroke_width=5, stroke_fill=with_alpha(PAL["ink"], a))
        d.text((cx, my + 30), self.desc, font=font("bold", 32 if self.i else 26),
               fill=with_alpha(PAL["white"], a), anchor="mm", stroke_width=4, stroke_fill=with_alpha(PAL["ink"], a))
        fr.comp(L)


class Step(El):
    """民主化の階段の1段（i=0 が一番下）"""

    def __init__(self, i, year, name, desc, col=PAL["teal"], n=4, **kw):
        super().__init__(**kw)
        self.i, self.year, self.name, self.desc, self.col, self.n = i, year, name, desc, col, n

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        k = ease_back(lt / 0.35)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        w, h = 660, 170
        x0 = 40 + self.i * 110 - (1 - clamp(k)) * 60
        y1 = STAGE_Y + 950 - self.i * 200
        y0 = y1 - h
        d.rounded_rectangle([x0 + 6, y0 + 8, x0 + w + 6, y1 + 8], radius=18, fill=(0, 0, 0, int(50 * a)))
        d.rounded_rectangle([x0, y0, x0 + w, y1], radius=18, fill=with_alpha(PAL["white"], a),
                            outline=with_alpha(self.col, a), width=6)
        d.rounded_rectangle([x0, y0, x0 + 170, y1], radius=18, fill=with_alpha(self.col, a))
        d.rectangle([x0 + 150, y0, x0 + 170, y1], fill=with_alpha(self.col, a))
        d.text((x0 + 85, (y0 + y1) / 2), self.year, font=font("black", 40), fill=with_alpha(PAL["white"], a),
               anchor="mm")
        d.text((x0 + 195, y0 + 50), self.name, font=font("black", 50), fill=with_alpha(PAL["ink"], a), anchor="lm")
        segs = parse_markup(self.desc)
        x = x0 + 197
        fb = font("bold", 32)
        for s, em in segs:
            d.text((x, y0 + 118), s, font=fb, fill=with_alpha(PAL["red"] if em else PAL["dim"], a), anchor="lm")
            x += text_w(s, fb)
        fr.comp(L)


class Phalanx(El):
    """重装歩兵の密集隊形（丸盾と槍が横から進む）"""
    sfx = "whoosh"

    def __init__(self, y=520, **kw):
        super().__init__(**kw)
        self.y = y

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        k = ease_out(lt / 1.0)
        base_x = -500 + k * 560
        for row in range(3):
            for col in range(7):
                x = base_x + col * 130 + row * 40
                y = STAGE_Y + self.y + row * 95 - 60
                if not -80 < x < W + 80:
                    continue
                d.line([(x + 10, y - 150), (x + 20, y + 60)], fill=with_alpha(PAL["coast"], a), width=7)
                d.polygon([(x + 8, y - 170), (x + 18, y - 150), (x + 2, y - 150)], fill=with_alpha(PAL["dim"], a))
                d.ellipse([x - 55, y - 55, x + 55, y + 55], fill=with_alpha(PAL["gold"], a),
                          outline=with_alpha(PAL["ink"], a), width=6)
                d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=with_alpha(PAL["red"], a))
        la = a * clamp((lt - 0.6) / 0.3)
        _label(d, W / 2, STAGE_Y + 110, "重装歩兵の密集隊形", font("black", 56), PAL["ink"], la, "mm", 7)
        _label(d, W / 2, STAGE_Y + 175, "（ファランクス）", font("bold", 38), PAL["ink"], la, "mm", 5)
        fr.comp(L)


class Ostracon(El):
    """陶片追放の陶片（実在するテミストクレスの陶片がモチーフ）"""

    def __init__(self, x, y, name="ΘΕΜΙΣΤΟΚΛΗΣ", caption="↑「テミストクレス」と書かれた実物がモデル", **kw):
        super().__init__(**kw)
        self.x, self.y, self.name, self.caption = x, y, name, caption

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        s = 0.6 + 0.4 * ease_back(lt / 0.35)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        cx, cy = self.x, STAGE_Y + self.y
        shape = [(-260, -120), (-120, -175), (90, -150), (250, -90), (275, 40), (180, 150), (-40, 170),
                 (-210, 120), (-285, 10)]
        pts = [(cx + px * s, cy + py * s) for px, py in shape]
        d.polygon([(px + 10, py + 12) for px, py in pts], fill=(0, 0, 0, int(60 * a)))
        d.polygon(pts, fill=with_alpha((196, 110, 70), a), outline=with_alpha((120, 60, 35), a), width=6)
        n = int(len(self.name) * clamp((lt - 0.3) / 1.0))
        d.text((cx, cy), self.name[:n], font=font("bold", int(50 * s)), fill=with_alpha((40, 25, 20), a),
               anchor="mm")
        if self.caption:
            _label(d, cx, cy + 230, self.caption, font("bold", 34), PAL["ink"], a * clamp((lt - 1.0) / 0.3), "mm", 5)
        fr.comp(L)


class Trireme(El):
    """三段櫂船（3段のオールが動く）"""
    sfx = "whoosh"

    def __init__(self, y=520, label=True, **kw):
        super().__init__(**kw)
        self.y, self.label = y, label

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        cx = W / 2 + (1 - ease_out(lt / 1.0)) * -700
        cy = STAGE_Y + self.y + math.sin(lt * 2) * 6
        # 波
        for i in range(4):
            yy = STAGE_Y + self.y + 90 + i * 45
            pts = [(x, yy + math.sin(x / 40 + lt * 3 + i) * 8) for x in range(0, W + 20, 20)]
            d.line(pts, fill=with_alpha((120, 170, 180), a * (0.8 - i * 0.15)), width=5)
        # オール（3段）
        for tier in range(3):
            for i in range(11):
                ox = cx - 330 + i * 62 + tier * 14
                oy = cy + 10 + tier * 18
                ang = math.radians(110 + 22 * math.sin(lt * 5 + i * 0.2 + tier))
                ln = 120 + tier * 20
                d.line([(ox, oy), (ox + math.cos(ang) * ln * 0.45, oy + math.sin(ang) * ln)],
                       fill=with_alpha((110, 80, 50), a), width=6)
        # 船体
        hull = [(cx - 420, cy - 40), (cx + 360, cy - 40), (cx + 470, cy + 20), (cx + 360, cy + 40),
                (cx - 360, cy + 40), (cx - 440, cy - 90)]
        d.polygon(hull, fill=with_alpha((120, 70, 45), a), outline=with_alpha(PAL["ink"], a), width=5)
        d.rectangle([cx - 400, cy - 20, cx + 380, cy - 4], fill=with_alpha(PAL["gold"], a))
        d.ellipse([cx + 330, cy - 34, cx + 360, cy - 14], fill=with_alpha(PAL["white"], a),
                  outline=with_alpha(PAL["ink"], a), width=3)
        # マスト・帆
        d.line([(cx - 20, cy - 40), (cx - 20, cy - 300)], fill=with_alpha((110, 80, 50), a), width=10)
        d.polygon([(cx - 170, cy - 280), (cx + 130, cy - 280), (cx + 110, cy - 110), (cx - 150, cy - 110)],
                  fill=with_alpha((245, 235, 210), a), outline=with_alpha(PAL["coast"], a), width=4)
        d.ellipse([cx - 60, cy - 235, cx + 20, cy - 155], outline=with_alpha(PAL["red"], a), width=8)
        if self.label:
            la = a * clamp((lt - 0.6) / 0.3)
            _label(d, W / 2, STAGE_Y + 70, "三段櫂船（さんだんかいせん）", font("black", 50), PAL["ink"], la, "mm", 7)
            _label(d, W / 2, STAGE_Y + 128, "こぎ手は財産のない市民", font("bold", 38), PAL["red"], la, "mm", 5)
        fr.comp(L)


ASSEMBLY_ROWS = [("成年男性市民", PAL["teal"]), ("女性", PAL["red"]), ("奴隷", PAL["dim"]), ("在留外人", PAL["gold"])]


def _person(d, x, y, col, a, s=1.0):
    d.ellipse([x - 20 * s, y - 62 * s, x + 20 * s, y - 22 * s], fill=with_alpha(col, a))
    d.rounded_rectangle([x - 30 * s, y - 16 * s, x + 30 * s, y + 50 * s], radius=int(18 * s), fill=with_alpha(col, a))


class Assembly(El):
    """民会に参加できる人・できない人"""

    def __init__(self, top=210, **kw):
        super().__init__(**kw)
        self.top = top

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        _label(d, W / 2, STAGE_Y + 90, "民会に参加できるのは？", font("black", 56), PAL["ink"], a, "mm", 7)
        for r, (name, col) in enumerate(ASSEMBLY_ROWS):
            k = ease_back((lt - r * 0.12) / 0.35)
            if k <= 0:
                continue
            y = STAGE_Y + self.top + r * 180 + 60
            ra = a * clamp(k)
            _label(d, 60, y, name, font("black", 44), col, ra, "lm", 6)
            for i in range(5):
                _person(d, 410 + i * 105, y + 4, col, ra, clamp(k, 0, 1.1))
        fr.comp(L)


class AssemblyCross(El):
    """女性・奴隷・在留外人に✕（参政権なし）"""
    sfx = "stamp"

    def __init__(self, top=210, **kw):
        super().__init__(**kw)
        self.top = top

    def draw(self, fr, lt):
        a = self.alpha(fr.t)
        L = fr.layer()
        d = ImageDraw.Draw(L)
        k = ease_out(lt / 0.25)
        for r in (1, 2, 3):
            y = STAGE_Y + self.top + r * 180 + 60
            d.rounded_rectangle([30, y - 80, W - 30, y + 70], radius=20, fill=(236, 226, 200, int(160 * a * k)))
            s = 50 * (2 - k)
            d.line([(W - 110 - s, y - s), (W - 110 + s, y + s)], fill=with_alpha(PAL["red"], a * k), width=16)
            d.line([(W - 110 - s, y + s), (W - 110 + s, y - s)], fill=with_alpha(PAL["red"], a * k), width=16)
        y = STAGE_Y + self.top + 60
        d.ellipse([W - 160, y - 50, W - 60, y + 50], outline=with_alpha(PAL["teal"], a * k), width=14)
        fr.comp(L)
