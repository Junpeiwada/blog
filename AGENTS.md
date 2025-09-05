# リポジトリガイドライン

エージェントワークフローと日本語レスポンス方針については `CLAUDE.md` を参照してください。

## プロジェクト構造・モジュール
- `posts/`: Markdownソースファイル（`YYYY-MM-DD-title.md`形式、YAMLフロントマター付き）
- `templates/`: Jinja2テンプレート（`base.html`, `post.html`, `index.html`）
- `scripts/`: ビルド・デプロイ・検証ツール（Python）
- `assets/` と `images/`: ソースCSS・画像（`docs/`にコピーされる）
- `docs/`: GitHub Pages用生成サイト（手動編集禁止）

## ビルド・テスト・開発
- `npm run ビルド`: サイトを`docs/`に生成
- `npm run プレビュー`: ビルドしてローカルプレビューサーバー起動
- `npm run 検証`: 記事フロントマター・画像パス等の基本チェック
- `npm run ビルドして公開`: フルビルド+公開
- Python直接実行（`source venv/bin/activate`後）: `python scripts/build.py [--serve]`, `python scripts/deploy.py`

## コーディングスタイル・命名規則
- Python: PEP 8準拠、4スペースインデント、`scripts/`内のファイル・関数は`snake_case`
- テンプレート: Jinja2ブロックを一貫して使用、共通レイアウトは`base.html`に
- 記事: ファイル名`YYYY-MM-DD-title.md`、画像パス形式`../images/filename.jpg`
- コンテンツ: YAMLフロントマターに`title`, `date`(YYYY-MM-DD), `category`, `description`必須、`tags`はリスト形式

## テストガイドライン
- プッシュ前に`npm run 検証`を実行、報告されたエラー・警告を修正
- `npm run プレビュー`でローカル確認、リンク・画像を目視チェック
- `docs/`配下の変更は必ずフレッシュビルド実行後にコミット

## コミット・プルリクエスト
- コミットスタイル例:
  - 新記事: `feat(post): add <タイトル>`
  - 記事更新: `chore(post): update <タイトル> - <変更内容>`
  - システム: `refactor(build): <範囲>` / `fix(validator): <問題>`
- PR要件: 明確な説明、関連Issue、検証手順（コマンド）、UI変更時はスクリーンショット

## セキュリティ・設定
- リポジトリ・記事内にシークレット情報なし、GitHub Pagesは`docs/`のみ公開
- `venv` + `pip install -r requirements.txt`使用、npm scripts用にNode >= 14
- 大容量メディア: `images/`にコミット、可能な限り外部ホットリンク避ける

## エージェント固有指示
- 最初に`CLAUDE.md`を読み、記事作成は`docs/ARTICLE_WORKFLOW.md`に従う
- `CLAUDE.md`の要求により日本語でコミュニケーション
- 公開前: `npm run 検証` → `npm run プレビュー`でプレビュー確認