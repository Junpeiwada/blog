#!/usr/bin/env python3
"""
高度なGoogle Photos画像URL抽出 - 複数手法の組み合わせ
"""

import time
import re
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def setup_advanced_chrome_driver(headless=False):
    """
    高度なChrome WebDriverセットアップ（ネットワーク監視対応）
    """
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")
    
    # ネットワーク監視とパフォーマンス向上設定
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--log-level=0")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    # DevTools Protocol有効化
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # ネットワーク監視開始
    driver.execute_cdp_cmd('Network.enable', {})
    
    return driver

def extract_from_network_logs(driver):
    """
    Chrome DevTools ProtocolでネットワークログからフルサイズURL抽出
    """
    try:
        # ネットワークログを取得
        logs = driver.get_log('performance')
        
        fullsize_urls = []
        
        for log in logs:
            message = json.loads(log['message'])
            
            if message['message']['method'] == 'Network.responseReceived':
                url = message['message']['params']['response']['url']
                
                # Google Photos画像URLをチェック
                if 'googleusercontent.com' in url and '=w' in url:
                    # サイズを確認
                    try:
                        width_part = url.split('=w')[1].split('-')[0]
                        width = int(width_part)
                        
                        # 3000px以上をフルサイズとして採用
                        if width >= 3000:
                            fullsize_urls.append(url)
                            print(f"🌐 ネットワークログから発見: w{width}px")
                            
                    except (ValueError, IndexError):
                        pass
        
        return fullsize_urls
        
    except Exception as e:
        print(f"ネットワークログエラー: {e}")
        return []

def manual_like_interaction(driver):
    """
    手動操作により近い画像インタラクション
    """
    fullsize_urls = []
    
    try:
        print("🖱️  手動操作模倣を開始...")
        
        # 1. ページ全体をスクロールして全画像を読み込み
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # 2. より具体的な画像セレクタで検索
        image_selectors = [
            "div[data-photo-index]",  # 画像インデックス
            "div[jsname][jsaction*='click']",  # Google Photos特有の画像要素
            "div[role='img']",  # アクセシビリティロール
            "c-wiz div[style*='background-image']",  # 背景画像として表示される写真
        ]
        
        all_clickable_elements = []
        
        for selector in image_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"   セレクタ '{selector[:25]}...': {len(elements)}個")
            all_clickable_elements.extend(elements)
        
        # 重複除去（位置で判定）
        unique_elements = []
        seen_positions = set()
        
        for element in all_clickable_elements:
            try:
                location = element.location
                position_key = f"{location['x']},{location['y']}"
                
                if position_key not in seen_positions:
                    unique_elements.append(element)
                    seen_positions.add(position_key)
            except:
                continue
        
        print(f"   ユニーク画像要素: {len(unique_elements)}個")
        
        # 3. 各画像を順番にクリックしてフルサイズURL取得
        for i, element in enumerate(unique_elements[:8]):  # 最大8枚
            try:
                print(f"     🎯 画像{i+1}を詳細表示...")
                
                # 要素が表示されるまでスクロール
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(1)
                
                # クリック実行
                ActionChains(driver).move_to_element(element).click().perform()
                
                # フルサイズビューの完全読み込み待機
                time.sleep(4)
                
                # 4. フルサイズビューでの画像URL取得
                try:
                    # フルサイズ画像要素を検索
                    fullsize_img_selectors = [
                        "img[src*='googleusercontent.com'][src*='=w4']",  # w4000番台
                        "img[src*='googleusercontent.com'][src*='=w3']",  # w3000番台
                        "img[src*='=w'][src*='-h'][src*='-s-no-gm']",  # フルサイズパターン
                    ]
                    
                    found_fullsize = False
                    
                    for fs_selector in fullsize_img_selectors:
                        fullsize_imgs = driver.find_elements(By.CSS_SELECTOR, fs_selector)
                        
                        for img in fullsize_imgs:
                            src = img.get_attribute("src")
                            if src and 'w4' in src or 'w3' in src:  # 3000px以上
                                if src not in fullsize_urls:
                                    fullsize_urls.append(src)
                                    # サイズ抽出
                                    try:
                                        width = src.split('=w')[1].split('-')[0]
                                        print(f"       ✅ フルサイズ取得: w{width}px")
                                    except:
                                        print(f"       ✅ フルサイズ取得")
                                    found_fullsize = True
                    
                    # 5. ページソースからも検索（バックアップ）
                    if not found_fullsize:
                        detail_source = driver.page_source
                        
                        # フルサイズパターン（より厳密）
                        fullsize_patterns = [
                            r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w[4-9][0-9]{3}-h[0-9]{4}-s-no-gm\?authuser=[0-9]+',
                            r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w[3-9][0-9]{3}-h[0-9]{4}-s-no-gm\?authuser=[0-9]+',
                            r'src="(https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w[3-9][0-9]{3}[^"]*)"',
                        ]
                        
                        for pattern in fullsize_patterns:
                            matches = re.findall(pattern, detail_source)
                            for match in matches:
                                if isinstance(match, tuple):
                                    match = match[0]  # groupがある場合
                                
                                if match not in fullsize_urls:
                                    try:
                                        width = match.split('=w')[1].split('-')[0]
                                        if int(width) >= 2000:  # 2000px以上
                                            fullsize_urls.append(match)
                                            print(f"       ✅ ソースから発見: w{width}px")
                                            found_fullsize = True
                                    except:
                                        pass
                    
                    if not found_fullsize:
                        print(f"       ❌ 画像{i+1}: フルサイズURL未発見")
                
                except Exception as fs_error:
                    print(f"       ❌ フルサイズ検索エラー: {fs_error}")
                
                # 6. フルサイズビューを閉じる（複数方法試行）
                try:
                    # 方法1: ESCキー
                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                    time.sleep(1)
                except:
                    try:
                        # 方法2: 閉じるボタンクリック
                        close_button = driver.find_element(By.CSS_SELECTOR, "[aria-label*='閉じる'], [aria-label*='Close'], button[jsname]")
                        close_button.click()
                        time.sleep(1)
                    except:
                        try:
                            # 方法3: ブラウザバック
                            driver.back()
                            time.sleep(2)
                        except:
                            pass
                
            except Exception as element_error:
                print(f"     ❌ 要素{i+1}処理エラー: {element_error}")
                continue
        
        return fullsize_urls
        
    except Exception as interaction_error:
        print(f"手動操作模倣エラー: {interaction_error}")
        return []

