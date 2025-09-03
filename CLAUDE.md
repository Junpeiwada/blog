# Claude Code ガイド - Junpei Wada's Blog

このリポジトリで作業する際は、必ず**日本語でレスポンス**してください。

## プロジェクト概要

GitHub Pagesを使った個人ブログサイト。日本アルプス登山完全ガイドを特集記事として持ち、その他の技術・旅行・日記などの記事を公開。

- **公開URL**: https://junpeiwada.github.io/blog/
- **リポジトリ**: https://github.com/Junpeiwada/blog
- **技術**: Python + Jinja2 + Bootstrap + GitHub Pages

## 🚨 記事作成時の必須チェックリスト

**記事作成を依頼された際は、必ず以下を確認・実行してください：**

### ✅ 記事作成前の確認
1. **画像URL抽出**: Google Photos URLが提供されている場合
   ```bash
   python scripts/google_photos_extractor.py "共有URL" --headless
   ```

2. **画像詳細分析（2段階プロセス）**: 画像と記事内容の正確性向上のため
   ```bash
   python scripts/download_images_for_review.py --clean [URL群]
   # → 詳細な画像分析ワークフロー実行（docs/IMAGE_ANALYSIS_WORKFLOW.md参照）
   ```
   
   **🔄 重要: 新しい2段階プロセス**
   - **Phase 1**: 画像分析MDファイル作成（必須）
   - **Phase 2**: 分析結果を基にした正確な記事作成
   
   **📁 重要: scripts/tmpディレクトリは自動削除しない**
   - 画像分析MDファイルは重要な品質管理資料
   - ユーザーが手動で管理・削除を実行

### ✅ 記事作成時の必須ルール
- **ファイル名**: `YYYY-MM-DD-article-title.md` 形式厳守
- **日付特定**: ユーザーが日付を明示しない場合は写真から日付を特定
  - 画像分析での撮影日推定
  - EXIF情報の確認
  - 画像内容からの時期推定
- **H1タイトル禁止**: 記事内に `# タイトル` は使用しない
- **featured_image必須**: 画像がある記事には必ず設定
- **Google Photos元URL記録**: コメントで元リンクを必ず記録
  ```markdown
  <!-- 元のGoogle Photosリンク: https://photos.app.goo.gl/... -->
  ```
- **カテゴリ統一**: 必ず標準分類から選択 → **[カテゴリ管理ガイド](docs/CATEGORY_GUIDE.md)を参照**
  - 全7カテゴリから適切なものを選択
  - 判断に迷う場合は分類基準を確認
  - フィルタとの連動を確保

### ✅ 記事完成後の必須確認
- フロントマター必須項目：`title`, `date`, `category`, `description`, `featured_image`
- 画像参照パス：`![説明](../images/ファイル名.jpg)` または Google Photos直接URL
- **画像分析品質チェック**: 画像内容と記事説明文の一致確認（docs/IMAGE_ANALYSIS_WORKFLOW.md のチェックリスト実行）
- URL重複チェック: 同一画像URLの重複使用なし
- ビルド・公開：`npm run ビルドして公開`

### 🔄 日本語対応
すべてのコミュニケーション、ファイル作成、コメントは日本語で行ってください。

## クイックスタート

### 記事作成の基本フロー（要チェックリスト確認）
```bash
# 1. 環境準備
cd /Users/junpeiwada/Documents/Project/blog
source venv/bin/activate

# 2. 画像処理（提供されている場合）
python scripts/google_photos_extractor.py "共有URL" --headless
python scripts/download_images_for_review.py --clean [URL群]

# 3. 2段階記事作成プロセス（画像品質向上）
# Phase 1: 画像分析MDファイル作成（scripts/tmp/image_analysis_日付-記事名.md）
# Phase 2: 分析結果を基にした記事作成（content/posts/YYYY-MM-DD-article-title.md）

# 4. ビルド・公開
npm run ビルドして公開
```

## 詳細ガイド

目的に応じて以下のガイドを参照してください：

### 📝 記事作成・分類管理
**→ [記事作成ガイド](docs/ARTICLE_GUIDE.md)**
- 記事作成の5ステップ
- テンプレートと記法
- YouTube動画埋め込み

**→ [画像分析ワークフロー](docs/IMAGE_ANALYSIS_WORKFLOW.md)** 🆕
- 2段階記事作成プロセス
- 画像と記事内容の正確性向上
- 品質チェックリスト

**→ [カテゴリ管理ガイド](docs/CATEGORY_GUIDE.md)**  
- 標準カテゴリ一覧と分類基準
- フィルタ連動システム
- カテゴリ変更・追加手順

### 🖼️ 画像管理
**→ [画像管理ガイド](docs/IMAGE_GUIDE.md)**
- Google Photos連携システム
- 画像分析・記事作成統合
- 命名規則とディレクトリ構造
- 自動化ワークフロー

### ⚙️ 開発・デプロイ
**→ [開発ガイド](docs/DEVELOPMENT.md)**
- npmコマンド一覧
- VSCode統合設定
- ビルド・デプロイ手順
- Git操作

### 🔧 システム仕様
**→ [技術仕様](docs/SYSTEM_SPECS.md)**
- 全文検索機能（Lunr.js）
- テンプレート継承システム
- CSS外部化システム
- 依存関係

### 🚨 トラブル対応
**→ [トラブルシューティング](docs/TROUBLESHOOTING.md)**
- よくある問題と解決方法
- エラー対応
- デバッグ手順

## ディレクトリ構造（概要）

```
blog/
├── content/posts/              # Markdownソースファイル
├── assets/css/                 # スタイルシート（開発時）
├── images/                     # ソース画像（開発時）
├── docs/                       # GitHub Pages出力（自動生成）
├── templates/                  # HTMLテンプレート
├── scripts/                    # ビルドスクリプト
├── docs/                       # 詳細ガイド集（このディレクトリ）
└── package.json                # npm設定・スクリプト定義
```

## 最初に読むべきガイド

1. **初回セットアップ**: [開発ガイド](docs/DEVELOPMENT.md) の「環境準備」
2. **記事を書く**: [記事作成ガイド](docs/ARTICLE_GUIDE.md)
3. **画像を追加**: [画像管理ガイド](docs/IMAGE_GUIDE.md)
4. **問題が発生**: [トラブルシューティング](docs/TROUBLESHOOTING.md)

---

**注意**: このファイルは全体の概要です。詳細な操作方法は各専用ガイドを参照してください。