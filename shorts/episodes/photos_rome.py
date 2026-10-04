"""ローマ時代の実写素材（長編 #2 と共通。Wikimedia Commons。ライセンスは engine/assets.py が取得時に確認）

(キー, Commons のファイル名, 説明欄に出す作品名)
"""
PHOTOS = [
    ("TURNER", "Turner, Snow Storm, 50508403226 b272cf84c3 o.jpg",
     "J.M.W.ターナー『吹雪：アルプスを越えるハンニバルとその軍勢』"),
    ("BUST", "Hannibal Barca bust from Capua photo.jpg", "ハンニバルとされる胸像（カプア出土）"),
    ("RHONE", "Hannibal traverse le Rhône Henri Motte 1878.jpg", "アンリ・モット『ローヌ川を渡るハンニバル』"),
    ("ZAMA", "Cornelis Cort - The Battle of Zama - 1990.563 - Art Institute of Chicago.jpg",
     "コルネリス・コルト『ザマの戦い』"),
    ("CARTHAGE", "Antonine Baths Carthage.jpg", "カルタゴのアントニヌス浴場跡（チュニジア）"),
    ("CORNELIA", "Angelica kauffman ra cornelia mother of the gracchi060808).jpg",
     "アンゲリカ・カウフマン『グラックス兄弟の母コルネリア』"),
    ("GRACCHUS", "Lodovico Pogliaghi - Tiberius Gracchus has the tribune Octavius Cecina dismissed.png",
     "ロドヴィコ・ポリアーギ『護民官ティベリウス・グラックス』"),
    ("MARIUS", "Marius Glyptothek Munich 319.jpg", "マリウスとされる胸像（ミュンヘン・グリプトテーク）"),
    ("SULLA", "Sulla Glyptothek Munich 309.jpg", "スラとされる胸像（ミュンヘン・グリプトテーク）"),
    ("POLLICE", "Jean-Leon Gerome Pollice Verso.jpg", "ジャン＝レオン・ジェローム『指し下ろされた親指』"),
    ("SPARTACUS", "Spartacus by Denis Foyatier (31851397233).jpg", "ドニ・フォワイアティエ『スパルタクス』"),
    ("POMPEY", "Pompeius.JPG", "ポンペイウスの胸像"),
    ("CAESAR", "Retrato de Julio César (26724093101).jpg", "カエサルの肖像彫刻"),
    ("VERCINGETORIX", "Lionel Royer - Vercingetorix Throwing down His Weapons at the feet of Julius Caesar.jpg",
     "リオネル・ロワイエ『カエサルの足元に武器を投げ出すウェルキンゲトリクス』"),
    ("RUBICON", "Caesar-ueberschreitet-den-rubikon.jpg", "『ルビコン川を渡るカエサル』（19世紀の挿絵）"),
    ("DEATH", "Jean-Léon Gérôme - The Death of Caesar - Walters 37884.jpg", "ジャン＝レオン・ジェローム『カエサルの死』"),
    ("ANTCLEO", "Sir Lawrence Alma-Tadema - The Meeting of Antony and Cleopatra.jpg",
     "ローレンス・アルマ＝タデマ『アントニウスとクレオパトラの出会い』"),
    ("ACTIUM", "Castro Battle of Actium.jpg", "ローレイス・ア・カストロ『アクティウムの海戦』"),
    ("AUGUSTUS", "Statue-Augustus.jpg", "アウグストゥス像（プリマ・ポルタのアウグストゥス）"),
]


def photo(key):
    """キー → (画像パス, クレジット, 作品名)"""
    from engine.assets import commons
    for k, title, name in PHOTOS:
        if k == key:
            path, credit = commons(title)
            return path, credit, name
    raise KeyError(key)
