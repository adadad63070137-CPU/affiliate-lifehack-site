"""ヨーロッパ編 #2 アテネとスパルタ（受験版・教養版）

usage: python3 episodes/europe_02_athens_sparta.py [exam|general|all] [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import (AnswerCard, Card, Marker, Ostracon, Phalanx, PyramidTier,  # noqa: E402
                             QuizHook, Stamp, Step, Table)

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #2  アテネとスパルタ"

ATHENS = (23.727, 37.984)
SPARTA = (22.430, 37.073)
CAM_GREECE = (22.9, 37.9, 150)
CAM_SPARTA = (22.6, 37.2, 230)
CAM_ATHENS = (23.6, 37.9, 230)

TIMELINE = dict(
    range=(-850, -450),
    ticks=[-800, -700, -600, -500],
    eras=[
        (-800, -621, "貴族政", (214, 190, 140), -710),
        (-621, -561, "改革期", (110, 175, 170), -591),
        (-561, -510, "僭主政", (95, 95, 105), -535),
        (-508, -450, "民主政", (225, 180, 70), -479),
    ],
)

SPARTA_TIERS = [
    ("スパルタ市民", "少数・全員が兵士", PAL["teal"]),
    ("ペリオイコイ", "周辺民・商工業", PAL["gold"]),
    ("ヘイロータイ", "隷属農民・多数", PAL["red"]),
]

STEPS = [
    ("前621", "ドラコン", "慣習法を【成文法】に"),
    ("前594", "ソロン", "【財産政治】・借金奴隷を禁止"),
    ("前561", "ペイシストラトス", "【僭主政】（独裁）"),
    ("前508", "クレイステネス", "【陶片追放】・10部族制"),
]


def tier(i, **kw):
    name, desc, col = SPARTA_TIERS[i]
    return PyramidTier(i, 3, name, desc, col, **kw)


def step(i, **kw):
    return Step(i, *STEPS[i], **kw)


def exam():
    """受験版（高校生・30〜45秒）"""
    scenes = [
        Scene([
            ("スパルタで農業をした/【隷属農民】を何という？", "スパルタで農業をした、隷属農民を何という？"),
        ], stage='plain', pad=0.15, caption='コメントで予想してね！', els=[
            QuizHook(['スパルタで農業をした', '【隷属農民】を何という？'], ['ペリオイコイ', 'ヘイロータイ', 'デマゴーゴス'], kicker='テストに出る！'),
        ]),
        Scene([
            "スパルタは【ドーリア人】/アテネは【イオニア人】のポリス",
        ], cam=CAM_GREECE, year=-750, els=[
            Marker(*SPARTA, "スパルタ", side="l", sub="ドーリア人"),
            Marker(*ATHENS, "アテネ", side="r", sub="イオニア人", at=0.5),
        ]),
        Scene([
            "征服した人々を/【ヘイロータイ】として支配",
            "商工業は/【ペリオイコイ】が担当",
            "少数の市民は/一生【兵士】",
            "反乱を防ぐ/【軍国主義】と鎖国",
        ], stage="plain", year=-650, els=[
            tier(2), tier(1, at="c1"), tier(0, at="c2"),
            Stamp(800, 880, "軍国主義", size=62, at="c3"),
        ]),
        Scene([
            "アテネでは【重装歩兵】の平民が/発言力をつけていく",
        ], stage="plain", year=-650, els=[Phalanx()]),
        Scene([("前621年【ドラコン】/法を文字にする", "前621年、ドラコン、法を文字にする")], stage="plain", year=-621,
              els=[step(0, span=4)]),
        Scene([("前594年【ソロン】/借金奴隷を禁止", "前594年、ソロン、借金奴隷を禁止")], stage="plain", year=-594,
              els=[step(1, span=3)]),
        Scene(["その後【ペイシストラトス】の/僭主政"], stage="plain", year=-561,
              els=[step(2, span=2)]),
        Scene([("前508年【クレイステネス】/【陶片追放】を導入", "前508年、クレイステネスが陶片追放を導入")], stage="plain", year=-508, hold=0.4,
              els=[step(3)]),
        Scene([
            "まとめ！/ここ、テストに出ます",
        ], stage="plain", hold=2.2, els=[Table(
            ["アテネ", "スパルタ"],
            [
                ("民族", "イオニア人", "ドーリア人"),
                ("政治", "【民主政】へ", "【軍国主義】"),
                ("支配", "市民と奴隷", "【ヘイロータイ】/を支配"),
                ("経済", "商工業・交易", "農業中心"),
                ("改革", "ソロン/クレイステネス", "リュクルゴスの制"),
            ],
            row_dt=0.5, title="まとめ｜アテネ vs スパルタ",
        )]),
        Scene([
            '答えは【ヘイロータイ】！',
        ], stage='plain', hold=1.2, els=[
            AnswerCard('ヘイロータイ', note='ペリオイコイ＝商工業の周辺民', next_text='次回：#3 ペルシア戦争'),
        ]),
    ]
    return Video(scenes, header=HEADER, badge="受験版", badge_color=PAL["red"],
                 credit="VOICEVOX:四国めたん", voice=2, speed=1.26, max_dur=45.0, timeline=TIMELINE)


def general():
    """教養版（一般・60秒）"""
    scenes = [
        Scene([
            ("スパルタの子どもは/何歳で【家族と離れた】？", "スパルタの子どもは、何歳で家族と離れた？"),
        ], stage='plain', pad=0.15, caption='コメントで予想してね！', els=[
            QuizHook(['スパルタの子どもは', '何歳で【家族と離れた】？']),
        ]),
        Scene([
            "舞台は古代ギリシアの/【スパルタ】",
            "隣の【アテネ】とは/まるで正反対の国です",
        ], cam=CAM_GREECE, year=-750, els=[
            Marker(*SPARTA, "スパルタ", side="l"),
            Marker(*ATHENS, "アテネ", side="r", at="c1"),
        ]),
        Scene([
            "スパルタでは/征服した大勢の人々を",
            "【ヘイロータイ】として/働かせました",
            "反乱が怖いので/少数の市民は一生【兵士】",
        ], stage="plain", year=-650, els=[
            tier(2), tier(1, at="c1"), tier(0, at="c2"),
        ]),
        Scene([
            "食事もみんなで【共同】/ぜいたくは禁止",
            "厳しい教育を表す/「【スパルタ教育】」",
            "その語源がこの国です",
        ], cam=CAM_SPARTA, year=-650, els=[
            Marker(*SPARTA, "スパルタ", side="t"),
            Card(540, 800, 640, "市民の暮らし", ["【共同食事】・質素が美徳"], col=PAL["teal"], dur=2.8),
            Card(540, 800, 640, "スパルタ教育", ["語源は【この国】！"], col=PAL["red"], at="c2"),
        ]),
        Scene([
            "一方アテネは/【海】と【交易】の町",
            "盾を並べて戦う/【重装歩兵】の平民たちが",
            "国を守る代わりに/発言力をつけていきます",
        ], cam=CAM_ATHENS, year=-600, els=[
            Marker(*ATHENS, "アテネ", side="t", dur=4.5),
            Phalanx(at="c1"),
        ]),
        Scene([
            "そしてついに/【民主政】の仕組みが誕生",
            "独裁者になりそうな人の名を/【陶片】に書いて追放",
            "これが【陶片追放】です",
            "名前入りの陶片は/今も実際に見つかっています",
        ], stage="plain", year=-508, els=[
            Card(540, 170, 700, None, ["前508年　クレイステネスの改革"]),
            Ostracon(540, 560, at="c1"),
            Stamp(800, 420, "追放！", at="c2+0.3"),
        ]),
        Scene([
            '答えは【7歳】！',
        ], stage='plain', hold=1.2, els=[
            AnswerCard('7歳', note='軍の共同生活で鍛えられた', next_text='次回：#3 ペルシア戦争'),
        ]),
    ]
    return Video(scenes, header=HEADER, badge="教養版", badge_color=PAL["teal"],
                 credit="VOICEVOX:春日部つむぎ", voice=8, speed=1.02, max_dur=59.0, timeline=TIMELINE)


VERSIONS = {"exam": exam, "general": general}

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    preview = "--preview" in sys.argv
    tts = TTS()
    for name, make in VERSIONS.items():
        if which not in ("all", name):
            continue
        print(f"[{name}]")
        v = make()
        out = os.path.join(OUT, f"europe_02_athens_sparta_{name}.mp4")
        if preview:
            v.build_audio(tts)
            times = [sc.t0 + (sc.t1 - sc.t0) * 0.85 for sc in v.scenes]
            v.render(out, tts, preview_times=times)
        else:
            log = v.render(out, tts)
            with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
                fh.write(log + "\n")
            print(log)
