"""ヨーロッパ編 #6 ローマの誕生と共和政（受験版・教養版）

usage: python3 episodes/europe_06_rome.py [exam|general|all] [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import (AnswerCard, Card, Glow, MapLabel, Marker, Phalanx,  # noqa: E402
                             QuizHook, Stamp, Step, Table)

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #6  ローマの誕生"
NEXT = "次回：#7 ポエニ戦争"

ROME = (12.48, 41.89)
CAM_ITALY = (12.8, 41.8, 95)
CAM_ROME = (12.3, 42.4, 190)

TIMELINE = dict(
    range=(-770, -255),
    ticks=[-753, -509, -367, -287],
    eras=[
        (-753, -509, "王政", (214, 190, 140), -630),
        (-509, -287, "共和政・身分闘争", (215, 120, 100), -398),
        (-287, -272, "半島統一", (225, 180, 70), -268),
    ],
)

STEPS = [
    ("前494", "護民官・平民会", "平民を守る役職と集会", 50),
    ("前450", "十二表法", "ローマ最初の【成文法】", 50),
    ("前367", "リキニウス・セクスティウス法", "コンスル1人を【平民】から", 34),
    ("前287", "ホルテンシウス法", "平民会の決議が【国法】に", 50),
]


def step(i, **kw):
    year, name, desc, size = STEPS[i]
    return Step(i, year, name, desc, col=PAL["red"], name_size=size, **kw)


def unify():
    return [Glow(13.5, 41.5, 4.2, 3.6, col=PAL["red"]), Stamp(760, 300, "統一", size=90, at=0.5)]


def exam():
    """受験版（高校生・30〜45秒）"""
    q = ["平民会の決議が", "【国法】になった法律は？"]
    scenes = [
        Scene([
            ("/".join(q), "平民会の決議が、国法になった法律は？"),
        ], stage="plain", pad=0.15, caption="コメントで予想してね！", els=[
            QuizHook(q, ["十二表法", "リキニウス・セクスティウス法", "ホルテンシウス法"], kicker="テストに出る！"),
        ]),
        Scene([
            ("前753年、伝説では/【ロムルス】がローマを建国", "紀元前753年、伝説では、ロムルスがローマを建国"),
        ], cam=CAM_ITALY, year=-753, els=[
            Marker(*ROME, "ローマ", side="r", sub="ラテン人の都市国家"),
        ]),
        Scene([
            ("前509年【エトルリア人】の王を追放/【共和政】へ", "紀元前509年、エトルリア人の王を追放し、共和政へ"),
        ], cam=CAM_ROME, year=-509, els=[
            Glow(11.4, 43.0, 1.3, 0.9, col=PAL["dim"]),
            MapLabel(11.3, 43.4, "エトルリア人", size=46, col=PAL["ink"]),
            Marker(*ROME, "ローマ", side="r"),
            Stamp(760, 820, "王を追放", size=64, at=0.8),
        ]),
        Scene([
            "最高職は【コンスル】2名/任期は1年",
            ("貴族【パトリキ】が元老院を独占/平民【プレブス】は不満", "貴族パトリキが元老院を独占。平民プレブスは不満"),
        ], stage="plain", year=-500, els=[
            Card(540, 170, 640, "コンスル（執政官）", ["2名・任期1年"], col=PAL["ink"]),
            Card(290, 560, 470, "元老院", ["貴族＝【パトリキ】"], col=PAL["teal"], at="c1"),
            Card(790, 560, 440, "平民", ["【プレブス】"], col=PAL["red"], at="c1+0.4"),
        ]),
        Scene([("【身分闘争】で/【護民官】と【平民会】を獲得", "身分闘争で、護民官と平民会を獲得")],
              stage="plain", year=-494, els=[step(0, span=4)]),
        Scene([("前450年ごろ【十二表法】/最初の成文法", "紀元前450年ごろ、十二表法。最初の成文法")],
              stage="plain", year=-450, els=[step(1, span=3)]),
        Scene([("前367年【リキニウス・】/【セクスティウス法】",
                "紀元前367年、リキニウス・セクスティウス法。コンスルの1人は平民から")],
              stage="plain", year=-367, els=[step(2, span=2)]),
        Scene([("前287年【ホルテンシウス法】/平民会の決議が国法に", "紀元前287年、ホルテンシウス法。平民会の決議が国法に")],
              stage="plain", year=-287, hold=0.3, els=[step(3)]),
        Scene([
            "まとめ！/ここ、テストに出ます",
        ], stage="plain", hold=2.0, els=[Table(
            ["できごと", "ポイント"],
            [
                ("前509", "共和政", "王を追放/【コンスル】2名"),
                ("前494", "護民官・平民会", "平民の権利を守る"),
                ("前450", "十二表法", "最初の【成文法】"),
                ("前367", "リキニウス・/セクスティウス法", "コンスル1人を平民から"),
                ("前287", "ホルテンシウス法", "平民会の決議＝【国法】"),
                ("前272", "半島統一", "【分割統治】"),
            ],
            row_dt=0.45, title="まとめ｜ローマ共和政", row_h=112,
        )]),
        Scene([
            "答えは【ホルテンシウス法】！",
        ], stage="plain", hold=1.2, els=[
            AnswerCard("ホルテンシウス法", note="前287年・身分闘争が終わる", next_text=NEXT),
        ]),
    ]
    return Video(scenes, header=HEADER, badge="受験版", badge_color=PAL["red"],
                 credit="VOICEVOX:四国めたん", voice=2, speed=1.26, max_dur=45.0, timeline=TIMELINE)


def general():
    """教養版（一般・60秒）"""
    q = ["ローマ建国の伝説", "双子を育てた【動物】は？"]
    scenes = [
        Scene([
            ("/".join(q), "ローマ建国の伝説で、双子を育てた動物は？"),
        ], stage="plain", pad=0.15, caption="コメントで予想してね！", els=[
            QuizHook(q),
        ]),
        Scene([
            "伝説では/ローマを作ったのは双子の兄弟",
            "川に捨てられた2人は/ある動物に育てられます",
            "兄【ロムルス】の名から/【ローマ】と呼ばれました",
        ], cam=CAM_ITALY, year=-753, els=[
            Marker(*ROME, "ローマ", side="r", sub="前753（伝説）"),
            Card(540, 850, 640, None, ["双子：ロムルスとレムス"], at="c1"),
        ]),
        Scene([
            "最初は王がいましたが/前509年に王を追放",
            "独裁を防ぐため/【2人のリーダー】が1年交代",
            "これが【共和政】の始まりです",
        ], cam=CAM_ROME, year=-509, els=[
            Marker(*ROME, "ローマ", side="r"),
            Stamp(760, 300, "王を追放", size=64, at=0.9, dur=3.0),
            Card(540, 820, 700, "コンスル（執政官）", ["2人・任期1年"], col=PAL["ink"], at="c1"),
        ]),
        Scene([
            "でも政治は/【貴族】がほぼ独占",
            "怒った平民たちは/町を出てストライキ！",
            "こうして平民を守る/【護民官】が生まれました",
        ], stage="plain", year=-494, els=[
            Card(540, 200, 600, "元老院", ["貴族が独占"], col=PAL["teal"]),
            Phalanx(y=600, at="c1", dur=3.2),
            Stamp(800, 420, "ストライキ", size=56, at="c1+0.4", dur=2.8),
            Card(540, 640, 640, "護民官", ["平民の味方"], col=PAL["red"], at="c2"),
        ]),
        Scene([
            "約200年かけて/平民は権利を勝ち取り",
            "前287年、平民の決定が/国の【法律】になりました",
        ], stage="plain", year=-287, els=[
            step(0, span=1), step(1, at=0.3), step(2, at=0.6), step(3, at="c1"),
        ]),
        Scene([
            "力をつけたローマは/【イタリア半島】を統一",
        ], cam=CAM_ITALY, year=-272, hold=0.3, els=unify()),
        Scene([
            "答えは【オオカミ】！",
        ], stage="plain", hold=1.2, els=[
            AnswerCard("オオカミ", note="オオカミと双子の像は/今もローマのシンボル", next_text=NEXT),
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
        out = os.path.join(OUT, f"europe_06_rome_{name}.mp4")
        if preview:
            v.build_audio(tts)
            times = [0.0] + [sc.t0 + (sc.t1 - sc.t0) * 0.85 for sc in v.scenes]
            v.render(out, tts, preview_times=times)
        else:
            log = v.render(out, tts)
            with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
                fh.write(log + "\n")
            print(log)
