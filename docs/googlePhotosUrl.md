# Google Photos URL パラメーター完全ガイド

## 📝 概要

Google Photos共有URLから高品質な画像を取得するための技術仕様とベストプラクティス。

**作成日**: 2025年9月4日  
**最終更新**: 2025年9月4日

## 🔍 URLパラメーター仕様

### 基本構造
```
https://lh3.googleusercontent.com/pw/{IMAGE_ID}={PARAMETERS}?authuser=0
```

### パラメーターの種類

| パラメーター | 説明 | 例 | 用途 |
|-------------|-----|----|----|
| `s1621` | 簡易サイズ指定 | `=s1621` | 一辺最大1621pxで縦横比維持 |
| `s800-no-gm` | **🌟推奨** アスペクト比保持800px収まり | `=s800-no-gm` | 800x800内・高品質・軽量 |
| `w{WIDTH}-h{HEIGHT}-s-no-gm` | HDR対応（非推奨） | `=w800-h450-s-no-gm` | 高品質・指定サイズ |
| `w{WIDTH}-h{HEIGHT}` | 基本サイズ指定 | `=w800-h600` | 指定サイズに強制リサイズ |

### パラメーター詳細

#### 🌟 `s800-no-gm` (推奨)
- **`s800`**: 800x800ピクセル内に収まるサイズ指定
- **`no-gm`**: 高品質処理フラグ
- **利点**: アスペクト比自動保持・軽量・高速・高品質

#### 品質・サイズ比較例
```
旧方式: =s1621?authuser=0 (大きいが処理が重い)
新方式: =s800-no-gm?authuser=0 (適切なサイズで高品質)
```

## 📊 実測データ

### ファイルサイズ比較（同じ画像）
| パラメーター | サイズ | ファイルサイズ | 品質 |
|-------------|--------|--------------|------|
| `s1621` | 1621×1081px | 430KB | 標準 |
| `w800-h533-s-no-gm` | 800×533px | 490KB | 高品質HDR |

**重要**: HDR版はサイズが小さくてもファイルサイズが大きい = 高密度・高品質

## 🛠️ 実装方針

### 1. URL取得戦略
- **`google_photos_extractor.py`**: JavaScriptクリック + 7秒固定待機
- **推奨実行方法**: `--headless` オプション使用（安定性向上）
- **新方式**: 元サイズで取得後、`s800-no-gm`に変換

### 2. 画像ダウンロード戦略（簡素化）
- **`download_images_for_review.py`**: 
  1. URLを`s800-no-gm`形式に変換
  2. **1回のダウンロードで完了** ⭐
  3. 複雑なサイズ取得・再ダウンロード処理を廃止

### 3. 一括更新戦略
- **`bulk_hdr_update.py`**: 既存記事の一括最適化
  1. 記事内`=s1621`パターン検出
  2. **`=s800-no-gm`に直接変換** ⭐
  3. サイズ取得処理を廃止

## 📐 新しい変換ルール（大幅簡素化）

### シンプル変換式
```python
def generate_optimized_url(original_url):
    """s1621をs800-no-gmに変換するだけ"""
    if '=s1621?authuser=0' in original_url:
        return original_url.replace('=s1621?authuser=0', '=s800-no-gm?authuser=0')
    elif '=s1621' in original_url:
        return original_url.replace('=s1621', '=s800-no-gm')
    return original_url
```

### 変換例
```
変換前: https://lh3.googleusercontent.com/pw/ABC123=s1621?authuser=0
変換後: https://lh3.googleusercontent.com/pw/ABC123=s800-no-gm?authuser=0
```

**利点**: サイズ計算・アスペクト比計算が不要！

## ⚡ パフォーマンス最適化

### レスポンシブ対応サイズ
- **デスクトップ**: 800px幅で十分な画質
- **モバイル**: 自動的にスケーリング
- **読み込み速度**: 大きすぎない適切なサイズ

### ファイルサイズ vs 品質
- **方針**: ファイルサイズより品質を優先
- **理由**: HDRは解像度密度が高いため、小サイズでも高品質
- **結果**: より鮮明で美しい画像表示

## 🔧 スクリプト仕様

### google_photos_extractor.py
```python
# HDR対応の修正点
HDR_WAIT_TIME = 7  # 固定7秒待機
driver.execute_script("arguments[0].click();", element)  # JavaScriptクリック
```

### download_images_for_review.py
```python
# 新しいシンプル機能
def generate_optimized_url(original_url):
    """s1621をs800-no-gmに変換するだけの軽量処理"""
    return original_url.replace('=s1621?authuser=0', '=s800-no-gm?authuser=0')
# 1回のダウンロードで完了、複雑な再処理なし
```

### bulk_hdr_update.py
```python
# 一括更新機能
# 158個のURL処理で156個（98.7%）成功
# 21記事で159回の置換実行
```

## ✅ 実績データ

### 一括更新実績（2025年9月4日）
- **処理対象**: 21記事、158ユニークURL
- **成功率**: 98.7%（156/158）
- **更新ファイル**: 21個
- **総置換回数**: 159回
- **処理時間**: 約2分（URL解析含む）

### 品質向上効果確認済み
- **石垣島記事**: 13個のURL → HDR対応
- **燕岳登山記**: 31個のURL → HDR対応  
- **H3ロケット記事**: 全画像 → HDR対応

## 🚀 今後の運用方針（簡素化）

### 新規記事作成時
1. `google_photos_extractor.py`でURL取得（7秒待機・JavaScriptクリック）
2. `download_images_for_review.py`で自動最適化（`s800-no-gm`変換）
3. **1回のダウンロードで高品質画像取得完了** ⭐

### 既存記事更新時
1. `bulk_hdr_update.py --dry-run`で確認
2. `bulk_hdr_update.py`で一括更新実行（`s800-no-gm`変換）

## ⚠️ 制限事項と対処法

### 取得失敗する場合
- **原因**: URL期限切れ、認証エラー
- **対処**: 元URLを維持（自動フォールバック）
- **頻度**: 約1-2%（実績ベース）

### HDR効果が薄い場合
- **原因**: 元画像が低解像度、圧縮率が高い
- **対処**: ファイルサイズに関係なくHDR版を使用
- **方針**: 品質優先アプローチ

## 🎯 ベストプラクティス

### URL取得時
1. **7秒固定待機**: HDR処理完了を確実に待機
2. **JavaScriptクリック**: 確実な高解像度画像取得
3. **通常モード推奨**: ヘッドレスモードは不安定

### 画像最適化時
1. **800px幅統一**: ブログ表示に最適
2. **アスペクト比維持**: 元の縦横比を正確に保持
3. **品質優先**: ファイルサイズより画質重視

### 一括更新時
1. **dry-runテスト**: 必ず事前確認
2. **段階的実行**: 必要に応じて特定記事のみ処理
3. **Git活用**: 万が一の際はGitで復元

---

**管理者**: Claude Code  
**関連スクリプト**: `google_photos_extractor.py`, `download_images_for_review.py`, `bulk_hdr_update.py`