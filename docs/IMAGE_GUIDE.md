# 画像管理ガイド

ブログ記事の画像管理、Google Photos連携、画像分析システムの詳細ガイドです。

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

例:
- **海水浴**: `2024-09-29-diving-01.jpg`
- **技術記事**: `2024-10-15-python-01.png`
- **旅行記事**: `2024-11-20-travel-01.jpg`

**利点**: 日付順ソート、記事との関連明確、一意性確保

### Markdownでの画像参照
```markdown
![説明文](../images/画像名.jpg)
```

**理由**: 記事ページ（`/docs/posts/`）から画像（`/docs/images/`）への相対パス

### 画像追加の手順
1. **画像ファイルを準備**: 適切なサイズ・形式に調整
2. **命名**: `YYYY-MM-DD-記事ID-連番.拡張子`形式
3. **配置**: `/blog/images/`ディレクトリに保存
4. **記事で参照**: `![説明](../images/ファイル名.jpg)`
5. **ビルド**: `python scripts/build.py`で自動的に`docs/images/`にコピー

## Google Photos統合システム

### 概要
Google Photosの共有URLから全ての画像の直接URLを自動抽出し、ブログ記事に使用可能な形式で取得するシステムです。

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
1. https://lh3.googleusercontent.com/pw/AP1GczN...=s1621?authuser=0
2. https://lh3.googleusercontent.com/pw/AP1GczM...=s1621?authuser=0
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
featured_image: "抽出された代表画像URL"
---

<!-- 元のGoogle Photosリンク: https://photos.app.goo.gl/YOUR_ORIGINAL_URL -->

記事の内容...

![画像の説明](https://lh3.googleusercontent.com/pw/抽出されたURL)
```

## Google Photos画像分析・記事作成統合システム

### 概要
Google Photosの共有URLから画像を抽出し、視覚的内容分析とEXIF情報を統合して、最適な記事を自動生成するシステムです。

### 統合ワークフロー（記事作成依頼時）

#### 1. 自動判定・実行フロー
```bash
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

#### 2. EXIF情報取得能力
- **DateTimeOriginal**: 正確な撮影時刻（IFD直接アクセス対応）
- **GPS情報**: 撮影位置（取得可能な場合）
- **カメラ情報**: メーカー、機種、撮影設定
- **Google Photos対応**: 隠されたEXIF情報も取得

#### 3. 視覚的分析プロセス
```bash
# 自動化された画像内容分析
mkdir -p scripts/tmp
for i, url in enumerate(image_urls, 1):
    curl -s "$url" -o "scripts/tmp/analysis_$i.jpg"
    # Claude Code の Read tool で内容確認
    # → 画像の具体的内容を把握
done
```

### 記事生成判断基準
- **時系列優先**: 撮影時刻がある場合は時系列構成
- **内容重視**: 画像の視覚的内容に基づく構成調整
- **トピック適応**: 画像内容から推測されるテーマに応じた文体
- **Write記事個性.md準拠**: 落ち着いた表現での記事作成

## 記事作成用画像ダウンロードスクリプト

### 概要
記事作成時に画像内容を効率的に確認するための専用スクリプト。複数画像を並列ダウンロードし、画像情報を表示します。

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

### 統合ワークフローでの活用
```bash
# 1. Google Photosから画像URL抽出
python scripts/google_photos_extractor.py "Google Photos URL" --headless

# 2. 抽出したURLで画像を一括ダウンロード・確認
python scripts/download_images_for_review.py --clean [抽出されたURL群]

# 3. scripts/tmp/の画像をReadツールで内容確認
# 4. 記事作成・公開
```

## 技術仕様

### Google Photos URL抽出システム

#### スクリプトの動作
1. **Chrome WebDriver起動**: 自動ブラウザ制御
2. **ページアクセス**: Google Photos共有URLにアクセス
3. **スクロール処理**: 遅延読み込みされる全画像を表示
4. **画像クリック**: 各画像をクリックして高解像度URL取得
5. **URL正規化**: `s1621`サイズに統一して出力

#### 出力URL仕様
- **サイズ**: `s1621` (長辺1621px、アスペクト比保持)
- **品質**: 高品質、透かしなし
- **認証**: `?authuser=0` (認証パラメータ)
- **形式**: Google Photos直接リンク

### アスペクト比保持対応

#### Google Photos URLパラメータ
- **改善前**: `w1621-h911-s-no-gm` (横向き強制、縦画像が潰れる)
- **改善後**: `s1621` (長辺1621px、アスペクト比保持)

#### 対応画像
- **横画像**: 元のアスペクト比でリサイズ
- **縦画像**: 元のアスペクト比でリサイズ（潰れない）
- **正方形**: 1621×1621pxでリサイズ

## 使用例

### 長良川花火大会記事作成例
```bash
# Google Photos URLから画像抽出
python scripts/google_photos_extractor.py "https://photos.app.goo.gl/4djm1jcdcEfvPPws6" --headless

# 抽出した7枚の画像を確認用ダウンロード
python scripts/download_images_for_review.py --clean [抽出されたURL群]

# 結果: scripts/tmp/に7枚の画像が保存され、詳細情報が表示
# Claude CodeのReadツールで内容確認し、記事作成
```

### 記事例（2025年8月の長良川花火大会）
```markdown
---
title: "長良川花火大会2025 - 撮影席からの絶景花火体験記"
date: 2025-08-09
category: travel
tags: [花火大会, 長良川, 岐阜, 撮影, イベント]
description: "2週間の花火大会がまとまった第3回目の長良川花火大会。"
featured_image: "https://lh3.googleusercontent.com/pw/AP1GczNRu..."
---

<!-- 元のGoogle Photosリンク: https://photos.app.goo.gl/4djm1jcdcEfvPPws6 -->

## 撮影席からの特別な体験

![長良川花火大会の開幕](https://lh3.googleusercontent.com/pw/AP1GczNRumwTujiaTpZZhyv6IjJVaVQxC31mQ7nkey9-iIBAY9MseUtPs8exlXGAZ2s8oExCTStB_pJsuPBHTnt0ArNa80XfZL8t-1mHn2l6G5v5J4toNdDH=s1621?authuser=0)
```

## 注意事項

### セキュリティ・プライバシー

#### Google Photos設定
- **共有設定**: 「リンクを知っている全員」に設定
- **ダウンロード**: 許可設定を確認
- **期限**: 共有リンクの有効期限に注意

#### プライバシー
- **個人情報**: 写真に位置情報や個人情報が含まれていないか確認
- **権利関係**: 使用権限のある写真のみ使用
- **公開範囲**: ブログ公開時の画像内容に配慮

### 自動化機能
- **build.py**: `images/` → `docs/images/`の自動コピー
- **画像検証**: 存在しない画像参照の検出（将来実装予定）
- **最適化**: 画像圧縮・リサイズ（将来実装予定）

### 推奨設定
- **外部画像**: Google Photos等の外部リンクはそのまま使用可能
- **画像サイズ**: Web表示に適したサイズ（推奨1920px以下）
- **ファイル形式**: JPG（写真）、PNG（スクリーンショット）を推奨

---

**関連ガイド**:
- 記事作成方法 → [記事作成ガイド](ARTICLE_GUIDE.md)
- スクリプト実行詳細 → [開発ガイド](DEVELOPMENT.md)
- エラーが発生した → [トラブルシューティング](TROUBLESHOOTING.md)