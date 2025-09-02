# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the blog project.

## 重要な指示

このリポジトリで作業する際は、必ず日本語でレスポンスしてください。ユーザーとのコミュニケーションは全て日本語で行うことが必要です。

### 記事作成時の必須事項
- **画像がある記事には必ずfeatured_imageを設定する**: 記事に画像が含まれる場合は、フロントマターに`featured_image`フィールドを追加し、記事の代表画像のURLを設定してください。これはカード表示やSEO対策のために重要です。

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
├── assets/                     # 静的アセット（開発時）
│   └── css/
│       └── style.css          # メインスタイルシート
├── images/                     # ソース画像（開発時）
├── docs/                       # GitHub Pages出力（自動生成）
│   ├── index.html             # ブログトップページ
│   ├── posts/                 # 記事HTMLファイル
│   ├── assets/                # 静的アセット（自動生成）
│   │   └── css/
│   │       └── style.css      # コピーされたCSS
│   └── images/                # コピーされた画像
├── templates/                  # HTMLテンプレート（Jinja2継承システム）
│   ├── base.html              # 親テンプレート（共通レイアウト）
│   ├── post.html              # 記事テンプレート（base.html継承）
│   └── index.html             # 一覧テンプレート（base.html継承）
├── scripts/                    # ビルドスクリプト
│   ├── build.py               # サイト生成（CSS/画像コピー含む）
│   ├── deploy.py              # 統合デプロイ
│   ├── validate_post.py       # 記事検証スクリプト
│   ├── remove_duplicate_titles.py  # H1タイトル重複除去ツール
│   ├── google_photos_extractor.py  # Google Photos画像URL抽出ツール
│   ├── image_content_analyzer.py   # 画像内容・EXIF分析ツール
│   ├── tmp/                   # 画像分析用一時ディレクトリ
│   └── mountain_converter.py  # 山岳データ変換（一回限り使用）
├── .vscode/                    # VSCode設定（ローカル環境用、gitignore対象）
│   ├── tasks.json             # ビルド・デプロイタスク定義
│   └── keybindings.json       # キーボードショートカット設定
├── package.json                # npm設定・スクリプト定義
├── Write記事個性.md            # 記事作成ガイドライン（shi3zテイスト準拠）
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
featured_image: "画像URL"  # 画像がある記事では必須。記事の代表画像のURLを設定
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

## Google Photos画像分析・記事作成統合システム

### 概要
Google Photosの共有URLから画像を抽出し、視覚的内容分析とEXIF情報を統合して、最適な記事を自動生成するシステムです。

### 🚀 統合ワークフロー（ユーザーが記事作成を依頼した場合）

#### 1. **自動判定・実行フロー**
```bash
# ユーザー: "このGoogle Photosから記事を書いて"
# → 以下を自動実行

# Step 1: 画像URL抽出
python scripts/google_photos_extractor.py "https://photos.app.goo.gl/..." --headless

# Step 2: 画像内容・時刻分析  
python scripts/image_content_analyzer.py [抽出されたURL群] --topic "推測されたトピック" --suggest-structure

# Step 3: 視覚的分析（各画像を一時保存してRead）
mkdir -p scripts/tmp
curl -s [画像URL] -o scripts/tmp/image_1.jpg
# Read tool で画像内容を確認・分析

# Step 4: 統合分析結果から記事生成
# 時系列 + 視覚的内容 + トピック分析 → 記事作成
```

#### 2. **自動化判断レベル**
- **完全自動**: URL抽出、EXIF分析、基本的な記事構成
- **Claude判断**: 画像内容に応じた詳細度、記事の文体、構成の最適化
- **ユーザー確認**: 記事生成前に構成提案を提示（簡潔に）

#### 3. **視覚的分析の標準化**

##### 画像一時保存・分析プロセス
```bash
# 標準化された画像分析フロー
for i, url in enumerate(extracted_urls, 1):
    curl -s "$url" -o "scripts/tmp/temp_image_$i.jpg"
    # Read toolで画像内容確認
    # → 内容に応じた記事への組み込み
```

##### 内容記述レベルの判断基準
- **風景・建物**: 場所、時間帯、雰囲気の簡潔な描写
- **イベント・花火**: 演出内容、規模感、色彩の特徴
- **人物・活動**: プライバシーに配慮し、活動内容のみ
- **食事・製品**: 外観、特徴、使用状況
- **その他**: 写っている内容の本質的な特徴

