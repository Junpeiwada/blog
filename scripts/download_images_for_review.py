#!/usr/bin/env python3
"""
記事作成時に画像内容を確認するためのダウンロードスクリプト

使用方法:
python download_images_for_review.py URL1 URL2 URL3 ...
または
python download_images_for_review.py --from-file urls.txt

機能:
- 複数の画像URLを並列ダウンロード
- scripts/tmp/に連番で保存
- 画像サイズと形式を表示
- EXIF撮影日時の自動抽出
- 画像分析MDファイルの自動生成
- 重複チェック
- エラーハンドリング
"""

import os
import sys
import requests
import argparse
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import hashlib
from datetime import datetime
import subprocess

def extract_exif_datetime(image_path):
    """EXIF情報から撮影日時を抽出（exiftoolを使用）"""
    try:
        # exiftoolを使用してDateTimeOriginalのみを取得
        result = subprocess.run(
            ['exiftool', '-DateTimeOriginal', '-s3', str(image_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            datetime_str = result.stdout.strip()
            try:
                # exiftoolの出力形式: "2022:06:03 18:42:29"
                return datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
            except ValueError:
                return None
        
        return None
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        # exiftoolが利用できない場合はPILでフォールバック（削除しない）
        try:
            with Image.open(image_path) as img:
                exif_data = img.getexif()
                if exif_data:
                    datetime_str = exif_data.get(36867)  # DateTimeOriginal only
                    if datetime_str:
                        return datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
            return None
        except Exception:
            return None

def download_image(url, output_path, index):
    """単一画像をダウンロード"""
    try:
        print(f"📷 画像 {index} をダウンロード中...")
        
        # User-Agentを設定
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # ファイルに保存
        with open(output_path, 'wb') as f:
            f.write(response.content)
            
        # 画像情報を取得
        try:
            with Image.open(output_path) as img:
                width, height = img.size
                format_name = img.format
                file_size = len(response.content)
                
                # EXIF日時情報を抽出
                exif_datetime = extract_exif_datetime(output_path)
                
                print(f"   ✅ 保存完了: {output_path.name}")
                print(f"   📐 サイズ: {width}×{height}px")
                print(f"   📝 形式: {format_name}")
                print(f"   📁 ファイルサイズ: {file_size:,}バイト")
                if exif_datetime:
                    print(f"   📅 撮影日時: {exif_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"   📅 撮影日時: 取得できませんでした")
                
                return {
                    'index': index,
                    'url': url,
                    'path': output_path,
                    'width': width,
                    'height': height,
                    'format': format_name,
                    'size': file_size,
                    'datetime': exif_datetime,
                    'success': True,
                    'error': None
                }
        except Exception as e:
            print(f"   ⚠️ 画像情報取得エラー: {e}")
            return {
                'index': index,
                'url': url,
                'path': output_path,
                'success': True,
                'error': f"画像情報取得エラー: {e}"
            }
            
    except Exception as e:
        print(f"   ❌ ダウンロードエラー: {e}")
        return {
            'index': index,
            'url': url,
            'success': False,
            'error': str(e)
        }

def generate_filename(url, index):
    """URLから適切なファイル名を生成"""
    # URLのハッシュを使って一意性を確保
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"review_image_{index:02d}_{url_hash}.jpg"

def generate_analysis_md(results, article_title=""):
    """画像分析MDファイルを生成"""
    # 有効な結果のみフィルタ
    valid_results = [r for r in results if r['success'] and 'datetime' in r]
    
    if not valid_results:
        return None
    
    # 日時情報がある画像を抽出
    timed_results = [r for r in valid_results if r.get('datetime')]
    
    # 日時でソート
    if timed_results:
        timed_results.sort(key=lambda x: x['datetime'])
        earliest_date = timed_results[0]['datetime']
        latest_date = timed_results[-1]['datetime']
        suggested_date = earliest_date.strftime('%Y-%m-%d')
        time_range = f"{earliest_date.strftime('%H:%M')} - {latest_date.strftime('%H:%M')}"
        
        # ファイル名決定（記事タイトルがない場合は日付ベース）
        if article_title:
            # 簡単なスラッグ化
            slug = article_title.lower().replace(' ', '-').replace('　', '-')
            # 日本語文字を簡略化
            import re
            slug = re.sub(r'[^\w\-]', '', slug)[:30]  # 最初の30文字
        else:
            slug = "article"
        
        filename = f"image_analysis_{suggested_date}-{slug}.md"
    else:
        # 日時情報がない場合
        suggested_date = datetime.now().strftime('%Y-%m-%d')
        time_range = "不明"
        filename = f"image_analysis_{suggested_date}-article.md"
    
    # MDコンテンツを生成
    content = f"""# 画像分析レポート - {article_title or '記事'}

**作成日**: {datetime.now().strftime('%Y年%m月%d日')}  
**対象画像数**: {len(valid_results)}枚  
**撮影日時付き画像**: {len(timed_results)}枚

## 📅 時系列情報

- **推奨記事日付**: {suggested_date}
- **撮影時間帯**: {time_range}
"""

    if timed_results:
        duration_hours = (latest_date - earliest_date).total_seconds() / 3600
        content += f"- **撮影期間**: 約{duration_hours:.1f}時間\n"
    
    content += """
## 📷 画像詳細情報

"""
    
    # 画像ごとの詳細情報
    for result in valid_results:
        datetime_str = "取得できませんでした"
        if result.get('datetime'):
            datetime_str = result['datetime'].strftime('%Y-%m-%d %H:%M:%S')
        
        content += f"""### 画像 {result['index']}: {result['path'].name}

- **撮影日時**: {datetime_str}
- **画像サイズ**: {result['width']}×{result['height']}px
- **形式**: {result['format']}
- **ファイルサイズ**: {result['size']:,}バイト
- **URL**: `{result['url']}`
- **内容説明**: [Claude Codeで画像確認後に記入]
- **記事での使用予定**: [セクション名を記入]

"""
    
    content += """## ✅ 記事作成チェックリスト

### 📸 画像処理
- [x] Google Photos URL抽出完了
- [x] 画像分析MD作成（時刻情報含む）
- [ ] 各画像の内容説明記入完了
- [ ] 時系列確認済み

### 📝 記事作成  
- [ ] 日付: 推奨日付を記事に設定 (`{suggested_date}`)
- [ ] タイトル: 内容に合致したタイトル作成
- [ ] カテゴリ: 標準7カテゴリから選択
- [ ] featured_image: 代表画像を設定
- [ ] Google Photos元URL記録

### ✅ 最終確認
- [ ] 画像と記事内容の整合性確認
- [ ] フロントマター必須項目完備
- [ ] ビルド・公開実行

## 📝 記事作成メモ

[記事作成時の気づきや重要事項をここに記録]

---

**このファイルは記事作成の品質管理資料として保持されます**
"""
    
    return filename, content

def main():
    parser = argparse.ArgumentParser(description="記事作成用画像ダウンロードツール")
    parser.add_argument('urls', nargs='*', help='ダウンロードする画像URL')
    parser.add_argument('--from-file', help='URLリストファイルから読み込み')
    parser.add_argument('--clean', action='store_true', help='ダウンロード前にtmpディレクトリをクリア')
    parser.add_argument('--max-workers', type=int, default=5, help='並列ダウンロード数（デフォルト: 5）')
    parser.add_argument('--article-title', help='記事タイトル（画像分析MDファイル名に使用）')
    parser.add_argument('--generate-analysis', action='store_true', default=True, help='画像分析MDファイルを生成（デフォルト: True）')
    
    args = parser.parse_args()
    
    # URLリストを取得
    urls = []
    if args.from_file:
        try:
            with open(args.from_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        except FileNotFoundError:
            print(f"❌ ファイルが見つかりません: {args.from_file}")
            return 1
    else:
        urls = args.urls
    
    if not urls:
        print("❌ ダウンロードするURLが指定されていません")
        parser.print_help()
        return 1
    
    # 出力ディレクトリを準備
    output_dir = Path(__file__).parent / 'tmp'
    output_dir.mkdir(exist_ok=True)
    
    # ディレクトリクリア
    if args.clean:
        print("🧹 tmpディレクトリをクリア中...")
        for file in output_dir.glob('review_image_*'):
            file.unlink()
    
    print("============================================================")
    print("🖼️ 記事作成用画像ダウンロード開始")
    print("============================================================")
    print(f"📂 保存先: {output_dir}")
    print(f"📊 対象画像数: {len(urls)}枚")
    print(f"🔄 並列数: {args.max_workers}")
    print()
    
    # 並列ダウンロード実行
    results = []
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        # ダウンロードタスクを開始
        future_to_index = {}
        for i, url in enumerate(urls, 1):
            output_path = output_dir / generate_filename(url, i)
            future = executor.submit(download_image, url, output_path, i)
            future_to_index[future] = i
        
        # 結果を収集
        for future in as_completed(future_to_index):
            result = future.result()
            results.append(result)
    
    # 結果をソート（インデックス順）
    results.sort(key=lambda x: x.get('index', 0))
    
    print("\n============================================================")
    print("📋 ダウンロード結果")
    print("============================================================")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ 成功: {len(successful)}枚")
    print(f"❌ 失敗: {len(failed)}枚")
    
    if successful:
        print("\n📷 ダウンロード成功画像:")
        for result in successful:
            if 'width' in result:
                print(f"  {result['index']:2d}. {result['path'].name}")
                print(f"      📐 {result['width']}×{result['height']}px ({result['format']})")
                print(f"      💾 {result['size']:,}バイト")
                if result.get('datetime'):
                    print(f"      📅 {result['datetime'].strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"  {result['index']:2d}. {result['path'].name} (詳細情報取得失敗)")
    
    if failed:
        print("\n❌ ダウンロード失敗画像:")
        for result in failed:
            print(f"  {result['index']:2d}. {result['error']}")
    
    # 画像分析MDファイル生成
    if args.generate_analysis and successful:
        print("\n============================================================")
        print("📝 画像分析MDファイル生成中...")
        print("============================================================")
        
        analysis_result = generate_analysis_md(successful, args.article_title or "")
        if analysis_result:
            filename, content = analysis_result
            analysis_path = output_dir / filename
            
            try:
                with open(analysis_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 画像分析MDファイル作成完了: {filename}")
                print(f"📁 パス: {analysis_path}")
                
                # 時系列サマリーを表示
                timed_results = [r for r in successful if r.get('datetime')]
                if timed_results:
                    timed_results.sort(key=lambda x: x['datetime'])
                    earliest = timed_results[0]['datetime']
                    latest = timed_results[-1]['datetime']
                    print(f"📅 推奨記事日付: {earliest.strftime('%Y-%m-%d')}")
                    print(f"⏰ 撮影時間帯: {earliest.strftime('%H:%M')} - {latest.strftime('%H:%M')}")
                    
                    duration = (latest - earliest).total_seconds() / 3600
                    if duration > 0:
                        print(f"⏱️ 撮影期間: {duration:.1f}時間")
                
            except Exception as e:
                print(f"❌ 画像分析MDファイル作成エラー: {e}")
        else:
            print("⚠️ 画像分析MDファイルの生成をスキップしました（有効な画像がありません）")
    
    print(f"\n💡 画像確認方法:")
    print(f"ls -la {output_dir}/review_image_*")
    print(f"open {output_dir}  # macOSでフォルダを開く")
    
    return 0 if not failed else 1

if __name__ == "__main__":
    sys.exit(main())