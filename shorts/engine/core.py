"""YouTube Shorts 用 図解・地図アニメ動画エンジン（1080x1920 / 30fps）

シーン（ナレーション文の並び＋演出要素）を受け取り、
VOICEVOX で音声合成 → Pillow でフレーム描画 → ffmpeg で MP4 に書き出す。
"""
import hashlib
import json
import math
import os
import re
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
SR = 24000
ASSETS = os.environ.get("SHORTS_ASSETS", "/opt/assets")
VV_DIR = os.environ.get("VOICEVOX_DIR", "/opt/vv")
CACHE = os.path.join(os.path.dirname(__file__), "..", ".cache")

# レイアウト（ショートの UI に隠れない範囲に情報を置く）
HEADER_H = 250
STAGE_Y, STAGE_H = 260, 980
SUB_Y = 1262
TL_Y = 1560

PAL = dict(
    bg=(243, 233, 210), ink=(31, 42, 68), red=(192, 57, 43), gold=(190, 140, 20),
    sea=(178, 208, 212), land=(236, 222, 187), coast=(112, 94, 64), white=(255, 252, 245),
    teal=(22, 121, 120), dim=(120, 110, 95), dark=(20, 22, 32),
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


def draw_text_c(d, cx, y, txt, f, fill, stroke=0, stroke_fill=None, anchor="mt"):
    d.text((cx, y), txt, font=f, fill=fill, anchor=anchor,
           stroke_width=stroke, stroke_fill=stroke_fill)


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


def plain(text):
    return text.replace("【", "").replace("】", "").replace("/", "")


READINGS = [(r"前(\d)", r"紀元前\1"), ("線文字A", "線文字エー"), ("線文字B", "線文字ビー"),
            ("＝", "、"), ("→", "から"), ("陶片", "とうへん"), ("並べて", "ならべて")]


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
            q.pre_phoneme_length = 0.04
            q.post_phoneme_length = 0.06
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
    LON0, LON1, LAT0, LAT1 = -12.0, 80.0, 7.0, 58.0
    PPD = 100  # base image: px per degree of longitude

    def __init__(self):
        path = os.path.join(CACHE, "mapbase_v2.png")
        self.w = int((self.LON1 - self.LON0) * self.PPD)
        self.h = int((merc(self.LAT1) - merc(self.LAT0)) * self.PPD)
        if os.path.exists(path):
            self.img = Image.open(path).convert("RGB")
        else:
            self.img = self._render()
            self.img.save(path)
        self._cache_key, self._cache_img = None, None

    def bxy(self, lon, lat, ss=1):
        return ((lon - self.LON0) * self.PPD * ss, (merc(self.LAT1) - merc(lat)) * self.PPD * ss)

    def _render(self):
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
                    if max(lons) < self.LON0 - 2 or min(lons) > self.LON1 + 2:
                        continue
                    if max(lats) < self.LAT0 - 2 or min(lats) > self.LAT1 + 2:
                        continue
                    pts = [self.bxy(lo, max(-80, min(80, la)), ss) for lo, la in ring]
                    md.polygon(pts, fill=0 if i else 255)
                    coast.append(pts)
        mask_s = mask.resize((self.w, self.h), Image.LANCZOS)
        # 海：沿岸ほど明るいグラデーション
        glow = mask_s.filter(ImageFilter.GaussianBlur(28))
        sea = Image.new("RGB", (self.w, self.h), PAL["sea"])
        sea_light = Image.new("RGB", (self.w, self.h), (205, 225, 222))
        sea = Image.composite(sea_light, sea, glow)
        land = Image.new("RGB", (self.w, self.h), PAL["land"])
        # 陸地にうっすら紙の質感
        rng = np.random.default_rng(1)
        noise = (rng.normal(0, 1, (self.h // 4, self.w // 4)) * 6).astype(np.float32)
        noise = np.array(Image.fromarray(noise, mode="F").resize((self.w, self.h), Image.BILINEAR))
        la = np.asarray(land).astype(np.float32) + noise[..., None]
        land = Image.fromarray(np.clip(la, 0, 255).astype(np.uint8))
        img = Image.composite(land, sea, mask_s)
        # 海岸線
        line = Image.new("L", (self.w * ss, self.h * ss), 0)
        ld = ImageDraw.Draw(line)
        for pts in coast:
            ld.line(pts + [pts[0]], fill=255, width=3 * ss)
        line = line.resize((self.w, self.h), Image.LANCZOS)
        img = Image.composite(Image.new("RGB", img.size, PAL["coast"]), img, line)
        # 経緯線
        d = ImageDraw.Draw(img)
        for lon in range(-10, 81, 5):
            x = self.bxy(lon, 0)[0]
            d.line([(x, 0), (x, self.h)], fill=(160, 150, 125), width=1)
        for lat in range(10, 58, 5):
            y = self.bxy(0, lat)[1]
            d.line([(0, y), (self.w, y)], fill=(160, 150, 125), width=1)
        return img

    def view(self, cam):
        """cam=(lon, lat, zoom[px/deg on screen]) → ステージ画像"""
        key = tuple(round(v, 4) for v in cam)
        if key == self._cache_key:
            return self._cache_img
        lon, lat, z = cam
        cx, cy = self.bxy(lon, lat)
        s = self.PPD / z
        box = (cx - W * s / 2, cy - STAGE_H * s / 2, cx + W * s / 2, cy + STAGE_H * s / 2)
        im = self.img.resize((W, STAGE_H), Image.BILINEAR, box=box, reducing_gap=2.0 if s > 2 else None)
        self._cache_key, self._cache_img = key, im
        return im

    def to_screen(self, cam, lon, lat):
        clon, clat, z = cam
        x = (lon - clon) * z + W / 2
        y = (merc(clat) - merc(lat)) * z + STAGE_H / 2 + STAGE_Y
        return x, y


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
        return 0.28 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)
    if kind == "whoosh":
        n = int(0.35 * SR)
        x = rng.normal(0, 1, n).astype(np.float32)
        k = np.hanning(41)
        x = np.convolve(x, k / k.sum(), "same")
        return 0.35 * x * np.sin(np.linspace(0, np.pi, n)) ** 2
    if kind == "stamp":
        n = int(0.25 * SR)
        t = np.arange(n) / SR
        thump = np.sin(2 * np.pi * 90 * t) * np.exp(-t * 22)
        noise = rng.normal(0, 1, n) * np.exp(-t * 60) * 0.3
        return 0.55 * (thump + noise)
    if kind == "ding":
        n = int(0.6 * SR)
        t = np.arange(n) / SR
        return 0.18 * (np.sin(2 * np.pi * 1320 * t) + 0.5 * np.sin(2 * np.pi * 1980 * t)) * np.exp(-t * 7)
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


def bgm(duration, bpm=84, seed=3):
    """D ドリアンのリラ風アルペジオ＋ドローン＋フレームドラム（自作・著作権フリー）"""
    n = int(duration * SR) + SR
    out = np.zeros(n, np.float32)
    beat = 60 / bpm
    midi = lambda m: 440 * 2 ** ((m - 69) / 12)
    chords = [[50, 57, 62, 65, 69], [48, 55, 60, 64, 67], [46, 53, 58, 62, 65], [48, 55, 60, 64, 67]]
    pattern = [0, 2, 3, 4, 3, 2, 1, 2]
    t = 0.0
    bar = 0
    rng = np.random.default_rng(seed)
    while t < duration + 1:
        ch = chords[bar % 4]
        for i, pi in enumerate(pattern):
            st = int((t + i * beat / 2) * SR)
            note = _pluck(midi(ch[pi] + 12), 1.6, 0.35, seed=bar * 8 + i)
            vel = 0.22 if i % 2 == 0 else 0.15
            e = min(n, st + len(note))
            if st < n:
                out[st:e] += vel * note[: e - st]
        # ベース音（ルート）
        st = int(t * SR)
        bass = _pluck(midi(ch[0] - 12), 3.2, 0.1, seed=999 + bar)
        e = min(n, st + len(bass))
        if st < n:
            out[st:e] += 0.35 * bass[: e - st]
        # フレームドラム 1・3拍
        for b in (0, 2):
            st = int((t + b * beat) * SR)
            dn = int(0.3 * SR)
            tt = np.arange(dn) / SR
            hit = (np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 14) * (0.35 if b == 0 else 0.22)
                   + rng.normal(0, 1, dn) * np.exp(-tt * 45) * 0.03)
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
        self.sub = sub                      # 字幕（【】で強調、/ で改行）
        self.tts = reading(tts or plain(sub))  # 読み上げ文
        self.audio = None
        self.t0 = self.t1 = 0.0


class Scene:
    def __init__(self, chunks, els=(), cam=None, cam_dur=1.1, stage="map", year=None,
                 dark=0.0, hold=0.0, pad=0.25):
        self.chunks = [c if isinstance(c, Chunk) else Chunk(*c) if isinstance(c, tuple) else Chunk(c)
                       for c in chunks]
        self.els = list(els)
        self.cam, self.cam_dur, self.stage, self.year = cam, cam_dur, stage, year
        self.dark, self.hold, self.pad = dark, hold, pad
        self.t0 = self.t1 = 0.0


class El:
    """演出要素。at: 秒 or 'c1'(そのシーンの1番目の文の開始)。span: 何シーン残すか"""
    sfx = "pop"

    def __init__(self, at=0.0, span=1, fade=0.25, dur=None):
        self.at, self.span, self.fade, self.dur = at, span, fade, dur
        self.t0 = self.t1 = 0.0

    def alpha(self, t):
        return clamp((t - self.t0) / 0.2) * clamp((self.t1 - t) / self.fade)

    def draw(self, fr, lt):
        raise NotImplementedError


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


# ---------------------------------------------------------------- video
class Video:
    def __init__(self, scenes, *, header, badge, badge_color, credit, voice, speed,
                 max_dur=59.0, timeline=None, pitch=0.0, intonation=1.15, gap=0.12):
        self.scenes = scenes
        self.header, self.badge, self.badge_color, self.credit = header, badge, badge_color, credit
        self.voice, self.speed, self.max_dur = voice, speed, max_dur
        self.pitch, self.intonation, self.gap = pitch, intonation, gap
        self.timeline = timeline
        self.map = MapBase()

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
            speed = round(speed * min(1.08, t / self.max_dur + 0.01), 3)
            print(f"  too long ({t:.1f}s) -> speed {speed}")
        self.speed_used, self.duration = speed, t
        # 要素のタイミング
        for i, sc in enumerate(self.scenes):
            for el in sc.els:
                at = el.at
                if isinstance(at, str):
                    ci, _, off = at[1:].partition("+")
                    at = sc.chunks[int(ci)].t0 - sc.t0 + float(off or 0)
                el.t0 = sc.t0 + at
                last = self.scenes[min(len(self.scenes) - 1, i + el.span - 1)]
                el.t1 = last.t1 if i + el.span - 1 < len(self.scenes) - 1 else self.duration + 1
                if el.dur is not None:
                    el.t1 = min(el.t1, el.t0 + el.dur)
        # 音声ミックス
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
        mix = voice * 0.95 + fx * 0.6 + music * 0.13 * duck
        fade = int(0.6 * SR)
        mix[-fade:] *= np.linspace(1, 0, fade)
        mix = np.clip(mix, -1, 1)
        return mix[: int(self.duration * SR)]

    # ---- 描画
    def scene_at(self, t):
        for sc in self.scenes:
            if t < sc.t1:
                return sc
        return self.scenes[-1]

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
                    # ズームは対数補間
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

    def draw_header(self, fr):
        d = ImageDraw.Draw(fr.canvas)
        d.rectangle([0, 0, W, HEADER_H], fill=PAL["ink"])
        f = font("black", 34)
        label = "世界史ずかん"
        lw = text_w(label, f)
        d.rounded_rectangle([48, 84, 48 + lw + 44, 140], radius=28, fill=PAL["gold"])
        d.text((70, 112), label, font=f, fill=PAL["ink"], anchor="lm")
        fb = font("black", 34)
        bw = text_w(self.badge, fb)
        d.rounded_rectangle([W - 48 - bw - 44, 84, W - 48, 140], radius=28, fill=self.badge_color)
        d.text((W - 48 - bw - 22, 112), self.badge, font=fb, fill=PAL["white"], anchor="lm")
        d.text((50, 172), self.header, font=font("black", 46), fill=PAL["white"], anchor="lt")
        d.text((W - 50, 76), self.credit, font=font("medium", 22), fill=(170, 175, 195), anchor="rb")

    def draw_stage(self, fr, sc):
        if sc.stage == "map":
            fr.cam = self.cam_at(fr.t)
            fr.canvas.paste(self.map.view(fr.cam), (0, STAGE_Y))
        else:
            fr.cam = self.cam_at(fr.t)
            d = ImageDraw.Draw(fr.canvas)
            d.rectangle([0, STAGE_Y, W, STAGE_Y + STAGE_H], fill=(236, 226, 200))
            for y in range(STAGE_Y + 30, STAGE_Y + STAGE_H, 60):
                d.line([(0, y), (W, y)], fill=(226, 214, 186), width=2)
        dk = self.dark_at(fr.t)
        if dk > 0.01:
            L = fr.layer()
            ImageDraw.Draw(L).rectangle([0, STAGE_Y, W, STAGE_Y + STAGE_H], fill=with_alpha(PAL["dark"], dk))
            fr.comp(L)

    def draw_frame_border(self, fr):
        d = ImageDraw.Draw(fr.canvas)
        d.rectangle([0, STAGE_Y - 10, W, STAGE_Y], fill=PAL["gold"])
        d.rectangle([0, STAGE_Y + STAGE_H, W, STAGE_Y + STAGE_H + 8], fill=PAL["gold"])

    def draw_subtitle(self, fr, sc):
        cur = None
        for c in sc.chunks:
            if c.t0 - 0.05 <= fr.t:
                cur = c
        if cur is None:
            return
        k = ease_back((fr.t - cur.t0 + 0.05) / 0.22)
        lines = cur.sub.split("/")
        f = font("black", 64)
        lh = 88
        L = fr.layer()
        d = ImageDraw.Draw(L)
        total_h = lh * len(lines)
        y = SUB_Y + (250 - total_h) / 2 + (1 - k) * 18
        a = int(255 * clamp(k))
        for line in lines:
            segs = parse_markup(line)
            lw = sum(text_w(s, f) for s, _ in segs)
            x = W / 2 - lw / 2
            for s, em in segs:
                col = PAL["red"] if em else PAL["ink"]
                d.text((x, y), s, font=f, fill=(*col, a), stroke_width=7,
                       stroke_fill=(255, 252, 245, a))
                x += text_w(s, f)
            y += lh
        fr.comp(L)

    def draw_timeline(self, fr):
        tl = self.timeline
        if not tl:
            return
        y0, x0, x1 = TL_Y, 70, W - 70
        y_min, y_max = tl["range"]
        X = lambda yr: x0 + (yr - y_min) / (y_max - y_min) * (x1 - x0)
        d = ImageDraw.Draw(fr.canvas)
        d.rounded_rectangle([x0, y0 + 30, x1, y0 + 52], radius=11, fill=(215, 203, 175))
        fs = font("bold", 24)
        for a, b, name, col, lab in tl["eras"]:
            d.rounded_rectangle([X(a), y0 + 30, X(b), y0 + 52], radius=11, fill=col)
        for a, b, name, col, lab in tl["eras"]:
            d.text((X(lab), y0 + 62), name, font=fs, fill=PAL["ink"], anchor="mt")
        for yr in tl["ticks"]:
            d.text((X(yr), y0 + 22), f"前{-yr}", font=font("medium", 22), fill=PAL["dim"], anchor="mb")
        # 現在地ポインタ
        yr_now, prev = None, None
        for sc in self.scenes:
            if fr.t < sc.t0:
                break
            if sc.year is not None:
                yr_now = sc.year if prev is None else lerp(prev, sc.year, ease_io((fr.t - sc.t0) / 0.9))
                prev = sc.year
        if yr_now is not None:
            x = X(yr_now)
            d.ellipse([x - 17, y0 + 24, x + 17, y0 + 58], fill=PAL["white"], outline=PAL["red"], width=7)
            d.ellipse([x - 6, y0 + 35, x + 6, y0 + 47], fill=PAL["red"])

    def render_frame(self, t):
        fr = Frame(self, t)
        fr.canvas = Image.new("RGBA", (W, H), (*PAL["bg"], 255))
        sc = self.scene_at(t)
        self.draw_stage(fr, sc)
        for s in self.scenes:
            for el in s.els:
                if el.t0 <= t < el.t1:
                    el.draw(fr, t - el.t0)
        self.draw_frame_border(fr)
        self.draw_header(fr)
        self.draw_subtitle(fr, sc)
        self.draw_timeline(fr)
        return fr.canvas.convert("RGB")

    def render(self, out_path, tts, preview_times=None):
        audio = self.build_audio(tts)
        print(f"  duration {self.duration:.2f}s, speed {self.speed_used}")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        if preview_times is not None:
            for pt in preview_times:
                self.render_frame(pt).save(out_path.replace(".mp4", f"_{pt:05.1f}.png"))
            return
        wav_path = out_path + ".wav"
        with wave.open(wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SR)
            wf.writeframes((audio * 32767).astype(np.int16).tobytes())
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        n_frames = int(self.duration * FPS)
        p = subprocess.Popen([
            ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
            "-r", str(FPS), "-i", "-", "-i", wav_path, "-c:v", "libx264", "-preset", "medium",
            "-crf", "19", "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart", "-shortest", out_path], stdin=subprocess.PIPE)
        for i in range(n_frames):
            p.stdin.write(self.render_frame(i / FPS).tobytes())
            if i % 150 == 0:
                print(f"  frame {i}/{n_frames}", flush=True)
        p.stdin.close()
        p.wait()
        os.remove(wav_path)
        return self.chapter_log()

    def chapter_log(self):
        rows = []
        for sc in self.scenes:
            for c in sc.chunks:
                rows.append(f"{c.t0:5.1f}-{c.t1:5.1f}s  {plain(c.sub)}")
        return "\n".join(rows)
