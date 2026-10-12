"""ヨーロッパ編 #11 ルビコン川（深掘り版）— 長編 #2 第4章を深掘り

usage: python3 episodes/europe_11_rubicon.py [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import AnswerCard, Arrow, Card, Glow, MapLabel, Marker, Photo, QuizHook, Stamp  # noqa: E402
from episodes.photos_rome import photo  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #11  ルビコン川"
NEXT = "次回：#12 ユリウス暦"

ROME = (12.48, 41.89)
RUBICON = (12.40, 44.10)
RAVENNA = (12.20, 44.42)
RIMINI = (12.57, 44.06)
CAM_GAUL = (5.5, 45.5, 60)
CAM_RUBICON = (12.2, 43.6, 170)

TIMELINE = dict(
    range=(-62, -45),
    ticks=[-60, -53, -49],
    eras=[
        (-60, -53, "第1回三頭政治", (110, 175, 170), -56.5),
        (-53, -49, "対立", (95, 95, 105), -51),
        (-49, -46, "内戦", (215, 120, 100), -47.5),
    ],
)


def ph(key, **kw):
    path, credit, _ = photo(key)
    return Photo(path, credit, **kw)


def deep():
    q = ["ルビコン川を軍と渡ることは", "何を【意味】した？"]
    scenes = [
        Scene([
            ("/".join(q), "ルビコン川を、軍と渡ることは、何を意味した？"),
        ], stage="plain", pad=0.15, caption="コメントで予想してね！", els=[
            QuizHook(q, ["国への反逆", "戦争の勝利", "皇帝の即位"], kicker="深掘り世界史"),
        ]),
        Scene([
            ("前60年【カエサル】は/2人の実力者と手を組みます", "紀元前60年、カエサルは、クラッスス、ポンペイウスと手を組みます"),
        ], year=-60, els=[
            ph("CAESAR", mode="fit", zoom=(1.0, 1.12), focus=(0.5, 0.3), caption="カエサルの肖像彫刻"),
            Card(540, 840, 640, None, ["【第1回三頭政治】"], at=1.0),
        ]),
        Scene([
            ("そして今のフランス/【ガリア】を8年かけて征服", "そして今のフランス、ガリアを、8年かけて征服"),
        ], cam=CAM_GAUL, cam_dur=0.01, year=-55, els=[
            Glow(2.5, 46.8, 4.8, 3.2, col=PAL["red"]),
            MapLabel(2.5, 47.0, "ガリア", size=60, col=PAL["ink"]),
            Marker(*ROME, "ローマ", side="l", at=0.4),
        ]),
        Scene([
            ("ガリアの英雄/ウェルキンゲトリクスも降伏", "ガリアの英雄ウェルキンゲトリクスも、最後は武器を捨てて降伏"),
        ], year=-52, els=[
            ph("VERCINGETORIX", zoom=(1.0, 1.25), focus=(0.4, 0.45), caption="降伏するウェルキンゲトリクス（ロワイエ画）"),
        ]),
        Scene([
            ("カエサルを恐れた元老院は/「軍を捨てて帰れ」と命令", "強くなったカエサルを恐れた元老院は、軍を捨てて帰れ、と命令"),
        ], stage="plain", year=-50, els=[
            Card(540, 260, 760, "元老院・ポンペイウス", ["カエサルを警戒"], col=PAL["teal"]),
            Card(540, 620, 760, "命令", ["「軍を解散してローマへ戻れ」"], col=PAL["ink"], at=0.8),
        ]),
        Scene([
            "ルビコン川は/属州とイタリア本国の境目",
            "軍を連れて越えるのは/法律で禁止されていました",
        ], cam=CAM_RUBICON, cam_dur=0.01, year=-49, els=[
            Marker(*RUBICON, "ルビコン川", side="r"),
            MapLabel(11.2, 44.9, "属州（ガリア）", size=40, col=PAL["ink"]),
            MapLabel(12.3, 43.0, "イタリア本国", size=44, col=PAL["ink"]),
            Arrow([RAVENNA, (12.32, 44.24), RIMINI], width=14, draw_dur=1.4, at="c1"),
            Stamp(780, 850, "越えたら反逆", size=56, at="c1+0.6"),
        ]),
        Scene([
            ("前49年、カエサルは/「【賽は投げられた】」", "紀元前49年、カエサルは、賽は投げられた"),
            "そう言って/軍とともに川を渡りました",
        ], year=-49, els=[
            ph("RUBICON", zoom=(1.0, 1.25), focus=(0.6, 0.35), caption="ルビコン川を渡るカエサル（19世紀の挿絵）"),
        ]),
        Scene([
            "内戦でポンペイウスを破り/カエサルはローマの頂点へ",
        ], year=-48, els=[
            ph("POMPEY", mode="fit", zoom=(1.0, 1.1), focus=(0.5, 0.4), caption="敗れたポンペイウス"),
            Stamp(800, 760, "敗北", size=70, at=0.6),
        ]),
        Scene([
            "答えは【国への反逆】！",
        ], hold=1.4, els=[
            ph("RUBICON", zoom=(1.2, 1.3), focus=(0.6, 0.4), caption=None),
            AnswerCard("国への反逆", note="今も「ルビコン川を渡る」は/後戻りできない決断のたとえ",
                       next_text=NEXT, on_photo=True),
        ]),
    ]
    return Video(scenes, header=HEADER, badge="深掘り", badge_color=PAL["gold"], look="doc",
                 credit="VOICEVOX:春日部つむぎ", voice=8, speed=1.05, max_dur=59.0, timeline=TIMELINE)


if __name__ == "__main__":
    preview = "--preview" in sys.argv
    tts = TTS()
    v = deep()
    out = os.path.join(OUT, "europe_11_rubicon_deep.mp4")
    if preview:
        v.build_audio(tts)
        times = [0.0] + [sc.t0 + (sc.t1 - sc.t0) * 0.85 for sc in v.scenes]
        v.render(out, tts, preview_times=times)
    else:
        log = v.render(out, tts)
        with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
            fh.write(log + "\n")
        print(log)
