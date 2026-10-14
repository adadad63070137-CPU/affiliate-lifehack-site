"""ヨーロッパ編 #15 アウグストゥスと帝政の始まり（深掘り版）— 長編 #2 第5章を深掘り

usage: python3 episodes/europe_15_augustus.py [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import AnswerCard, Card, Glow, MapLabel, Marker, Photo, QuizHook  # noqa: E402
from episodes.photos_rome import photo  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #15  アウグストゥス"
NEXT = "次回：#16 五賢帝"

ROME = (12.48, 41.89)
CAM_EMPIRE = (15.0, 39.5, 24)

TIMELINE = dict(
    range=(-32, 20),
    ticks=[-27, 14],
    eras=[
        (-27, 14, "アウグストゥスの治世", (225, 180, 70), -6),
        (14, 20, "パクス・ロマーナ", (110, 175, 170), 17),
    ],
)


def ph(key, **kw):
    path, credit, _ = photo(key)
    return Photo(path, credit, **kw)


def deep():
    q = ["初代皇帝アウグストゥスが", "名乗った【肩書き】は？"]
    scenes = [
        Scene([
            ("/".join(q), "初代皇帝アウグストゥスが、名乗った肩書きは？"),
        ], stage="plain", pad=0.15, caption="コメントで予想してね！", els=[
            QuizHook(q, ["王（レックス）", "プリンケプス", "ファラオ"], kicker="深掘り世界史"),
        ]),
        Scene([
            ("内乱を終わらせた/【オクタウィアヌス】", "内乱を終わらせた、オクタウィアヌス"),
            ("前27年、元老院が贈った称号/【アウグストゥス】", "紀元前27年、元老院は彼に、アウグストゥスの称号を贈ります"),
        ], year=-27, els=[
            ph("AUGUSTUS", mode="fit", zoom=(1.0, 1.15), focus=(0.5, 0.25), caption="アウグストゥス像（プリマ・ポルタ）"),
            Card(540, 840, 640, "アウグストゥス", ["＝「尊厳者」"], col=PAL["gold"], at="c1"),
        ]),
        Scene([
            "でも彼は/【王】とは名乗りませんでした",
            ("王になると疑われたカエサルが/暗殺されたのを見ていたからです", "王になると疑われたカエサルが、暗殺されたのを、見ていたからです"),
        ], stage="plain", year=-27, els=[
            Card(540, 260, 760, None, ["「王」と名乗る ＝ 危険"], col=PAL["red"]),
            Card(540, 580, 760, "前44年", ["カエサル暗殺の教訓"], col=PAL["ink"], at="c1"),
        ]),
        Scene([
            ("共和政の形は残したまま/実際には権力をすべて握る", "共和政の形は残したまま、実際には、権力をすべて握る"),
            ("この政治を【元首政】といいます", "この政治を、元首政といいます"),
        ], stage="plain", year=-20, els=[
            Card(290, 300, 470, "見た目", ["元老院・共和政"], col=PAL["teal"]),
            Card(790, 300, 440, "実際", ["すべての権力"], col=PAL["red"], at=0.8),
            Card(540, 680, 760, None, ["＝【元首政】（帝政の始まり）"], col=PAL["gold"], at="c1"),
        ]),
        Scene([
            ("ここから約200年続く平和/【パクス・ロマーナ】", "ここから約200年、パクス・ロマーナと呼ばれる平和が続きます"),
        ], cam=CAM_EMPIRE, cam_dur=0.01, year=-10, els=[
            Glow(15.0, 39.0, 17.0, 7.5, col=PAL["red"]),
            MapLabel(23.0, 45.0, "ローマ帝国", size=60, col=PAL["ink"]),
            Marker(*ROME, "ローマ", side="b", at=0.5),
        ]),
        Scene([
            ("帝国中に道路や水道が整えられ/「すべての道はローマに通ず」", "帝国中に道路や水道が整えられ、すべての道は、ローマに通ず"),
        ], year=0, els=[
            ph("PONTDUGARD", zoom=(1.0, 1.2), focus=(0.5, 0.5), caption="ローマの水道橋（ポン・デュ・ガール）"),
        ]),
        Scene([
            ("彼は「レンガの町ローマを/【大理石】の町にした」と語りました", "彼は、レンガの町ローマを、大理石の町にした、と語りました"),
        ], year=5, els=[
            ph("FORUM", zoom=(1.0, 1.2), focus=(0.55, 0.5), caption="フォロ・ロマーノ（ローマの中心広場）"),
        ]),
        Scene([
            "そして最期の言葉は",
            ("「人生という芝居/うまく演じられたかな？」", "人生という芝居、うまく演じられたかな？"),
        ], year=14, els=[
            ph("AUGUSTUS", mode="fit", zoom=(1.1, 1.25), focus=(0.5, 0.2), caption="紀元14年に死去"),
        ]),
        Scene([
            "答えは【プリンケプス】！",
        ], hold=1.4, els=[
            ph("AUGUSTUS", mode="fit", zoom=(1.2, 1.3), focus=(0.5, 0.2), caption=None),
            AnswerCard("プリンケプス", note="「市民の中の第一人者」/元首政＝プリンキパトゥス", next_text=NEXT, on_photo=True),
        ]),
    ]
    return Video(scenes, header=HEADER, badge="深掘り", badge_color=PAL["gold"], look="doc",
                 credit="VOICEVOX:春日部つむぎ", voice=8, speed=1.05, max_dur=59.0, timeline=TIMELINE)


if __name__ == "__main__":
    preview = "--preview" in sys.argv
    tts = TTS()
    v = deep()
    out = os.path.join(OUT, "europe_15_augustus_deep.mp4")
    if preview:
        v.build_audio(tts)
        times = [0.0] + [sc.t0 + (sc.t1 - sc.t0) * 0.85 for sc in v.scenes]
        v.render(out, tts, preview_times=times)
    else:
        log = v.render(out, tts)
        with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
            fh.write(log + "\n")
        print(log)
