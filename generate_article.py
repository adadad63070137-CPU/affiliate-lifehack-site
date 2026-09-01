#!/usr/bin/env python3
"""
Weekly article generator for the affiliate site.

Picks the next pending keyword from data/keywords.csv, asks Claude to draft
an article, runs it through a compliance filter, renders it to static HTML,
and updates the site index + sitemap. Intended to run unattended via
GitHub Actions (see .github/workflows/publish.yml).
"""
import csv
import html
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).parent
KEYWORDS_CSV = ROOT / "data" / "keywords.csv"
ARTICLES_DIR = ROOT / "articles"
SITE_INDEX = ROOT / "index.html"
SITEMAP = ROOT / "sitemap.xml"

# "sonnet"/"opus" のようなエイリアスも指定可能。フルの型番だと将来的に古くなるためエイリアス推奨。
MODEL = os.environ.get("CLAUDE_MODEL", "sonnet")
AMAZON_ASSOC_TAG = os.environ.get("AMAZON_ASSOC_TAG", "").strip()
RAKUTEN_AFFILIATE_ID = os.environ.get("RAKUTEN_AFFILIATE_ID", "").strip()
SITE_URL = os.environ.get("SITE_URL", "https://example.github.io").rstrip("/")
SITE_NAME = os.environ.get("SITE_NAME", "ひとり暮らし家電・便利グッズ比較ラボ")

# 景品表示法・薬機法まわりで自動生成コンテンツに残すと危険な表現。
# これらのフレーズを含む「文」単位で丸ごと削除し、公開自体は止めない(フル自動運用のための安全弁)。
BANNED_PHRASES = [
    # 断定的・優良誤認のおそれがある表現
    "絶対に",
    "100%",
    "必ず治",
    "医学的に証明",
    "副作用は一切",
    "副作用がありません",
    "完全に安全",
    "誰でも簡単に",
    "確実に効果",
    # 捏造された一人称の体験談
    "実際に使ってみた",
    "実際に使用した感想",
    "私が使ってみて",
    "私は実際に",
    "筆者が使用した",
    "使ってみた感想",
    "使用してみた感想",
]

SYSTEM_PROMPT = f"""あなたは「{SITE_NAME}」というアフィリエイトサイトの編集者です。
一人暮らし・新生活向けの家電や生活便利グッズについて、比較・選び方記事を書きます。

厳守事項:
- 自分が実際にその商品を使用したかのような一人称の体験談(「私は使ってみて」「実際に使用した感想」等)は絶対に書かない。
  あくまで公開されている製品仕様・一般的な評価傾向・選び方の基準にもとづく客観的な比較記事とすること。
- 「絶対」「100%」「必ず」など効果を保証する断定表現は使わない。
- 特定の商品名を捏造しない。型番や具体的すぎる製品名を書く場合は一般的なカテゴリ表現(例:「コンパクトタイプの全自動洗濯機」)に留める。
- 医療的・健康的な効能を示唆しない。
- 出力は必ず指定のJSON形式のみ。説明文やコードブロックの記法(```)は付けない。
"""

USER_PROMPT_TEMPLATE = """次のキーワードで記事を作成してください。

キーワード: {keyword}
商品カテゴリ: {category}

以下のJSON形式で出力してください(キー名は厳守):
{{
  "title": "記事タイトル(32文字前後、キーワードを含む)",
  "meta_description": "検索結果に表示される説明文(100文字前後)",
  "intro": "導入文。読者の悩みに共感し記事の要点を提示する(150字程度)",
  "sections": [
    {{"heading": "見出し1", "body": "本文(300字程度、選び方のポイントなど)"}},
    {{"heading": "見出し2", "body": "本文(300字程度)"}},
    {{"heading": "見出し3", "body": "本文(300字程度)"}}
  ],
  "faq": [
    {{"q": "よくある質問1", "a": "回答"}},
    {{"q": "よくある質問2", "a": "回答"}}
  ],
  "conclusion": "まとめ文(150字程度)"
}}
"""


