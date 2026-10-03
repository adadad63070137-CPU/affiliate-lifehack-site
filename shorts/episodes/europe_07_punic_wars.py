"""ヨーロッパ編 #7 ポエニ戦争（受験版・教養版）— 実写寄りの見た目（look="doc"）

usage: python3 episodes/europe_07_punic_wars.py [exam|general|all] [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.assets import commons  # noqa: E402
from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import (AnswerCard, Arrow, Card, Glow, Marker, Photo, QuizHook,  # noqa: E402
                             Stamp, Table)

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #7  ポエニ戦争"
NEXT = "次回：#8 内乱の1世紀"

ROME = (12.48, 41.89)
CARTHAGE = (10.32, 36.85)
SICILY = (14.10, 37.55)
CANNAE = (16.13, 41.31)
ZAMA = (9.40, 36.30)
CARTAGENA = (-0.98, 37.60)
MACEDONIA = (22.50, 40.80)

CAM_WMED = (7.5, 40.0, 43)
CAM_SICILY = (12.0, 38.5, 110)
CAM_MED = (13.0, 38.5, 34)

HANNIBAL = [CARTAGENA, (0.6, 40.6), (3.2, 42.6), (4.7, 43.9), (6.8, 45.2), (9.6, 45.0), (12.1, 43.2), CANNAE]
SCIPIO = [SICILY, (12.2, 37.4), (10.6, 37.0), ZAMA]

# 実写素材（すべてパブリックドメイン。ライセンスは engine/assets.py が取得時に確認）
TURNER = commons("Turner, Snow Storm, 50508403226 b272cf84c3 o.jpg")
RHONE = commons("Hannibal traverse le Rhône Henri Motte 1878.jpg")
CARTHAGE_RUINS = commons("Antonine Baths Carthage.jpg")
ZAMA_ART = commons("Cornelis Cort - The Battle of Zama - 1990.563 - Art Institute of Chicago.jpg")
BUST = commons("Hannibal Barca bust from Capua photo.jpg")

TIMELINE = dict(
    range=(-272, -140),
    ticks=[-264, -218, -202, -146],
    eras=[
        (-264, -241, "第1回", (110, 175, 170), -252),
        (-218, -201, "第2回", (215, 120, 100), -209),
        (-149, -146, "第3回", (95, 95, 105), -152),
    ],
)


def exam():
    """受験版（高校生・30〜45秒）"""
    q = ["ハンニバルを破った", "ローマの【将軍】は？"]
    scenes = [
        Scene([
            ("/".join(q), "ハンニバルを破った、ローマの将軍は？"),
        ], stage="plain", pad=0.15, caption="コメントで予想してね！", els=[
            QuizHook(q, ["スキピオ", "カエサル", "ポンペイウス"], kicker="テストに出る！"),
        ]),
        Scene([
            "ライバルは北アフリカの/【カルタゴ】",
        ], year=-264, els=[
            Photo(*CARTHAGE_RUINS, zoom=(1.05, 1.2), focus=(0.6, 0.55), caption="カルタゴの遺跡（チュニジア）"),
        ]),
        Scene([
            ("前264年【第1回】/シチリアをめぐって開戦", "紀元前264年、第1回。シチリアをめぐって開戦"),
            ("勝ったローマは/シチリアを最初の【属州】に", "かったローマは、シチリアを最初の属州に"),
        ], cam=CAM_SICILY, cam_dur=0.01, year=-241, els=[
            Glow(14.1, 37.55, 1.3, 0.6, col=PAL["gold"]),
            Card(540, 830, 640, None, ["最初の【属州】＝シチリア"], at="c1"),
        ]),
        Scene([
            ("前218年【第2回】/【ハンニバル】が【アルプス越え】", "紀元前218年、第2回。ハンニバルがアルプス越え"),
        ], year=-218, els=[
            Photo(*TURNER, zoom=(1.0, 1.25), focus=(0.35, 0.6), caption="アルプスを越えるハンニバル（ターナー画）"),
        ]),
        Scene([
            ("前216年【カンネーの戦い】で/ローマ大敗", "紀元前216年、カンネーの戦いで、ローマ大敗"),
        ], cam=CAM_WMED, cam_dur=0.01, year=-216, els=[
            Arrow(HANNIBAL, width=14, draw_dur=1.6, label="ハンニバル", label_at=0.25),
            Marker(*CANNAE, "カンネー", side="t", at=1.0),
            Stamp(820, 640, "大敗", size=70, at=1.3),
        ]),
        Scene([
            ("【スキピオ】がアフリカを攻め/前202年【ザマの戦い】で勝利",
             "スキピオがアフリカを攻め、紀元前202年、ザマの戦いで勝利"),
        ], year=-202, els=[
            Photo(*ZAMA_ART, zoom=(1.0, 1.2), focus=(0.4, 0.4), caption="ザマの戦い（16世紀の版画）"),
        ]),
        Scene([
            ("前146年【カルタゴ滅亡】/【マケドニア】も属州に", "紀元前146年、カルタゴ滅亡。マケドニアも属州に"),
        ], cam=CAM_MED, cam_dur=0.01, year=-146, els=[
            Marker(*CARTHAGE, "カルタゴ", side="b"),
            Stamp(360, 720, "滅亡", size=70, at=0.3),
            Marker(*MACEDONIA, "マケドニア", side="t", at=1.0),
        ]),
        Scene([
            "属州の富で/【ラティフンディア】が広がり",
            "【中小農民】が没落していく",
        ], stage="plain", year=-146, els=[
            Card(540, 260, 760, "ラティフンディア", ["奴隷を使う【大農場】"], col=PAL["gold"]),
            Card(540, 640, 760, "中小農民（重装歩兵）", ["没落 → 共和政の危機へ"], col=PAL["red"], at="c1"),
        ]),
        Scene([
            "まとめ！/ここ、テストに出ます",
        ], stage="plain", hold=2.0, els=[Table(
            ["できごと", "ポイント"],
            [
                ("前264", "第1回", "シチリア＝最初の【属州】"),
                ("前216", "カンネー", "【ハンニバル】の大勝"),
                ("前202", "ザマ", "【スキピオ】の勝利"),
                ("前146", "第3回", "カルタゴ滅亡"),
                ("影響", "社会の変化", "【ラティフンディア】/中小農民の没落"),
            ],
            row_dt=0.45, title="まとめ｜ポエニ戦争",
        )]),
        Scene([
            "答えは【スキピオ】！",
        ], hold=1.2, els=[
            Photo(*ZAMA_ART, zoom=(1.15, 1.25), focus=(0.6, 0.5)),
            AnswerCard("スキピオ", note="前202年 ザマの戦い", next_text=NEXT, on_photo=True),
        ]),
    ]
    return Video(scenes, header=HEADER, badge="受験版", badge_color=PAL["red"], look="doc",
                 credit="VOICEVOX:四国めたん", voice=2, speed=1.26, max_dur=45.0, timeline=TIMELINE)


def general():
    """教養版（一般・60秒）"""
    q = ["ハンニバルが", "アルプス越えに", "連れていった【動物】は？"]
    scenes = [
        Scene([
            ("/".join(q), "ハンニバルがアルプス越えに、連れていった動物は？"),
        ], stage="plain", pad=0.15, caption="コメントで予想してね！", els=[
            QuizHook(q),
        ]),
        Scene([
            "ローマ最大のライバル/北アフリカの【カルタゴ】",
        ], cam=CAM_WMED, year=-264, els=[
            Marker(*CARTHAGE, "カルタゴ", side="b"),
            Marker(*ROME, "ローマ", side="r", at=0.3),
        ]),
        Scene([
            "その将軍【ハンニバル】は/とんでもない作戦に出ます",
        ], year=-218, els=[
            Photo(*BUST, mode="fit", zoom=(1.0, 1.12), focus=(0.5, 0.3), caption="ハンニバルとされる胸像"),
        ]),
        Scene([
            "スペインから陸路で/雪の【アルプス】を越え",
        ], cam=CAM_WMED, cam_dur=0.01, year=-218, els=[
            Arrow(HANNIBAL, width=14, draw_dur=2.6, label="ハンニバル", label_at=0.25),
        ]),
        Scene([
            "背後からイタリアに/攻め込みました",
        ], year=-218, els=[
            Photo(*TURNER, zoom=(1.0, 1.25), focus=(0.35, 0.6), caption="アルプスを越えるハンニバル（ターナー画）"),
        ]),
        Scene([
            "カンネーの戦いでは/ローマ軍に歴史的な大勝利",
            "「【ハンニバルが門前に】」は/ローマで恐怖の言葉になりました",
        ], cam=CAM_WMED, cam_dur=0.01, year=-216, els=[
            Arrow(HANNIBAL, width=14, draw_dur=0.01, label="ハンニバル", label_at=0.25),
            Marker(*CANNAE, "カンネー", side="t"),
            Stamp(820, 640, "ローマ大敗", size=60, at=0.5),
        ]),
        Scene([
            "追い詰められたローマの【スキピオ】は",
            "逆にカルタゴの本国を攻撃",
        ], cam=CAM_WMED, year=-204, els=[
            Arrow(SCIPIO, col=PAL["teal"], width=14, label="スキピオ", label_at=0.1, at="c1"),
        ]),
        Scene([
            "ザマの戦いで/ついにハンニバルを破ります",
        ], cam=CAM_WMED, year=-202, els=[
            Arrow(SCIPIO, col=PAL["teal"], width=14, draw_dur=0.01, label="スキピオ", label_at=0.1),
            Marker(*ZAMA, "ザマ", side="l", sub="前202"),
            Stamp(760, 330, "ローマ勝利", size=60, at=0.6),
        ]),
        Scene([
            "そしてカルタゴは滅ぼされ/ローマは【地中海】の覇者に",
            "ローマ人は地中海を/「【我らが海】」と呼びました",
        ], year=-146, hold=0.3, els=[
            Photo(*CARTHAGE_RUINS, zoom=(1.05, 1.2), focus=(0.6, 0.55), caption="今も残るカルタゴの遺跡"),
        ]),
        Scene([
            "答えは【ゾウ】！",
        ], hold=1.4, els=[
            Photo(*RHONE, zoom=(1.1, 1.25), focus=(0.55, 0.4), caption="ローヌ川を渡るゾウ（1878年の絵）"),
            AnswerCard("ゾウ", note="戦象（せんぞう）/多くは寒さで倒れたといわれます", next_text=NEXT, on_photo=True),
        ]),
    ]
    return Video(scenes, header=HEADER, badge="教養版", badge_color=PAL["teal"], look="doc",
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
        out = os.path.join(OUT, f"europe_07_punic_wars_{name}.mp4")
        if preview:
            v.build_audio(tts)
            times = [0.0] + [sc.t0 + (sc.t1 - sc.t0) * 0.85 for sc in v.scenes]
            v.render(out, tts, preview_times=times)
        else:
            log = v.render(out, tts)
            with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
                fh.write(log + "\n")
            print(log)