def extract_fullsize_with_advanced_methods(shared_link):
    """
    複数の高度な手法を組み合わせてフルサイズURL抽出
    """
    print(f"🚀 高度なGoogle Photos URL抽出開始")
    print(f"🔗 対象: {shared_link}")
    
    driver = None
    try:
        # 1. ブラウザ起動（デバッグ用に非ヘッドレス）
        print("🌐 Chrome起動中（ブラウザ表示有効）...")
        driver = setup_advanced_chrome_driver(headless=False)
        
        # 2. ページアクセス
        print("📱 Google Photosページにアクセス...")
        driver.get(shared_link)
        
        # ページ読み込み完了待機
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(5)  # JavaScript完全実行待機
        
        print(f"📍 最終URL: {driver.current_url}")
        
        # 3. ネットワークログからフルサイズURL抽出
        print("🌐 ネットワークログ分析中...")
        network_urls = extract_from_network_logs(driver)
        
        # 4. 手動操作模倣でフルサイズURL取得
        print("🖱️  手動操作模倣実行中...")
        interaction_urls = manual_like_interaction(driver)
        
        # 5. 結果統合
        all_fullsize_urls = list(set(network_urls + interaction_urls))
        
        # 6. 最終フィルタリング
        final_urls = []
        
        for url in all_fullsize_urls:
            # URL クリーンアップ
            clean_url = url.split('&quot;')[0].split('"); ')[0].strip()
            
            # プロフィール画像除外
            if '/a/' in clean_url:
                continue
                
            # サイズチェック
            if '=w' in clean_url:
                try:
                    width = int(clean_url.split('=w')[1].split('-')[0])
                    if width >= 2000:  # 2000px以上のみ
                        final_urls.append(clean_url)
                        print(f"✅ 最終採用: w{width}px")
                except:
                    final_urls.append(clean_url)
            else:
                final_urls.append(clean_url)
        
        return final_urls
        
    except Exception as e:
        print(f"❌ 抽出エラー: {e}")
        return []
    
    finally:
        if driver:
            print("🔚 ブラウザ終了...")
            driver.quit()

def main():
    print("🎯 高度なGoogle Photos フルサイズURL抽出")
    print("=" * 60)
    print("手法: Selenium + DevTools Protocol + 手動操作模倣")
    print("注意: ブラウザが表示されます（デバッグのため）")
    
    test_url = "https://photos.app.goo.gl/qctTRRMsqWvjHaPKA"
    
    # 高度な抽出実行
    extracted_urls = extract_fullsize_with_advanced_methods(test_url)
    
    if extracted_urls:
        print(f"\n✅ {len(extracted_urls)}個のフルサイズURLを抽出成功！")
        
        print(f"\n📋 フルサイズURL一覧:")
        print("=" * 50)
        
        for i, url in enumerate(extracted_urls, 1):
            # サイズ情報表示
            size_info = ""
            if '=w' in url:
                try:
                    width = url.split('=w')[1].split('-')[0]
                    height = url.split('-h')[1].split('-')[0]
                    size_info = f" ({width}x{height}px)"
                except:
                    pass
            
            print(f"{i:2d}. {url}{size_info}")
        
        print(f"\n📝 記事用Markdown:")
        print("=" * 30)
        
        for i, url in enumerate(extracted_urls, 1):
            print(f"![画像{i}]({url})")
        
    else:
        print(f"\n❌ フルサイズURLの抽出に失敗")
        print("手動での対応またはベースURLの使用をお勧めします")

if __name__ == "__main__":
    main()