def load_keywords():
    with open(KEYWORDS_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_keywords(rows):
    with open(KEYWORDS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["keyword", "category", "status"])
        writer.writeheader()
        writer.writerows(rows)


def sanitize(text: str) -> str:
    """危険フレーズを含む文をまるごと落とし、残りの文だけをつなぎ直す。"""
    sentences = re.split(r"(?<=。)", text)
    kept = [s for s in sentences if not any(p in s for p in BANNED_PHRASES)]
    return "".join(kept).strip()


def sanitize_article(article: dict) -> dict:
    article["intro"] = sanitize(article["intro"])
    article["conclusion"] = sanitize(article["conclusion"])
    for s in article["sections"]:
        s["body"] = sanitize(s["body"])
    for qa in article.get("faq", []):
        qa["a"] = sanitize(qa["a"])
    return article


ARTICLE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "meta_description": {"type": "string"},
        "intro": {"type": "string"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"heading": {"type": "string"}, "body": {"type": "string"}},
                "required": ["heading", "body"],
            },
        },
        "faq": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"q": {"type": "string"}, "a": {"type": "string"}},
                "required": ["q", "a"],
            },
        },
        "conclusion": {"type": "string"},
    },
    "required": ["title", "meta_description", "intro", "sections", "faq", "conclusion"],
}


