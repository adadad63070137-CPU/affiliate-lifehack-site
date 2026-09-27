"""ヨーロッパ編 #1 エーゲ文明とポリスの成立（受験版・教養版）

usage: python3 -m episodes.europe_01_aegean [exam|general|all] [--preview]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.core import PAL, TTS, Scene, Video  # noqa: E402
from engine.elements import (Arrow, Card, EndCard, Glow, Hook, Labyrinth, MapLabel, Marker,  # noqa: E402
                             Polis, Stamp, Table)

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
HEADER = "ヨーロッパ編 #1  エーゲ文明とポリス"

# 地名（経度, 緯度）
KNOSSOS = (25.163, 35.298)
MYCENAE = (22.756, 37.731)
TROY = (26.239, 39.957)
ATHENS = (23.727, 37.984)
SPARTA = (22.430, 37.073)

# カメラ（中心経度, 中心緯度, 1度あたりのpx）
CAM_EUROPE = (15.0, 45.0, 26)
CAM_AEGEAN = (25.0, 37.6, 115)
CAM_CRETE = (24.9, 35.3, 240)
CAM_GREECE = (23.6, 39.0, 110)
CAM_TROY = (24.6, 38.7, 105)
CAM_POLIS = (23.1, 37.7, 150)

MIGRATION = [(22.3, 42.4), (21.9, 40.7), (22.5, 39.1), (22.7, 38.0)]

TIMELINE = dict(
    range=(-3100, -650),
    ticks=[-3000, -2000, -1600, -1200, -800],
    eras=[
        (-3000, -2000, "青銅器文明", (214, 190, 140), -2500),
        (-2000, -1400, "クレタ", (110, 175, 170), -1850),
        (-1600, -1200, "ミケーネ", (215, 120, 100), -1330),
        (-1200, -800, "暗黒時代", (95, 95, 105), -1000),
        (-800, -650, "ポリス", (225, 180, 70), -725),
    ],
)

SUMMARY = Table(
    ["クレタ文明", "ミケーネ文明"],
    [
        ("時期", "前2000年〜", "前1600年〜"),
        ("中心", "クノッソス", "ミケーネ"),
        ("特徴", "【開放的】/城壁なし", "【巨石城塞】/戦闘的"),
        ("文字", "【線文字A】/未解読", "【線文字B】/ヴェントリス解読"),
        ("発掘", "エヴァンズ", "シュリーマン"),
    ],
    row_dt=0.5,
    title="まとめ｜ここがテストに出る！",
)


def exam():
    """受験版（高校生・30〜45秒）：用語と年代を最短で整理"""
    scenes = [
        Scene([
            "【エーゲ文明】から/【ポリス成立】まで",
            "40秒で/総整理！",
        ], cam=CAM_EUROPE, els=[
            Hook("テスト頻出", ["エーゲ文明", "→【ポリス】"], sub="40秒で総整理"),
        ]),
        Scene([
            "前2000年ごろ/【クレタ文明】がおこる",
            "中心は/【クノッソス宮殿】",
            "【城壁なし】の/開放的な海洋文明",
            "文字は【線文字A】/＝未解読！",
            "発掘したのは/【エヴァンズ】",
        ], cam=CAM_CRETE, cam_dur=1.3, year=-2000, els=[
            Glow(24.9, 35.2, 1.55, 0.5),
            MapLabel(24.3, 34.72, "クレタ島", at=0.3),
            Marker(*KNOSSOS, "クノッソス", side="t", at="c1"),
            Card(540, 170, 600, None, ["【城壁なし】＝開放的", "海上交易で繁栄"], at="c2", dur=4.0),
            Card(330, 820, 460, "線文字A", ["まだ読めない"], col=PAL["teal"], at="c3"),
            Stamp(790, 800, "未解読", at="c3+0.5"),
            Card(540, 170, 600, None, ["発掘：【エヴァンズ】（英）"], at="c4"),
        ]),
        Scene([
            "前1600年ごろ/北から【ギリシア人】が南下",
            "【ミケーネ文明】を築く",
            "巨石の【城塞】と/【線文字B】が特徴",
            "線文字Bは/【ヴェントリス】が解読",
            "ミケーネとトロイアは/【シュリーマン】が発掘",
        ], cam=CAM_GREECE, year=-1600, els=[
            Arrow(MIGRATION, label="ギリシア人", label_at=0.35, span=1),
            Marker(*MYCENAE, "ミケーネ", side="l", at="c1"),
            Card(800, 820, 460, "特徴", ["巨石の【城塞】", "戦闘的な王国"], col=PAL["red"], at="c2", dur=3.2),
            Card(800, 820, 460, "線文字B", ["【解読済み】", "中身はギリシア語"], col=PAL["red"], at="c3"),
            Marker(*TROY, "トロイア", side="t", at="c4"),
        ]),
        Scene([
            "前1200年ごろ滅亡し/【暗黒時代】へ",
            "約400年の間に/【鉄器】が普及",
        ], cam=CAM_AEGEAN, year=-1200, dark=0.55, els=[
            Stamp(540, 330, "滅亡", col=PAL["gold"], size=90, at=0.4),
            Card(540, 700, 620, "暗黒時代（約400年）", ["文字の記録が途絶える", "【鉄器】が広まる"],
                 col=PAL["ink"], at="c1"),
        ]),
        Scene([
            "前8世紀、【集住】して/【ポリス】が成立",
            "丘の【アクロポリス】と/広場の【アゴラ】が中心",
            "自らを【ヘレネス】/異民族を【バルバロイ】と呼んだ",
        ], stage="plain", year=-800, els=[
            Polis(),
            Card(540, 915, 900, None, ["ヘレネス ⇔ バルバロイ"], at="c2", body_size=46),
        ]),
        Scene([
            "まとめ！/ここ、テストに出ます",
        ], stage="plain", hold=2.6, els=[SUMMARY]),
        Scene([
            "次回は/【アテネとスパルタ】",
        ], stage="plain", hold=0.8, els=[EndCard("ヨーロッパ編 #2", "アテネとスパルタ")]),
    ]
    return Video(scenes, header=HEADER, badge="受験版", badge_color=PAL["red"],
                 credit="VOICEVOX:四国めたん", voice=2, speed=1.26, max_dur=45.0, timeline=TIMELINE)


def general():
    """教養版（一般・60秒）：エピソードで「へぇ」を狙う"""
    scenes = [
        Scene([
            "ギリシア神話の/【迷宮】は",
            "本当にあったのかも/しれません",
        ], cam=(25.0, 36.6, 95), els=[
            Hook("ミノタウロスの迷宮", ["迷宮は", "【実在】した？"]),
            Labyrinth(540, 800, 130),
        ]),
        Scene([
            "舞台は【エーゲ海】",
            "約4000年前/【クレタ島】に文明が栄えます",
        ], cam=CAM_AEGEAN, cam_dur=1.0, year=-2000, els=[
            MapLabel(25.3, 38.3, "エーゲ海", size=64, at=0.2),
            Glow(24.9, 35.2, 1.55, 0.5, at="c1"),
            MapLabel(24.9, 34.55, "クレタ島", at="c1+0.3"),
        ]),
        Scene([
            "【クノッソス宮殿】は/部屋が複雑に入り組み",
            "まるで【迷宮】そのもの",
            "壁画には【イルカ】が泳ぎ/海とともに生きた人々",
            "しかも【城壁がない】/平和な海の王国でした",
        ], cam=CAM_CRETE, year=-1800, els=[
            Marker(*KNOSSOS, "クノッソス宮殿", side="t"),
            Labyrinth(830, 800, 110, at="c1", dur=2.2),
            Card(540, 180, 560, "イルカの壁画", ["海を愛した王国"], col=PAL["teal"], at="c2", dur=3.4),
            Card(540, 820, 620, None, ["【城壁なし】", "海上交易で栄えた"], at="c3"),
        ]),
        Scene([
            "やがて北から/【ギリシア人】が南下",
            "城塞を築き/【ミケーネ文明】をおこします",
        ], cam=CAM_GREECE, year=-1600, els=[
            Arrow(MIGRATION, label="ギリシア人", label_at=0.35),
            Marker(*MYCENAE, "ミケーネ", side="l", at="c1"),
        ]),
        Scene([
            "伝説のトロイア戦争を/信じた男がいました",
            "彼は本当に/遺跡を掘り当てます",
            "それが実業家/【シュリーマン】",
        ], cam=CAM_TROY, year=-1300, els=[
            Marker(*TROY, "トロイア", side="t"),
            Stamp(820, 560, "発見！", col=PAL["gold"], at="c1+0.6", dur=2.0),
            Card(540, 800, 720, "ハインリヒ・シュリーマン", ["商売で財を成し", "【トロイア】と【ミケーネ】を発掘"],
                 col=PAL["red"], at="c2", body_size=40),
        ]),
        Scene([
            ("ミケーネの文字/【線文字B】を解読したのは", "ミケーネの文字、線文字Bを解読したのは"),
            "本業が【建築家】の/ヴェントリス",
            "一方クレタの【線文字A】は/今も読めていません",
        ], cam=CAM_AEGEAN, year=-1300, els=[
            Card(540, 200, 700, "線文字B（ミケーネ）", ["解読したのは…？"], col=PAL["red"], dur=2.4),
            Card(540, 200, 700, "線文字B（ミケーネ）", ["【ヴェントリス】が解読", "本業は建築家！"],
                 col=PAL["red"], at="c1"),
            Card(360, 700, 540, "線文字A（クレタ）", ["いまだ謎のまま"], col=PAL["teal"], at="c2"),
            Stamp(820, 720, "未解読", at="c2+0.5"),
        ]),
        Scene([
            "前1200年ごろ/文明は突然崩壊",
            "約400年の/【暗黒時代】へ",
        ], cam=CAM_AEGEAN, year=-1200, dark=0.55, els=[
            Stamp(540, 380, "崩壊", col=PAL["gold"], size=90, at=0.5),
            Card(540, 720, 560, "暗黒時代", ["約400年の空白"], col=PAL["ink"], at="c1"),
        ]),
        Scene([
            "そして前8世紀/【ポリス】が誕生",
            "【アテネ】や【スパルタ】の/物語が始まります",
        ], cam=CAM_POLIS, year=-800, els=[
            Card(540, 170, 640, None, ["都市国家【ポリス】の誕生"]),
            Marker(*ATHENS, "アテネ", side="r", at="c1"),
            Marker(*SPARTA, "スパルタ", side="l", at="c1+0.5"),
        ]),
        Scene([
            "次回/【アテネとスパルタ】",
            "フォローして/お待ちください",
        ], stage="plain", hold=0.6, els=[EndCard("ヨーロッパ編 #2", "アテネとスパルタ")]),
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
        out = os.path.join(OUT, f"europe_01_aegean_{name}.mp4")
        if preview:
            v.build_audio(tts)
            times = [sc.t0 + (sc.t1 - sc.t0) * 0.8 for sc in v.scenes]
            v.render(out, tts, preview_times=times)
        else:
            log = v.render(out, tts)
            with open(out.replace(".mp4", "_timing.txt"), "w") as fh:
                fh.write(log + "\n")
            print(log)
