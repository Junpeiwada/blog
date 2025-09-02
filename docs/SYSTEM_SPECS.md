# システム技術仕様

ブログシステムの技術仕様、アーキテクチャ、機能詳細です。

## 技術スタック

### フロントエンド
- **HTML**: Jinja2テンプレート生成
- **CSS**: Bootstrap 5.3 + カスタムスタイル
- **JavaScript**: Lunr.js（全文検索）、vanilla JS

### バックエンド
- **言語**: Python 3.8+
- **テンプレート**: Jinja2 3.1.6
- **Markdown**: markdown 3.8.2
- **シンタックスハイライト**: Pygments 2.19.2

### インフラ
- **ホスティング**: GitHub Pages
- **CDN**: GitHub Pages自動CDN
- **ドメイン**: github.io サブドメイン

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

## テンプレートシステム

### Jinja2継承システム

#### アーキテクチャ
```
base.html (親テンプレート)
├── post.html (記事ページ)
└── index.html (トップページ)
```

#### base.html（親テンプレート）
- **共通要素**: ヘッダー、ナビゲーション、フッター
- **CSS/JS読み込み**: 外部ライブラリ、カスタムスタイル
- **メタタグ**: SEO、OGP設定
- **ブロック定義**: content、title、meta等

#### post.html（記事テンプレート）
- **継承**: base.htmlを継承
- **記事固有要素**: タイトル、日付、カテゴリ、タグ
- **本文表示**: Markdown→HTML変換後の内容
- **ナビゲーション**: 前後の記事リンク

#### index.html（一覧テンプレート）
- **継承**: base.htmlを継承
- **記事カード**: サムネイル、タイトル、概要
- **フィルタリング**: カテゴリ、検索機能
- **ページネーション**: 将来実装予定

### テンプレート変数

#### 共通変数
```python
{
    'site_title': 'Junpei Wada\'s Blog',
    'site_url': 'https://junpeiwada.github.io/blog/',
    'posts': [post_objects],
    'categories': ['tech', 'travel', 'life'],
    'build_time': datetime.now()
}
```

#### 記事固有変数
```python
{
    'post': {
        'title': '記事タイトル',
        'date': datetime.date,
        'category': 'tech',
        'tags': ['Python', 'Web'],
        'description': 'SEO用説明文',
        'featured_image': '画像URL',
        'content': 'HTML変換済み本文',
        'url': 'posts/2024-01-01-title.html'
    }
}
```

## CSSアーキテクチャ

### 外部化システム

#### ファイル構成
```
assets/css/style.css          # ソースCSS
docs/assets/css/style.css     # 公開用（自動コピー）
```

#### 改修効果
- **ファイルサイズ削減**: 各HTMLから約3KB削減
- **キャッシュ効率化**: CSS独立キャッシュ
- **メンテナンス性**: 1ファイルで一元管理

### CSS構成

#### Bootstrap拡張
- **ベース**: Bootstrap 5.3 CDN
- **カスタマイズ**: 独自カラーパレット、タイポグラフィ
- **コンポーネント**: カード、ナビゲーション、ボタン

#### レスポンシブデザイン
- **ブレークポイント**: Bootstrap標準（xs, sm, md, lg, xl, xxl）
- **画像**: 自動リサイズ、アスペクト比維持
- **動画**: 16:9アスペクト比維持

## データフロー

### ビルドプロセス

#### 1. 記事処理
```python
# 1. Markdownファイル読み込み
for md_file in content/posts/:
    # 2. フロントマター解析
    metadata = parse_frontmatter(md_file)
    
    # 3. Markdown→HTML変換
    html_content = markdown.markdown(content)
    
    # 4. テンプレート適用
    rendered_html = template.render(post=metadata, content=html_content)
    
    # 5. HTMLファイル出力
    write_file(f'docs/posts/{filename}.html', rendered_html)
```

#### 2. インデックス生成
```python
# 1. 全記事メタデータ収集
all_posts = collect_all_posts()

# 2. カテゴリ別分類
categorized_posts = group_by_category(all_posts)

# 3. トップページ生成
index_html = index_template.render(posts=all_posts, categories=categorized_posts)

# 4. 検索インデックス生成
search_index = create_search_index(all_posts)
write_json('docs/search-index.json', search_index)
```

### デプロイフロー

#### GitHub Pagesワークフロー
1. **Git Push**: main ブランチにプッシュ
2. **GitHub Actions**: 自動デプロイ開始
3. **Jekyll処理**: GitHub側で処理（今回は使用しない）
4. **CDN配信**: 全世界のCDNノードに配信
5. **公開完了**: 数分後に反映完了

## パフォーマンス仕様

### 読み込み速度最適化

#### CSS最適化
- **外部化**: インラインCSSを外部ファイル化
- **CDN使用**: Bootstrap、Lunr.jsはCDN経由
- **キャッシュ**: ブラウザキャッシュ活用

#### 画像最適化
- **適切なサイズ**: Web表示に最適化
- **アスペクト比**: 元比率維持でリサイズ
- **遅延読み込み**: 将来実装予定

#### JavaScript最適化
- **非同期読み込み**: 検索機能のみ
- **ミニファイ**: 将来実装予定
- **キャッシュ**: ブラウザキャッシュ活用

### メトリクス目標

#### Core Web Vitals
- **LCP（Largest Contentful Paint）**: < 2.5秒
- **FID（First Input Delay）**: < 100ms
- **CLS（Cumulative Layout Shift）**: < 0.1

#### その他メトリクス
- **ページサイズ**: < 1MB（画像込み）
- **初回読み込み**: < 3秒
- **検索応答**: < 100ms

## セキュリティ仕様

### データ保護
- **機密情報**: 環境変数、設定ファイルで管理
- **画像EXIF**: 個人情報削除推奨
- **アクセスログ**: GitHub Pages標準ログのみ

### XSS対策
- **テンプレート**: Jinja2自動エスケープ
- **ユーザー入力**: 検索のみ（出力はエスケープ済み）
- **外部リンク**: `rel="noopener noreferrer"`

## 拡張性・将来計画

### 機能拡張予定
- **コメント機能**: Disqus or 自作システム
- **タグクラウド**: 人気タグの可視化
- **関連記事**: 機械学習ベース推薦
- **RSS/Atom**: フィード配信

### パフォーマンス改善
- **画像最適化**: WebP対応、自動圧縮
- **キャッシュ戦略**: Service Worker実装
- **CDN**: 独自CDN導入検討
- **PWA化**: オフライン対応

### システム改善
- **CMS化**: 管理画面の実装
- **API化**: ヘッドレスCMS化
- **マルチ言語**: 国際化対応
- **アナリティクス**: Google Analytics導入

---

**関連ガイド**:
- 開発・ビルド詳細 → [開発ガイド](DEVELOPMENT.md)
- 問題発生時 → [トラブルシューティング](TROUBLESHOOTING.md)
- 記事作成方法 → [記事作成ガイド](ARTICLE_GUIDE.md)