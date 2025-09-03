# 記事作成ガイド

ブログ記事の作成から公開までの詳細手順です。

## 記事作成の流れ

### 1. 環境準備
```bash
cd /Users/junpeiwada/Documents/Project/blog
source venv/bin/activate
```

### 2. 記事日付の決定
**ユーザーが日付を明示した場合**: その日付を使用
**ユーザーが日付を明示しない場合**: 写真から日付を特定
- 画像分析ワークフローで撮影日を推定
- EXIF情報から撮影日時を抽出
- 画像内容から時期・季節を推定
- 複数画像の時系列比較で最適な日付を決定

### 3. 新記事作成
```bash
# content/posts/ に新しいMarkdownファイルを作成
# ファイル名: YYYY-MM-DD-article-title.md（特定された日付を使用）
```

### 4. サイトビルド・ローカル確認
```bash
# サイト生成
python scripts/build.py

# ローカル確認（オプション）
python scripts/build.py --serve
# http://localhost:8000 でプレビュー可能
```

### 5. デプロイ（推奨）
```bash
# 統合デプロイ（ビルド + コミット + プッシュ）
npm run ビルドして公開

# または手動デプロイ
python scripts/build.py
git add .
git commit -m "新記事追加: 記事タイトル"
git push origin main
```

### 6. 公開確認
- GitHub Pagesは数分でデプロイ完了
- https://junpeiwada.github.io/blog/ で確認

## 記事テンプレート

### 基本テンプレート
```yaml
---
title: "記事のタイトル"
date: 2024-XX-XX  # 写真から特定された日付を使用
category: "standard-category"  # docs/CATEGORY_GUIDE.md参照
tags: [タグ1, タグ2, タグ3]  # 必須（下記タグ付けルール参照）
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
- **tags必須**: すべての記事に適切なタグを付けることが必須
- **ファイル名**: `YYYY-MM-DD-title.md` 形式を厳守
- **日付**: ユーザーが明示しない場合は写真から特定された日付を使用

## タグ付けルール

**すべての記事に適切なタグを付けることが必須です。**

### タグ選択の基本方針
1. **記事の主要内容を表すタグ**: 読者が検索しそうなキーワード
2. **固有名詞**: 場所名、装備名、人物名など
3. **カテゴリを補完するタグ**: より具体的な分類
4. **イベント・活動タグ**: 体験や参加したことを表すタグ

### カテゴリ別タグ付け例

#### 旅行記
```yaml
# 航空祭の場合
tags: [航空祭, F-2, 築城基地, 編隊飛行, 航空自衛隊, イベント]

# 花火大会の場合  
tags: [花火大会, 長良川, 岐阜, 撮影, イベント]

# 観光旅行の場合
tags: [石垣島, 沖縄, 観光, 旅行, 海]
```

#### 海・潜水
```yaml
tags: [石鯛, 海釣り, 魚突き, ダイビング]
tags: [イシダイ, メバル, スピアフィッシング, 日本海]
```

#### 釣り
```yaml
tags: [海釣り, キジハタ, イシダイ, 初夏, 釣果]
tags: [釣り, 船釣り, ブリ, ジギング, 高手礁, うみんぴあ]
```

#### 登山・クライミング
```yaml
tags: [登山, 北アルプス, 燕岳, 山小屋泊, 表銀座, 槍ヶ岳]
tags: [西穂高, 独標, 新穂高ロープウェイ, 西穂山荘, 星景写真, 北アルプス, 1泊2日, 天の川]
```

#### ギア・道具
```yaml
tags: [モーラナイフ, ナイフ, キャンプ, アウトドア, レビュー]
```

#### クラフト・DIY
```yaml
tags: [骨格標本, DIY, 自然標本, 工作, 実験]
```

### タグ付けのチェックポイント
- ✅ 3-6個のタグを選択（多すぎず少なすぎず）
- ✅ 記事の内容を正確に表現している
- ✅ 読者が検索しそうなキーワードを含む
- ✅ 固有名詞（場所、装備、機体名など）を含む
- ✅ カテゴリと矛盾しない内容
- ❌ 関係ないタグは付けない
- ❌ 抽象的すぎるタグ（「体験」「感想」など）は避ける

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