#!/usr/bin/env python3
"""
Google Photos共有リンクから画像URLを抽出するテストスクリプト
"""

import re
import requests
from urllib.parse import urlparse, parse_qs

def extract_google_photos_urls(shared_link):
    """
    Google Photos共有リンクから画像URLを抽出
    """
    print(f"🔗 Google Photos共有リンク: {shared_link}")
    
    try:
        # 1. リダイレクト先URLを取得
        response = requests.get(shared_link, allow_redirects=True)
        final_url = response.url
        print(f"📍 リダイレクト先: {final_url}")
        
        # 2. ページ内容を取得
        html_content = response.text
        
        # 3. フルサイズ画像URLパターンを検索
        # パターン1: フルサイズ画像（w4238-h2382等の大きなサイズ）
        fullsize_pattern = r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w[3-9][0-9]{3}-h[0-9]+-s-no-gm\?authuser=[0-9]+'
        
        # パターン2: authuser無しのフルサイズ
        fullsize_pattern2 = r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w[3-9][0-9]{3}-h[0-9]+-s-no-gm'
        
        # パターン3: ベースURL（パラメータ無し）からフルサイズを推測
        base_pattern = r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+'
        
        # フルサイズURLを抽出
        fullsize_urls1 = re.findall(fullsize_pattern, html_content)
        fullsize_urls2 = re.findall(fullsize_pattern2, html_content)
        base_urls = re.findall(base_pattern, html_content)
        
        # フルサイズURLが見つかった場合はそれを使用
        if fullsize_urls1 or fullsize_urls2:
            all_urls = list(set(fullsize_urls1 + fullsize_urls2))
            print(f"✅ フルサイズ画像URLを発見")
        else:
            # フルサイズが見つからない場合はベースURLを使用
            all_urls = list(set(base_urls))
            print(f"⚠️  フルサイズURLが見つからないため、ベースURLを使用")
        
        # プロフィール画像（/a/ディレクトリ）を除外
        filtered_urls = [url for url in all_urls if '/a/' not in url]
        
        if len(filtered_urls) != len(all_urls):
            excluded_count = len(all_urls) - len(filtered_urls)
            print(f"🚫 プロフィール画像を除外: {excluded_count}個")
        
        all_urls = filtered_urls
        
        print(f"🖼️  抽出された画像URL数: {len(all_urls)}")
        
        if all_urls:
            print("\n📋 抽出されたURL一覧:")
            for i, url in enumerate(all_urls, 1):
                print(f"{i:2d}. {url}")
        else:
            print("❌ 画像URLが見つかりませんでした")
            
            # デバッグ用: ページ内容の一部を表示
            print("\n🔍 デバッグ情報:")
            print(f"ページサイズ: {len(html_content)} 文字")
            
            # googleusercontent.com の文字列があるかチェック
            if 'googleusercontent.com' in html_content:
                print("✅ googleusercontent.com文字列は存在します")
                
                # より緩い条件で検索
                loose_pattern = r'googleusercontent\.com[^"\']*'
                loose_matches = re.findall(loose_pattern, html_content)
                print(f"🔍 緩い条件での検索: {len(loose_matches)}件")
                
                if loose_matches:
                    print("サンプル:")
                    for match in loose_matches[:3]:
                        print(f"  {match}")
            else:
                print("❌ googleusercontent.com文字列が見つかりません")
        
        return all_urls
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return []

def clean_google_photos_urls(urls):
    """
    Google Photos URLからサイズパラメータを除去してクリーンなURLにする
    """
    cleaned_urls = []
    
    for url in urls:
        # URLパラメータを除去してベースURLのみ取得
        if '=' in url:
            base_url = url.split('=')[0]
        else:
            base_url = url
        
        cleaned_urls.append(base_url)
    
    return cleaned_urls

def generate_markdown_images(urls, base_alt_text="画像"):
    """
    URLからMarkdown画像記法を生成
    """
    markdown_lines = []
    
    for i, url in enumerate(urls, 1):
        alt_text = f"{base_alt_text}{i}"
        markdown = f"![{alt_text}]({url})"
        markdown_lines.append(markdown)
    
    return markdown_lines

def main():
    print("🔗 Google Photos URL抽出テスト")
    print("=" * 50)
    
    # テスト用URL
    test_url = "https://photos.app.goo.gl/qctTRRMsqWvjHaPKA"
    
    # URL抽出
    extracted_urls = extract_google_photos_urls(test_url)
    
    if extracted_urls:
        print(f"\n✅ {len(extracted_urls)}個の画像URLを抽出しました")
        
        # URLをクリーンアップ
        cleaned_urls = clean_google_photos_urls(extracted_urls)
        
        print(f"\n📝 記事用Markdown生成:")
        print("=" * 30)
        
        markdown_images = generate_markdown_images(cleaned_urls)
        for markdown in markdown_images:
            print(markdown)
        
        print(f"\n💡 使用方法:")
        print("上記のMarkdownを記事にコピー＆ペーストしてください")
        
    else:
        print(f"\n❌ 画像URLの抽出に失敗しました")
        print(f"💡 手動での対応をお勧めします:")
        print(f"1. {test_url} をブラウザで開く")
        print(f"2. 各画像で右クリック→'画像のアドレスをコピー'")
        print(f"3. URLの末尾を '=w800-s-no-gm' に変更")

if __name__ == "__main__":
    main()