# CLAUDE.md

このファイルは、このリポジトリでClaude Codeが作業する際のガイダンスを提供します。

## 重要な指示

このリポジトリで作業する際は、必ず日本語でレスポンスしてください。ユーザーとのコミュニケーションは全て日本語で行うことが必要です。

# ブログプロジェクト

## プロジェクト概要
日本アルプス登山ガイドをメインとしたPython製の静的サイトジェネレータベースのブログプロジェクト。

## プロジェクト構成

### ディレクトリ構造
```
blog/
├── content/posts/           # Markdownブログ記事
│   ├── 2024-09-01-blog-launch.md
│   ├── 2024-09-04-japanese-alps-complete-guide.md
│   └── 各山岳ガイド記事（剱岳、槍ヶ岳、白馬岳など）
├── scripts/                 # ビルド・デプロイスクリプト
│   ├── build.py            # メインビルドスクリプト
│   ├── deploy.py           # デプロイスクリプト  
│   └── mountain_converter.py # 山岳記事変換ツール
├── templates/              # Jinja2 HTMLテンプレート
│   ├── base.html          # ベーステンプレート
│   ├── index.html         # インデックスページ
│   └── post.html          # 記事詳細ページ
├── docs/                  # 生成されたHTML（GitHub Pages用）
├── venv/                  # Python仮想環境
└── requirements.txt       # Python依存関係
```

## 技術スタック
- **Python**: メインプログラミング言語
- **Jinja2**: HTMLテンプレートエンジン
- **Markdown**: コンテンツマークアップ
- **PyYAML**: YAML設定ファイル処理
- **Pygments**: シンタックスハイライト
- **GitHub Pages**: ホスティングプラットフォーム

## 開発コマンド

### 環境準備
```bash
# Python仮想環境の有効化
source venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

### ビルド・デプロイ
```bash
# ブログサイト生成
python scripts/build.py

# GitHub Pagesへデプロイ
python scripts/deploy.py

# 山岳記事の変換処理
python scripts/mountain_converter.py
```

## コンテンツ作成規則

### ブログ記事
- **ファイル命名**: `YYYY-MM-DD-記事タイトル.md`
- **場所**: `content/posts/`ディレクトリ
- **フォーマット**: Markdown形式
- **メタデータ**: YAML frontmatterで記事情報を記載

### 山岳ガイド記事の特徴
- 剱岳、槍ヶ岳、白馬岳、木曽駒ヶ岳、薬師岳、五竜岳、鹿島槍ヶ岳などの詳細ガイド
- ルート情報、難易度、アクセス方法などを体系的に整理
- mountain_converter.pyによる専用変換処理

## 開発時の注意点

### コンテンツ管理
- 新しい記事は必ず `content/posts/` に配置
- ファイル名は日付プレフィックス必須
- 山岳記事は専用コンバーターの使用推奨

### ビルドプロセス
- 記事追加後は必ず `python scripts/build.py` でビルド
- テンプレート変更時も同様にビルドが必要
- GitHub Pagesへの反映は `python scripts/deploy.py`

### 依存関係管理
- 新しいPythonパッケージ追加時はrequirements.txtを更新
- 仮想環境内での開発を徹底

## デプロイメント
- **ターゲット**: GitHub Pages
- **出力ディレクトリ**: `docs/`
- **URL**: 自動的にGitHub Pagesで公開
- **プロセス**: ローカルビルド → コミット → プッシュ → 自動反映