### 🔧 技術仕様（統合システム）

#### 使用スクリプト
1. **`scripts/google_photos_extractor.py`**: URL抽出専用
2. **`scripts/image_content_analyzer.py`**: EXIF分析・記事構成提案
3. **統合処理**: Claude Codeが自動判断で両方を活用

#### EXIF情報取得能力
- **DateTimeOriginal**: 正確な撮影時刻（IFD直接アクセス対応）
- **GPS情報**: 撮影位置（取得可能な場合）
- **カメラ情報**: メーカー、機種、撮影設定
- **Google Photos対応**: 隠されたEXIF情報も取得

#### 視覚的分析プロセス
```bash
# 自動化された画像内容分析
mkdir -p scripts/tmp
for i, url in enumerate(image_urls, 1):
    curl -s "$url" -o "scripts/tmp/analysis_$i.jpg"
    # Claude Code の Read tool で内容確認
    # → 画像の具体的内容を把握
done
```

#### 記事生成判断基準
- **時系列優先**: 撮影時刻がある場合は時系列構成
- **内容重視**: 画像の視覚的内容に基づく構成調整
- **トピック適応**: 画像内容から推測されるテーマに応じた文体
- **Write記事個性.md準拠**: 落ち着いた表現での記事作成

### 🎯 実用例：長良川花火大会記事

#### 分析結果例
```
📊 画像分析結果:
- 総画像数: 7枚
- 撮影時間: 19:33:12 - 20:38:58 (約1時間)
- 内容: ワイドスターマイン、水中花火、フィナーレ等

📝 提案構成:
1. 花火大会開幕 (19:33) - 2枚
2. 前半戦の演出 (19:50) - 1枚  
3. メインのワイドスターマイン (20:01) - 1枚
4. 幻想的な中盤 (20:21) - 1枚
5. クライマックス・フィナーレ (20:30-20:38) - 2枚
```

#### 実際の記事反映
- **正確な撮影時刻**に基づく記事構成
- **画像内容**（煙の効果、色彩、演出規模）を記事に反映
- **適切な順序**での画像配置

### 📋 記事作成時の自動プロセス

#### Claude Codeが自動実行する内容
1. **Google Photos URL判定**: `photos.app.goo.gl`を含むURLを検出
2. **画像URL抽出**: `google_photos_extractor.py`実行
3. **EXIF・内容分析**: `image_content_analyzer.py`実行  
4. **視覚的分析**: 画像を一時保存してRead toolで内容確認
5. **記事構成決定**: 分析結果統合して最適な構成を判断
6. **記事生成**: Write記事個性.mdに従った文体で作成
7. **元URL記録**: HTMLコメントでGoogle Photos URLを記録

#### 🔧 **実際のコマンド例（新インスタンス向け）**
```bash
# 完全なワークフロー例
cd /Users/junpeiwada/Documents/Project/blog
source venv/bin/activate

# 1. URL抽出
python scripts/google_photos_extractor.py "https://photos.app.goo.gl/4djm1jcdcEfvPPws6" --headless

# 2. 時刻・構成分析  
python scripts/image_content_analyzer.py [抽出されたURL群] --topic "花火大会" --suggest-structure

# 3. 視覚的分析（複数画像）
mkdir -p scripts/tmp
curl -s "URL1" -o scripts/tmp/image_1.jpg
curl -s "URL2" -o scripts/tmp/image_2.jpg
# Read /Users/junpeiwada/Documents/Project/blog/scripts/tmp/image_X.jpg で内容確認

# 4. 統合して記事作成
# → 時系列 + 視覚的内容 + EXIF情報を統合した記事を生成
```

#### ユーザーへの確認ポイント
- **記事のトピック/テーマ**: 画像内容から推測して提示
- **撮影日時**: EXIFから取得した日時を記事日付に反映  
- **特別な要望**: 画像の特定の内容に焦点を当てたい場合

### 🎪 Claude Codeの自動判断基準

#### 統合システムを使用する条件
1. **Google Photos URLが提供された場合**
2. **「記事を書いて」「ブログを作成して」等の依頼**
3. **画像の内容分析が記事品質向上に寄与する場合**

