# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the blog project.

## 重要な指示

このリポジトリで作業する際は、必ず日本語でレスポンスしてください。ユーザーとのコミュニケーションは全て日本語で行うことが必要です。

# Junpei Wada's Blog プロジェクト

## プロジェクト概要
GitHub Pagesを使った個人ブログサイト。日本アルプス登山完全ガイドを特集記事として持ち、その他の技術・旅行・日記などの記事を公開。

## サイト情報
- **公開URL**: https://junpeiwada.github.io/blog/
- **リポジトリ**: https://github.com/Junpeiwada/blog
- **技術**: Python + Jinja2 + Bootstrap + GitHub Pages

## ディレクトリ構造

```
blog/
├── content/posts/              # Markdownソースファイル
│   ├── 2024-09-04-japanese-alps-complete-guide.md  # メイン山岳ガイド
│   ├── 2024-09-05-槍ヶ岳-guide.md                # 個別山岳記事
│   └── 2024-XX-XX-new-post.md                    # 通常ブログ記事
├── docs/                       # GitHub Pages出力（自動生成）
│   ├── index.html             # ブログトップページ
│   └── posts/                 # 記事HTMLファイル
├── templates/                  # HTMLテンプレート
│   ├── base.html              # 共通レイアウト
│   ├── post.html              # 記事テンプレート
│   └── index.html             # 一覧テンプレート
├── scripts/                    # ビルドスクリプト
│   ├── build.py               # サイト生成
│   ├── deploy.py              # 統合デプロイ
│   └── mountain_converter.py  # 山岳データ変換（一回限り使用）
├── requirements.txt            # Python依存関係
├── venv/                       # Python仮想環境
└── .gitignore                  # Git除外設定
```

## 通常ブログ記事の追加から公開までの流れ

### 1. 環境準備
```bash
cd /Users/junpeiwada/Documents/Project/blog
source venv/bin/activate
```

### 2. 新記事作成
```bash
# content/posts/ に新しいMarkdownファイルを作成
# ファイル名: YYYY-MM-DD-article-title.md
```

#### 記事テンプレート
```yaml
---
title: "記事のタイトル"
date: 2024-XX-XX
category: tech  # tech, travel, life, etc.
tags: [タグ1, タグ2, タグ3]
description: "記事の簡潔な説明（SEO用）"
---

# 記事のタイトル

ここに記事の内容を書きます。Markdown記法が使用可能です。

## 見出し

- リスト項目
- リスト項目

**太字** や *斜体* も使えます。

```code
コードブロックも対応
```

[リンク](https://example.com) も作成可能です。
```

### 3. サイトビルド・ローカル確認
```bash
# サイト生成
python scripts/build.py

# ローカル確認（オプション）
python scripts/build.py --serve
# http://localhost:8000 でプレビュー可能
```

### 4. デプロイ（推奨）
```bash
# 統合デプロイ（ビルド + コミット + プッシュ）
python scripts/deploy.py

# または手動デプロイ
python scripts/build.py
git add .
git commit -m "新記事追加: 記事タイトル"
git push origin main
```

### 5. 公開確認
- GitHub Pagesは数分でデプロイ完了
- https://junpeiwada.github.io/blog/ で確認

## 画像管理ルール

### ディレクトリ構造
```
blog/
├── images/                    # ソース画像（開発時）
│   ├── 2024-09-29-diving-01.jpg
│   ├── 2024-10-15-tech-01.png
│   └── 2024-11-20-travel-01.jpg
└── docs/
    └── images/               # 公開用画像（GitHub Pages、自動生成）
```

### 命名規則
**記事画像**: `YYYY-MM-DD-記事ID-連番.拡張子`
- **海水浴**: `2024-09-29-diving-01.jpg`
- **技術記事**: `2024-10-15-python-01.png`
- **旅行記事**: `2024-11-20-travel-01.jpg`
- **利点**: 日付順ソート、記事との関連明確、一意性確保

### Markdownでの画像参照
```markdown
![説明文](../images/画像名.jpg)
```
- **理由**: 記事ページ（`/docs/posts/`）から画像（`/docs/images/`）への相対パス
- **GitHub Pages対応**: docsがルートディレクトリになるため

### 画像追加の手順
1. **画像ファイルを準備**: 適切なサイズ・形式に調整
2. **命名**: `YYYY-MM-DD-記事ID-連番.拡張子`形式
3. **配置**: `/blog/images/`ディレクトリに保存
4. **記事で参照**: `![説明](../images/ファイル名.jpg)`
5. **ビルド**: `python scripts/build.py`で自動的に`docs/images/`にコピー

