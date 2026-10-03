"""実写素材の取得（ライセンス確認つき・キャッシュあり）

- Wikimedia Commons：パブリックドメイン / CC0 / CC BY のみ使う（CC BY-SA や NC は使わない）
- メトロポリタン美術館（Open Access）：isPublicDomain が True のもののみ
"""
import json
import os
import re
import subprocess
import time
import urllib.parse

from PIL import Image

CACHE = os.path.join(os.path.dirname(__file__), "..", ".cache", "photos")
UA = "SekaishiZukan/1.0 (https://github.com/adadad63070137-cpu; educational video)"
ALLOWED = re.compile(r"^(public domain|pd|cc0|cc by( \d(\.\d)?)?)$", re.I)
MAX_SIDE = 2600


def _get(url, out=None):
    """curl 経由で取得（プロキシの CA 設定をそのまま使える）"""
    env = dict(os.environ, SSL_CERT_FILE=os.environ.get("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt"))
    cmd = ["curl", "-sS", "-L", "-m", "60", "-A", UA, url]
    if out:
        cmd[1:1] = ["-o", out]
    for attempt in range(4):
        r = subprocess.run(cmd, capture_output=True, env=env)
        if r.returncode == 0:
            return r.stdout
        time.sleep(2 ** attempt)
    raise RuntimeError(f"download failed: {url}: {r.stderr.decode()[:200]}")


def _api(url):
    """Commons API（混雑時は待って再試行）"""
    for attempt in range(6):
        body = _get(url)
        try:
            return json.loads(body)
        except ValueError:
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"Commons API unavailable: {body[:120]!r}")


def _shrink(path):
    im = Image.open(path)
    im = im.convert("RGB")
    if max(im.size) > MAX_SIDE:
        im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    im.save(path, quality=92)


def _plain(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def commons(title):
    """Commons のファイル名 → (画像パス, クレジット文字列)。許可されていないライセンスなら例外"""
    os.makedirs(CACHE, exist_ok=True)
    key = re.sub(r"[^A-Za-z0-9_.-]", "_", title)[:120]
    meta_p = os.path.join(CACHE, key + ".json")
    img_p = os.path.join(CACHE, key + ".jpg")
    if not os.path.exists(meta_p):
        q = urllib.parse.urlencode({"action": "query", "titles": "File:" + title, "prop": "imageinfo",
                                    "iiprop": "url|extmetadata", "iiurlwidth": 1920, "format": "json"})
        d = _api("https://commons.wikimedia.org/w/api.php?" + q)
        page = list(d["query"]["pages"].values())[0]
        ii = page["imageinfo"][0]
        if "thumburl" not in ii or ii["thumburl"].split("?")[0] == ii["url"].split("?")[0]:
            # 元画像が 1920px より小さいと縮小版が作られない。元画像の直接取得は断られやすいので標準の 1280px 版を使う
            q = q.replace("iiurlwidth=1920", "iiurlwidth=1280")
            ii = list(_api("https://commons.wikimedia.org/w/api.php?" + q)["query"]["pages"].values())[0]["imageinfo"][0]
        m = ii["extmetadata"]
        lic = _plain(m.get("LicenseShortName", {}).get("value", ""))
        # Wikimedia の案内に従い、元画像ではなく標準サイズ（1920px）の縮小版を使う
        meta = {"url": ii.get("thumburl", ii["url"]).split("?")[0], "license": lic,
                "artist": _plain(m.get("Artist", {}).get("value", ""))[:60] or "不明"}
        with open(meta_p, "w") as fh:
            json.dump(meta, fh, ensure_ascii=False)
        time.sleep(1)
    with open(meta_p) as fh:
        meta = json.load(fh)
    if not ALLOWED.match(meta["license"]):
        raise ValueError(f"{title}: license '{meta['license']}' is not allowed")
    for attempt in range(5):
        if os.path.exists(img_p):
            break
        _get(meta["url"].replace("//thumb.wikimedia.org/", "//upload.wikimedia.org/"), img_p)
        try:
            _shrink(img_p)
        except OSError:  # 混雑時は画像ではなくエラーページが返る
            os.remove(img_p)
            time.sleep(20 * (attempt + 1))
    if not os.path.exists(img_p):
        raise RuntimeError(f"{title}: image download failed")
    lic = "パブリックドメイン" if meta["license"].lower() in ("public domain", "pd", "cc0") else meta["license"]
    credit = f"画像：{meta['artist']}（{lic}）/ Wikimedia Commons" if lic != "パブリックドメイン" \
        else "画像：Wikimedia Commons（パブリックドメイン）"
    return img_p, credit


def met(object_id):
    """メトロポリタン美術館の作品ID → (画像パス, クレジット文字列, 作品情報)"""
    os.makedirs(CACHE, exist_ok=True)
    meta_p = os.path.join(CACHE, f"met_{object_id}.json")
    img_p = os.path.join(CACHE, f"met_{object_id}.jpg")
    if not os.path.exists(meta_p):
        d = json.loads(_get(f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"))
        with open(meta_p, "w") as fh:
            json.dump({k: d.get(k) for k in ("isPublicDomain", "primaryImage", "title", "objectDate", "culture")},
                      fh, ensure_ascii=False)
    with open(meta_p) as fh:
        meta = json.load(fh)
    if not meta["isPublicDomain"]:
        raise ValueError(f"Met {object_id} is not public domain")
    if not os.path.exists(img_p):
        _get(meta["primaryImage"], img_p)
        _shrink(img_p)
    return img_p, "画像：メトロポリタン美術館（CC0）", meta


def commons_search(query, limit=12):
    """候補探し用：検索語 → [(ファイル名, ライセンス, 幅x高さ)]（許可ライセンスのみ）"""
    q = urllib.parse.urlencode({"action": "query", "generator": "search", "gsrsearch": query, "gsrnamespace": 6,
                                "gsrlimit": limit, "prop": "imageinfo", "iiprop": "size|extmetadata",
                                "format": "json"})
    d = _api("https://commons.wikimedia.org/w/api.php?" + q)
    out = []
    for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        ii = p["imageinfo"][0]
        lic = _plain(ii["extmetadata"].get("LicenseShortName", {}).get("value", ""))
        if ALLOWED.match(lic):
            out.append((p["title"][5:], lic, f"{ii['width']}x{ii['height']}"))
    return out