#### 視覚的分析の詳細度判断
- **イベント・体験**: 詳細な内容描写（花火の種類、演出、雰囲気）
- **製品・レビュー**: 外観、特徴、使用状況の具体的描写
- **風景・旅行**: 場所の特徴、時間帯、印象的な要素
- **日常・ライフスタイル**: プライバシーに配慮し、適度な描写

#### 記事構成の自動最適化
- **時系列データあり**: 撮影時刻に基づく時間軸構成
- **時系列データなし**: 画像内容の変化・進行に基づく構成
- **混合**: 部分的な時系列＋内容分析の組み合わせ

### 💡 実装上の注意点

#### 自動化のバランス
- **過度な自動化を避ける**: ユーザーの意図を適切に確認
- **適切な提案**: 構成案は簡潔に提示、詳細な説明は避ける
- **柔軟性保持**: ユーザーの要望に応じて構成変更可能

#### プライバシー・セキュリティ
- **個人情報の配慮**: 人物、プライベート空間の適切な処理
- **GPS情報の取り扱い**: 位置情報は必要最小限の記載
- **一時ファイル管理**: `scripts/tmp/`の適切なクリーンアップ

## Google Photos画像URL抽出システム（従来システム）

### 概要
Google Photosの共有URLから全ての画像の直接URLを自動抽出し、ブログ記事に使用可能な形式で取得するシステムです。

### 使用可能スクリプト
- **ファイル**: `scripts/google_photos_extractor.py`
- **機能**: Google Photos共有URLから画像URLを自動抽出
- **技術**: Selenium WebDriver + Chrome自動制御

### 使用方法

#### 1. 依存関係の確認
```bash
# 仮想環境の確認・作成
source venv/bin/activate
pip install selenium webdriver-manager

# または新規仮想環境作成
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install selenium webdriver-manager
```

#### 2. URL抽出の実行
```bash
# 基本実行（ブラウザ表示あり）
python scripts/google_photos_extractor.py "https://photos.app.goo.gl/YOUR_URL"

# ヘッドレスモード（ブラウザ非表示、推奨）
python scripts/google_photos_extractor.py "https://photos.app.goo.gl/YOUR_URL" --headless
```

#### 3. 出力結果の活用
スクリプトは以下の形式で画像URLを出力します：
```
1. https://lh3.googleusercontent.com/pw/AP1GczN...=w1621-h911-s-no-gm?authuser=0
2. https://lh3.googleusercontent.com/pw/AP1GczM...=w1621-h911-s-no-gm?authuser=0
...
```

### 記事への適用手順

#### 1. Google Photos URLの取得
- Google Photosで写真アルバムを作成
- 「共有」→「リンクを作成」で共有URLを生成
- `https://photos.app.goo.gl/...` 形式のURLを取得

#### 2. 画像URL抽出
```bash
cd /Users/junpeiwada/Documents/Project/blog
source venv/bin/activate
python scripts/google_photos_extractor.py "共有URL" --headless
```

#### 3. Markdownファイルへの記録
**重要**: 記事のMarkdownファイルには必ず以下の形式でGoogle Photos元URLをコメントとして記録する：

```markdown
---
title: "記事タイトル"
date: 2025-XX-XX
category: travel
tags: [タグ1, タグ2]
description: "記事の説明"
---

<!-- 元のGoogle Photosリンク: https://photos.app.goo.gl/YOUR_ORIGINAL_URL -->

記事の内容...

![画像の説明](https://lh3.googleusercontent.com/pw/抽出されたURL)
```

#### 4. 画像の配置
抽出したURLをMarkdown記法で記事に埋め込み：
```markdown
![画像の説明](抽出されたGooglePhotoURL)
```

### 技術仕様

#### スクリプトの動作
1. **Chrome WebDriver起動**: 自動ブラウザ制御
2. **ページアクセス**: Google Photos共有URLにアクセス
3. **スクロール処理**: 遅延読み込みされる全画像を表示
4. **画像クリック**: 各画像をクリックして高解像度URL取得
5. **URL正規化**: `w1621-h911`サイズに統一して出力

#### 出力URL仕様
- **サイズ**: `w1621-h911` (横1621px×縦911px)
- **品質**: `-s-no-gm` (高品質、透かしなし)
- **認証**: `?authuser=0` (認証パラメータ)
- **形式**: Google Photos直接リンク

#### 利点
- **高画質**: 元の画像品質を維持
- **一括処理**: 複数画像を自動で一度に取得
- **URL永続性**: Google Photosの直接URLで安定アクセス
- **レスポンシブ対応**: 指定サイズで統一表示

