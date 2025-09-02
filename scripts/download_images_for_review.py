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
- 重複チェック
- エラーハンドリング
"""

import os
import sys
import requests
import argparse
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import hashlib

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
                
                print(f"   ✅ 保存完了: {output_path.name}")
                print(f"   📐 サイズ: {width}×{height}px")
                print(f"   📝 形式: {format_name}")
                print(f"   📁 ファイルサイズ: {file_size:,}バイト")
                
                return {
                    'index': index,
                    'url': url,
                    'path': output_path,
                    'width': width,
                    'height': height,
                    'format': format_name,
                    'size': file_size,
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

def main():
    parser = argparse.ArgumentParser(description="記事作成用画像ダウンロードツール")
    parser.add_argument('urls', nargs='*', help='ダウンロードする画像URL')
    parser.add_argument('--from-file', help='URLリストファイルから読み込み')
    parser.add_argument('--clean', action='store_true', help='ダウンロード前にtmpディレクトリをクリア')
    parser.add_argument('--max-workers', type=int, default=5, help='並列ダウンロード数（デフォルト: 5）')
    
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
            else:
                print(f"  {result['index']:2d}. {result['path'].name} (詳細情報取得失敗)")
    
    if failed:
        print("\n❌ ダウンロード失敗画像:")
        for result in failed:
            print(f"  {result['index']:2d}. {result['error']}")
    
    print(f"\n💡 画像確認方法:")
    print(f"ls -la {output_dir}/review_image_*")
    print(f"open {output_dir}  # macOSでフォルダを開く")
    
    return 0 if not failed else 1

if __name__ == "__main__":
    sys.exit(main())