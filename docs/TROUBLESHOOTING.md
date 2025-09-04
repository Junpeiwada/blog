# トラブルシューティング

ブログシステムでよく発生する問題と解決方法です。

## よくある問題と解決方法

### 1. 仮想環境エラー

#### 問題: `source venv/bin/activate` が失敗する
```bash
# エラー例
bash: venv/bin/activate: No such file or directory
```

#### 解決方法
```bash
# 仮想環境を再作成
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 問題: パッケージインストールエラー
```bash
# エラー例
ERROR: Could not install packages due to an EnvironmentError
```

#### 解決方法
```bash
# 権限の問題の場合
pip install --user -r requirements.txt

# または仮想環境を確認
which python  # 仮想環境のpythonか確認
pip list       # インストール済みパッケージ確認
```

### 2. ビルドエラー

#### 問題: `python scripts/build.py` が失敗する
```bash
# エラー例
ModuleNotFoundError: No module named 'jinja2'
```

#### 解決方法
```bash
# 依存関係確認・再インストール
pip list
pip install -r requirements.txt

# 個別インストール
pip install jinja2 markdown pyyaml pygments
```

#### 問題: テンプレートエラー
```bash
# エラー例
jinja2.exceptions.TemplateNotFound: base.html
```

#### 解決方法
```bash
# テンプレートディレクトリ確認
ls -la templates/
# base.html, post.html, index.html が存在するか確認

