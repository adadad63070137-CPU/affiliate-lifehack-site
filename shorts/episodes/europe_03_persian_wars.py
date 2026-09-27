"""ヨーロッパ編 #3 ペルシア戦争とアテネ民主政（受験版・教養版）

usage: python3 episodes/europe_03_persian_wars.py [exam|general|all] [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import (Arrow, Assembly, AssemblyCross, Card, EndCard, Hook, Marker, Phalanx,  # noqa: E402
                             Stamp, Table, Trireme)

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #3  ペルシア戦争"

ATHENS = (23.727, 37.984)
MILETUS = (27.278, 37.530)
MARATHON = (23.970, 38.150)
THERMOPYLAE = (22.540, 38.800)
SALAMIS = (23.500, 37.950)

CAM_WAR = (25.4, 38.4, 92)
CAM_ATTICA = (23.3, 38.35, 200)

PERSIA_ARROW = [(34.5, 39.2), (31.0, 38.6), (27.6, 37.7)]
PERSIA_INVASION = [(28.5, 40.6), (25.5, 40.9), (23.2, 40.3), (22.7, 39.2)]

TIMELINE = dict(
    range=(-510, -425),
    ticks=[-500, -490, -480, -449],
    eras=[
        (-500, -449, "ペルシア戦争", (215, 120, 100), -485),
        (-449, -429, "ペリクレス時代", (225, 180, 70), -440),
    ],
)


def exam():
    """受験版（高校生・30〜45秒）"""
    scenes = [
        Scene([
            "【ペルシア戦争】を/40秒で総整理！",
        ], cam=CAM_WAR, els=[
            Hook("テスト頻出", ["ペルシア", "【戦争】"], sub="前500〜前449年"),
        ]),
        Scene([
            "前500年【イオニア植民市】が/ペルシアに反乱",
            "アテネが支援し/戦争が始まる",
        ], cam=CAM_WAR, year=-500, els=[
            Arrow(PERSIA_ARROW, label="アケメネス朝", label_at=0.62),
            Marker(*MILETUS, "ミレトス", side="b", at=0.4),
            Arrow([ATHENS, (25.5, 37.4), (27.0, 37.5)], col=PAL["teal"], width=12, at="c1"),
        ]),
        Scene([
            ("前490年【マラトンの戦い】/重装歩兵で勝利", "前490年、マラトンの戦い。重装歩兵で勝利"),
        ], cam=CAM_ATTICA, year=-490, els=[
            Marker(*MARATHON, "マラトン", side="r", sub="前490"),
        ]),
        Scene([
            "前480年【テルモピレー】で/スパルタ軍が全滅",
            ("同じ年【サラミスの海戦】/【テミストクレス】が大勝", "同じ年、サラミスの海戦で、テミストクレスが大勝"),
        ], cam=CAM_ATTICA, year=-480, els=[
            Marker(*THERMOPYLAE, "テルモピレー", side="r", sub="前480"),
            Marker(*SALAMIS, "サラミス", side="l", sub="前480", at="c1"),
        ]),
        Scene([
            "船をこいだ【無産市民】も/発言力を強める",
        ], stage="plain", year=-480, els=[Trireme()]),
        Scene([
            ("前479年【プラタイア】で勝利/【デロス同盟】の盟主はアテネ", "前479年、プラタイアで勝利。デロス同盟の盟主はアテネ"),
        ], stage="plain", year=-478, els=[
            Card(540, 480, 820, "デロス同盟（前478年ごろ）", ["盟主は【アテネ】", "ペルシアの再来に備える"],
                 col=PAL["teal"]),
        ]),
        Scene([
            "【ペリクレス】の時代に/民主政が完成",
            ("成年男性市民の【民会】で決める/【直接民主政】", "成年男性市民の民会で決める、直接民主政"),
            "でも【女性】や【奴隷】は/参政権なし",
        ], stage="plain", year=-445, els=[
            Assembly(), AssemblyCross(at="c2"),
        ]),
        Scene([
            "まとめ！/ここ、テストに出ます",
        ], stage="plain", hold=2.6, els=[Table(
            ["できごと", "ポイント"],
            [
                ("前500", "イオニア反乱", "【ミレトス】中心"),
                ("前490", "マラトン", "【重装歩兵】が活躍"),
                ("前480", "サラミス", "【テミストクレス】/【無産市民】が活躍"),
                ("前478", "デロス同盟", "盟主【アテネ】"),
                ("前5c", "ペリクレス", "【直接民主政】/女性・奴隷は×"),
            ],
            row_dt=0.5, title="まとめ｜ペルシア戦争",
        )]),
        Scene([
            "次回は/【ペロポネソス戦争】",
        ], stage="plain", hold=0.8, els=[EndCard("ヨーロッパ編 #4", "ペロポネソス戦争")]),
    ]
    return Video(scenes, header=HEADER, badge="受験版", badge_color=PAL["red"],
                 credit="VOICEVOX:四国めたん", voice=2, speed=1.26, max_dur=45.0, timeline=TIMELINE)


def general():
    """教養版（一般・60秒）"""
    scenes = [
        Scene([
            "たった300人で/大軍に立ち向かった王",
            "伝説の戦いは/本当にありました",
        ], cam=(22.8, 38.8, 170), els=[
            Hook("伝説の300人", ["300人", "vs【大帝国】"]),
        ]),
        Scene([
            "相手は当時/世界最大の【ペルシア帝国】",
            "ギリシアのポリスは/力を合わせて戦います",
        ], cam=CAM_WAR, year=-500, els=[
            Arrow(PERSIA_ARROW, label="ペルシア", label_at=0.62),
            Marker(*ATHENS, "アテネ", side="l", at="c1"),
        ]),
        Scene([
            "前490年【マラトン】で勝利",
            "勝利を伝えに走った兵士の伝説が/【マラソン】の由来です",
        ], cam=CAM_ATTICA, year=-490, els=[
            Marker(*MARATHON, "マラトン", side="r"),
            Arrow([MARATHON, (23.9, 38.05), ATHENS], col=PAL["teal"], width=12, draw_dur=1.8, at="c1"),
            Card(540, 830, 640, "マラソンの由来", ["勝利を伝えた【伝令】の伝説"], col=PAL["teal"], at="c1+0.5"),
        ]),
        Scene([
            "10年後、スパルタ王【レオニダス】が",
            "狭い道で大軍を食い止め/最後まで戦い抜きました",
            "実はほかのギリシア兵も/一緒に戦っていたんです",
        ], cam=CAM_ATTICA, year=-480, els=[
            Arrow(PERSIA_INVASION, label="ペルシア軍"),
            Marker(*THERMOPYLAE, "テルモピレー", side="r", at="c1"),
            Card(540, 830, 700, None, ["スパルタ兵300人", "＋ほかのギリシア兵"], at="c2"),
        ]),
        Scene([
            "そして【サラミス】の海で/アテネ艦隊が大勝利",
            "指揮したのは【テミストクレス】/前回の陶片の人物です",
            "船をこいだのは/財産のない【市民】たち",
            "1隻を【約170人】で/こぐ巨大な船でした",
        ], stage="plain", year=-480, els=[
            Trireme(),
            Card(540, 830, 640, None, ["指揮：【テミストクレス】"], dur=3.4, at="c1"),
            Card(540, 830, 640, None, ["こぎ手 約【170人】"], at="c3"),
        ]),
        Scene([
            "彼らも発言力を得て/アテネの【民主政】が完成",
            "ただし女性や奴隷は/参加できませんでした",
        ], stage="plain", year=-445, els=[
            Assembly(), AssemblyCross(at="c1"),
        ]),
        Scene([
            "ところが勝ったギリシアは/やがて仲間割れへ…",
            "次回【ペロポネソス戦争】",
            "フォローして/お待ちください",
        ], stage="plain", hold=0.6, els=[
            Phalanx(y=560, dur=2.6),
            EndCard("ヨーロッパ編 #4", "ペロポネソス戦争", at="c1"),
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
        out = os.path.join(OUT, f"europe_03_persian_wars_{name}.mp4")
        if preview:
            v.build_audio(tts)
            times = [sc.t0 + (sc.t1 - sc.t0) * 0.85 for sc in v.scenes]
            v.render(out, tts, preview_times=times)
        else:
            log = v.render(out, tts)
            with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
                fh.write(log + "\n")
            print(log)