def call_claude(keyword: str, category: str) -> dict:
    """`claude -p` (Claude Codeのサブスクリプション認証) 経由で記事を生成する。
    ANTHROPIC_API_KEYの従量課金は使わず、CLAUDE_CODE_OAUTH_TOKENでの認証を前提とする。
    """
    prompt = USER_PROMPT_TEMPLATE.format(keyword=keyword, category=category)
    cmd = [
        "claude", "-p", prompt,
        "--append-system-prompt", SYSTEM_PROMPT,
        "--json-schema", json.dumps(ARTICLE_SCHEMA),
        "--output-format", "json",
        "--tools", "",
        "--no-session-persistence",
        "--model", MODEL,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed (exit {proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}")
    envelope = json.loads(proc.stdout)
    if envelope.get("is_error"):
        raise RuntimeError(f"claude CLI returned an error: {envelope}")
    return envelope["structured_output"]


def affiliate_box_html(keyword: str) -> str:
    q = quote_plus(keyword)
    links = []
    if AMAZON_ASSOC_TAG:
        links.append(
            f'<a class="aff-btn amazon" href="https://www.amazon.co.jp/s?k={q}&tag={AMAZON_ASSOC_TAG}" '
            f'rel="nofollow sponsored" target="_blank">Amazonで探す</a>'
        )
    else:
        links.append(
            f'<a class="aff-btn amazon disabled" href="https://www.amazon.co.jp/s?k={q}" '
            f'rel="nofollow" target="_blank">Amazonで探す(提携未設定)</a>'
        )
    if RAKUTEN_AFFILIATE_ID:
        links.append(
            f'<a class="aff-btn rakuten" href="https://search.rakuten.co.jp/search/mall/{q}/?affiliateId={RAKUTEN_AFFILIATE_ID}" '
            f'rel="nofollow sponsored" target="_blank">楽天市場で探す</a>'
        )
    else:
        links.append(
            f'<a class="aff-btn rakuten disabled" href="https://search.rakuten.co.jp/search/mall/{q}/" '
            f'rel="nofollow" target="_blank">楽天市場で探す(提携未設定)</a>'
        )
    return '<div class="affiliate-box">' + "".join(links) + "</div>"


ARTICLE_TEMPLATE = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>{title} | {site_name}</title>
<meta name="description" content="{meta_description}">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="../style.css">
</head>
<body>
<header><a href="../index.html">{site_name}</a></header>
<main>
<div class="disclosure">本記事はプロモーション(アフィリエイトプログラム)を含みます。掲載情報は公開されている製品情報等をもとに作成した比較・紹介コンテンツであり、効果・効能を保証するものではありません。</div>
<h1>{title}</h1>
<p class="intro">{intro}</p>
{affiliate_box_top}
{sections_html}
<h2>よくある質問</h2>
{faq_html}
<h2>まとめ</h2>
<p>{conclusion}</p>
{affiliate_box_bottom}
<p class="date">公開日: {pub_date}</p>
</main>
<footer><p>&copy; {site_name}</p></footer>
</body>
</html>
"""


def slugify(keyword: str) -> str:
    s = re.sub(r"[^\w]+", "-", keyword.strip())
    return s.strip("-") or "article"


def render_article(article: dict, keyword: str) -> str:
    sections_html = "\n".join(
        f"<h2>{html.escape(s['heading'])}</h2>\n<p>{html.escape(s['body'])}</p>"
        for s in article["sections"]
    )
    faq_html = "\n".join(
        f"<h3>{html.escape(qa['q'])}</h3>\n<p>{html.escape(qa['a'])}</p>"
        for qa in article.get("faq", [])
    )
    box = affiliate_box_html(keyword)
    return ARTICLE_TEMPLATE.format(
        title=html.escape(article["title"]),
        meta_description=html.escape(article["meta_description"]),
        intro=html.escape(article["intro"]),
        sections_html=sections_html,
        faq_html=faq_html,
        conclusion=html.escape(article["conclusion"]),
        affiliate_box_top=box,
        affiliate_box_bottom=box,
        site_name=html.escape(SITE_NAME),
        pub_date=date.today().isoformat(),
    )


def rebuild_index():
    files = sorted(ARTICLES_DIR.glob("*.html"), reverse=True)
    items = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        m = re.search(r"<h1>(.*?)</h1>", text)
        title = m.group(1) if m else f.stem
        items.append(f'<li><a href="articles/{f.name}">{title}</a></li>')
    body = "\n".join(items) if items else "<li>準備中です</li>"
    SITE_INDEX.write_text(
        f"""<!doctype html>
<html lang="ja">
<head><meta charset="utf-8"><title>{SITE_NAME}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="style.css"></head>
<body>
<header>{SITE_NAME}</header>
<main>
<div class="disclosure">本サイトはAmazonアソシエイト・楽天アフィリエイト等のプログラムを利用し、商品リンクからの購入により収益を得ることがあります。</div>
<h1>{SITE_NAME}</h1>
<ul>
{body}
</ul>
</main>
</body>
</html>
""",
        encoding="utf-8",
    )


def rebuild_sitemap():
    files = sorted(ARTICLES_DIR.glob("*.html"))
    urls = [f"  <url><loc>{SITE_URL}/</loc></url>"]
    for f in files:
        urls.append(f"  <url><loc>{SITE_URL}/articles/{f.name}</loc></url>")
    SITEMAP.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n",
        encoding="utf-8",
    )


def main():
    rows = load_keywords()
    pending = [r for r in rows if r["status"] == "pending"]
    if not pending:
        print("No pending keywords left. Add more rows to data/keywords.csv.")
        return 0

    target = pending[0]
    keyword, category = target["keyword"], target["category"]
    print(f"Generating article for: {keyword} ({category})")

    try:
        article = call_claude(keyword, category)
        article = sanitize_article(article)
    except Exception as e:
        print(f"Generation failed for '{keyword}': {e}", file=sys.stderr)
        return 1  # leave status=pending so it's retried next run

    slug = slugify(keyword)
    out_path = ARTICLES_DIR / f"{slug}.html"
    out_path.write_text(render_article(article, keyword), encoding="utf-8")

    for r in rows:
        if r is target:
            r["status"] = f"published:{date.today().isoformat()}"
    save_keywords(rows)

    rebuild_index()
    rebuild_sitemap()
    print(f"Published: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