## 記事作成用画像ダウンロードスクリプト

### 概要
記事作成時に画像内容を効率的に確認するための専用スクリプト。複数画像を並列ダウンロードし、画像情報を表示します。

### 使用スクリプト
- **ファイル**: `scripts/download_images_for_review.py`
- **機能**: 複数画像の並列ダウンロード・情報表示
- **保存先**: `scripts/tmp/` (自動作成)

### 使用方法

#### 基本使用
```bash
# 複数URLを指定してダウンロード
python scripts/download_images_for_review.py URL1 URL2 URL3

# tmpディレクトリをクリアしてからダウンロード
python scripts/download_images_for_review.py --clean URL1 URL2

# 並列数を指定（デフォルト: 5）
python scripts/download_images_for_review.py --max-workers 3 URL1 URL2
```

#### ファイルからURL読み込み
```bash
# URLリストファイルを作成
echo "URL1" > urls.txt
echo "URL2" >> urls.txt
echo "URL3" >> urls.txt

# ファイルから読み込んでダウンロード
python scripts/download_images_for_review.py --from-file urls.txt
```

### 出力仕様

#### ファイル名形式
`review_image_連番_ハッシュ.jpg`
- **例**: `review_image_01_80ad6141.jpg`
- **連番**: 01, 02, 03...で順序管理
- **ハッシュ**: URLのMD5ハッシュ（重複防止）

#### 表示される情報
- **画像サイズ**: 幅×高さ（ピクセル）
- **ファイル形式**: JPEG, PNG等
- **ファイルサイズ**: バイト数
- **ダウンロード成功/失敗**: エラー情報付き

### 記事作成での活用

#### 統合ワークフロー
```bash
# 1. Google Photosから画像URL抽出
python scripts/google_photos_extractor.py "Google Photos URL" --headless

# 2. 抽出したURLで画像を一括ダウンロード・確認
python scripts/download_images_for_review.py --clean [抽出されたURL群]

# 3. scripts/tmp/の画像をReadツールで内容確認
# 4. 記事作成・公開
```

#### Claude Codeでの使用
1. **URL抽出後**: 抽出されたURLをスクリプトに渡して一括ダウンロード
2. **画像確認**: `scripts/tmp/review_image_*.jpg` をReadツールで内容分析
3. **記事作成**: 分析結果を基に記事構成・画像選択を決定

### 技術仕様

#### 並列処理
- **ThreadPoolExecutor**: 並列ダウンロードで高速化
- **デフォルト並列数**: 5（`--max-workers`で調整可能）
- **タイムアウト**: 30秒

#### エラーハンドリング
- **ネットワークエラー**: 接続失敗、タイムアウト処理
- **画像形式エラー**: 破損ファイル、未対応形式の検出
- **権限エラー**: アクセス拒否、認証失敗の処理

#### ファイル管理
- **自動ディレクトリ作成**: `scripts/tmp/`が存在しない場合は自動作成
- **クリーンオプション**: `--clean`で既存ファイルを削除
- **重複防止**: URLハッシュでファイル名の一意性確保

### 使用例

#### モーラナイフ記事作成例
```bash
# Google Photos URLから画像抽出
python scripts/google_photos_extractor.py "https://photos.app.goo.gl/..." --headless

# 抽出した3枚の画像を確認用ダウンロード
python scripts/download_images_for_review.py --clean \
  "https://lh3.googleusercontent.com/pw/...=s1621?authuser=0" \
  "https://lh3.googleusercontent.com/pw/...=s1621?authuser=0" \
  "https://lh3.googleusercontent.com/pw/...=s1621?authuser=0"

# 結果: scripts/tmp/に3枚の画像が保存され、詳細情報が表示
# Claude CodeのReadツールで内容確認し、記事作成
```

### アスペクト比保持対応

#### Google Photos URLパラメータ
- **改善前**: `w1621-h911-s-no-gm` (横向き強制、縦画像が潰れる)
- **改善後**: `s1621` (長辺1621px、アスペクト比保持)

#### 対応画像
- **横画像**: 元のアスペクト比でリサイズ
- **縦画像**: 元のアスペクト比でリサイズ（潰れない）
- **正方形**: 1621×1621pxでリサイズ

### ダウンロードスクリプトのトラブルシューティング

