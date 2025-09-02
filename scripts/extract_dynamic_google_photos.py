#!/usr/bin/env python3
"""
requests-htmlを使用してGoogle Photosから動的にフルサイズ画像URLを取得
"""

import re
import time
from requests_html import HTMLSession

def extract_dynamic_google_photos_urls(shared_link):
    """
    requests-htmlでJavaScript実行後にフルサイズ画像URLを抽出
    """
    print(f"🔗 Google Photos共有リンク: {shared_link}")
    
    try:
        # HTMLSessionでJavaScript実行可能にする
        session = HTMLSession()
        
        print("🌐 ページにアクセス中...")
        r = session.get(shared_link)
        
        print("📍 リダイレクト先:", r.url)
        
        # JavaScript実行してレンダリング
        print("⚡ JavaScript実行中（時間がかかる場合があります）...")
        r.html.render(wait=3, timeout=30)  # 3秒待機、30秒タイムアウト
        
        # レンダリング後のHTMLを取得
        rendered_html = r.html.html
        
        print(f"📄 レンダリング後HTMLサイズ: {len(rendered_html)} 文字")
        
        # フルサイズ画像URLパターンを検索
        patterns = [
            # パターン1: w4000番台のフルサイズ画像
            r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w[4-9][0-9]{3}-h[0-9]+-s-no-gm\?authuser=[0-9]+',
            
            # パターン2: authuser無しのフルサイズ
            r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w[4-9][0-9]{3}-h[0-9]+-s-no-gm',
            
            # パターン3: JavaScript配列内のベースURL
            r'"(https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+)"',
            
            # パターン4: より広範囲なサイズ（w2000以上）
            r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w[2-9][0-9]{3}-h[0-9]+-s-no-gm',
        ]
        
        all_urls = []
        
        for i, pattern in enumerate(patterns, 1):
            matches = re.findall(pattern, rendered_html)
            if matches:
                print(f"✅ パターン{i}で{len(matches)}個のURLを発見")
                all_urls.extend(matches)
            else:
                print(f"⚠️  パターン{i}: URLが見つかりません")
        
        # 重複除去
        unique_urls = list(set(all_urls))
        
        # プロフィール画像（/a/ディレクトリ）を除外
        filtered_urls = [url for url in unique_urls if '/a/' not in url]
        
        if len(filtered_urls) != len(unique_urls):
            excluded_count = len(unique_urls) - len(filtered_urls)
            print(f"🚫 プロフィール画像を除外: {excluded_count}個")
        
        print(f"🖼️  最終取得URL数: {len(filtered_urls)}")
        
        return filtered_urls
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return []
    finally:
        try:
            session.close()
        except:
            pass

def generate_markdown_with_fullsize_urls(urls):
    """
    フルサイズURLからMarkdown画像記法を生成
    """
    markdown_lines = []
    
    for i, url in enumerate(urls, 1):
        # URLからクォートを除去（JavaScript配列から抽出した場合）
        clean_url = url.strip('"\'')
        
        alt_text = f"画像{i}"
        markdown = f"![{alt_text}]({clean_url})"
        markdown_lines.append(markdown)
    
    return markdown_lines

def main():
    print("⚡ 動的Google Photos URL抽出テスト")
    print("=" * 50)
    print("注意: JavaScript実行のため時間がかかります")
    
    # テスト用URL
    test_url = "https://photos.app.goo.gl/qctTRRMsqWvjHaPKA"
    
    # 動的URL抽出
    extracted_urls = extract_dynamic_google_photos_urls(test_url)
    
    if extracted_urls:
        print(f"\n✅ {len(extracted_urls)}個のフルサイズ画像URLを抽出しました")
        
        print(f"\n📋 抽出されたフルサイズURL:")
        print("=" * 40)
        
        for i, url in enumerate(extracted_urls, 1):
            print(f"{i:2d}. {url}")
        
        print(f"\n📝 記事用Markdown:")
        print("=" * 40)
        
        markdown_images = generate_markdown_with_fullsize_urls(extracted_urls)
        for markdown in markdown_images:
            print(markdown)
        
    else:
        print(f"\n❌ フルサイズ画像URLの抽出に失敗しました")

if __name__ == "__main__":
    main()