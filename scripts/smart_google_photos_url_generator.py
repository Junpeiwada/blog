#!/usr/bin/env python3
"""
スマートGoogle Photos URL生成 - ベースURLからフルサイズURL自動生成
"""

import re
import requests

def analyze_user_provided_urls():
    """
    ユーザー提供のフルサイズURLのパターンを分析
    """
    sample_urls = [
        "https://lh3.googleusercontent.com/pw/AP1GczPh2vPU8BavZbRjLKN7P8G1g2z9TzVX9mvR2Gwu6hWqfa58t7Epuga5SPcWvEVHemWssozaUmLxktvxLF9NT2ehXPKwzEpEauBxZgsuCcpIyOrAQ6yQeGpCCS_42EAtp_DisEXd3Q7--gLAxhnzK0tMjA=w4238-h2382-s-no-gm?authuser=0",
        "https://lh3.googleusercontent.com/pw/AP1GczMITnmFejNzG5ft5rKYNfmaJWuT7GD-VbZm9K5lGmRHOVO4L3VaFifm5f1ZBJGuIpyYoayJ_Tc1RJ4-0ncQ40Sv3CtGvPRL9BQR_AqYNxh6BuX5nO4j6Kb-NJgTdmJDzMuetpkzWuek1uCpYcrFSUoolw=w4238-h2384-s-no-gm?authuser=0"
    ]
    
    print("🔍 ユーザー提供URLパターン分析:")
    
    for i, url in enumerate(sample_urls, 1):
        print(f"   {i}. ベースURL: {url.split('=')[0]}")
        print(f"      パラメータ: {url.split('=', 1)[1]}")
    
    return {
        "base_pattern": r"(https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+)",
        "fullsize_suffix": "=w4238-h2382-s-no-gm?authuser=0",
        "alternative_suffix": "=w4238-h2384-s-no-gm?authuser=0"
    }

def extract_base_urls_with_simple_requests(shared_link):
    """
    シンプルなrequestsでベースURLを抽出
    """
    print(f"🌐 シンプルHTTP取得でベースURL抽出...")
    
    try:
        response = requests.get(shared_link, allow_redirects=True)
        html_content = response.text
        
        print(f"📄 HTMLサイズ: {len(html_content)} 文字")
        
        # ベースURLパターンを検索
        base_pattern = r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+'
        base_urls = re.findall(base_pattern, html_content)
        
        # 重複除去とフィルタリング
        unique_base_urls = list(set(base_urls))
        
        # 長さでフィルタリング（短すぎるURLは除外）
        filtered_base_urls = [url for url in unique_base_urls if len(url) > 80]
        
        print(f"✅ ベースURL取得: {len(filtered_base_urls)}個")
        
        return filtered_base_urls
        
    except Exception as e:
        print(f"❌ ベースURL取得エラー: {e}")
        return []

def generate_fullsize_urls_from_base(base_urls, patterns):
    """
    ベースURLからフルサイズURLを生成
    """
    print(f"🛠️  フルサイズURL生成中...")
    
    fullsize_urls = []
    
    for base_url in base_urls:
        # 複数のサイズパターンを試行
        size_patterns = [
            "=w4238-h2382-s-no-gm?authuser=0",  # 標準フルサイズ
            "=w4238-h2384-s-no-gm?authuser=0",  # 別アスペクト比
            "=w3840-h2160-s-no-gm?authuser=0",  # 4K UHD
            "=w4096-h3072-s-no-gm?authuser=0",  # 4:3アスペクト
        ]
        
        for pattern in size_patterns:
            fullsize_url = base_url + pattern
            fullsize_urls.append(fullsize_url)
    
    return fullsize_urls

def verify_url_accessibility(urls):
    """
    URLのアクセス可能性を検証
    """
    print(f"🔗 URL有効性検証中...")
    
    valid_urls = []
    
    for i, url in enumerate(urls, 1):
        try:
            # HEADリクエストで存在確認
            response = requests.head(url, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ URL{i}: 有効")
                valid_urls.append(url)
            else:
                print(f"   ❌ URL{i}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ URL{i}: アクセスエラー")
    
    return valid_urls

def main():
    print("🧠 スマートGoogle Photos フルサイズURL生成")
    print("=" * 60)
    print("手法: パターン分析 + ベースURL抽出 + フルサイズ生成")
    
    test_url = "https://photos.app.goo.gl/qctTRRMsqWvjHaPKA"
    
    # 1. パターン分析
    patterns = analyze_user_provided_urls()
    
    # 2. ベースURL抽出
    base_urls = extract_base_urls_with_simple_requests(test_url)
    
    if base_urls:
        print(f"\n📋 ベースURL一覧:")
        for i, url in enumerate(base_urls, 1):
            print(f"   {i}. {url}")
        
        # 3. フルサイズURL生成
        generated_urls = generate_fullsize_urls_from_base(base_urls, patterns)
        
        # 4. URL有効性検証
        valid_urls = verify_url_accessibility(generated_urls[:20])  # 最大20個まで検証
        
        if valid_urls:
            print(f"\n✅ {len(valid_urls)}個の有効なフルサイズURLを生成！")
            
            print(f"\n📋 有効なフルサイズURL:")
            print("=" * 50)
            
            for i, url in enumerate(valid_urls, 1):
                print(f"{i:2d}. {url}")
            
            print(f"\n📝 記事用Markdown:")
            print("=" * 30)
            
            for i, url in enumerate(valid_urls, 1):
                print(f"![画像{i}]({url})")
        else:
            print(f"\n❌ 有効なフルサイズURLを生成できませんでした")
    else:
        print(f"\n❌ ベースURLの抽出に失敗")

if __name__ == "__main__":
    main()