#### よくある問題
1. **依存関係エラー**
   ```bash
   # 必要なパッケージをインストール
   pip install pillow requests
   ```

2. **ダウンロード失敗**
   - URLの有効性確認
   - ネットワーク接続確認
   - 認証パラメータ（`?authuser=0`）の有無確認

3. **権限エラー**
   ```bash
   # tmpディレクトリの権限確認
   ls -la scripts/tmp/
   chmod 755 scripts/tmp/
   ```

#### デバッグ方法
```bash
# 単一画像でテスト
python scripts/download_images_for_review.py "単一URL"

# 詳細ログ付きで実行
python scripts/download_images_for_review.py --max-workers 1 URL1 URL2
```

### トラブルシューティング

#### よくある問題
1. **ChromeDriver関連エラー**
   ```bash
   # WebDriverの再インストール
   pip uninstall webdriver-manager
   pip install webdriver-manager
   ```

2. **画像が検出されない**
   - Google Photosの共有設定を確認
   - URLが正しいかチェック
   - `--headless`フラグを外してブラウザ表示で確認

3. **権限エラー**
   ```bash
   # 仮想環境の再作成
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install selenium webdriver-manager
   ```

### 使用例

#### コマンド例
```bash
# 長良川花火大会の写真処理例
python scripts/google_photos_extractor.py "https://photos.app.goo.gl/4djm1jcdcEfvPPws6" --headless
```

#### 記事例（2025年8月の長良川花火大会）
```markdown
---
title: "長良川花火大会2025 - 撮影席からの絶景花火体験記"
date: 2025-08-09
category: travel
tags: [花火大会, 長良川, 岐阜, 撮影, イベント]
description: "2週間の花火大会がまとまった第3回目の長良川花火大会。"
---

<!-- 元のGoogle Photosリンク: https://photos.app.goo.gl/4djm1jcdcEfvPPws6 -->

## 撮影席からの特別な体験

![長良川花火大会の開幕](https://lh3.googleusercontent.com/pw/AP1GczNRumwTujiaTpZZhyv6IjJVaVQxC31mQ7nkey9-iIBAY9MseUtPs8exlXGAZ2s8oExCTStB_pJsuPBHTnt0ArNa80XfZL8t-1mHn2l6G5v5J4toNdDH=w1621-h911-s-no-gm?authuser=0)
```

### セキュリティ・注意事項

#### Google Photos設定
- **共有設定**: 「リンクを知っている全員」に設定
- **ダウンロード**: 許可設定を確認
- **期限**: 共有リンクの有効期限に注意

#### プライバシー
- **個人情報**: 写真に位置情報や個人情報が含まれていないか確認
- **権利関係**: 使用権限のある写真のみ使用
- **公開範囲**: ブログ公開時の画像内容に配慮

## YouTube動画埋め込みルール

### 標準埋め込み形式
記事内にYouTube動画を埋め込む際は、以下の形式を使用する。この形式により、写真と同じ幅でレスポンシブ表示される。

```html
<div style="position: relative; width: 100%; height: 0; padding-bottom: 56.25%; margin: 1rem 0;">
<iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 8px;" src="https://www.youtube.com/embed/VIDEO_ID" title="動画タイトル" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>
```

### スタイリング仕様
- **幅**: `width: 100%` で親要素の幅いっぱい（写真と同じ）
- **アスペクト比**: `padding-bottom: 56.25%` で16:9比率を維持
- **角丸**: `border-radius: 8px` で写真と同じスタイル
- **マージン**: `margin: 1rem 0` で写真と同じ上下間隔
- **レスポンシブ**: 全デバイスで適切に表示

### 使用例
```markdown
## 動画で見る燕岳登山

今回の登山の様子を動画でまとめましたので、まずはこちらをご覧ください。

<div style="position: relative; width: 100%; height: 0; padding-bottom: 56.25%; margin: 1rem 0;">
<iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 8px;" src="https://www.youtube.com/embed/ty3CS3eNpGU" title="燕岳登山動画" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>
```

## 記事の種類と表示ルール

### カテゴリ別表示ルール
- **`mountain-guide`**: 特別記事（メインカード表示）
- **`mountain`**: 個別山岳記事（カード非表示、直URLアクセス可能）
- **その他** (`tech`, `travel`, `life`等): 通常記事（カード表示）

