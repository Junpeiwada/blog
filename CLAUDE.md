# Claude Code ガイド - Junpei Wada's Blog

このリポジトリで作業する際は、必ず**日本語でレスポンス**してください。

## プロジェクト概要

GitHub Pagesを使った個人ブログサイト。日本アルプス登山完全ガイドを特集記事として持ち、その他の技術・旅行・日記などの記事を公開。

- **公開URL**: https://junpeiwada.github.io/blog/
- **リポジトリ**: https://github.com/Junpeiwada/blog
- **技術**: Python + Jinja2 + Bootstrap + GitHub Pages

## 重要な基本ルール

### 1. 記事作成時の必須事項
**画像がある記事には必ずfeatured_imageを設定する**: 記事に画像が含まれる場合は、フロントマターに`featured_image`フィールドを追加し、記事の代表画像のURLを設定してください。これはカード表示やSEO対策のために重要です。

### 2. タイトル管理
**記事内にH1タイトル（# タイトル）は使用禁止**: フロントマターの`title`のみ使用してください。テンプレートが自動的にタイトルを表示します。

### 3. 日本語対応
すべてのコミュニケーション、ファイル作成、コメントは日本語で行ってください。

## クイックスタート

### 新記事作成から公開まで
```bash
# 1. 環境準備
cd /Users/junpeiwada/Documents/Project/blog
source venv/bin/activate

# 2. 記事作成
# content/posts/YYYY-MM-DD-article-title.md を作成

# 3. ビルド・公開
npm run ビルドして公開
```

## 詳細ガイド

目的に応じて以下のガイドを参照してください：

### 📝 記事作成
**→ [記事作成ガイド](docs/ARTICLE_GUIDE.md)**
- 記事作成の5ステップ
- テンプレートと記法
- YouTube動画埋め込み
- カテゴリ別表示ルール

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