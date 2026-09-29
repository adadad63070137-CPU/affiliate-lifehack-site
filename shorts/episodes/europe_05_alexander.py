"""ヨーロッパ編 #5 アレクサンドロス大王とヘレニズム（受験版・教養版）

usage: python3 episodes/europe_05_alexander.py [exam|general|all] [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import (Arrow, Card, EndCard, Glow, Hook, MapLabel, Marker, Stamp, Table)  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #5  アレクサンドロス大王"

PELLA = (22.52, 40.76)
CHAERONEA = (22.84, 38.49)
ISSUS = (36.20, 36.85)
ALEXANDRIA = (29.92, 31.20)
GAUGAMELA = (43.30, 36.40)
BABYLON = (44.42, 32.54)
PERSEPOLIS = (52.89, 29.93)
INDUS = (72.50, 32.00)

CAM_GREECE = (23.0, 39.4, 150)
CAM_WORLD = (47.0, 35.5, 19)

# 東方遠征のおおよそのルート
ROUTE = [PELLA, (26.4, 40.2), (29.5, 38.8), ISSUS, (35.2, 33.3), ALEXANDRIA, (34.0, 31.5),
         (38.5, 35.5), GAUGAMELA, BABYLON, PERSEPOLIS, (54.0, 35.5), (61.0, 36.5), (66.9, 36.7),
         (70.0, 34.5), INDUS]
RETURN = [INDUS, (68.0, 26.5), (62.0, 25.5), (56.0, 27.5), PERSEPOLIS, BABYLON]

TIMELINE = dict(
    range=(-352, -290),
    ticks=[-338, -323, -301],
    eras=[
        (-350, -336, "マケドニア台頭", (110, 175, 170), -343),
        (-336, -323, "大王の治世", (215, 120, 100), -329),
        (-323, -301, "後継者争い", (95, 95, 105), -312),
        (-301, -292, "3王朝", (225, 180, 70), -296),
    ],
)


def kingdoms(**kw):
    return [
        Glow(23.5, 40.0, 3.0, 2.0, col=PAL["teal"], **kw),
        Glow(47.0, 34.5, 12.0, 6.0, col=PAL["red"], **kw),
        Glow(30.5, 28.0, 4.0, 3.5, col=PAL["gold"], **kw),
        MapLabel(28.5, 44.5, "アンティゴノス朝", size=40, col=PAL["teal"], **kw),
        MapLabel(47.5, 39.0, "セレウコス朝", size=46, col=PAL["red"], **kw),
        MapLabel(30.5, 24.0, "プトレマイオス朝", size=40, col=PAL["gold"], **kw),
    ]


def exam():
    """受験版（高校生・30〜45秒）"""
    scenes = [
        Scene([
            "【アレクサンドロス大王】を/40秒で総整理！",
        ], cam=CAM_WORLD, els=[
            Hook("テスト頻出", ["アレクサンドロス", "【大王】"], sub="前336〜前323年"),
        ]),
        Scene([
            ("前338年【カイロネイアの戦い】/マケドニアがギリシアを制圧",
             "前338年、カイロネイアの戦い。マケドニアがギリシアを制圧"),
            ("【フィリッポス2世】が/【コリントス同盟】を結成", "フィリッポス2世が、コリントス同盟を結成"),
        ], cam=CAM_GREECE, year=-338, els=[
            Marker(*PELLA, "マケドニア", side="r"),
            Marker(*CHAERONEA, "カイロネイア", side="l", sub="前338", at=0.5),
            Card(540, 850, 760, None, ["【コリントス同盟】（スパルタ除く）"], at="c1"),
        ]),
        Scene([
            "前334年【東方遠征】開始",
            ("【イッソスの戦い】で/【ダレイオス3世】を破る", "イッソスの戦いで、ダレイオス3世を破る"),
            "前330年【アケメネス朝】滅亡",
            "【インダス川】まで到達",
        ], cam=CAM_WORLD, cam_dur=1.4, year=-334, els=[
            Arrow(ROUTE, width=12, draw_dur=9.0, span=2),
            Marker(*ISSUS, "イッソス", side="t", at="c1"),
            Marker(*PERSEPOLIS, "ペルセポリス", side="b", at="c2"),
            Stamp(800, 300, "滅亡", size=70, at="c2+0.4", dur=1.8),
            Marker(*INDUS, "インダス川", side="l", at="c3"),
        ]),
        Scene([
            "前323年【バビロン】で急死",
        ], cam=CAM_WORLD, year=-323, els=[
            Arrow(RETURN, width=12, col=PAL["dim"], draw_dur=1.5),
            Marker(*BABYLON, "バビロン", side="t", sub="前323 死去", at=0.8),
        ]),
        Scene([
            "帝国は【3つの王朝】に分裂",
        ], cam=CAM_WORLD, year=-301, els=kingdoms()),
        Scene([
            ("ギリシアとオリエントが融合/【ヘレニズム文化】", "ギリシアとオリエントが融合、ヘレニズム文化"),
            ("中心は【アレクサンドリア】の/研究所【ムセイオン】", "中心はアレクサンドリアの、研究所ムセイオン"),
        ], cam=(31.5, 33.0, 45), year=-300, els=[
            Marker(*ALEXANDRIA, "アレクサンドリア", side="b", sub="ムセイオン", at="c1"),
            Card(540, 180, 720, "ヘレニズム文化", ["ギリシア＋オリエント"], col=PAL["teal"]),
        ]),
        Scene([
            "まとめ！/ここ、テストに出ます",
        ], stage="plain", hold=2.6, els=[Table(
            ["できごと", "ポイント"],
            [
                ("前338", "カイロネイア", "【フィリッポス2世】/コリントス同盟"),
                ("前334", "東方遠征", "イッソス/【ダレイオス3世】"),
                ("前330", "アケメネス朝滅亡", "インダス川まで"),
                ("前323", "大王の死", "【3王朝】に分裂"),
                ("文化", "ヘレニズム", "【アレクサンドリア】/ムセイオン"),
            ],
            row_dt=0.5, title="まとめ｜アレクサンドロス大王",
        )]),
        Scene([
            "次回は/【ローマの誕生】",
        ], stage="plain", hold=0.8, els=[EndCard("ヨーロッパ編 #6", "ローマの誕生")]),
    ]
    return Video(scenes, header=HEADER, badge="受験版", badge_color=PAL["red"],
                 credit="VOICEVOX:四国めたん", voice=2, speed=1.26, max_dur=45.0, timeline=TIMELINE)


def general():
    """教養版（一般・60秒）"""
    scenes = [
        Scene([
            "家庭教師はあの【アリストテレス】",
            "20歳で王になり/世界の果てを目指した男",
        ], cam=CAM_WORLD, els=[
            Hook("世界征服の若き王", ["20歳の", "【大王】"]),
        ]),
        Scene([
            "その名は【アレクサンドロス】",
            ("北の国【マケドニア】の王です", "北の国、マケドニアの王です"),
        ], cam=CAM_GREECE, year=-336, els=[
            Marker(*PELLA, "マケドニア", side="r"),
            Card(540, 850, 700, None, ["師：【アリストテレス】"], at=0.3),
        ]),
        Scene([
            "前334年、少ない兵で/超大国【ペルシア】に挑みます",
            "戦いでは一度も/負けなかったといわれます",
            "エジプトでは/【ファラオ】として迎えられ",
            "自分の名の都市/【アレクサンドリア】を建設",
        ], cam=CAM_WORLD, cam_dur=1.4, year=-334, els=[
            Arrow(ROUTE, width=12, draw_dur=13.0, span=3),
            Card(540, 850, 560, None, ["【無敗】の王"], at="c1", dur=2.6),
            Marker(*ALEXANDRIA, "アレクサンドリア", side="b", at="c2"),
            Card(540, 850, 600, None, ["エジプトの【ファラオ】に"], at="c2", dur=2.8),
        ]),
        Scene([
            "ペルシアを滅ぼし/ペルシアの王女と結婚",
            "東西をひとつにしようとします",
            "ついにインドの/【インダス川】まで",
            "でも兵士たちが/「もう帰りたい」と拒否",
        ], cam=CAM_WORLD, year=-330, els=[
            Marker(*PERSEPOLIS, "ペルシア滅亡", side="b"),
            Marker(*INDUS, "インダス川", side="l", at="c2"),
            Card(540, 850, 600, None, ["東西の【融合】をめざす"], at="c1", dur=2.8),
            Card(760, 820, 520, None, ["兵士が進軍を【拒否】"], at="c3"),
        ]),
        Scene([
            "帰り道のバビロンで/【32歳】の若さで死去",
        ], cam=CAM_WORLD, year=-323, els=[
            Arrow(RETURN, width=12, col=PAL["dim"], draw_dur=1.5),
            Marker(*BABYLON, "バビロン", side="t", sub="32歳で死去", at=0.8),
        ]),
        Scene([
            "でも彼が広げた世界で/ギリシアと東方の文化が融合",
            "これが【ヘレニズム文化】です",
            "共通語の【コイネー】で/人々がつながりました",
        ], cam=CAM_WORLD, year=-300, els=[
            *kingdoms(),
            Card(750, 850, 560, "ヘレニズム文化", ["ギリシア＋オリエント"], col=PAL["teal"], at="c1"),
        ]),
        Scene([
            "次回は舞台を西へ/【ローマの誕生】",
            "フォローして/お待ちください",
        ], stage="plain", hold=0.6, els=[EndCard("ヨーロッパ編 #6", "ローマの誕生")]),
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
        out = os.path.join(OUT, f"europe_05_alexander_{name}.mp4")
        if preview:
            v.build_audio(tts)
            times = [sc.t0 + (sc.t1 - sc.t0) * 0.85 for sc in v.scenes]
            v.render(out, tts, preview_times=times)
        else:
            log = v.render(out, tts)
            with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
                fh.write(log + "\n")
            print(log)