### URL構造
- **記事一覧**: https://junpeiwada.github.io/blog/
- **個別記事**: https://junpeiwada.github.io/blog/posts/YYYY-MM-DD-title.html

## 開発コマンド

### npm スクリプト（推奨）
```bash
# メインコマンド：ビルド + GitHub Pages公開
npm run ビルドして公開

# ビルドのみ（HTML生成）
npm run build

# ローカルサーバー起動（プレビュー用）
npm run serve

# 開発モード（ビルド → サーバー起動）
npm run dev

# 記事検証
npm run validate

# エイリアス
npm run deploy    # = npm run ビルドして公開
npm run publish   # = npm run ビルドして公開
```

### Python 直接実行（従来方法）
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

### VSCode統合
- **コマンドパレット**: `Cmd+Shift+P` → `Tasks: Run Task`
- **ショートカット**: 
  - `Cmd+Shift+B`: ビルド
  - `Cmd+Shift+D`: デプロイ
  - `Cmd+Shift+S`: サーバー起動
- **NPMスクリプトビュー**: エクスプローラーから直接実行

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

## CSS・テンプレートシステム（2025年9月更新）

### テンプレート継承システム
**Jinja2テンプレート継承**を活用した効率的な管理システム:

#### 構成
- **`base.html`**: 親テンプレート（共通レイアウト）
- **`post.html`**: 記事ページ（base.html継承）  
- **`index.html`**: トップページ（base.html継承）

#### 利点
- **共通部分の一元管理**: ナビゲーション、フッター、CSS読み込みなど
- **メンテナンス性向上**: 共通部分の変更は1箇所のみ
- **コード重複削除**: DRY原則に基づく効率的な構造

### CSS外部化システム

#### ディレクトリ構造
```
blog/
├── assets/css/style.css        # ソースCSS（開発時）
└── docs/assets/css/style.css   # 公開用CSS（自動生成）
```

#### 改修前後の比較
**改修前**: 各HTMLに約80行のインラインCSS埋め込み
**改修後**: 1行のCSS読み込みリンクのみ

#### パフォーマンス向上
1. **ファイルサイズ削減**: 各HTMLから約3KB削減
2. **ブラウザキャッシュ**: CSSファイルの独立キャッシュ
3. **並列読み込み**: HTML/CSS同時ダウンロード
4. **メンテナンス性**: CSS変更時は1ファイルのみ修正

#### 自動化プロセス
1. `assets/css/style.css` でスタイル編集
2. `python scripts/build.py` 実行
3. 自動的に `docs/assets/css/` にコピー
4. テンプレートが正しいパスで参照

### 記事検証スクリプト

#### 使用方法
```bash
# 基本検証
python scripts/validate_post.py content/posts/記事名.md

# 表示予測付き検証
python scripts/validate_post.py content/posts/記事名.md --info
```

#### 検証項目
- ファイル名形式（YYYY-MM-DD-title.md）
- フロントマター構文
- 必須フィールド（title, date, category, description）
- 画像パス存在確認
- カテゴリ表示予測

## タイトル重複問題と解決方法

### 問題
記事のMarkdown内にH1タイトル（`# タイトル名`）があると、テンプレートのタイトルと重複表示される問題がありました。

### 解決方法
**scripts/remove_duplicate_titles.py**スクリプトで一括修正済み。

### 記事作成時の注意
- **記事内にH1タイトルを書かない**
- フロントマターの`title`のみ使用
- テンプレートが自動的にタイトル表示

### 既存記事の修正
```bash
# H1タイトル重複チェック・除去（必要時のみ）
python scripts/remove_duplicate_titles.py
```

### 記事作成ガイドライン
**Write記事個性.md**を参照。shi3zblogテイストに基づく記事スタイルを定義。

## 重要な注意事項

1. **山岳ガイドは特別記事**: 通常のブログフローとは別管理
2. **記事追加は簡単**: Markdownファイル作成 → `npm run ビルドして公開`
3. **自動化重視**: 手動HTML編集は避け、npmスクリプト経由で更新
4. **GitHub Pages**: /docs フォルダから自動デプロイ
5. **検索機能**: 記事追加時に自動でインデックス更新
6. **CSS/アセット管理**: assets/ディレクトリで一元管理、自動コピー
7. **タイトル管理**: 記事内のH1タイトル使用禁止、フロントマターのみ
8. **VSCode統合**: タスク・npm統合で効率的な開発環境