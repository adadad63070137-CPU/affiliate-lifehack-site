"""ヨーロッパ編 #4 ペロポネソス戦争とポリスの衰退（受験版・教養版）

usage: python3 episodes/europe_04_peloponnesian_war.py [exam|general|all] [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import (AnswerCard, Arrow, Card, Glow, Marker, QuizHook, Stamp, Step, Table, Temple)  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #4  ペロポネソス戦争"

ATHENS = (23.727, 37.984)
SPARTA = (22.430, 37.073)
DELOS = (25.270, 37.400)
THEBES = (23.320, 38.320)

CAM_BLOCS = (24.4, 38.2, 105)
CAM_ATHENS = (24.2, 37.8, 190)

TREASURY = [DELOS, (24.6, 37.5), (24.0, 37.8), ATHENS]
PERSIAN_GOLD = [(30.5, 37.0), (27.0, 36.6), (24.0, 36.7), (22.6, 37.0)]

TIMELINE = dict(
    range=(-485, -330),
    ticks=[-478, -431, -404, -371],
    eras=[
        (-478, -431, "デロス同盟", (110, 175, 170), -455),
        (-431, -404, "ペロポネソス戦争", (215, 120, 100), -417),
        (-404, -371, "スパルタ覇権", (95, 95, 105), -387),
        (-371, -338, "テーベ", (225, 180, 70), -352),
    ],
)

def blocs(**kw):
    return [Glow(25.3, 38.4, 2.4, 1.5, col=PAL["teal"], **kw), Glow(22.3, 37.35, 1.1, 0.8, col=PAL["red"], **kw)]


def exam():
    """受験版（高校生・30〜45秒）"""
    scenes = [
        Scene([
            ("アテネと戦うスパルタを/【支援】したのは？", "アテネと戦うスパルタを、支援したのは？"),
        ], stage='plain', pad=0.15, caption='コメントで予想してね！', els=[
            QuizHook(['アテネと戦うスパルタを', '【支援】したのは？'], ['ペルシア', 'マケドニア', 'ローマ'], kicker='テストに出る！'),
        ]),
        Scene([
            ("アテネの【デロス同盟】vs/スパルタの【ペロポネソス同盟】",
             "アテネのデロス同盟、対、スパルタのペロポネソス同盟"),
            "アテネが同盟の【資金】を/独占して反発を招く",
        ], cam=CAM_BLOCS, year=-454, els=[
            *blocs(span=2),
            Marker(*ATHENS, "アテネ", side="t", sub="デロス同盟", span=2),
            Marker(*SPARTA, "スパルタ", side="l", sub="ペロポネソス同盟", at=0.4, span=2),
            Arrow(TREASURY, col=PAL["gold"], width=12, label="同盟の金庫", label_at=0.1, at="c1"),
        ]),
        Scene([
            ("前431年に開戦/【海のアテネ】vs【陸のスパルタ】", "前431年に開戦。海のアテネ、対、陸のスパルタ"),
        ], cam=CAM_BLOCS, year=-431, els=[
            Card(540, 830, 700, None, ["アテネ＝【海軍】", "スパルタ＝【陸軍】"]),
        ]),
        Scene([
            "アテネで【疫病】が流行し/【ペリクレス】も死去",
            "【デマゴーゴス】が台頭し/【衆愚政治】へ",
        ], cam=CAM_ATHENS, year=-429, dark=0.45, els=[
            Stamp(540, 300, "疫病", col=PAL["gold"], size=90, at=0.3),
            Card(540, 780, 760, "デマゴーゴス", ["＝扇動政治家", "民主政が【衆愚政治】に"], at="c1"),
        ]),
        Scene([
            "【ペルシア】がスパルタを支援し",
            "前404年【アテネ降伏】",
        ], cam=CAM_BLOCS, year=-410, els=[
            Arrow(PERSIAN_GOLD, col=PAL["gold"], width=14, label="ペルシアの資金", label_at=0.7, label_dy=-60),
            Marker(*SPARTA, "スパルタ", side="l"),
            Marker(*ATHENS, "アテネ", side="l", col=PAL["ink"], at="c1"),
            Stamp(660, 400, "降伏", size=90, at="c1+0.3"),
        ]),
        Scene([("その後は【スパルタ】/続いて【テーベ】が覇権", "その後はスパルタ、続いてテーベが覇権")], stage="plain", year=-371, els=[
            Step(0, "前404", "スパルタ覇権", "勝ったスパルタが主導", col=PAL["red"], span=2),
            Step(1, "前371", "テーベ覇権", "スパルタを破る", col=PAL["gold"], at=1.0, span=2),
        ]),
        Scene(["ポリスは弱り/【傭兵】が増えていく"], stage="plain", year=-350, hold=0.3, els=[
            Step(2, "前4c", "ポリスの衰退", "市民が没落・【傭兵】増加", col=PAL["dim"]),
        ]),
        Scene([
            "まとめ！/ここ、テストに出ます",
        ], stage="plain", hold=2.2, els=[Table(
            ["アテネ側", "スパルタ側"],
            [
                ("同盟", "デロス同盟", "ペロポネソス同盟"),
                ("強み", "【海軍】", "【陸軍】"),
                ("転機", "【疫病】/ペリクレス死去", "【ペルシア】の支援"),
                ("政治", "【衆愚政治】へ", "寡頭政"),
                ("結果", "前404 降伏", "勝利→覇権"),
            ],
            row_dt=0.5, title="まとめ｜ペロポネソス戦争",
        )]),
        Scene([
            '答えは【ペルシア】！',
        ], stage='plain', hold=1.2, els=[
            AnswerCard('ペルシア', note='かつての宿敵がスパルタ側に', next_text='次回：#5 アレクサンドロス大王'),
        ]),
    ]
    return Video(scenes, header=HEADER, badge="受験版", badge_color=PAL["red"],
                 credit="VOICEVOX:四国めたん", voice=2, speed=1.26, max_dur=45.0, timeline=TIMELINE)


def general():
    """教養版（一般・60秒）"""
    scenes = [
        Scene([
            ("パルテノン神殿を/建てた【お金】はどこから？", "パルテノン神殿を建てたお金は、どこから？"),
        ], stage='plain', pad=0.15, caption='コメントで予想してね！', els=[
            QuizHook(['パルテノン神殿を', '建てた【お金】はどこから？']),
        ]),
        Scene([
            "ペルシアに備えて作った/【デロス同盟】",
            "その資金をアテネは/自分の町のために使います",
        ], cam=CAM_BLOCS, year=-454, els=[
            Marker(*DELOS, "デロス島", side="r"),
            Arrow(TREASURY, col=PAL["gold"], width=12, label="同盟の金庫", label_at=0.1, at="c1"),
        ]),
        Scene([
            "あの【パルテノン神殿】の建設にも/使われたといわれます",
            "今もアテネに残る/町のシンボルです",
        ], stage="plain", year=-447, els=[
            Temple(540, 480, 1.3),
            Card(540, 850, 700, None, ["パルテノン神殿（前447〜）"]),
        ]),
        Scene([
            "反発したスパルタ側と/ついに戦争が始まります",
        ], cam=CAM_BLOCS, year=-431, els=[
            *blocs(),
            Marker(*ATHENS, "アテネ", side="t"),
            Marker(*SPARTA, "スパルタ", side="l", at=0.3),
        ]),
        Scene([
            "ペリクレスは市民を/【城壁】の中に避難させます",
            "ところが人が密集した町で/恐ろしい【疫病】が発生",
            "指導者【ペリクレス】まで/亡くなってしまいます",
            "その後は人気取りの政治家が/議会を動かし",
            "民主政は【衆愚政治】に",
        ], cam=CAM_ATHENS, year=-429, dark=0.45, els=[
            Marker(*ATHENS, "アテネ", side="t", dur=3.0),
            Stamp(540, 300, "疫病", col=PAL["gold"], size=90, at="c1+0.3"),
            Card(540, 780, 700, None, ["【ペリクレス】死去（前429）"], at="c2", dur=2.8),
            Card(540, 780, 700, "デマゴーゴス", ["人気取りの扇動政治家"], at="c3"),
        ]),
        Scene([
            "最後にスパルタは/なんと宿敵【ペルシア】の支援を受け",
            "前404年、アテネは降伏",
        ], cam=CAM_BLOCS, year=-410, els=[
            Arrow(PERSIAN_GOLD, col=PAL["gold"], width=14, label="ペルシアの資金", label_at=0.7, label_dy=-60),
            Marker(*SPARTA, "スパルタ", side="l"),
            Marker(*ATHENS, "アテネ", side="l", col=PAL["ink"], at="c1"),
            Stamp(660, 400, "降伏", size=90, at="c1+0.3"),
        ]),
        Scene([
            '答えは【デロス同盟の資金】！',
        ], stage='plain', hold=1.2, els=[
            AnswerCard('デロス同盟の資金', note='同盟の金庫をアテネが使った/といわれています', next_text='次回：#5 アレクサンドロス大王'),
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
        out = os.path.join(OUT, f"europe_04_peloponnesian_war_{name}.mp4")
        if preview:
            v.build_audio(tts)
            times = [sc.t0 + (sc.t1 - sc.t0) * 0.85 for sc in v.scenes]
            v.render(out, tts, preview_times=times)
        else:
            log = v.render(out, tts)
            with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
                fh.write(log + "\n")
            print(log)
