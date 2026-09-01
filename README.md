# ひとり暮らし家電・便利グッズ比較ラボ(自動アフィリエイトサイト)

Claude APIで毎週アフィリエイト記事を自動生成し、GitHub Pagesに自動公開する仕組みです。

## 仕組み

```
data/keywords.csv (ネタ帳)
    → GitHub Actions が毎週月曜に起動
    → generate_article.py が Claude API で記事を1本生成
    → 禁止表現フィルタで危険な表現を自動除去
    → articles/*.html に書き出し、index.html / sitemap.xml を更新
    → 自動で git commit & push → GitHub Pages に反映
```

完全自動公開のため、生成された記事は**人間のレビューなしにそのまま公開**されます。
その分のリスクを下げるため、以下を組み込んでいます:

- 一人称の体験談(「実際に使ってみて」等)を書かせないプロンプト設計
- 「絶対」「100%」「必ず治る」等の断定表現を検出して自動削除するフィルタ
- 全ページに景品表示法対応のアフィリエイト表示(プロモーション表記)を自動挿入
- 医療・健康効能を扱わない家電・生活雑貨ジャンルを選定(薬機法リスクの回避)

**それでも中身は月1回など定期的に人間が目視確認することを強く推奨します。**
`data/keywords.csv` の `status` 列で公開履歴を追えます。

## セットアップ手順(ここからはあなたの操作が必要です)

Claude Codeはアカウント作成やパスワード入力を代行できないため、以下はご自身で行ってください。

### 1. GitHubリポジトリを作る
1. https://github.com にログイン(アカウントがなければ作成)
2. 右上の「+」→「New repository」で空のリポジトリを作成(例: `affiliate-lifehack-site`)
3. このディレクトリ(`~/affiliate-lifehack-site`)の中身をpush:
   ```bash
   cd ~/affiliate-lifehack-site
   git init
   git add .
   git commit -m "Initial scaffold"
   git branch -M main
   git remote add origin https://github.com/<your-account>/affiliate-lifehack-site.git
   git push -u origin main
   ```
4. リポジトリの Settings → Pages で「Deploy from a branch」→ `main` / `/(root)` を選択して保存
   → `https://<your-account>.github.io/affiliate-lifehack-site/` で公開されます

### 2. Anthropic API キーを発行する
1. https://console.anthropic.com でAPIキーを発行(Claude Codeのサブスクとは別に、従量課金のAPIキーが必要です)
2. リポジトリの Settings → Secrets and variables → Actions → **Secrets** タブで
   `ANTHROPIC_API_KEY` を追加(値はここにしか保存されず、あなた以外は見られません)

### 3. サイト設定を Variables に登録
同じ画面の **Variables** タブで以下を追加(値は任意):
- `SITE_URL` = `https://<your-account>.github.io/affiliate-lifehack-site`
- `SITE_NAME` = `ひとり暮らし家電・便利グッズ比較ラボ`
- `CLAUDE_MODEL` = `claude-sonnet-5`(未設定でもこの値がデフォルトで使われます)

### 4. アフィリエイトプログラムに提携申請する(未提携とのことなので)
- **Amazonアソシエイト**: https://affiliate.amazon.co.jp/ から申請。審査には実際に動いているサイト(記事が数本ある状態)が必要なため、先に1〜2週間分の記事をActionsで生成してから申請するとスムーズです。
- **楽天アフィリエイト**: https://affiliate.rakuten.co.jp/ から登録(こちらは即日〜数日で使えることが多いです)
- 承認されたら発行されたトラッキングID/アフィリエイトIDを Variables に追加:
  - `AMAZON_ASSOC_TAG` = 発行された Associate Tag(例: `yourid-22`)
  - `RAKUTEN_AFFILIATE_ID` = 発行されたアフィリエイトID
- 未設定の間はリンクが「(提携未設定)」の非収益リンクとして表示されるだけで、サイトは問題なく動きます。

### 5. 動作確認
Actionsタブ → 左のワークフロー「Generate and publish article」→ 「Run workflow」で手動実行できます。
毎週月曜(JST火曜朝)に自動実行されるので、それ以降は基本的に何もしなくても記事が増えていきます。

## ネタ切れ対策
`data/keywords.csv` の行がすべて `published:...` になると新しい記事が生成されなくなります。
定期的にキーワード(1行 = 1記事)を追記してください。ジャンルを広げる場合は
`generate_article.py` の `SYSTEM_PROMPT` 内のサイトコンセプト説明も合わせて見直してください。

## ローカルでのテスト実行
```bash
cd ~/affiliate-lifehack-site
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-xxxx
python generate_article.py
open index.html
```