### 自動化機能
- **build.py**: `images/` → `docs/images/`の自動コピー
- **画像検証**: 存在しない画像参照の検出（将来実装予定）
- **最適化**: 画像圧縮・リサイズ（将来実装予定）

### 注意事項
- **外部画像**: Google Photos等の外部リンクはそのまま使用可能
- **画像サイズ**: Web表示に適したサイズ（推奨1920px以下）
- **ファイル形式**: JPG（写真）、PNG（スクリーンショット）を推奨

## 記事の種類と表示ルール

### カテゴリ別表示ルール
- **`mountain-guide`**: 特別記事（メインカード表示）
- **`mountain`**: 個別山岳記事（カード非表示、直URLアクセス可能）
- **その他** (`tech`, `travel`, `life`等): 通常記事（カード表示）

### URL構造
- **記事一覧**: https://junpeiwada.github.io/blog/
- **個別記事**: https://junpeiwada.github.io/blog/posts/YYYY-MM-DD-title.html

## 開発コマンド

### 基本コマンド
```bash
# 仮想環境アクティベート
source venv/bin/activate

# サイトビルド
python scripts/build.py

# ローカルサーバー起動
python scripts/build.py --serve --port 8000

# フルデプロイ
python scripts/deploy.py

# ビルドのみ（コミットしない）
python scripts/deploy.py --build-only

# ステータス確認
python scripts/deploy.py --status
```

### Git操作
```bash
# 状態確認
git status

# 変更をステージング
git add .

# コミット
git commit -m "記事追加: タイトル"

# GitHub Pages用プッシュ
git push origin main
```

## 特別記事（山岳ガイド）について

### 山岳ガイドの構成
- **メインガイド**: `2024-09-04-japanese-alps-complete-guide.md`
  - 日本アルプス全41山の一覧表
  - インタラクティブフィルタリング
  - 各山への個別記事リンク
- **個別山岳記事**: 41記事（槍ヶ岳、剱岳等）
  - 直URLでアクセス可能
  - メインガイドから「ガイドに戻る」リンク

### 山岳記事の特徴
- カテゴリ `mountain-guide` または `mountain`
- カード一覧には表示されない（山岳ガイドのみ表示）
- 直URLアクセス: `/posts/2024-09-XX-山名-guide.html`

## トラブルシューティング

### よくある問題

#### 1. 仮想環境エラー
```bash
# 仮想環境再作成
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. ビルドエラー
```bash
# 依存関係確認
pip list
pip install -r requirements.txt

