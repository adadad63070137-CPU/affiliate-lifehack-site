"""ヨーロッパ編 #8 グラックス兄弟（深掘り版）— 長編 #2 第2章を深掘り

usage: python3 episodes/europe_08_gracchi.py [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import AnswerCard, Card, Photo, QuizHook, Stamp  # noqa: E402
from episodes.photos_rome import photo  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #8  グラックス兄弟"
NEXT = "次回：#9 マリウスとスラ"

TIMELINE = dict(
    range=(-150, -105),
    ticks=[-146, -133, -123],
    eras=[
        (-146, -133, "格差の拡大", (95, 95, 105), -140),
        (-133, -121, "兄弟の改革", (215, 120, 100), -127),
        (-121, -105, "内乱の1世紀へ", (225, 180, 70), -112),
    ],
)


def ph(key, **kw):
    path, credit, name = photo(key)
    kw.setdefault("caption", name.split("『")[-1].rstrip("』") if "『" in name else name)
    return Photo(path, credit, **kw)


def deep():
    q = ["グラックス兄弟の母が", "「これが私の【宝石】」と", "指さしたのは？"]
    scenes = [
        Scene([
            ("/".join(q), "グラックス兄弟の母が、これが私の宝石、と指さしたのは？"),
        ], stage="plain", pad=0.15, caption="コメントで予想してね！", els=[
            QuizHook(q, ["金の指輪", "ローマの地図", "2人の息子"], kicker="深掘り世界史"),
        ]),
        Scene([
            ("ポエニ戦争に勝ったローマ/でも国の中はボロボロでした", "ポエニ戦争に勝ったローマ。でも国の中はボロボロでした"),
            ("属州から【安い穀物】/戦争で【奴隷】が大量に流れ込み", "属州から安い穀物、戦争で奴隷が、大量に流れ込み"),
        ], stage="plain", year=-146, els=[
            Card(540, 230, 760, "地中海の覇者に", ["でも社会はボロボロ"], col=PAL["ink"]),
            Card(290, 600, 470, "属州から", ["【安い穀物】"], col=PAL["gold"], at="c1"),
            Card(790, 600, 440, "戦争で", ["大量の【奴隷】"], col=PAL["red"], at="c1+0.4"),
        ]),
        Scene([
            "金持ちは奴隷を使う大農場/【ラティフンディア】を広げ",
            "兵士だった【中小農民】は/土地を失いました",
        ], stage="plain", year=-140, els=[
            Card(540, 260, 760, "ラティフンディア", ["奴隷を使う【大農場】"], col=PAL["gold"]),
            Card(540, 620, 760, "中小農民（重装歩兵）", ["土地を失い【無産市民】に"], col=PAL["red"], at="c1"),
            Stamp(820, 820, "没落", size=70, at="c1+0.6"),
        ]),
        Scene([
            ("ローマにあふれた市民に/有力者は【パンとサーカス】", "ローマにあふれた市民に、有力者は、パンとサーカス"),
            "食べ物と見せ物で/人気を集めたのです",
        ], year=-135, els=[
            ph("POLLICE", zoom=(1.0, 1.18), focus=(0.55, 0.45), caption="剣闘士の見せ物（ジェローム画）"),
        ]),
        Scene([
            ("前133年、立ち上がったのが/護民官【ティベリウス・グラックス】", "紀元前133年、立ち上がったのが、護民官ティベリウス・グラックス"),
            "金持ちの土地を制限し/貧しい市民に分けようとします",
            "しかし元老院の反発で/【殺されて】しまいました",
        ], year=-133, els=[
            ph("GRACCHUS", zoom=(1.0, 1.3), focus=(0.75, 0.3), caption="護民官ティベリウス・グラックス"),
            Card(540, 820, 700, None, ["大土地所有を【制限】→ 土地を分配"], at="c1", dur=3.2),
            Stamp(780, 700, "暗殺", size=80, at="c2+0.4"),
        ]),
        Scene([
            ("弟【ガイウス】も/穀物を安く配る改革を進めますが", "弟ガイウスも、穀物を安く配る改革を進めますが"),
            "やはり反対派に追いつめられ/命を落としました",
            "ここからローマは/【内乱の1世紀】へ",
        ], stage="plain", year=-121, els=[
            Card(540, 250, 760, "弟ガイウス・グラックス", ["前123年〜 穀物を安く配給"], col=PAL["teal"]),
            Stamp(780, 470, "死去", size=70, at="c1+0.3"),
            Card(540, 730, 760, None, ["→ 将軍たちが争う【内乱の1世紀】へ"], col=PAL["red"], at="c2"),
        ]),
        Scene([
            "答えは【2人の息子】！",
            ("宝石を自慢する客に/母コルネリアはこう答えたそうです", "宝石を自慢する客に、母コルネリアは、こう答えたそうです"),
        ], hold=1.4, els=[
            ph("CORNELIA", zoom=(1.0, 1.35), focus=(0.18, 0.62), caption=None),
            AnswerCard("2人の息子", note="「これが私の宝石です」/（グラックス兄弟の母コルネリア）",
                       next_text=NEXT, on_photo=True),
        ]),
    ]
    return Video(scenes, header=HEADER, badge="深掘り", badge_color=PAL["gold"], look="doc",
                 credit="VOICEVOX:春日部つむぎ", voice=8, speed=1.05, max_dur=59.0, timeline=TIMELINE)


if __name__ == "__main__":
    preview = "--preview" in sys.argv
    tts = TTS()
    v = deep()
    out = os.path.join(OUT, "europe_08_gracchi_deep.mp4")
    if preview:
        v.build_audio(tts)
        times = [0.0] + [sc.t0 + (sc.t1 - sc.t0) * 0.85 for sc in v.scenes]
        v.render(out, tts, preview_times=times)
    else:
        log = v.render(out, tts)
        with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
            fh.write(log + "\n")
        print(log)
