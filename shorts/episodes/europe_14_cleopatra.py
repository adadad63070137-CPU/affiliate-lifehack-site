"""ヨーロッパ編 #14 クレオパトラとアクティウムの海戦（深掘り版）— 長編 #2 第5章を深掘り

usage: python3 episodes/europe_14_cleopatra.py [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import AnswerCard, Arrow, Card, Glow, Marker, Photo, QuizHook, Stamp  # noqa: E402
from episodes.photos_rome import photo  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #14  クレオパトラ"
NEXT = "次回：#15 アウグストゥス"

ROME = (12.48, 41.89)
ACTIUM = (20.75, 38.95)
ALEXANDRIA = (29.92, 31.20)
CAM_ACTIUM = (20.5, 38.8, 150)
CAM_EMED = (24.0, 35.5, 40)

TIMELINE = dict(
    range=(-50, -27),
    ticks=[-48, -43, -31],
    eras=[
        (-48, -44, "カエサルと同盟", (110, 175, 170), -46),
        (-43, -31, "第2回三頭政治", (95, 95, 105), -37),
        (-31, -30, "滅亡", (215, 120, 100), -29),
    ],
)


def ph(key, **kw):
    path, credit, _ = photo(key)
    return Photo(path, credit, **kw)


def deep():
    q = ["クレオパトラの王家は", "【何系】？"]
    scenes = [
        Scene([
            ("/".join(q), "クレオパトラの王家は、何系？"),
        ], stage="plain", pad=0.15, caption="コメントで予想してね！", els=[
            QuizHook(q, ["エジプト人", "ギリシア系", "ローマ人"], kicker="深掘り世界史"),
        ]),
        Scene([
            "エジプトの女王/【クレオパトラ】",
            ("実力者カエサルと手を結び/息子も生まれました", "ローマの実力者カエサルと手を結び、息子も生まれました"),
        ], year=-48, els=[
            ph("ANTCLEO", zoom=(1.0, 1.35), focus=(0.72, 0.45), caption="クレオパトラ（アルマ＝タデマ画）"),
        ]),
        Scene([
            ("カエサル暗殺後は/【アントニウス】と結びます", "カエサル暗殺後は、部下だったアントニウスと結びます"),
        ], year=-41, els=[
            ph("ANTCLEO", zoom=(1.2, 1.45), focus=(0.4, 0.28), caption="クレオパトラを迎えるアントニウス"),
        ]),
        Scene([
            ("対抗したのはカエサルの養子/【オクタウィアヌス】", "対抗したのは、カエサルの養子、オクタウィアヌス"),
        ], stage="plain", year=-33, els=[
            Card(290, 300, 470, "東", ["アントニウス", "＋クレオパトラ"], col=PAL["red"]),
            Card(790, 300, 440, "西（ローマ）", ["オクタウィアヌス"], col=PAL["teal"], at=0.6),
            Stamp(540, 650, "対決", size=90, at=1.2),
        ]),
        Scene([
            ("前31年、ギリシア西岸の/【アクティウムの海戦】", "紀元前31年、ギリシア西岸の、アクティウムの海戦"),
        ], cam=CAM_ACTIUM, cam_dur=0.01, year=-31, els=[
            Marker(*ACTIUM, "アクティウム", side="r", sub="前31"),
            Arrow([(19.4, 38.4), (20.3, 38.85)], col=PAL["teal"], width=14, draw_dur=1.0),
        ]),
        Scene([
            "オクタウィアヌスが大勝し/2人はエジプトへ逃げました",
        ], year=-31, els=[
            ph("ACTIUM", zoom=(1.0, 1.25), focus=(0.4, 0.55), caption="アクティウムの海戦（17世紀の絵）"),
        ]),
        Scene([
            "翌年クレオパトラは/自ら命を絶ちます",
            ("こうして【プトレマイオス朝】は滅亡", "こうして、プトレマイオス朝は滅亡"),
            ("大王から続いた/【ヘレニズム時代】も終わりました", "アレクサンドロス大王から続いた、ヘレニズム時代も、幕を閉じました"),
        ], cam=CAM_EMED, cam_dur=0.01, year=-30, els=[
            Marker(*ALEXANDRIA, "アレクサンドリア", side="b"),
            Stamp(300, 760, "滅亡", size=80, at="c1"),
            Glow(30.0, 28.0, 4.5, 4.0, col=PAL["gold"], at="c2"),
            Card(540, 180, 760, None, ["ヘレニズム時代の終わり（前30）"], at="c2"),
        ]),
        Scene([
            "答えは【ギリシア系】！",
        ], hold=1.4, els=[
            ph("ANTCLEO", zoom=(1.25, 1.35), focus=(0.72, 0.45), caption=None),
            AnswerCard("ギリシア系", note="大王の部下プトレマイオスの子孫/王家で初めてエジプト語を話したとも",
                       next_text=NEXT, on_photo=True),
        ]),
    ]
    return Video(scenes, header=HEADER, badge="深掘り", badge_color=PAL["gold"], look="doc",
                 credit="VOICEVOX:春日部つむぎ", voice=8, speed=1.05, max_dur=59.0, timeline=TIMELINE)


if __name__ == "__main__":
    preview = "--preview" in sys.argv
    tts = TTS()
    v = deep()
    out = os.path.join(OUT, "europe_14_cleopatra_deep.mp4")
    if preview:
        v.build_audio(tts)
        times = [0.0] + [sc.t0 + (sc.t1 - sc.t0) * 0.85 for sc in v.scenes]
        v.render(out, tts, preview_times=times)
    else:
        log = v.render(out, tts)
        with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
            fh.write(log + "\n")
        print(log)