# 権限確認
chmod 644 templates/*.html
```

#### 問題: Markdownファイル解析エラー
```bash
# エラー例
yaml.scanner.ScannerError: mapping values are not allowed here
```

#### 解決方法
```bash
# フロントマターの記法確認
# 正しい形式:
---
title: "記事タイトル"
date: 2024-01-01
category: tech
---

# 間違った形式（例）:
---
title: 記事タイトル（引用符なし、特殊文字含む）
date: 2024/01/01（ハイフンでなくスラッシュ）
---
```

### 3. GitHub Pages反映されない

#### 問題: プッシュ後にサイトが更新されない

#### 解決方法
1. **GitHub リポジトリで確認**
   - Settings > Pages でソースが `main` ブランチの `/docs` フォルダになっているか確認
   - Actions タブでビルド状況確認

2. **ローカルで確認**
```bash
# docs ディレクトリに正しくファイルが生成されているか
ls -la docs/
ls -la docs/posts/

# 最新のコミットが含まれているか
git log --oneline -5
git status
```

3. **強制更新**
```bash
# キャッシュクリア後再ビルド
rm -rf docs/*
python scripts/build.py
git add .
git commit -m "再ビルド: GitHub Pages更新"
git push origin main
```

#### 問題: 404 Not Found エラー

#### 解決方法
```bash
# docs/index.html が存在するか確認
ls -la docs/index.html

# URLパスの確認
# 正: https://junpeiwada.github.io/blog/
# 誤: https://junpeiwada.github.io/blog/index.html
```

### 4. Google Photos関連エラー

#### 問題: ChromeDriver エラー
```bash
# エラー例
selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH
```

#### 解決方法
```bash
# WebDriverの再インストール
pip uninstall webdriver-manager
pip install webdriver-manager

# 手動で確認
python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"
```

#### 問題: 画像が検出されない
```bash
# エラー例
No images found on the page
```

#### 解決方法
1. **Google Photos設定確認**
   - 共有設定が「リンクを知っている全員」になっているか
   - アルバムが空でないか

2. **URLの確認**
   - `https://photos.app.goo.gl/` で始まる正しい共有URLか
   - URLが有効期限内か

3. **デバッグモード実行**
```bash
# ヘッドレスモードを無効にして確認
python scripts/google_photos_extractor.py "URL" 
# ブラウザが開いて動作を確認できる
```

#### 問題: SSL証明書エラー
```bash
# エラー例
SSL: CERTIFICATE_VERIFY_FAILED
```

#### 解決方法
```bash
# 証明書の更新（macOS）
/Applications/Python\ 3.x/Install\ Certificates.command

# または一時的に回避
pip install --trusted-host pypi.org --trusted-host pypi.python.org certifi
```

### 5. 画像関連問題

#### 問題: 画像が表示されない

#### 解決方法
1. **パスの確認**
```markdown
# 正しい相対パス
![説明](../images/image.jpg)

# 間違ったパス例
![説明](images/image.jpg)        # 相対パスが違う
![説明](/images/image.jpg)       # 絶対パスは使用しない
```

2. **ファイル存在確認**
```bash
# 元ファイルの存在確認
ls -la images/
# 公開用ファイルの存在確認
ls -la docs/images/
```

3. **自動コピーの確認**
```bash
# ビルド時に画像が正しくコピーされるか確認
python scripts/build.py --verbose
```

#### 問題: 画像サイズが大きすぎる

#### 解決方法
```bash
# 画像サイズ確認
du -sh images/*

# 推奨: 1920px以下、1MB以下に調整
# macOS の場合
sips -Z 1920 images/large_image.jpg
```

### 6. npm スクリプトエラー

#### 問題: `npm run ビルドして公開` が失敗する

#### 解決方法
1. **Node.js・npm確認**
```bash
node --version
npm --version

# npm キャッシュクリア
npm cache clean --force
```

2. **package.json確認**
```bash
# package.jsonの存在確認
ls -la package.json

# スクリプト定義確認
cat package.json | grep -A 10 '"scripts"'
```

3. **権限の問題**
```bash
# npm の権限確認
ls -la node_modules/
chmod -R 755 node_modules/
```

### 7. 検索機能の問題

#### 問題: 検索が動作しない

#### 解決方法
1. **検索インデックス確認**
```bash
# search-index.json の存在確認
ls -la docs/search-index.json

# 内容確認（最初の数行）
head -20 docs/search-index.json
```

2. **ブラウザ開発者ツール確認**
   - F12 > Console タブ
   - JavaScript エラーの確認
   - ネットワークタブで search-index.json の読み込み確認

3. **Lunr.js CDN確認**
```bash
# CDN接続確認
curl -I https://cdn.jsdelivr.net/npm/lunr@2.3.9/lunr.min.js
```

### 8. CSS・スタイル問題

#### 問題: スタイルが適用されない

#### 解決方法
1. **CSS ファイル確認**
```bash
# ソースCSS
ls -la assets/css/style.css
# 公開用CSS
ls -la docs/assets/css/style.css

# 自動コピーの確認
python scripts/build.py
```

2. **ブラウザキャッシュクリア**
   - Cmd+Shift+R (macOS) で強制リロード
   - 開発者ツール > Network タブで CSS読み込み確認

3. **CSS構文確認**
```bash
# CSS構文チェック（基本的な確認）
grep -n "{" assets/css/style.css | wc -l  # 開始ブレース数
grep -n "}" assets/css/style.css | wc -l  # 終了ブレース数
# 数が一致するか確認
```

## デバッグ方法

### 1. 詳細ログでビルド
```bash
# build.py の詳細ログ
python scripts/build.py --verbose

# 特定記事のみビルド
python scripts/build.py --single posts/2024-01-01-test.md
```

### 2. ローカルサーバーでテスト
```bash
# ローカルサーバー起動
python scripts/build.py --serve

# 別ターミナルで確認
curl http://localhost:8000
curl http://localhost:8000/search-index.json
```

### 3. Git 操作デバッグ
```bash
# コミット履歴確認
git log --oneline -10

# ファイル変更確認
git status
git diff

# ブランチ状態確認
git branch -v
git remote -v
```

### 4. Python環境デバッグ
```bash
# Python バージョン確認
python --version
which python

# パッケージ詳細確認
pip list | grep jinja2
pip show jinja2

# インポートテスト
python -c "import jinja2; print(jinja2.__version__)"
```

## 緊急対処方法

### サイトが完全にダウンした場合
1. **最後の正常コミットに戻す**
```bash
# 最近のコミット確認
git log --oneline -10

# 正常だったコミットにリセット
git reset --hard COMMIT_HASH
git push --force-with-lease origin main
```

2. **クリーンな状態から再構築**
```bash
# 全削除して再生成
rm -rf docs/*
python scripts/build.py
git add .
git commit -m "緊急修復: サイト再構築"
git push origin main
```

### データを失った場合
1. **Git履歴から復旧**
```bash
# 削除されたファイルを検索
git log --diff-filter=D --summary | grep delete

# 特定ファイルを復旧
git checkout COMMIT_HASH -- path/to/file
```

2. **バックアップの活用**
   - GitHubリポジトリから最新版をクローン
   - ローカルバックアップがあれば活用

## 予防策

### 1. 定期的なバックアップ
```bash
# ローカルバックアップ作成
rsync -av /Users/junpeiwada/Documents/Project/blog/ ~/backups/blog-$(date +%Y%m%d)/
```

### 2. テスト環境での確認
```bash
# 本番プッシュ前にローカルで確認
python scripts/build.py --serve
# http://localhost:8000 で動作確認後にプッシュ
```

### 3. 段階的デプロイ
```bash
# 1. ビルドのみ
python scripts/build.py

# 2. ローカル確認
python scripts/build.py --serve

# 3. デプロイ
git add .
git commit -m "..."
git push origin main
```

---

**さらにサポートが必要な場合**:
- [記事作成ガイド](ARTICLE_GUIDE.md) - 記事作成で問題が発生
- [画像管理ガイド](IMAGE_GUIDE.md) - 画像関連で問題が発生
- [開発ガイド](DEVELOPMENT.md) - ビルド・デプロイで問題が発生
- [技術仕様](SYSTEM_SPECS.md) - システム仕様を詳しく知りたい