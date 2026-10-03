#!/usr/bin/env bash
# 動画生成に必要なもの（Python ライブラリ・VOICEVOX・フォント・地図データ）を入れる
set -euo pipefail
VV=${VOICEVOX_DIR:-/opt/vv}
AS=${SHORTS_ASSETS:-/opt/assets}
mkdir -p "$VV" "$AS"
pip install -q pillow numpy imageio-ffmpeg
cd "$VV"
GH=https://github.com
curl -sSLO $GH/VOICEVOX/voicevox_core/releases/download/0.16.3/voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_x86_64.whl
curl -sSLO $GH/VOICEVOX/onnxruntime-builder/releases/download/voicevox_onnxruntime-1.17.3/voicevox_onnxruntime-linux-x64-1.17.3.tgz
curl -sSLO $GH/VOICEVOX/voicevox_vvm/releases/download/0.16.3/0.vvm   # 四国めたん/ずんだもん/春日部つむぎ/雨晴はう
curl -sSLO $GH/r9y9/open_jtalk/releases/download/v1.11.1/open_jtalk_dic_utf_8-1.11.tar.gz
tar xzf voicevox_onnxruntime-linux-x64-1.17.3.tgz
tar xzf open_jtalk_dic_utf_8-1.11.tar.gz
pip install -q voicevox_core-0.16.3-*.whl
cd "$AS"
RAW=https://raw.githubusercontent.com
for f in Sans/OTF/Japanese/NotoSansCJKjp-Black.otf Sans/OTF/Japanese/NotoSansCJKjp-Bold.otf \
         Sans/OTF/Japanese/NotoSansCJKjp-Medium.otf Serif/OTF/Japanese/NotoSerifCJKjp-Black.otf; do
  curl -sSL -o "$(basename $f)" $RAW/notofonts/noto-cjk/main/$f
done
curl -sSL -o land.geojson $RAW/nvkelso/natural-earth-vector/master/geojson/ne_10m_land.geojson
echo "setup done"

# 実写寄りの見た目（look="doc"）用：衛星画像と標高タイル
mkdir -p "$AS/terrain/t7" && cd "$AS/terrain"
curl -sSL -o bluemarble.jpg $RAW/vasturiano/three-globe/master/example/img/earth-blue-marble.jpg
python3 - <<'PY'
import math
def tx(lon, z): return int((lon + 180) / 360 * 2 ** z)
def ty(lat, z):
    r = math.radians(lat); return int((1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * 2 ** z)
open("tiles.txt", "w").write("\n".join(f"7/{x}/{y}" for x in range(tx(-12, 7), tx(80, 7) + 1)
                                       for y in range(ty(58, 7), ty(7, 7) + 1)))
PY
cat tiles.txt | xargs -P 16 -I{} sh -c 'f=t7/$(echo {} | tr / _).png; [ -s $f ] || curl -sS -o $f https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{}.png'
echo "terrain done"
