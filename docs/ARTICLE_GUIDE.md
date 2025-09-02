# 記事作成ガイド

ブログ記事の作成から公開までの詳細手順です。

## 記事作成の流れ

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
npm run ビルドして公開

# または手動デプロイ
python scripts/build.py
git add .
git commit -m "新記事追加: 記事タイトル"
git push origin main
```

### 5. 公開確認
- GitHub Pagesは数分でデプロイ完了
- https://junpeiwada.github.io/blog/ で確認

## 記事テンプレート

### 基本テンプレート
```yaml
---
title: "記事のタイトル"
date: 2024-XX-XX
category: tech  # tech, travel, life, etc.
tags: [タグ1, タグ2, タグ3]
description: "記事の簡潔な説明（SEO用）"
featured_image: "画像URL"  # 画像がある記事では必須
---

記事の内容をここに書きます。Markdown記法が使用可能です。

## 見出し

- リスト項目
- リスト項目

**太字** や *斜体* も使えます。

```code
コードブロックも対応
```

[リンク](https://example.com) も作成可能です。
```

### 重要な注意事項
- **記事内にH1タイトル（# タイトル）は使用禁止**: フロントマターの`title`のみ使用
- **featured_image必須**: 画像がある記事には必ず設定
- **ファイル名**: `YYYY-MM-DD-title.md` 形式を厳守

## カテゴリ別表示ルール

### 表示される記事
- **`tech`**: 技術記事（カード表示）
- **`travel`**: 旅行記事（カード表示）
- **`life`**: 生活・日記記事（カード表示）
- **その他通常カテゴリ**: カード表示

### 特別扱いの記事
- **`mountain-guide`**: 特別記事（メインカード表示）
- **`mountain`**: 個別山岳記事（カード非表示、直URLアクセス可能）

### URL構造
- **記事一覧**: https://junpeiwada.github.io/blog/
- **個別記事**: https://junpeiwada.github.io/blog/posts/YYYY-MM-DD-title.html

## YouTube動画埋め込み

### 標準埋め込み形式
記事内にYouTube動画を埋め込む際は、以下の形式を使用してください：

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

### 使用例
```markdown
## 動画で見る燕岳登山

今回の登山の様子を動画でまとめましたので、まずはこちらをご覧ください。

<div style="position: relative; width: 100%; height: 0; padding-bottom: 56.25%; margin: 1rem 0;">
<iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 8px;" src="https://www.youtube.com/embed/ty3CS3eNpGU" title="燕岳登山動画" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>
```

## 記事検証

### 検証スクリプトの使用
```bash
# 基本検証
python scripts/validate_post.py content/posts/記事名.md

# 表示予測付き検証
python scripts/validate_post.py content/posts/記事名.md --info
```

### 検証項目
- ファイル名形式（YYYY-MM-DD-title.md）
- フロントマター構文
- 必須フィールド（title, date, category, description）
- 画像パス存在確認
- カテゴリ表示予測

## よく使用するMarkdown記法

### 基本記法
```markdown
**太字**
*斜体*
~~打ち消し線~~

> 引用文

- リスト項目1
- リスト項目2

1. 番号付きリスト1
2. 番号付きリスト2

[リンクテキスト](URL)

![画像の説明](../images/image.jpg)
```

### コードブロック
````markdown
```python
def hello_world():
    print("Hello, World!")
```
````

### テーブル
```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| データ1 | データ2 | データ3 |
| データ4 | データ5 | データ6 |
```

## 記事作成のベストプラクティス

### SEO対策
- **description**: 記事の内容を120文字程度で要約
- **featured_image**: 記事の代表画像を必ず設定
- **タグ**: 関連するキーワードを3-5個設定

### 読みやすさ
- **見出し構造**: H2, H3を適切に使用して構造化
- **画像配置**: 説明文と合わせて適切に配置
- **改行**: 長い段落は避け、適度に改行

### メンテナンス
- **画像パス**: 相対パス（`../images/`）を使用
- **リンク**: 外部リンクは適切に設定
- **更新**: 内容が古くなった場合は適宜更新

---

**関連ガイド**:
- 画像を追加したい → [画像管理ガイド](IMAGE_GUIDE.md)
- ビルド・デプロイ詳細 → [開発ガイド](DEVELOPMENT.md)
- 問題が発生した → [トラブルシューティング](TROUBLESHOOTING.md)