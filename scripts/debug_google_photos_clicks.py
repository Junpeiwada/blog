#!/usr/bin/env python3
"""
Google Photos画像クリック詳細デバッグ版
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def setup_debug_chrome_driver():
    """
    デバッグ用Chrome WebDriverセットアップ（ブラウザ表示有効）
    """
    chrome_options = Options()
    # ヘッドレスモードOFF（デバッグのため）
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    chrome_options.add_argument("--window-size=1920,1080")  # 大きな画面サイズ
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def debug_page_elements(driver):
    """
    ページ内の要素を詳細にデバッグ
    """
    print("\n🔍 ページ要素詳細分析:")
    print("=" * 40)
    
    # 様々なセレクタで要素を検索
    debug_selectors = {
        "全img要素": "img",
        "Google Photos画像": "img[src*='googleusercontent.com']",
        "クリック可能div": "div[jsaction*='click']",
        "背景画像div": "div[style*='background-image']",
        "c-wiz要素": "c-wiz",
        "data属性": "[data-photo-index], [data-image-url]",
        "role=img": "[role='img']",
        "aria-label写真": "[aria-label*='写真'], [aria-label*='Photo']",
    }
    
    clickable_elements = []
    
    for name, selector in debug_selectors.items():
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"   {name}: {len(elements)}個")
            
            if elements and "クリック可能" in name:
                clickable_elements.extend(elements[:3])  # 最大3個まで
                
        except Exception as e:
            print(f"   {name}: エラー - {e}")
    
    return clickable_elements

def debug_single_image_click(driver, element, index):
    """
    単一画像の詳細クリックデバッグ
    """
    print(f"\n🎯 画像{index} 詳細デバッグ:")
    print("-" * 30)
    
    try:
        # 要素情報取得
        tag_name = element.tag_name
        location = element.location
        size = element.size
        
        print(f"   タグ: {tag_name}")
        print(f"   位置: {location}")
        print(f"   サイズ: {size}")
        
        # 属性情報
        attributes = ['src', 'data-photo-index', 'jsaction', 'aria-label', 'class', 'style']
        for attr in attributes:
            try:
                value = element.get_attribute(attr)
                if value:
                    print(f"   {attr}: {value[:100]}{'...' if len(str(value)) > 100 else ''}")
            except:
                pass
        
        # クリック前のURL記録
        before_url = driver.current_url
        before_title = driver.title
        
        print(f"\n   🖱️  クリック実行中...")
        
        # スクロールして要素を表示
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(2)
        
        # クリック実行
        ActionChains(driver).move_to_element(element).click().perform()
        
        # クリック後の変化を監視
        print(f"   ⏳ クリック後の変化を監視中...")
        time.sleep(3)
        
        after_url = driver.current_url
        after_title = driver.title
        
        print(f"   📍 URL変化: {before_url != after_url}")
        print(f"   📑 タイトル変化: {before_title != after_title}")
        
        if before_url != after_url:
            print(f"      前: {before_url}")
            print(f"      後: {after_url}")
        
        # フルサイズビューの兆候を確認
        print(f"\n   🔍 フルサイズビュー検出中...")
        
        # 大きな画像を検索
        large_images = driver.find_elements(By.CSS_SELECTOR, "img")
        max_width = 0
        largest_image_url = None
        
        for img in large_images:
            try:
                src = img.get_attribute("src")
                if src and "googleusercontent.com" in src and "=w" in src:
                    width_str = src.split("=w")[1].split("-")[0]
                    width = int(width_str)
                    
                    if width > max_width:
                        max_width = width
                        largest_image_url = src
                        
                    print(f"      画像発見: w{width}px")
                    
            except Exception as img_error:
                pass
        
        if largest_image_url:
            print(f"   🏆 最大画像: w{max_width}px")
            print(f"   🔗 URL: {largest_image_url}")
            
            if max_width >= 3000:
                print(f"   ✅ フルサイズ画像を発見！")
                return largest_image_url
            else:
                print(f"   ⚠️  まだフルサイズではありません")
        
        # さらに待機してみる
        print(f"   ⏳ 追加待機中（フルサイズ読み込み完了まで）...")
        time.sleep(5)
        
        # 再度検索
        final_large_images = driver.find_elements(By.CSS_SELECTOR, "img[src*='googleusercontent.com']")
        final_max_width = 0
        final_largest_url = None
        
        for img in final_large_images:
            try:
                src = img.get_attribute("src")
                if src and "=w" in src:
                    width_str = src.split("=w")[1].split("-")[0]
                    width = int(width_str)
                    
                    if width > final_max_width:
                        final_max_width = width
                        final_largest_url = src
                        
            except:
                pass
        
        if final_largest_url and final_max_width != max_width:
            print(f"   🔄 最終画像: w{final_max_width}px")
            print(f"   🔗 URL: {final_largest_url}")
            
            if final_max_width >= 3000:
                print(f"   ✅ フルサイズ画像を発見！")
                return final_largest_url
        
        print(f"   ❌ フルサイズ画像を取得できませんでした")
        
        # ESCキーで閉じる
        print(f"   🔙 ビューを閉じる...")
        try:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(2)
        except:
            pass
        
        return None
        
    except Exception as e:
        print(f"   ❌ デバッグエラー: {e}")
        return None

def main():
    print("🔍 Google Photos 詳細デバッグ版")
    print("=" * 50)
    print("注意: ブラウザが表示されます。手動操作も確認できます。")
    
    test_url = "https://photos.app.goo.gl/qctTRRMsqWvjHaPKA"
    
    driver = None
    try:
        print("\n🚀 Chrome起動中...")
        driver = setup_debug_chrome_driver()
        
        print("🌐 Google Photosにアクセス中...")
        driver.get(test_url)
        
        # ページ読み込み完了待機
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(5)
        
        print(f"📍 最終URL: {driver.current_url}")
        
        # ページ要素分析
        clickable_elements = debug_page_elements(driver)
        
        print(f"\n🖱️  クリック可能要素: {len(clickable_elements)}個")
        
        # 各要素を詳細にテスト
        successful_urls = []
        
        for i, element in enumerate(clickable_elements[:3], 1):  # 最大3個まで詳細テスト
            result_url = debug_single_image_click(driver, element, i)
            if result_url:
                successful_urls.append(result_url)
        
        if successful_urls:
            print(f"\n✅ {len(successful_urls)}個のフルサイズURLを取得！")
            print("\n📋 取得されたフルサイズURL:")
            for i, url in enumerate(successful_urls, 1):
                print(f"{i}. {url}")
                
            print(f"\n📝 記事用Markdown:")
            for i, url in enumerate(successful_urls, 1):
                print(f"![画像{i}]({url})")
        else:
            print(f"\n❌ フルサイズURLを取得できませんでした")
            print("デバッグ用にブラウザは開いたままにします。手動で操作して確認してください。")
            print("Enterキーで終了...")
            input()
        
    except Exception as e:
        print(f"❌ エラー: {e}")
    
    finally:
        if driver:
            print("🔚 ブラウザを終了...")
            driver.quit()

if __name__ == "__main__":
    main()