"""YouTube 長編（横型 1920x1080 / 30fps）用 図解・地図アニメ動画エンジン

ショート用エンジン（shorts/engine）を横型・長尺向けに作り直したもの。
シーン（ナレーション文の並び＋演出要素）を受け取り、
VOICEVOX で音声合成 → Pillow でフレーム描画 → ffmpeg で MP4 に書き出す。

画面構成（上から）
  ヘッダー 0-72 / ステージ（地図・図解）72-888 / 字幕帯 888-1012 / 年表帯 1012-1080
字幕と年表は専用の帯に置くので、地図や図解と重ならない。
"""
import hashlib
import json
import math
import multiprocessing as mp
import os
import re
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 30
SR = 24000
ASSETS = os.environ.get("SHORTS_ASSETS", "/opt/assets")
VV_DIR = os.environ.get("VOICEVOX_DIR", "/opt/vv")
CACHE = os.path.join(os.path.dirname(__file__), "..", ".cache")

HEADER_H = 72
STAGE_Y, STAGE_H = 72, 816
SUB_Y, SUB_H = 888, 124
TL_Y, TL_H = 1012, 68

PAL = dict(
    bg=(243, 233, 210), ink=(31, 42, 68), red=(192, 57, 43), gold=(190, 140, 20),
    sea=(178, 208, 212), land=(236, 222, 187), coast=(112, 94, 64), white=(255, 252, 245),
    teal=(22, 121, 120), dim=(120, 110, 95), dark=(20, 22, 32), purple=(120, 72, 140),
    green=(70, 120, 60),
)

# ---------------------------------------------------------------- utilities
_fonts = {}


def font(kind, size):
    key = (kind, size)
    if key not in _fonts:
        name = {"black": "NotoSansCJKjp-Black.otf", "bold": "NotoSansCJKjp-Bold.otf",
                "medium": "NotoSansCJKjp-Medium.otf", "serif": "NotoSerifCJKjp-Black.otf"}[kind]
        _fonts[key] = ImageFont.truetype(os.path.join(ASSETS, name), size)
    return _fonts[key]


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_io(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_back(x):
    x = clamp(x)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def lerp(a, b, t):
    return a + (b - a) * t


def with_alpha(rgb, a):
    return (*rgb, int(clamp(a) * 255))


def text_w(txt, f):
    return f.getlength(txt)


def parse_markup(line):
    """「【強調】」を (文字列, 強調か) のリストへ"""
    out = []
    for part in re.split(r"(【[^】]*】)", line):
        if not part:
            continue
        if part.startswith("【"):
            out.append((part[1:-1], True))
        else:
            out.append((part, False))
    return out


def markup_w(line, f):
    return sum(text_w(s, f) for s, _ in parse_markup(line))


def draw_markup(d, x, y, line, f, col, em_col, a=1.0, anchor="ls", stroke=0, stroke_col=None):
    """強調つき1行を x（左端）から描く"""
    for s, em in parse_markup(line):
        d.text((x, y), s, font=f, fill=with_alpha(em_col if em else col, a), anchor=anchor,
               stroke_width=stroke, stroke_fill=with_alpha(stroke_col or PAL["white"], a) if stroke else None)
        x += text_w(s, f)


def plain(text):
    return text.replace("【", "").replace("】", "").replace("/", "")


def year_str(yr):
    yr = int(round(yr))
    return f"前{-yr}年" if yr < 0 else f"{yr}年"


# VOICEVOX が読み違えやすい語（字幕はそのまま、読み上げだけ置き換える）
READINGS = [
    (r"(?<!紀元)前(\d)", r"紀元前\1"), ("線文字A", "線文字エー"), ("線文字B", "線文字ビー"),
    ("＝", "、"), ("→", "から"), ("陶片", "とうへん"), ("集住", "しゅうじゅう"),
    ("三段櫂船", "さんだんかいせん"), ("護民官", "ごみんかん"), ("十二表法", "じゅうにひょうほう"),
    ("植民市", "しょくみんし"), ("無産市民", "むさんしみん"), ("隷属", "れいぞく"), ("何百", "なんびゃく"),
    (r"(?<=[ァ-ヴー])朝", "ちょう"), (r"(\d+)世(?!紀)", r"\1せい"),
    (r"(?<![\d])7歳", "ななさい"), (r"(?<![\d])1人", "ひとり"), (r"(?<![\d])2人", "ふたり"),
    (r"(?<![\d])1年", "いちねん"), (r"(?<![\d])4年", "よねん"), (r"(?<![\d])10年", "じゅうねん"),
    (r"(?<![\d])200以上", "二百以上"), ("平民会", "へいみんかい"),
]


def reading(text):
    for a, b in READINGS:
        text = re.sub(a, b, text)
    return text


# ---------------------------------------------------------------- TTS
class TTS:
    def __init__(self):
        from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
        ort = Onnxruntime.load_once(filename=os.path.join(
            VV_DIR, "voicevox_onnxruntime-linux-x64-1.17.3/lib/libvoicevox_onnxruntime.so.1.17.3"))
        self.s = Synthesizer(ort, OpenJtalk(os.path.join(VV_DIR, "open_jtalk_dic_utf_8-1.11")))
        with VoiceModelFile.open(os.path.join(VV_DIR, "0.vvm")) as m:
            self.s.load_voice_model(m)
        os.makedirs(CACHE, exist_ok=True)

    def kana(self, text, style):
        return self.s.create_audio_query(text, style).kana

    def say(self, text, style, speed, pitch=0.0, intonation=1.15):
        key = hashlib.md5(json.dumps([text, style, speed, pitch, intonation]).encode()).hexdigest()
        path = os.path.join(CACHE, key + ".wav")
        if not os.path.exists(path):
            q = self.s.create_audio_query(text, style)
            q.speed_scale = speed
            q.pitch_scale = pitch
            q.intonation_scale = intonation
            q.pre_phoneme_length = 0.05
            q.post_phoneme_length = 0.08
            with open(path, "wb") as fh:
                fh.write(self.s.synthesis(q, style))
        with wave.open(path) as wf:
            assert wf.getframerate() == SR
            a = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        return a.astype(np.float32) / 32768.0


# ---------------------------------------------------------------- map
def merc(lat):
    return math.degrees(math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))