# キャッシュクリア
rm -rf docs/*
python scripts/build.py
```

#### 3. GitHub Pages反映されない
- コミット・プッシュ後、数分待つ
- GitHub リポジトリの Settings > Pages で状態確認
- Actions タブでビルド状況確認

### デバッグ
```bash
# 詳細ログでビルド
python scripts/build.py --verbose

# 個別記事のみビルド
python scripts/build.py --no-clean
```

## セキュリティ・注意事項

### 機密情報
- API キーや個人情報を記事に含めない
- 位置情報の詳細な記述に注意
- 写真のExifデータ削除を推奨

### Git管理
- `venv/` は `.gitignore` で除外済み
- `__pycache__/` も除外済み
- 一時ファイルの管理に注意

## 依存関係

### Python パッケージ
```
jinja2==3.1.6      # HTMLテンプレート
markdown==3.8.2    # Markdown→HTML変換
pyyaml==6.0.2      # YAMLパース
pygments==2.19.2   # コードハイライト
MarkupSafe==3.0.2  # HTMLエスケープ
```

### システム要件
- Python 3.8以上
- Git
- インターネット接続（GitHub Pages用）

## 参考リンク

- [GitHub Pages ドキュメント](https://docs.github.com/pages)
- [Markdown 記法ガイド](https://www.markdownguide.org/)
- [Bootstrap ドキュメント](https://getbootstrap.com/docs/)
- [Jinja2 ドキュメント](https://jinja.palletsprojects.com/)

---

## 全文検索機能（Lunr.js）

### 概要
- **技術**: Lunr.js + 自動生成検索インデックス
- **対象**: 全記事（タイトル・本文・タグ・カテゴリ・説明文）
- **機能**: リアルタイム検索、ハイライト表示、カテゴリ・日付表示

### 検索の種類

#### 1. 全文検索（上部検索バー）
- **Lunr.js使用**: 全記事から高度な検索
- **対象範囲**: タイトル（重み10）、説明文（重み5）、タグ（重み3）、カテゴリ（重み2）、本文（重み1）
- **機能**: 
  - 2文字以上で検索開始
  - あいまい検索対応
  - 結果ハイライト
  - 最大10件表示

#### 2. ローカルフィルタ（下部検索バー）
- **JavaScript使用**: 表示中のカードをフィルタ
- **対象**: 現在表示されているカードのみ
- **用途**: カテゴリフィルタと組み合わせた絞り込み

### 検索インデックス生成

#### 自動生成プロセス
1. `python scripts/build.py` 実行時に自動生成
2. 全記事の内容を解析してJSON化
3. `docs/search-index.json` に出力
4. フロントエンドで読み込み・検索実行

#### インデックス内容
```json
[
  {
    "id": "2024-09-04-japanese-alps-complete-guide",
    "title": "日本アルプス登山完全ガイド",
    "content": "記事本文の抜粋（1000文字まで）",
    "description": "記事の説明文",
    "category": "mountain-guide",
    "tags": "登山 日本アルプス 百名山",
    "date": "2024-09-04",
    "url": "posts/2024-09-04-japanese-alps-complete-guide.html"
  }
]
```

### 検索UI仕様

#### グローバル検索バー
- **場所**: ページ上部（Hero Section下）
- **プレースホルダー**: "全記事から検索 (タイトル・本文・タグ)..."
- **検索結果**: ドロップダウン形式で表示
- **結果クリック**: 該当記事に直接移動

#### 結果表示内容
- **タイトル**: ハイライト付きで強調表示
- **メタ情報**: カテゴリ・日付
- **本文抜粋**: 150文字 + ハイライト
- **タグ**: バッジ形式で表示

### 検索パフォーマンス

#### 最適化設定
- **インデックスサイズ**: 本文は1000文字に制限
- **結果件数**: 最大10件表示
- **検索開始**: 2文字以上で実行
- **リアルタイム**: 入力と同時に検索

#### CDN使用
```html
<script src="https://cdn.jsdelivr.net/npm/lunr@2.3.9/lunr.min.js"></script>
```

### 使用方法

#### 基本検索
- **単語検索**: `槍ヶ岳` → 槍ヶ岳関連記事
- **複数キーワード**: `北アルプス 登山` → AND検索
- **部分マッチ**: `やり` → 槍ヶ岳がヒット

#### 高度な検索
- **フィールド指定**: `title:槍ヶ岳` → タイトルに槍ヶ岳を含む記事
- **カテゴリ**: `category:mountain` → 山岳カテゴリの記事
- **タグ**: `tags:百名山` → 百名山タグの記事

### 検索対象記事

#### 含まれる記事
- **山岳ガイド**: メイン山岳ガイド（重要度最高）
- **個別山岳記事**: 41の山岳個別記事
- **通常記事**: 技術・旅行・生活記事
- **魚釣り記事**: 海・釣り関連記事

#### 除外される要素
- **ナビゲーション**: ヘッダー・フッター
- **メタデータ**: HTMLタグ・属性
- **重複コンテンツ**: テンプレート共通部分

### メンテナンス

#### 記事追加時
- 新記事作成 → `python scripts/build.py` → 検索インデックス自動更新
- 検索対象に自動追加（特別な作業不要）

#### パフォーマンス監視
- インデックスファイルサイズ監視（推奨: 1MB以下）
- 記事数増加時の検索速度確認
- 必要に応じて本文抜粋文字数調整

### トラブルシューティング

#### 検索が動作しない
1. **ブラウザ開発者ツール確認**: コンソールエラーチェック
2. **search-index.json存在確認**: `docs/search-index.json`ファイル確認
3. **ネットワーク確認**: Lunr.js CDN読み込み確認

#### 検索結果がおかしい
1. **インデックス再構築**: `python scripts/build.py`で再生成
2. **記事内容確認**: Markdown記法の問題チェック
3. **文字エンコーディング**: UTF-8確認

## 重要な注意事項

1. **山岳ガイドは特別記事**: 通常のブログフローとは別管理
2. **記事追加は簡単**: Markdownファイル作成 → デプロイスクリプト実行
3. **自動化重視**: 手動HTML編集は避け、スクリプト経由で更新
4. **GitHub Pages**: /docs フォルダから自動デプロイ
5. **検索機能**: 記事追加時に自動でインデックス更新