"""ヨーロッパ編 #9 マリウスとスラ（深掘り版）— 長編 #2 第3章を深掘り

usage: python3 episodes/europe_09_marius_sulla.py [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import AnswerCard, Arrow, Card, Marker, Photo, QuizHook, Stamp  # noqa: E402
from episodes.photos_rome import photo  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #9  マリウスとスラ"
NEXT = "次回：#10 スパルタクスの反乱"

ROME = (12.48, 41.89)
NOLA = (14.53, 40.93)
CAM_ITALY = (12.9, 41.6, 120)

TIMELINE = dict(
    range=(-114, -74),
    ticks=[-107, -88, -82],
    eras=[
        (-107, -88, "マリウスの改革", (110, 175, 170), -98),
        (-88, -82, "内戦", (215, 120, 100), -85),
        (-82, -79, "スラの独裁", (95, 95, 105), -78),
    ],
)


def deep():
    q = ["マリウスの改革で", "兵士が【忠誠】を誓った相手は？"]
    scenes = [
        Scene([
            ("/".join(q), "マリウスの改革で、兵士が忠誠を誓った相手は？"),
        ], stage="plain", pad=0.15, caption="コメントで予想してね！", els=[
            QuizHook(q, ["ローマの国", "元老院", "将軍"], kicker="深掘り世界史"),
        ]),
        Scene([
            "グラックス兄弟の死後/ローマは2つの派に分かれます",
            ("元老院を守る【閥族派】と/民衆が支える【平民派】", "元老院を守る閥族派と、民衆が支える平民派"),
        ], stage="plain", year=-110, els=[
            Card(540, 220, 760, "内乱の1世紀", ["ローマが2つに分裂"], col=PAL["ink"]),
            Card(290, 600, 470, "閥族派", ["元老院・有力者"], col=PAL["teal"], at="c1"),
            Card(790, 600, 440, "平民派", ["民衆の支持"], col=PAL["red"], at="c1+0.4"),
        ]),
        Scene([
            ("平民派の将軍【マリウス】は/軍の仕組みを変えます", "平民派の将軍マリウスは、軍の仕組みを変えます"),
            ("土地のない【無産市民】に/給料を払って兵士にしたのです", "土地のない無産市民に、給料を払って、兵士にしたのです"),
        ], year=-107, els=[
            Photo(*photo("MARIUS")[:2], mode="fit", zoom=(1.0, 1.1), focus=(0.5, 0.35),
                  caption="マリウスとされる胸像"),
            Card(540, 830, 700, None, ["無産市民 ＋ 給料 ＝ 【志願兵】"], at="c1"),
        ]),
        Scene([
            "兵士は退役すると/将軍から【土地】をもらえました",
            "だから兵士は国より/将軍に従う【私兵】になったのです",
        ], stage="plain", year=-100, els=[
            Card(540, 230, 760, "将軍 → 兵士", ["給料 ＋ 退役後の【土地】"], col=PAL["gold"]),
            Card(540, 560, 760, "兵士 → 将軍", ["国より将軍に【忠誠】"], col=PAL["red"], at="c1"),
            Stamp(800, 800, "私兵化", size=72, at="c1+0.6"),
        ]),
        Scene([
            ("これに対抗したのが/閥族派の【スラ】", "これに対抗したのが、閥族派のスラ"),
        ], year=-88, els=[
            Photo(*photo("SULLA")[:2], mode="fit", zoom=(1.0, 1.12), focus=(0.5, 0.35),
                  caption="スラとされる胸像"),
        ]),
        Scene([
            ("前88年、スラは自分の軍を率いて/【ローマに進軍】", "紀元前88年、スラは自分の軍を率いて、ローマに進軍"),
            "ローマの将軍が/ローマを攻めた初めての事件でした",
        ], cam=CAM_ITALY, cam_dur=0.01, year=-88, els=[
            Marker(*ROME, "ローマ", side="l"),
            Arrow([NOLA, (13.8, 41.3), (12.9, 41.75)], width=16, draw_dur=1.6, label="スラの軍", label_at=0.2),
            Stamp(760, 300, "前代未聞", size=64, at="c1+0.3"),
        ]),
        Scene([
            ("反対派の名前を張り出し/次々に【処刑】していきます", "反対派の名前を張り出し、次々に処刑していきます"),
            ("軍を持つ者が政治を動かす時代/その先に【カエサル】が現れます", "軍を持つ者が政治を動かす時代。その先にカエサルが現れます"),
        ], stage="plain", year=-82, els=[
            Card(540, 250, 760, "スラの独裁（前82〜）", ["処罰者名簿を張り出し【粛清】"], col=PAL["ink"]),
            Card(540, 620, 760, None, ["軍を持つ者が勝つ → 【カエサル】へ"], col=PAL["red"], at="c1"),
        ]),
        Scene([
            "答えは【将軍】！",
        ], hold=1.4, els=[
            Photo(*photo("MARIUS")[:2], mode="fit", zoom=(1.12, 1.2), focus=(0.5, 0.35)),
            AnswerCard("将軍", note="給料と土地をくれる将軍に忠誠/＝兵士の私兵化", next_text=NEXT, on_photo=True),
        ]),
    ]
    return Video(scenes, header=HEADER, badge="深掘り", badge_color=PAL["gold"], look="doc",
                 credit="VOICEVOX:春日部つむぎ", voice=8, speed=1.05, max_dur=59.0, timeline=TIMELINE)


if __name__ == "__main__":
    preview = "--preview" in sys.argv
    tts = TTS()
    v = deep()
    out = os.path.join(OUT, "europe_09_marius_sulla_deep.mp4")
    if preview:
        v.build_audio(tts)
        times = [0.0] + [sc.t0 + (sc.t1 - sc.t0) * 0.85 for sc in v.scenes]
        v.render(out, tts, preview_times=times)
    else:
        log = v.render(out, tts)
        with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
            fh.write(log + "\n")
        print(log)