class MapBase:
    """ある範囲・解像度で描いた地図の下地（陸地マスクつき）

    style="parchment"：古地図風 / style="terrain"：衛星写真風（Blue Marble の色＋標高の陰影・海の深さ）
    """

    def __init__(self, name, lon0, lon1, lat0, lat1, ppd, style="parchment"):
        self.lon0, self.lon1, self.lat0, self.lat1, self.ppd = lon0, lon1, lat0, lat1, ppd
        self.style = style
        self.sea_rgb = PAL["sea"] if style == "parchment" else (20, 52, 92)
        self.w = int((lon1 - lon0) * ppd)
        self.h = int((merc(lat1) - merc(lat0)) * ppd)
        tag = "" if style == "parchment" else "_terrain"
        path = os.path.join(CACHE, f"map_{name}_{ppd}{tag}.png")
        mpath = os.path.join(CACHE, f"mask_{name}_{ppd}.png")
        if os.path.exists(path) and os.path.exists(mpath):
            self.img = Image.open(path).convert("RGB")
            self.mask = Image.open(mpath).convert("L")
        else:
            os.makedirs(CACHE, exist_ok=True)
            mask_s, coast = self._land()
            self.img = self._render(mask_s, coast) if style == "parchment" else self._render_terrain(mask_s, coast)
            self.mask = mask_s
            self.img.save(path)
            self.mask.save(mpath)

    def bxy(self, lon, lat, ss=1):
        return ((lon - self.lon0) * self.ppd * ss, (merc(self.lat1) - merc(lat)) * self.ppd * ss)

    def covers(self, box_lon0, box_lon1, box_lat0, box_lat1):
        return (box_lon0 >= self.lon0 and box_lon1 <= self.lon1
                and box_lat0 >= self.lat0 and box_lat1 <= self.lat1)

    def _land(self):
        """Natural Earth の海岸線 → 陸地マスク（アンチエイリアス）と海岸線の座標（2倍解像度）"""
        ss = 2
        mask = Image.new("L", (self.w * ss, self.h * ss), 0)
        md = ImageDraw.Draw(mask)
        coast = []
        with open(os.path.join(ASSETS, "land.geojson")) as fh:
            gj = json.load(fh)
        for feat in gj["features"]:
            g = feat["geometry"]
            polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
            for poly in polys:
                for i, ring in enumerate(poly):
                    lons = [p[0] for p in ring]
                    lats = [p[1] for p in ring]
                    if max(lons) < self.lon0 - 2 or min(lons) > self.lon1 + 2:
                        continue
                    if max(lats) < self.lat0 - 2 or min(lats) > self.lat1 + 2:
                        continue
                    pts = [self.bxy(lo, max(-80, min(80, la)), ss) for lo, la in ring]
                    md.polygon(pts, fill=0 if i else 255)
                    coast.append(pts)
        return mask.resize((self.w, self.h), Image.LANCZOS), coast

    def _render(self, mask_s, coast):
        ss = 2
        blur = max(8, int(self.ppd * 0.28))
        glow = mask_s.filter(ImageFilter.GaussianBlur(blur))
        sea = Image.new("RGB", (self.w, self.h), PAL["sea"])
        sea_light = Image.new("RGB", (self.w, self.h), (205, 225, 222))
        sea = Image.composite(sea_light, sea, glow)
        land = Image.new("RGB", (self.w, self.h), PAL["land"])
        rng = np.random.default_rng(1)
        noise = (rng.normal(0, 1, (self.h // 4, self.w // 4)) * 6).astype(np.float32)
        noise = np.array(Image.fromarray(noise, mode="F").resize((self.w, self.h), Image.BILINEAR))
        la = np.asarray(land).astype(np.float32) + noise[..., None]
        land = Image.fromarray(np.clip(la, 0, 255).astype(np.uint8))
        img = Image.composite(land, sea, mask_s)
        line = Image.new("L", (self.w * ss, self.h * ss), 0)
        ld = ImageDraw.Draw(line)
        lw = max(2, int(round(3 * ss * (self.ppd / 100) ** 0.5)))
        for pts in coast:
            ld.line(pts + [pts[0]], fill=255, width=lw)
        line = line.resize((self.w, self.h), Image.LANCZOS)
        img = Image.composite(Image.new("RGB", img.size, PAL["coast"]), img, line)
        d = ImageDraw.Draw(img)
        for lon in range(-10, 81, 5):
            x = self.bxy(lon, 0)[0]
            d.line([(x, 0), (x, self.h)], fill=(160, 150, 125), width=1)
        for lat in range(10, 60, 5):
            y = self.bxy(0, lat)[1]
            d.line([(0, y), (self.w, y)], fill=(160, 150, 125), width=1)
        return img

    # ---- 衛星写真風（ショート #7 の look="doc" と同じ作り方）
    def _elevation(self):
        """AWS Terrain Tiles（terrarium）を貼り合わせ、この下地の座標に合わせた標高[m]を返す（足りないタイルは取得）"""
        z = 7 if self.ppd <= 100 else 8
        ts, n = 256, 2 ** z * 256
        tdir = os.path.join(ASSETS, "terrain", f"t{z}")
        os.makedirs(tdir, exist_ok=True)
        tx = lambda lon: int((lon + 180) / 360 * 2 ** z)
        ty = lambda lat: int((1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi)
                             / 2 * 2 ** z)
        xs = list(range(tx(self.lon0), tx(self.lon1) + 1))
        ys = list(range(ty(self.lat1), ty(self.lat0) + 1))
        tile = lambda x, y: os.path.join(tdir, f"{z}_{x}_{y}.png")
        need = [(x, y) for x in xs for y in ys if not os.path.exists(tile(x, y)) or not os.path.getsize(tile(x, y))]
        if need:
            from concurrent.futures import ThreadPoolExecutor
            print(f"  fetching {len(need)} terrain tiles (z{z})", flush=True)

            def fetch(xy):
                x, y = xy
                subprocess.run(["curl", "-sS", "-m", "60", "--retry", "3", "-o", tile(x, y),
                                f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"])
            with ThreadPoolExecutor(16) as ex:
                list(ex.map(fetch, need))
        mosaic = np.zeros((len(ys) * ts, len(xs) * ts), np.float32)
        for i, x in enumerate(xs):
            for j, y in enumerate(ys):
                a = np.asarray(Image.open(tile(x, y)).convert("RGB")).astype(np.float32)
                mosaic[j * ts:(j + 1) * ts, i * ts:(i + 1) * ts] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
        # ウェブメルカトルとこの下地は同じメルカトルなので、切り抜いて拡大するだけ
        k = n / (360 * self.ppd)
        X0 = (self.lon0 + 180) / 360 * n - xs[0] * ts
        Y0 = n / 2 - merc(self.lat1) * n / 360 - ys[0] * ts
        box = (X0, Y0, X0 + self.w * k, Y0 + self.h * k)
        return np.asarray(Image.fromarray(mosaic, mode="F").resize((self.w, self.h), Image.BILINEAR, box=box))

    def _render_terrain(self, mask_s, coast):
        land = np.asarray(mask_s).astype(np.float32)[..., None] / 255
        elev = self._elevation()
        bm = Image.open(os.path.join(ASSETS, "terrain", "bluemarble.jpg")).convert("RGB")
        bw, bh = bm.size
        lons = self.lon0 + np.arange(self.w) / self.ppd
        mercs = merc(self.lat1) - np.arange(self.h) / self.ppd
        lats = np.degrees(2 * np.arctan(np.exp(np.radians(mercs))) - np.pi / 2)
        bx = np.clip((lons + 180) / 360 * bw, 0, bw - 1).astype(int)
        by = np.clip((90 - lats) / 180 * bh, 0, bh - 1).astype(int)
        bmc = np.asarray(bm.filter(ImageFilter.GaussianBlur(1.2)))
        col = bmc[by][:, bx]
        col = np.asarray(Image.fromarray(col).filter(ImageFilter.GaussianBlur(max(3, self.ppd // 20)))).astype(np.float32)
        # Blue Marble の海の色が混ざった所（海岸沿い・小さな島）は、近くの陸の色で埋める（正規化畳み込み）
        wl = 1 - np.clip((col[..., 2:3] - col[..., 0:1] - 5) / 30, 0, 1)
        r = max(6, self.ppd // 6)
        blur = lambda a: np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(r))).astype(np.float32)
        den = blur(wl[..., 0] * 255)[..., None] / 255
        fill = np.stack([blur(col[..., c] * wl[..., 0]) for c in range(3)], axis=-1) / np.maximum(den, 0.02)
        fill = np.where(den > 0.05, fill, np.array([150, 138, 100], np.float32))
        col = col * wl + fill * (1 - wl)
        g = col.mean(axis=2, keepdims=True)
        col = g + (col - g) * 1.25
        e = np.clip(elev, 0, None)[..., None]
        col = col + (np.array([150, 132, 110], np.float32) - col) * np.clip((e - 1200) / 1800, 0, 0.6)
        col = col + (np.array([238, 240, 245], np.float32) - col) * np.clip((e - 2600) / 900, 0, 0.85)
        # 陰影（北西からの光）
        dy, dx = np.gradient(np.clip(elev, 0, None))
        cell = 111000 / self.ppd
        slope = np.arctan(6.0 * np.hypot(dx, dy) / cell)
        aspect = np.arctan2(-dx, dy)
        az, alt = np.radians(315), np.radians(40)
        shade = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - aspect)
        shade = np.clip(shade / np.sin(alt), 0.35, 1.35)[..., None]
        land_rgb = np.clip(col * (0.25 + 0.75 * shade), 0, 255)
        del col, dx, dy, slope, aspect
        # 海：深さで色を変える
        depth = np.clip(-elev, 0, 5000)[..., None] / 5000
        shallow, deep = np.array([62, 130, 160], np.float32), np.array([12, 38, 78], np.float32)
        sea = shallow + (deep - shallow) * np.sqrt(depth)
        sea = sea * np.where(elev[..., None] < 0, np.clip(1 + (np.clip(shade, 0.6, 1.2) - 1) * 0.25, 0.85, 1.1), 1.0)
        img = land_rgb * land + sea * (1 - land)
        out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
        line = Image.new("L", (self.w * 2, self.h * 2), 0)
        ld = ImageDraw.Draw(line)
        for pts in coast:
            ld.line(pts + [pts[0]], fill=110, width=3)
        line = line.resize((self.w, self.h), Image.LANCZOS)
        return Image.composite(Image.new("RGB", out.size, (235, 230, 210)), out, line)


class WorldMap:
    """広域用と詳細用の下地を、ズームに応じて使い分ける"""

    def __init__(self, look="classic"):
        if look == "doc":
            self.bases = [
                MapBase("wide", -12.0, 62.0, 8.0, 56.0, 60, style="terrain"),
                MapBase("med", -10.0, 36.0, 28.0, 53.0, 160, style="terrain"),
            ]
        else:
            self.bases = [
                MapBase("wide", -12.0, 82.0, 8.0, 56.0, 60),
                MapBase("aegean", 8.0, 42.0, 28.0, 47.0, 240),
            ]
        self._ck, self._ci = None, None
        self._mk, self._mi = None, None

    def _pick(self, cam):
        lon, lat, z = cam
        half_w = W / 2 / z
        half_h = STAGE_H / 2 / z
        my = merc(lat)
        box = (lon - half_w, lon + half_w, _imerc(my - half_h), _imerc(my + half_h))
        best = self.bases[0]
        for b in self.bases[1:]:
            if z > b.ppd * 0.3 and b.covers(*box):
                best = b
        return best

    def _crop(self, base, img, cam, mode):
        lon, lat, z = cam
        cx, cy = base.bxy(lon, lat)
        s = base.ppd / z
        bx0, by0 = cx - W * s / 2, cy - STAGE_H * s / 2
        bx1, by1 = cx + W * s / 2, cy + STAGE_H * s / 2
        rg = 2.0 if s > 2 else None
        if bx0 >= 0 and by0 >= 0 and bx1 <= base.w and by1 <= base.h:
            return img.resize((W, STAGE_H), mode, box=(bx0, by0, bx1, by1), reducing_gap=rg)
        # 下地の範囲外は海（マスクは 0）で埋める
        out = Image.new(img.mode, (W, STAGE_H), base.sea_rgb if img.mode == "RGB" else 0)
        ix0, iy0, ix1, iy1 = max(0, bx0), max(0, by0), min(base.w, bx1), min(base.h, by1)
        if ix1 - ix0 < 1 or iy1 - iy0 < 1:
            return out
        ox0, oy0 = int(round((ix0 - bx0) / s)), int(round((iy0 - by0) / s))
        ow, oh = int(round((ix1 - ix0) / s)), int(round((iy1 - iy0) / s))
        if ow > 0 and oh > 0:
            out.paste(img.resize((ow, oh), mode, box=(ix0, iy0, ix1, iy1), reducing_gap=rg), (ox0, oy0))
        return out

    def view(self, cam):
        key = tuple(round(v, 4) for v in cam)
        if key != self._ck:
            b = self._pick(cam)
            self._ck, self._ci = key, self._crop(b, b.img, cam, Image.BILINEAR)
        return self._ci

    def land_mask(self, cam):
        key = tuple(round(v, 4) for v in cam)
        if key != self._mk:
            b = self._pick(cam)
            self._mk, self._mi = key, self._crop(b, b.mask, cam, Image.BILINEAR)
        return self._mi

    @staticmethod
    def to_screen(cam, lon, lat):
        clon, clat, z = cam
        x = (lon - clon) * z + W / 2
        y = (merc(clat) - merc(lat)) * z + STAGE_H / 2 + STAGE_Y
        return x, y


def _imerc(m):
    return math.degrees(2 * math.atan(math.exp(math.radians(m))) - math.pi / 2)


# ---------------------------------------------------------------- audio fx / bgm
def _env(n, a, r):
    e = np.ones(n, np.float32)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def sfx(kind):
    rng = np.random.default_rng(len(kind))
    if kind == "pop":
        n = int(0.08 * SR)
        t = np.arange(n) / SR
        f = np.linspace(700, 1150, n)
        return 0.22 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)
    if kind == "whoosh":
        n = int(0.35 * SR)
        x = rng.normal(0, 1, n).astype(np.float32)
        k = np.hanning(41)
        x = np.convolve(x, k / k.sum(), "same")
        return 0.3 * x * np.sin(np.linspace(0, np.pi, n)) ** 2
    if kind == "stamp":
        n = int(0.25 * SR)
        t = np.arange(n) / SR
        thump = np.sin(2 * np.pi * 90 * t) * np.exp(-t * 22)
        noise = rng.normal(0, 1, n) * np.exp(-t * 60) * 0.3
        return 0.5 * (thump + noise)
    if kind == "ding":
        n = int(0.6 * SR)
        t = np.arange(n) / SR
        return 0.16 * (np.sin(2 * np.pi * 1320 * t) + 0.5 * np.sin(2 * np.pi * 1980 * t)) * np.exp(-t * 7)
    if kind == "chapter":
        n = int(1.2 * SR)
        t = np.arange(n) / SR
        out = np.zeros(n, np.float32)
        for i, m in enumerate((62, 69, 74)):
            st = int(i * 0.09 * SR)
            f = 440 * 2 ** ((m - 69) / 12)
            tt = t[: n - st]
            out[st:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 3.5) * 0.12
        return out
    raise ValueError(kind)


def _pluck(freq, dur, bright=0.5, seed=0):
    """Karplus-Strong（竪琴っぽい撥弦音）"""
    n_total = int(dur * SR)
    p = int(SR / freq)
    rng = np.random.default_rng(seed)
    y = np.zeros(n_total + p + 1, np.float32)
    y[:p] = rng.uniform(-1, 1, p) * (1 - bright) + np.sign(rng.uniform(-1, 1, p)) * bright
    y[:p] -= y[:p].mean()
    decay = 0.996
    k = p
    while k < len(y):
        end = min(k + p, len(y))
        idx = np.arange(k, end)
        y[k:end] = decay * 0.5 * (y[idx - p] + y[idx - p - 1])
        k = end
    return y[:n_total] * _env(n_total, 0.002, 0.2)


# 長尺で単調にならないよう、16小節ごとに進行と伴奏を変える
PROGRESSIONS = [
    [[50, 57, 62, 65, 69], [48, 55, 60, 64, 67], [46, 53, 58, 62, 65], [48, 55, 60, 64, 67]],  # Dm C Bb C
    [[50, 57, 62, 65, 69], [53, 57, 60, 65, 69], [48, 55, 60, 64, 67], [45, 52, 57, 61, 64]],  # Dm F C A
    [[46, 53, 58, 62, 65], [48, 55, 60, 64, 67], [50, 57, 62, 65, 69], [50, 57, 62, 65, 69]],  # Bb C Dm Dm
]
PATTERNS = [[0, 2, 3, 4, 3, 2, 1, 2], [0, 1, 2, 3, 4, 3, 2, 1], [0, 2, 4, 2, 3, 1, 2, 4]]


def bgm(duration, bpm=80, seed=3):
    """D ドリアンのリラ風アルペジオ＋ドローン＋フレームドラム（自作・著作権フリー）"""
    n = int(duration * SR) + SR
    out = np.zeros(n, np.float32)
    beat = 60 / bpm
    midi = lambda m: 440 * 2 ** ((m - 69) / 12)
    t = 0.0
    bar = 0
    rng = np.random.default_rng(seed)
    while t < duration + 1:
        sec = (bar // 16) % 3
        chords, pattern = PROGRESSIONS[sec], PATTERNS[sec]
        ch = chords[bar % 4]
        sparse = (bar // 8) % 4 == 3  # ときどきアルペジオを減らして息継ぎ
        for i, pi in enumerate(pattern):
            if sparse and i % 2:
                continue
            st = int((t + i * beat / 2) * SR)
            note = _pluck(midi(ch[pi] + 12), 1.6, 0.35, seed=bar * 8 + i)
            vel = 0.22 if i % 2 == 0 else 0.15
            e = min(n, st + len(note))
            if st < n:
                out[st:e] += vel * note[: e - st]
        st = int(t * SR)
        bass = _pluck(midi(ch[0] - 12), 3.2, 0.1, seed=999 + bar)
        e = min(n, st + len(bass))
        if st < n:
            out[st:e] += 0.35 * bass[: e - st]
        if not sparse:
            for b in (0, 2):
                st = int((t + b * beat) * SR)
                dn = int(0.3 * SR)
                tt = np.arange(dn) / SR
                hit = (np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 14) * (0.3 if b == 0 else 0.18)
                       + rng.normal(0, 1, dn) * np.exp(-tt * 45) * 0.025)
                e = min(n, st + dn)
                if st < n:
                    out[st:e] += hit[: e - st]
        t += 4 * beat
        bar += 1
    tt = np.arange(n) / SR
    out += 0.05 * np.sin(2 * np.pi * midi(38) * tt) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.2 * tt))
    out /= np.max(np.abs(out)) + 1e-6
    return out


# ---------------------------------------------------------------- scene model
class Chunk:
    def __init__(self, sub, tts=None):
        self.sub = sub                         # 字幕（【】で強調、/ で改行）
        self.tts = reading(tts or plain(sub))  # 読み上げ文
        self.audio = None
        self.t0 = self.t1 = 0.0


class Scene:
    """chapter=("第1章", "エーゲ文明") を渡すと、そこから新しい章（YouTube チャプター）になる"""

    def __init__(self, chunks, els=(), cam=None, cam_dur=1.6, stage="map", year=None, year_text=None,
                 dark=0.0, hold=0.0, pad=0.35, chapter=None):
        self.chunks = [c if isinstance(c, Chunk) else Chunk(*c) if isinstance(c, tuple) else Chunk(c)
                       for c in chunks]
        self.els = list(els)
        self.cam, self.cam_dur, self.stage, self.year, self.year_text = cam, cam_dur, stage, year, year_text
        self.dark, self.hold, self.pad, self.chapter = dark, hold, pad, chapter
        self.t0 = self.t1 = 0.0


class El:
    """演出要素。at: 秒 or 'c1'(そのシーンの1番目の文の開始) or 'c1+0.5'。span: 何シーン残すか

    layer="bg" の要素（写真など）は地図と同じ背景扱いで、実写寄りの見た目では映画風の質感がかかる
    """
    sfx = "pop"
    layer = "fg"

    def __init__(self, at=0.0, span=1, fade=0.3, dur=None):
        self.at, self.span, self.fade, self.dur = at, span, fade, dur
        self.t0 = self.t1 = 0.0

    def alpha(self, t):
        # 0秒目から出る要素はフェードインしない（1コマ目で内容が見えるように）
        fade_in = 1.0 if self.t0 <= 0.001 else clamp((t - self.t0) / 0.25)
        return fade_in * clamp((self.t1 - t) / self.fade)

    def draw(self, fr, lt):
        raise NotImplementedError


class FilmLook:
    """ステージ（地図・写真）部分だけにかける映画風の質感：色調・周辺減光・粒子（ショート #7 と同じ）"""

    def __init__(self, seed=7):
        yy, xx = np.mgrid[0:STAGE_H, 0:W].astype(np.float32)
        r = np.hypot((xx - W / 2) / (W / 2), (yy - STAGE_H / 2) / (STAGE_H / 2))
        self.vignette = (1 - 0.34 * np.clip(r - 0.5, 0, 1) ** 1.6)[..., None]
        rng = np.random.default_rng(seed)
        self.grain = [np.asarray(Image.fromarray(rng.normal(128, 40, (STAGE_H // 2, W // 2)).clip(0, 255)
                                                 .astype(np.uint8)).resize((W, STAGE_H), Image.BILINEAR),
                                 np.float32)[..., None] - 128 for _ in range(6)]
        x = np.arange(256, dtype=np.float32) / 255
        curve = x + 0.12 * np.sin((x - 0.5) * np.pi) * x * (1 - x) * 4 * 0.5  # 弱いS字
        self.lut = np.stack([np.clip(curve * 255 * m + o, 0, 255) for m, o in ((1.03, 4), (1.0, 1), (0.94, -2))])

    def apply(self, canvas, frame_no):
        box = (0, STAGE_Y, W, STAGE_Y + STAGE_H)
        a = np.asarray(canvas.crop(box).convert("RGB"))
        g = np.stack([self.lut[c][a[..., c]] for c in range(3)], axis=-1)
        g = g * self.vignette + self.grain[frame_no % len(self.grain)] * 0.09
        canvas.paste(Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA"), box[:2])


class Frame:
    def __init__(self, video, t):
        self.v, self.t = video, t
        self.canvas = None
        self.cam = None

    def comp(self, layer):
        self.canvas.alpha_composite(layer)

    def layer(self):
        return Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def xy(self, lon, lat):
        return self.v.map.to_screen(self.cam, lon, lat)

    def zoom(self):
        return self.cam[2]


# ---------------------------------------------------------------- video
_RENDER_VIDEO = None


def _render_segment(args):
    """並列書き出しの1区間（fork したプロセスで実行）"""
    a, b, path = args
    v = _RENDER_VIDEO
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    p = subprocess.Popen([
        ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", str(v.crf),
        "-threads", "1", "-pix_fmt", "yuv420p", "-g", str(FPS * 4), path], stdin=subprocess.PIPE)
    for i in range(a, b):
        p.stdin.write(v.render_frame(i / FPS).tobytes())
        if (i - a) % 600 == 0:
            print(f"  [{os.path.basename(path)}] {i - a}/{b - a}", flush=True)
    p.stdin.close()
    p.wait()
    return path


class Video:
    def __init__(self, scenes, *, header, credit, voice, speed, max_dur=600.0, timeline=None,
                 pitch=0.0, intonation=1.15, gap=0.22, crf=20, music_vol=0.11, look="classic"):
        self.scenes = scenes
        self.header, self.credit = header, credit
        self.voice, self.speed, self.max_dur = voice, speed, max_dur
        self.pitch, self.intonation, self.gap = pitch, intonation, gap
        self.timeline, self.crf, self.music_vol = timeline, crf, music_vol
        self.look = look  # "classic"：古地図風 / "doc"：実写寄り（衛星写真風の地図＋写真＋映画風の質感）
        self.map = WorldMap(look)
        self.film = FilmLook() if look == "doc" else None
        self._plain_bg = None
        self._add_chapter_banners()

    def _add_chapter_banners(self):
        from .elements import ChapterBanner
        for i, sc in enumerate(self.scenes):
            if sc.chapter and i > 0:
                sc.els.insert(0, ChapterBanner(*sc.chapter, dur=4.0))

    # ---- タイミング決定
    def build_audio(self, tts):
        speed = self.speed
        for _ in range(8):
            t = 0.0
            for sc in self.scenes:
                sc.t0 = t
                for c in sc.chunks:
                    c.audio = tts.say(c.tts, self.voice, speed, self.pitch, self.intonation)
                    c.t0 = t
                    c.t1 = t + len(c.audio) / SR
                    t = c.t1 + self.gap
                t += sc.pad + sc.hold
                sc.t1 = t
            if t <= self.max_dur:
                break
            speed = round(speed * min(1.06, t / self.max_dur + 0.005), 3)
            print(f"  too long ({t:.1f}s) -> speed {speed}")
        self.speed_used, self.duration = speed, t
        for i, sc in enumerate(self.scenes):
            for el in sc.els:
                el.t0 = sc.t0 + scene_time(sc, el.at)
                if hasattr(el, "resolve"):
                    el.resolve(lambda ref, sc=sc, el=el: sc.t0 + scene_time(sc, ref) - el.t0)
                last = self.scenes[min(len(self.scenes) - 1, i + el.span - 1)]
                el.t1 = last.t1 if i + el.span - 1 < len(self.scenes) - 1 else self.duration + 1
                if el.dur is not None:
                    el.t1 = min(el.t1, el.t0 + el.dur)
        n = int(self.duration * SR) + SR
        voice = np.zeros(n, np.float32)
        for sc in self.scenes:
            for c in sc.chunks:
                s = int(c.t0 * SR)
                voice[s:s + len(c.audio)] += c.audio
        fx = np.zeros(n, np.float32)
        for sc in self.scenes:
            for el in sc.els:
                if el.sfx:
                    a = sfx(el.sfx)
                    s = int(el.t0 * SR)
                    e = min(n, s + len(a))
                    fx[s:e] += a[: e - s]
        music = bgm(self.duration + 1)[:n]
        env = np.convolve(np.abs(voice), np.ones(SR // 10) / (SR // 10), "same")
        duck = 1 - 0.45 * np.clip(env / 0.05, 0, 1)
        duck = np.convolve(duck, np.ones(SR // 5) / (SR // 5), "same")
        mix = voice * 0.95 + fx * 0.5 + music * self.music_vol * duck
        fade = int(1.5 * SR)
        mix[-fade:] *= np.linspace(1, 0, fade)
        mix = np.clip(mix, -1, 1)
        return mix[: int(self.duration * SR)]

    # ---- 状態
    def scene_at(self, t):
        for sc in self.scenes:
            if t < sc.t1:
                return sc
        return self.scenes[-1]

    def chapter_at(self, t):
        cur = None
        for sc in self.scenes:
            if t < sc.t0:
                break
            if sc.chapter:
                cur = sc.chapter
        return cur

    def cam_at(self, t):
        prev = None
        for sc in self.scenes:
            if sc.cam is not None:
                if t < sc.t0:
                    break
                if prev is None:
                    cur = sc.cam
                else:
                    k = ease_io((t - sc.t0) / sc.cam_dur)
                    z = math.exp(lerp(math.log(prev[2]), math.log(sc.cam[2]), k))
                    cur = (lerp(prev[0], sc.cam[0], k), lerp(prev[1], sc.cam[1], k), z)
                prev = sc.cam if t >= sc.t0 + sc.cam_dur else cur
        return prev

    def dark_at(self, t):
        v, prev = 0.0, 0.0
        for sc in self.scenes:
            if t < sc.t0:
                break
            v = lerp(prev, sc.dark, ease_io((t - sc.t0) / 0.8))
            prev = sc.dark
        return v

    def year_at(self, t):
        yr_now, prev, text, settled = None, None, None, True
        for sc in self.scenes:
            if t < sc.t0:
                break
            if sc.year is not None:
                k = ease_io((t - sc.t0) / 1.0)
                yr_now = sc.year if prev is None else lerp(prev, sc.year, k)
                settled = k >= 1.0 or prev is None or prev == sc.year
                prev = sc.year
                text = sc.year_text
        if yr_now is None:
            return None, None
        return yr_now, (text if (text and settled) else year_str(yr_now if not settled else prev))

    # ---- 描画
    def draw_header(self, fr):
        d = ImageDraw.Draw(fr.canvas)
        d.rectangle([0, 0, W, HEADER_H], fill=PAL["ink"])
        f = font("black", 30)
        label = "世界史ずかん"
        lw = text_w(label, f)
        d.rounded_rectangle([24, 14, 24 + lw + 40, 58], radius=22, fill=PAL["gold"])
        d.text((44, 36), label, font=f, fill=PAL["ink"], anchor="lm")
        x = 24 + lw + 64
        ch = self.chapter_at(fr.t)
        if ch:
            no, title = ch
            fn = font("black", 30)
            d.text((x, 36), no, font=fn, fill=PAL["gold"], anchor="lm")
            d.text((x + text_w(no, fn) + 18, 36), title, font=font("black", 34), fill=PAL["white"], anchor="lm")
        d.text((W - 26, 30), self.header, font=font("bold", 24), fill=(215, 205, 175), anchor="rm")
        d.text((W - 26, 57), self.credit, font=font("medium", 18), fill=(160, 165, 185), anchor="rm")

    def draw_stage(self, fr, sc):
        fr.cam = self.cam_at(fr.t)
        if sc.stage == "map" and fr.cam is not None:
            fr.canvas.paste(self.map.view(fr.cam), (0, STAGE_Y))
        elif sc.stage == "map" and self.look == "doc":  # 写真だけの場面（地図のカメラがまだ無い）
            ImageDraw.Draw(fr.canvas).rectangle([0, STAGE_Y, W, STAGE_Y + STAGE_H], fill=(16, 18, 26))
        elif sc.stage == "plain" and self.look == "doc":
            fr.canvas.paste(self._doc_plain(), (0, STAGE_Y))
        else:  # "paper"：どちらの見た目でも紙の背景（年表など細かい図向け）
            d = ImageDraw.Draw(fr.canvas)
            d.rectangle([0, STAGE_Y, W, STAGE_Y + STAGE_H], fill=(236, 226, 200))
            for y in range(STAGE_Y + 34, STAGE_Y + STAGE_H, 64):
                d.line([(0, y), (W, y)], fill=(227, 215, 188), width=2)
        dk = self.dark_at(fr.t)
        if dk > 0.01:
            L = fr.layer()
            ImageDraw.Draw(L).rectangle([0, STAGE_Y, W, STAGE_Y + STAGE_H], fill=with_alpha(PAL["dark"], dk))
            fr.comp(L)

    def _doc_plain(self):
        """実写寄りの見た目で使う、図解用の暗い背景（中央が少し明るい）"""
        if self._plain_bg is None:
            yy, xx = np.mgrid[0:STAGE_H, 0:W].astype(np.float32)
            r = np.hypot((xx - W / 2) / W, (yy - STAGE_H / 2) / STAGE_H)
            base = np.array([44, 50, 64], np.float32) * (1.15 - 0.6 * r)[..., None]
            self._plain_bg = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
        return self._plain_bg

    def draw_frame_border(self, fr):
        d = ImageDraw.Draw(fr.canvas)
        d.rectangle([0, STAGE_Y, W, STAGE_Y + 5], fill=PAL["gold"])
        d.rectangle([0, SUB_Y - 5, W, SUB_Y], fill=PAL["gold"])

    def draw_subtitle(self, fr, sc):
        d = ImageDraw.Draw(fr.canvas)
        d.rectangle([0, SUB_Y, W, SUB_Y + SUB_H], fill=(250, 244, 228))
        cur = None
        for c in sc.chunks:
            if c.t0 - 0.05 <= fr.t:
                cur = c
        if cur is None:
            return
        k = 1.0 if cur.t0 <= 0.001 else ease_out((fr.t - cur.t0 + 0.05) / 0.18)
        lines = cur.sub.split("/")
        f = font("black", 52 if len(lines) == 1 else 46)
        lh = 58
        total_h = lh * len(lines)
        y = SUB_Y + (SUB_H - total_h) / 2 + lh * 0.78 + (1 - k) * 10
        L = fr.layer()
        dl = ImageDraw.Draw(L)
        for line in lines:
            lw = markup_w(line, f)
            draw_markup(dl, W / 2 - lw / 2, y, line, f, PAL["ink"], PAL["red"], a=k)
            y += lh
        fr.comp(L)

    def draw_timeline(self, fr):
        tl = self.timeline
        d = ImageDraw.Draw(fr.canvas)
        d.rectangle([0, TL_Y, W, H], fill=PAL["ink"])
        if not tl:
            return
        yr_now, label = self.year_at(fr.t)
        X = tl_scale(tl["breaks"], 330, W - 30)
        # 現在の年
        d.rounded_rectangle([16, TL_Y + 11, 206, TL_Y + 57], radius=23, fill=PAL["white"])
        if label:
            fl = font("black", 30 if len(label) <= 6 else 24)
            d.text((111, TL_Y + 34), label, font=fl, fill=PAL["red"], anchor="mm")
        fs = font("bold", 17)
        for li, (lane, eras) in enumerate(tl["lanes"]):
            y0 = TL_Y + 9 + li * 26
            d.text((314, y0 + 11), lane, font=font("bold", 18), fill=(200, 195, 175), anchor="rm")
            d.rounded_rectangle([X(tl["breaks"][0][0]), y0, X(tl["breaks"][-1][0]), y0 + 22], radius=11,
                                fill=(60, 70, 95))
            for a, b, name, col in eras:
                x0, x1 = X(a), X(b)
                d.rounded_rectangle([x0 + 1, y0, x1 - 1, y0 + 22], radius=11, fill=col)
                if text_w(name, fs) + 12 < x1 - x0:
                    d.text(((x0 + x1) / 2, y0 + 11), name, font=fs, fill=PAL["ink"], anchor="mm")
        if yr_now is not None:
            x = X(yr_now)
            d.line([(x, TL_Y + 4), (x, TL_Y + 64)], fill=PAL["white"], width=6)
            d.line([(x, TL_Y + 4), (x, TL_Y + 64)], fill=PAL["red"], width=3)
            d.polygon([(x - 9, TL_Y + 2), (x + 9, TL_Y + 2), (x, TL_Y + 13)], fill=PAL["red"])

    def render_frame(self, t):
        fr = Frame(self, t)
        fr.canvas = Image.new("RGBA", (W, H), (*PAL["bg"], 255))
        sc = self.scene_at(t)
        self.draw_stage(fr, sc)
        active = [el for s in self.scenes for el in s.els if el.t0 <= t < el.t1]
        for layer in ("bg", "fg"):
            for el in active:
                if el.layer == layer:
                    el.draw(fr, t - el.t0 + (3.0 if el.t0 <= 0.001 else 0.0))
            if layer == "bg" and self.film:
                self.film.apply(fr.canvas, int(round(t * FPS)))
        self.draw_frame_border(fr)
        self.draw_header(fr)
        self.draw_subtitle(fr, sc)
        self.draw_timeline(fr)
        return fr.canvas.convert("RGB")

    def render(self, out_path, tts, preview_times=None, workers=None):
        global _RENDER_VIDEO
        audio = self.build_audio(tts)
        print(f"  duration {self.duration:.2f}s ({self.duration / 60:.1f}min), speed {self.speed_used}")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        if preview_times is not None:
            if preview_times == "scenes":
                preview_times = [min(sc.t1 - 0.3, sc.t0 + 3.0) for sc in self.scenes]
            paths = []
            for pt in preview_times:
                p = out_path.replace(".mp4", f"_{pt:06.1f}.png")
                self.render_frame(pt).save(p)
                paths.append(p)
            return paths
        wav_path = out_path + ".wav"
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SR)
            wf.writeframes((audio * 32767).astype(np.int16).tobytes())
        n_frames = int(self.duration * FPS)
        workers = workers or os.cpu_count() or 2
        bounds = np.linspace(0, n_frames, workers * 2 + 1).astype(int)
        segs = [(int(bounds[i]), int(bounds[i + 1]), f"{out_path}.seg{i:02d}.mp4") for i in range(len(bounds) - 1)]
        _RENDER_VIDEO = self
        with mp.get_context("fork").Pool(workers) as pool:
            done = pool.map(_render_segment, segs, chunksize=1)
        lst = out_path + ".txt"
        with open(lst, "w") as fh:
            for p in done:
                fh.write(f"file '{os.path.abspath(p)}'\n")
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run([
            ff, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav_path,
            "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", out_path],
            check=True)
        for p in done:
            os.remove(p)
        os.remove(lst)
        os.remove(wav_path)

    # ---- 書き出し用テキスト
    def timing_log(self):
        rows = []
        for sc in self.scenes:
            if sc.chapter:
                rows.append(f"\n== {sc.chapter[0]} {sc.chapter[1]} ==")
            for c in sc.chunks:
                rows.append(f"{fmt_ts(c.t0)}  {plain(c.sub)}")
        credits = self.credits()
        if credits:
            rows += ["", "[画像クレジット]"] + credits
        return "\n".join(rows).strip() + "\n"

    def credits(self):
        """使った画像の出典（重複なし・登場順）"""
        out = []
        for sc in self.scenes:
            for el in sc.els:
                c = getattr(el, "credit_full", None) or getattr(el, "credit", None)
                if c and c not in out:
                    out.append(c)
        return out

    def chapters(self):
        rows = []
        for sc in self.scenes:
            if sc.chapter:
                rows.append(f"{fmt_ts(sc.t0 if rows else 0)} {sc.chapter[0]} {sc.chapter[1]}")
        return "\n".join(rows) + "\n"


def scene_time(sc, at):
    """演出の出るタイミング（秒 or 'c1' / 'c1+0.5'）→ シーン先頭からの秒"""
    if isinstance(at, str):
        ci, _, off = at[1:].partition("+")
        return sc.chunks[int(ci)].t0 - sc.t0 + float(off or 0)
    return at


def fmt_ts(t):
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


def tl_scale(breaks, x0, x1):
    """年表の目盛り（区間ごとに幅を変えられる）。breaks=[(年, 0〜1の位置), ...]"""
    def X(yr):
        for (ya, pa), (yb, pb) in zip(breaks, breaks[1:]):
            if yr <= yb or (yb, pb) == breaks[-1]:
                k = (yr - ya) / (yb - ya)
                return x0 + (pa + (pb - pa) * clamp(k)) * (x1 - x0)
        return x1
    return X
