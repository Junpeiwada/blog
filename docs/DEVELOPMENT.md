# 開発・デプロイガイド

ブログ開発、ビルド、デプロイに関する詳細ガイドです。

## ディレクトリ構造

```
blog/
├── posts/                      # Markdownソースファイル
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

## 開発コマンド

### npm スクリプト（推奨）
```bash
# メインコマンド：ビルド + GitHub Pages公開
npm run ビルドして公開

# ビルドのみ（HTML生成）
npm run ビルド

# ローカルサーバー起動（プレビュー用）
npm run プレビュー

# 記事検証
npm run 検証
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

### 環境準備
```bash
# 初回セットアップ
cd /Users/junpeiwada/Documents/Project/blog
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 必要時：追加パッケージインストール
pip install selenium webdriver-manager  # Google Photos用
```

## VSCode統合

### タスク実行
- **コマンドパレット**: `Cmd+Shift+P` → `Tasks: Run Task`
- **ショートカット**: 
  - `Cmd+Shift+B`: ビルド
  - `Cmd+Shift+D`: デプロイ
  - `Cmd+Shift+S`: サーバー起動

### NPMスクリプトビュー
エクスプローラーの「NPM SCRIPTS」から直接実行可能

### タスク設定（.vscode/tasks.json）
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "ビルド",
            "type": "shell",
            "command": "npm",
            "args": ["run", "ビルド"],
            "group": {
                "kind": "build",
                "isDefault": true
            }
        },
        {
            "label": "デプロイ",
            "type": "shell",
            "command": "npm",
            "args": ["run", "ビルドして公開"]
        },
        {
            "label": "サーバー起動",
            "type": "shell",
            "command": "npm",
            "args": ["run", "プレビュー"]
        }
    ]
}
```

## Git操作

### 基本操作
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

### 推奨コミットメッセージ形式
```bash
# 新記事追加
git commit -m "新記事追加: 記事タイトル"

# 記事更新
git commit -m "記事更新: 記事タイトル - 修正内容"

# システム改修
git commit -m "システム改修: 機能名 - 変更内容"

# バグ修正
git commit -m "バグ修正: 問題の説明"
```

## CSS・テンプレートシステム

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

## ビルドシステム詳細

### build.py の動作
1. **テンプレート読み込み**: Jinja2テンプレートを初期化
2. **記事解析**: posts/ の全Markdownファイルを処理
3. **HTML生成**: 記事ごとにHTMLファイル生成
4. **インデックス生成**: トップページ（記事一覧）生成
5. **検索インデックス生成**: 全文検索用JSONファイル作成
6. **アセットコピー**: CSS・画像ファイルをdocs/へコピー

### deploy.py の動作
1. **ビルド実行**: build.pyを呼び出し
2. **Git操作**: 変更をステージング・コミット
3. **プッシュ**: GitHub Pagesへデプロイ
4. **ステータス確認**: デプロイ状況の確認

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

## パフォーマンス最適化

### ビルド最適化
- **増分ビルド**: 変更された記事のみ再生成（将来実装予定）
- **画像最適化**: 自動リサイズ・圧縮（将来実装予定）
- **CSS最適化**: ミニファイ・圧縮（将来実装予定）

### デプロイ最適化
- **並列処理**: 複数ファイルの同時処理
- **キャッシュ活用**: 未変更ファイルのスキップ
- **GitHub Pages**: 自動CDN配信

## セキュリティ・注意事項

### 機密情報
- API キーや個人情報を記事に含めない
- 位置情報の詳細な記述に注意
- 写真のExifデータ削除を推奨

### Git管理
- `venv/` は `.gitignore` で除外済み
- `__pycache__/` も除外済み
- 一時ファイルの管理に注意
- `scripts/tmp/` の定期的なクリーンアップ

## 依存関係

### Python パッケージ
```
jinja2==3.1.6      # HTMLテンプレート
markdown==3.8.2    # Markdown→HTML変換
pyyaml==6.0.2      # YAMLパース
pygments==2.19.2   # コードハイライト
MarkupSafe==3.0.2  # HTMLエスケープ
selenium           # Google Photos自動化用
webdriver-manager  # ChromeDriver管理用
pillow             # 画像処理用
requests           # HTTP通信用
```

### システム要件
- Python 3.8以上
- Git
- Chrome（Google Photos用）
- インターネット接続（GitHub Pages用）

## デバッグ・ログ

### ビルドデバッグ
```bash
# 詳細ログでビルド
python scripts/build.py --verbose

# 個別記事のみビルド
python scripts/build.py --no-clean

# サーバー起動ログ
python scripts/build.py --serve --verbose
```

### Git デバッグ
```bash
# コミット履歴確認
git log --oneline -10

# ブランチ状態確認
git branch -v

# リモート状態確認
git remote -v
```

---

**関連ガイド**:
- 記事作成詳細 → [記事作成ガイド](ARTICLE_GUIDE.md)
- システム詳細仕様 → [技術仕様](SYSTEM_SPECS.md)
- 問題が発生した → [トラブルシューティング](TROUBLESHOOTING.md)