"""ヨーロッパ編 #13 カエサル暗殺（深掘り版）— 長編 #2 第4章を深掘り

usage: python3 episodes/europe_13_caesar_assassination.py [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import AnswerCard, Card, Photo, QuizHook, Stamp  # noqa: E402
from episodes.photos_rome import photo  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #13  カエサル暗殺"
NEXT = "次回：#14 クレオパトラ"

TIMELINE = dict(
    range=(-47, -41),
    ticks=[-44, -42],
    eras=[
        (-46, -44, "カエサルの独裁", (110, 175, 170), -45),
        (-44, -42, "暗殺後の混乱", (215, 120, 100), -43),
    ],
)


def ph(key, **kw):
    path, credit, _ = photo(key)
    return Photo(path, credit, **kw)


def deep():
    q = ["「ブルートゥス、", "お前もか」の", "【出どころ】は？"]
    scenes = [
        Scene([
            ("/".join(q), "ブルートゥス、お前もか。このセリフの、出どころは？"),
        ], stage="plain", pad=0.15, caption="コメントで予想してね！", els=[
            QuizHook(q, ["古代ローマの記録", "シェイクスピアの劇", "カエサルの日記"], kicker="深掘り世界史"),
        ]),
        Scene([
            ("内戦に勝ったカエサルは/前44年【終身独裁官】に", "内戦に勝ったカエサルは、紀元前44年、終身独裁官に"),
        ], year=-44.6, els=[
            ph("CAESAR", mode="fit", zoom=(1.0, 1.12), focus=(0.5, 0.3), caption="カエサルの肖像彫刻"),
        ]),
        Scene([
            "でもローマ人は/【王】を何より嫌っていました",
            "「王になるつもりだ」と/疑われてしまいます",
        ], stage="plain", year=-44.5, els=[
            Card(540, 260, 760, "前509年", ["王を追放して【共和政】に"], col=PAL["teal"]),
            Card(540, 600, 760, "元老院の疑い", ["カエサルは【王】になる気だ…"], col=PAL["red"], at="c1"),
            Stamp(820, 820, "危険人物", size=64, at="c1+0.6"),
        ]),
        Scene([
            ("暗殺の仲間には/目をかけていた【ブルートゥス】も", "暗殺の仲間には、カエサルにかわいがられた、ブルートゥスも"),
        ], year=-44.3, els=[
            ph("BRUTUS", zoom=(1.25, 1.4), focus=(0.48, 0.32), caption="マルクス・ブルートゥス"),
        ]),
        Scene([
            ("前44年3月15日/元老院の会議場で暗殺", "紀元前44年、3月15日。元老院の会議場で暗殺"),
            "体には23か所の/刺し傷があったといいます",
        ], year=-44, els=[
            ph("DEATH", zoom=(1.0, 1.25), focus=(0.25, 0.75), caption="カエサルの死（ジェローム画）"),
            Stamp(780, 300, "3月15日", size=70, col=PAL["gold"], at="c1"),
        ]),
        Scene([
            "では最期の言葉は？/古代の歴史家によると…",
            ("「わが子よ、お前もか」/何も言わなかったという説も", "ギリシア語で、わが子よ、お前もか。何も言わなかった、という説も"),
        ], stage="plain", year=-44, els=[
            Card(540, 270, 780, "古代の記録（スエトニウス）", ["「わが子よ、お前もか」（ギリシア語）"], col=PAL["ink"]),
            Card(540, 620, 780, None, ["あるいは【何も言わなかった】"], col=PAL["teal"], at="c1+0.8"),
        ]),
        Scene([
            ("ブルートゥスは暗殺を記念する/【コイン】まで作りました", "ブルートゥスは、暗殺を記念するコインまで作りました"),
        ], year=-42, els=[
            ph("EIDMAR", mode="fit", zoom=(1.0, 1.1), focus=(0.75, 0.5), caption="「EID MAR」＝3月15日の銀貨"),
        ]),
        Scene([
            "答えは【シェイクスピアの劇】！",
        ], hold=1.4, els=[
            ph("SHAKESPEARE", mode="fit", zoom=(1.05, 1.15), focus=(0.5, 0.35), caption=None),
            AnswerCard("シェイクスピアの劇", note="『ジュリアス・シーザー』（1599年ごろ）/有名なセリフは劇の中の言葉",
                       next_text=NEXT, on_photo=True),
        ]),
    ]
    return Video(scenes, header=HEADER, badge="深掘り", badge_color=PAL["gold"], look="doc",
                 credit="VOICEVOX:春日部つむぎ", voice=8, speed=1.05, max_dur=59.0, timeline=TIMELINE)


if __name__ == "__main__":
    preview = "--preview" in sys.argv
    tts = TTS()
    v = deep()
    out = os.path.join(OUT, "europe_13_caesar_assassination_deep.mp4")
    if preview:
        v.build_audio(tts)
        times = [0.0] + [sc.t0 + (sc.t1 - sc.t0) * 0.85 for sc in v.scenes]
        v.render(out, tts, preview_times=times)
    else:
        log = v.render(out, tts)
        with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
            fh.write(log + "\n")
        print(log)
