"""ヨーロッパ編 #10 スパルタクスの反乱（深掘り版）— 長編 #2 第3章を深掘り

usage: python3 episodes/europe_10_spartacus.py [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import AnswerCard, Card, Glow, Marker, Photo, QuizHook  # noqa: E402
from episodes.photos_rome import photo  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #10  スパルタクスの反乱"
NEXT = "次回：#11 ルビコン川"

CAPUA = (14.25, 41.08)
VESUVIUS = (14.43, 40.82)
CAM_CAMPANIA = (14.1, 41.1, 200)

TIMELINE = dict(
    range=(-76, -68),
    ticks=[-73, -71],
    eras=[(-73, -71, "スパルタクスの反乱", (215, 120, 100), -72)],
)


def ph(key, **kw):
    path, credit, _ = photo(key)
    return Photo(path, credit, **kw)


def deep():
    q = ["スパルタクスの反乱を", "【鎮圧】したのは？"]
    scenes = [
        Scene([
            ("/".join(q), "スパルタクスの反乱を、鎮圧したのは？"),
        ], stage="plain", pad=0.15, caption="コメントで予想してね！", els=[
            QuizHook(q, ["クラッスス", "カエサル", "スキピオ"], kicker="深掘り世界史"),
        ]),
        Scene([
            ("前73年、カプアの剣闘士養成所から/70人ほどが脱走します", "紀元前73年、カプアの剣闘士養成所から、70人ほどが脱走します"),
        ], year=-73, els=[
            ph("POLLICE", zoom=(1.0, 1.2), focus=(0.4, 0.55), caption="剣闘士の戦い（ジェローム画）"),
        ]),
        Scene([
            ("リーダーはトラキア出身の剣闘士/【スパルタクス】", "リーダーは、トラキア出身の剣闘士、スパルタクス"),
        ], year=-73, els=[
            ph("SPARTACUS2", zoom=(1.0, 1.25), focus=(0.35, 0.3), caption="スパルタクス像（ルーヴル美術館）"),
        ]),
        Scene([
            "ヴェスヴィオ山にこもると/各地の奴隷が次々に合流",
            ("その数はなんと数万人/ローマ軍を何度も打ち破りました", "その数はなんと数万人。ローマ軍を何度も打ち破りました"),
        ], cam=CAM_CAMPANIA, cam_dur=0.01, year=-72, els=[
            Marker(*CAPUA, "カプア", side="t"),
            Marker(*VESUVIUS, "ヴェスヴィオ山", side="r", at=0.6),
            Glow(14.35, 40.95, 0.5, 0.35, col=PAL["red"], at=1.0),
            Card(540, 840, 640, "反乱軍", ["数万人にふくれあがる"], col=PAL["red"], at="c1"),
        ]),
        Scene([
            ("背景には、大農場で酷使される/大量の【奴隷】がいました", "背景には、大農場で酷使される、大量の奴隷がいました"),
        ], stage="plain", year=-72, els=[
            Card(540, 300, 760, "ラティフンディア", ["奴隷を使う【大農場】"], col=PAL["gold"]),
            Card(540, 640, 760, None, ["奴隷の不満が爆発 → 【反乱】へ"], col=PAL["red"], at=0.8),
        ]),
        Scene([
            ("前71年、ある大富豪の軍に敗れ/スパルタクスは戦死", "紀元前71年、ある大富豪の軍に敗れ、スパルタクスは戦死"),
        ], year=-71, els=[
            ph("SPARTACUS_DEATH", zoom=(1.0, 1.25), focus=(0.6, 0.55), caption="スパルタクスの死（19世紀の版画）"),
        ]),
        Scene([
            ("捕まった6000人は/【アッピア街道】沿いで処刑されました", "捕まった6000人は、アッピア街道沿いで処刑されました"),
        ], year=-71, els=[
            ph("APPIA", zoom=(1.0, 1.2), focus=(0.6, 0.6), caption="今も残るアッピア街道"),
        ]),
        Scene([
            ("逃げた残党を倒した【ポンペイウス】も/手柄は自分だと主張します", "逃げた残党を倒したポンペイウスも、手柄は自分だと主張します"),
        ], year=-71, els=[
            ph("POMPEY", mode="fit", zoom=(1.0, 1.1), focus=(0.5, 0.4), caption="ポンペイウスの胸像"),
        ]),
        Scene([
            "答えは大富豪【クラッスス】！",
        ], hold=1.4, els=[
            ph("CRASSUS", mode="fit", zoom=(1.05, 1.15), focus=(0.5, 0.4), caption=None),
            AnswerCard("クラッスス", note="のちにカエサル・ポンペイウスと/第1回三頭政治を結ぶ",
                       next_text=NEXT, on_photo=True),
        ]),
    ]
    return Video(scenes, header=HEADER, badge="深掘り", badge_color=PAL["gold"], look="doc",
                 credit="VOICEVOX:春日部つむぎ", voice=8, speed=1.05, max_dur=59.0, timeline=TIMELINE)


if __name__ == "__main__":
    preview = "--preview" in sys.argv
    tts = TTS()
    v = deep()
    out = os.path.join(OUT, "europe_10_spartacus_deep.mp4")
    if preview:
        v.build_audio(tts)
        times = [0.0] + [sc.t0 + (sc.t1 - sc.t0) * 0.85 for sc in v.scenes]
        v.render(out, tts, preview_times=times)
    else:
        log = v.render(out, tts)
        with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
            fh.write(log + "\n")
        print(log)
