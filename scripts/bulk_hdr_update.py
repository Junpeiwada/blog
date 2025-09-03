#!/usr/bin/env python3
"""
既存記事の画像URLをHDR版に一括更新するスクリプト

使用方法:
python bulk_hdr_update.py --dry-run    # 確認用実行
python bulk_hdr_update.py              # 実際の更新
python bulk_hdr_update.py --file "記事ファイル名.md"  # 特定記事のみ

機能:
- content/posts/*.mdから=s1621パターンのURLを検出
- 各URLから実際の画像サイズを取得
- 800px幅基準でHDR URLを生成
- 記事ファイル内のURLを一括置換
- 処理統計とレポートを表示
"""

import os
import re
import sys
import glob
import argparse
import requests
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse
import time

def get_image_size_from_url(url):
    """URLから画像のサイズを取得"""
    try:
        # HEADリクエストでContent-Lengthのみ取得し、実際にはダウンロード
        response = requests.get(url, timeout=10, stream=True)
        response.raise_for_status()
        
        # 画像の最初の部分を読んでサイズを取得
        from PIL import Image
        from io import BytesIO
        
        # 最初の数KB読んでサイズを取得
        chunk_size = 2048
        image_data = BytesIO()
        for chunk in response.iter_content(chunk_size=chunk_size):
            image_data.write(chunk)
            image_data.seek(0)
            try:
                with Image.open(image_data) as img:
                    return img.size  # (width, height)
            except Exception:
                if len(image_data.getvalue()) > chunk_size * 10:  # 20KB以上読んでもダメなら諦める
                    break
                continue
        
        return None
    except Exception as e:
        print(f"   ⚠️ サイズ取得エラー ({url[:60]}...): {e}")
        return None

def generate_hdr_url_800px(original_url, width, height):
    """800px幅基準でHDR URLを生成"""
    try:
        # アスペクト比を計算
        aspect_ratio = height / width
        target_width = 800
        target_height = int(target_width * aspect_ratio)
        
        # s1621パラメーターをHDR対応パラメーターに変更
        if '=s1621?authuser=0' in original_url:
            return original_url.replace('=s1621?authuser=0', f'=w{target_width}-h{target_height}-s-no-gm?authuser=0')
        elif '=s1621' in original_url:
            return original_url.replace('=s1621', f'=w{target_width}-h{target_height}-s-no-gm')
        else:
            return original_url
    except Exception as e:
        print(f"   ⚠️ HDR URL生成エラー: {e}")
        return original_url

def scan_markdown_files(target_file=None):
    """Markdownファイルをスキャンして s1621 URLを抽出"""
    content_dir = Path("content/posts")
    
    if target_file:
        files = [content_dir / target_file]
    else:
        files = list(content_dir.glob("*.md"))
    
    url_pattern = re.compile(r'https://lh3\.googleusercontent\.com/[^)\s]*=s1621[^)\s]*')
    
    file_urls = {}  # ファイル名 -> URLリスト
    all_urls = set()  # 重複排除用
    
    for file_path in files:
        if not file_path.exists():
            print(f"⚠️ ファイルが見つかりません: {file_path}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            urls = url_pattern.findall(content)
            if urls:
                file_urls[file_path.name] = urls
                all_urls.update(urls)
        except Exception as e:
            print(f"⚠️ ファイル読み込みエラー {file_path.name}: {e}")
    
    return file_urls, list(all_urls)

def process_urls_to_hdr(urls):
    """URLリストをHDR版に変換"""
    url_mapping = {}  # 元URL -> HDR URL
    
    print(f"\n🔍 {len(urls)}個のURLのサイズを取得中...")
    
    for i, url in enumerate(urls, 1):
        print(f"[{i:2d}/{len(urls)}] サイズ取得中...")
        
        size = get_image_size_from_url(url)
        if size:
            width, height = size
            hdr_url = generate_hdr_url_800px(url, width, height)
            url_mapping[url] = hdr_url
            print(f"   ✅ {width}×{height}px → 800×{int(800 * height / width)}px")
        else:
            url_mapping[url] = url  # 失敗時は元URLを維持
            print(f"   ❌ サイズ取得失敗、元URLを維持")
        
        # レート制限対策
        time.sleep(0.5)
    
    return url_mapping

def update_markdown_files(file_urls, url_mapping, dry_run=False):
    """Markdownファイル内のURLを更新"""
    content_dir = Path("content/posts")
    updated_files = 0
    total_replacements = 0
    
    print(f"\n{'🔍 [DRY RUN]' if dry_run else '✏️'} 記事ファイル更新中...")
    
    for filename, urls in file_urls.items():
        file_path = content_dir / filename
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_replacements = 0
            
            # 各URLを置換
            for old_url in urls:
                new_url = url_mapping.get(old_url, old_url)
                if new_url != old_url:
                    content = content.replace(old_url, new_url)
                    file_replacements += 1
            
            if file_replacements > 0:
                if not dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                updated_files += 1
                total_replacements += file_replacements
                print(f"   ✅ {filename}: {file_replacements}個のURL更新")
            else:
                print(f"   📷 {filename}: 更新不要")
                
        except Exception as e:
            print(f"   ❌ {filename}: 更新エラー - {e}")
    
    return updated_files, total_replacements

def main():
    parser = argparse.ArgumentParser(description='既存記事の画像URLをHDR版に一括更新')
    parser.add_argument('--dry-run', action='store_true', help='実際の更新を行わず、確認のみ実行')
    parser.add_argument('--file', type=str, help='特定のファイルのみ処理')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 既存記事HDR一括更新スクリプト")
    print("=" * 60)
    
    if args.dry_run:
        print("🔍 DRY RUNモード: 実際の更新は行いません")
    
    # Step 1: Markdownファイルをスキャン
    print("\n📂 記事ファイルスキャン中...")
    file_urls, all_urls = scan_markdown_files(args.file)
    
    if not all_urls:
        print("✨ s1621パターンのURLが見つかりませんでした")
        return
    
    print(f"📊 検出結果:")
    print(f"   📄 対象ファイル数: {len(file_urls)}個")
    print(f"   🔗 ユニークURL数: {len(all_urls)}個")
    
    # Step 2: URLをHDR版に変換
    url_mapping = process_urls_to_hdr(all_urls)
    
    # 変換統計
    converted_count = sum(1 for old, new in url_mapping.items() if old != new)
    print(f"\n📈 変換統計:")
    print(f"   ✅ HDR変換成功: {converted_count}個")
    print(f"   📷 変換不要/失敗: {len(all_urls) - converted_count}個")
    
    # Step 3: ファイル更新
    if converted_count > 0:
        updated_files, total_replacements = update_markdown_files(file_urls, url_mapping, args.dry_run)
        
        print(f"\n📋 最終結果:")
        print(f"   📄 更新ファイル数: {updated_files}個")
        print(f"   🔄 総置換回数: {total_replacements}回")
        
        if args.dry_run:
            print(f"\n💡 実際に更新するには以下を実行:")
            if args.file:
                print(f"   python scripts/bulk_hdr_update.py --file \"{args.file}\"")
            else:
                print(f"   python scripts/bulk_hdr_update.py")
        else:
            print(f"\n✅ HDR一括更新完了！")
    else:
        print(f"\n📷 更新対象のURLがありませんでした")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによって中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)