"""ヨーロッパ編 #12 ユリウス暦と今のカレンダー（深掘り版）— 長編 #2 第4章を深掘り

usage: python3 episodes/europe_12_julian_calendar.py [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import AnswerCard, Card, Marker, MonthGrid, Photo, QuizHook, Stamp  # noqa: E402
from episodes.photos_rome import photo  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #12  ユリウス暦"
NEXT = "次回：#13 カエサル暗殺"

ROME = (12.48, 41.89)
ALEXANDRIA = (29.92, 31.20)
CAM_EMED = (21.0, 37.0, 45)

TIMELINE = dict(
    range=(-50, -40),
    ticks=[-46, -45, -44],
    eras=[
        (-46, -45, "改革", (215, 120, 100), -46.5),
        (-45, -41, "ユリウス暦スタート", (225, 180, 70), -43),
    ],
)


def ph(key, **kw):
    path, credit, _ = photo(key)
    return Photo(path, credit, **kw)


def deep():
    q = ["7月（July）の名前の", "【由来】になった人物は？"]
    scenes = [
        Scene([
            ("/".join(q), "7月、ジュライの名前の、由来になった人物は？"),
        ], stage="plain", pad=0.15, caption="コメントで予想してね！", els=[
            QuizHook(q, ["アウグストゥス", "カエサル", "ネロ"], kicker="深掘り世界史"),
        ]),
        Scene([
            "古代ローマの暦は/1年が355日しかありませんでした",
            ("うるう月は政治家の都合で/入れたり入れなかったり", "ずれを直すうるう月は、政治家の都合で、入れたり入れなかったり"),
        ], year=-50, els=[
            ph("FASTI", zoom=(1.3, 1.6), focus=(0.45, 0.45), caption="ユリウス暦以前のローマの暦"),
            Card(540, 830, 600, None, ["1年＝【355日】"], dur=3.0),
        ]),
        Scene([
            "そのせいで暦と季節が/約3か月もずれていたのです",
        ], stage="plain", year=-48, els=[
            Card(540, 300, 760, "暦では「春」", ["でも実際は まだ冬…"], col=PAL["teal"]),
            Stamp(800, 620, "3か月ずれ", size=70, at=0.6),
        ]),
        Scene([
            ("そこで、ある権力者が/エジプトの【太陽暦】をお手本に改革", "そこで、ある権力者が、エジプトの太陽暦をお手本に、改革"),
        ], cam=CAM_EMED, cam_dur=0.01, year=-46, els=[
            Marker(*ALEXANDRIA, "エジプト", side="b", sub="太陽暦"),
            Marker(*ROME, "ローマ", side="t", at=0.6),
        ]),
        Scene([
            ("1年を【365日】にして/4年に1度【うるう年】を入れました", "1年を365日にして、4年に1度、うるう年を入れました"),
            ("これが前45年から使われた/【ユリウス暦】です", "これが、紀元前45年から使われた、ユリウス暦です"),
        ], stage="plain", year=-45, els=[
            Card(540, 240, 760, "新しい暦", ["1年＝【365日】"], col=PAL["gold"]),
            Card(540, 560, 760, None, ["4年に1度【うるう年】（＋1日）"], col=PAL["red"], at=1.2),
            Card(540, 830, 760, None, ["＝ ユリウス暦（前45年〜）"], col=PAL["ink"], at="c1"),
        ]),
        Scene([
            ("それでも少しずつずれ/1582年【グレゴリウス暦】へ", "それでも1年に11分ずつずれ、1582年、グレゴリウス暦に改良"),
            ("日本も明治6年から/この暦を使っています", "日本も、明治6年から、この暦を使っています"),
        ], year=-44, els=[
            ph("GREGORY", mode="fit", zoom=(1.0, 1.12), focus=(0.5, 0.3), caption="教皇グレゴリウス13世（1582年）"),
            Card(540, 840, 720, None, ["今のカレンダー＝【グレゴリウス暦】"], at="c1"),
        ]),
        Scene([
            "そして今の月の名前にも/2人のローマ人が隠れています",
        ], stage="plain", year=-44, els=[
            MonthGrid(marks={6: "？", 7: "？"}),
        ]),
        Scene([
            "答えは【カエサル】！",
            ("ユリウス→ジュライ/8月はアウグストゥス", "ユリウス・カエサルからジュライ。8月は、アウグストゥスです"),
        ], hold=1.2, els=[
            ph("CAESAR", mode="fit", zoom=(1.08, 1.16), focus=(0.5, 0.3), caption=None),
            AnswerCard("カエサル", note="Julius（ユリウス）→ July/August → アウグストゥス", next_text=NEXT, on_photo=True),
        ]),
    ]
    return Video(scenes, header=HEADER, badge="深掘り", badge_color=PAL["gold"], look="doc",
                 credit="VOICEVOX:春日部つむぎ", voice=8, speed=1.05, max_dur=59.0, timeline=TIMELINE)


if __name__ == "__main__":
    preview = "--preview" in sys.argv
    tts = TTS()
    v = deep()
    out = os.path.join(OUT, "europe_12_julian_calendar_deep.mp4")
    if preview:
        v.build_audio(tts)
        times = [0.0] + [sc.t0 + (sc.t1 - sc.t0) * 0.85 for sc in v.scenes]
        v.render(out, tts, preview_times=times)
    else:
        log = v.render(out, tts)
        with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
            fh.write(log + "\n")
        print(log)
