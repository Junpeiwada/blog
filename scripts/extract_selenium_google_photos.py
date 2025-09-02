#!/usr/bin/env python3
"""
Seleniumを使用してGoogle Photosから手動操作を模倣してフルサイズ画像URLを取得
"""

import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def setup_chrome_driver():
    """
    Chrome WebDriverのセットアップ
    """
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # デバッグのためヘッドレス無効
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
    
    # WebDriverManagerで自動的にChromeDriverをダウンロード・設定
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def extract_fullsize_urls_with_selenium(shared_link):
    """
    Seleniumで手動操作を模倣してフルサイズ画像URLを取得
    """
    print(f"🤖 Selenium自動化でGoogle Photos処理開始")
    print(f"🔗 対象リンク: {shared_link}")
    
    driver = None
    try:
        # 1. Chrome WebDriverを起動
        print("🚀 Chrome WebDriverを起動中...")
        driver = setup_chrome_driver()
        
        # 2. Google Photosページにアクセス
        print("🌐 Google Photosページにアクセス中...")
        driver.get(shared_link)
        
        # 3. ページの完全読み込みを待機
        print("⏳ ページ読み込み待機中...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 追加待機（JavaScript完全実行のため）
        time.sleep(5)
        
        print("📍 最終URL:", driver.current_url)
        
        # 4. 画像要素を検索
        print("🖼️  画像要素を検索中...")
        
        # Google Photosの画像要素セレクタを試行
        image_selectors = [
            "img[src*='googleusercontent.com']",  # 標準的な画像
            "[data-image-url*='googleusercontent.com']",  # data属性
            "div[style*='background-image'][style*='googleusercontent.com']",  # 背景画像
            "c-wiz img",  # Google Photosの特定構造
        ]
        
        all_image_urls = []
        
        for selector in image_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"   セレクタ '{selector}': {len(elements)}個の要素")
                
                for element in elements:
                    # src属性から画像URL取得
                    src = element.get_attribute("src")
                    if src and "googleusercontent.com" in src:
                        all_image_urls.append(src)
                    
                    # data-src属性も確認
                    data_src = element.get_attribute("data-src")
                    if data_src and "googleusercontent.com" in data_src:
                        all_image_urls.append(data_src)
                        
            except Exception as e:
                print(f"   セレクタエラー: {e}")
        
        # 5. JavaScript実行でより詳細な検索
        print("⚡ JavaScript実行でURL検索中...")
        try:
            # ページソースからURL抽出
            page_source = driver.page_source
            
            # フルサイズURLパターン
            patterns = [
                r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w[3-9][0-9]{3}-h[0-9]+-s-no-gm\?authuser=[0-9]+',
                r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w[3-9][0-9]{3}-h[0-9]+-s-no-gm',
                r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=[^"\'\\s]+',
            ]
            
            for i, pattern in enumerate(patterns, 1):
                matches = re.findall(pattern, page_source)
                if matches:
                    print(f"   パターン{i}: {len(matches)}個のURL発見")
                    all_image_urls.extend(matches)
        
        except Exception as js_error:
            print(f"   JavaScript検索エラー: {js_error}")
        
        # 6. より効果的な画像クリック処理でフルサイズURL取得
        print("🖱️  画像クリックでフルサイズURL取得中...")
        try:
            # Google Photosの画像要素を特定
            photo_selectors = [
                "[data-photo-index]",  # 写真インデックス
                "div[jsaction*='click']",  # クリック可能な画像
                "img[src*='googleusercontent.com'][src*='=w']",  # Google Photos画像
                "[aria-label*='写真'] img, [aria-label*='Photo'] img",  # アクセシビリティラベル
            ]
            
            fullsize_urls = []
            clicked_photos = set()  # 重複クリック防止
            
            # Stale element reference回避のため、毎回要素を再取得
            for selector in photo_selectors:
                try:
                    print(f"   セレクタ '{selector[:30]}...' で画像検索中...")
                    
                    # 毎回新しく要素を取得
                    photos = driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"   見つかった要素: {len(photos)}個")
                    
                    # 最大5枚まで処理
                    for i in range(min(5, len(photos))):
                        try:
                            # 毎回要素を再取得（stale回避）
                            current_photos = driver.find_elements(By.CSS_SELECTOR, selector)
                            
                            if i >= len(current_photos):
                                break
                                
                            photo = current_photos[i]
                            
                            print(f"     📸 セレクタ{selector[:15]}...の画像{i+1}をクリック中...")
                            
                            # 要素が見える位置までスクロール
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", photo)
                            time.sleep(2)  # スクロール完了待機
                            
                            # より確実なクリック方法を複数試行
                            click_success = False
                            
                            # 方法1: ActionChainsでクリック
                            try:
                                from selenium.webdriver.common.action_chains import ActionChains
                                ActionChains(driver).move_to_element(photo).click().perform()
                                print(f"       ✅ ActionChainsクリック成功")
                                click_success = True
                            except Exception as action_error:
                                print(f"       ❌ ActionChainsクリック失敗: {action_error}")
                            
                            # 方法2: 直接クリック
                            if not click_success:
                                try:
                                    photo.click()
                                    print(f"       ✅ 直接クリック成功")
                                    click_success = True
                                except Exception as direct_error:
                                    print(f"       ❌ 直接クリック失敗: {direct_error}")
                            
                            # 方法3: JavaScriptクリック
                            if not click_success:
                                try:
                                    driver.execute_script("arguments[0].click();", photo)
                                    print(f"       ✅ JavaScriptクリック成功")
                                    click_success = True
                                except Exception as js_error:
                                    print(f"       ❌ JavaScriptクリック失敗: {js_error}")
                            
                            if not click_success:
                                print(f"       ❌ 全てのクリック方法が失敗")
                                continue
                            
                            # フルサイズビューが開いたか確認
                            print(f"       ⏳ フルサイズビュー確認中...")
                            
                            # URL変化やモーダル表示を確認
                            current_url = driver.current_url
                            time.sleep(3)
                            
                            # フルサイズビューの特徴を確認
                            fullsize_indicators = [
                                "img[src*='=w4']",  # 4000px台画像
                                "img[src*='=w3']",  # 3000px台画像  
                                "[aria-label*='フルサイズ']", "[aria-label*='Full size']",
                            ]
                            
                            fullsize_view_detected = False
                            for indicator in fullsize_indicators:
                                try:
                                    elements = driver.find_elements(By.CSS_SELECTOR, indicator)
                                    if elements:
                                        fullsize_view_detected = True
                                        print(f"       ✅ フルサイズビュー検出: {indicator}")
                                        break
                                except:
                                    pass
                            
                            if not fullsize_view_detected:
                                print(f"       ⚠️  フルサイズビューが開いていない可能性")
                            
                            # さらに5秒待機（フルサイズ画像読み込み完了まで）
                            time.sleep(5)
                            
                            # ページソースからフルサイズURL検索
                            detail_source = driver.page_source
                            print(f"       📄 詳細ページサイズ: {len(detail_source)}文字")
                            
                            # フルサイズURL検索（より広範囲に）
                            fullsize_patterns = [
                                # パターン1: 4000px台のフルサイズ
                                r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w4[0-9]{3}-h[0-9]{4}-s-no-gm\?authuser=[0-9]+',
                                # パターン2: authuser無し4000px台  
                                r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w4[0-9]{3}-h[0-9]{4}-s-no-gm',
                                # パターン3: 3000px台以上
                                r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w[3-9][0-9]{3}-h[0-9]{4}-s-no-gm\?authuser=[0-9]+',
                                # パターン4: img src属性内
                                r'src="(https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w[4-9][0-9]{3}-[^"]*)"',
                                # パターン5: より一般的（サイズ不問）
                                r'https://lh[0-9]+\.googleusercontent\.com/pw/[A-Za-z0-9_-]+=w[0-9]+-h[0-9]+-s-no-gm\?authuser=[0-9]+',
                            ]
                            
                            # 実際に表示されている画像要素からもURL取得
                            try:
                                current_images = driver.find_elements(By.CSS_SELECTOR, "img[src*='googleusercontent.com']")
                                for img in current_images:
                                    img_src = img.get_attribute("src")
                                    if img_src and "=w" in img_src:
                                        width_str = img_src.split("=w")[1].split("-")[0]
                                        try:
                                            width = int(width_str)
                                            if width >= 2000:  # 2000px以上
                                                fullsize_patterns.append(re.escape(img_src))
                                                print(f"       📱 表示中画像から発見: w{width}px")
                                        except:
                                            pass
                            except Exception as img_error:
                                print(f"       ⚠️  画像要素検索エラー: {img_error}")
                            
                            found_fullsize = False
                            for pattern in fullsize_patterns:
                                matches = re.findall(pattern, detail_source)
                                for match in matches:
                                    if match not in fullsize_urls:
                                        fullsize_urls.append(match)
                                        print(f"       ✅ フルサイズ発見: w{match.split('=w')[1].split('-')[0]}px")
                                        found_fullsize = True
                            
                            if not found_fullsize:
                                print(f"       ⚠️  フルサイズURLが見つかりません")
                            
                            # フルサイズビューを確実に閉じる
                            print(f"       🔙 フルサイズビューを閉じる...")
                            try:
                                # 方法1: ESCキー（ActionChainsを使用）
                                from selenium.webdriver.common.action_chains import ActionChains
                                from selenium.webdriver.common.keys import Keys
                                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                                time.sleep(2)
                            except:
                                try:
                                    # 方法2: 閉じるボタン検索・クリック
                                    close_selectors = [
                                        "[aria-label*='閉じる']", "[aria-label*='Close']", 
                                        "[aria-label*='戻る']", "[aria-label*='Back']",
                                        "button[jsname]", "[role='button'][aria-label]"
                                    ]
                                    
                                    for close_selector in close_selectors:
                                        try:
                                            close_btn = driver.find_element(By.CSS_SELECTOR, close_selector)
                                            close_btn.click()
                                            time.sleep(2)
                                            break
                                        except:
                                            continue
                                            
                                except:
                                    # 方法3: ブラウザバック
                                    try:
                                        driver.back()
                                        time.sleep(3)
                                    except:
                                        pass
                        
                        except Exception as photo_error:
                            print(f"     ❌ 画像処理エラー: {photo_error}")
                            continue
                            
                except Exception as selector_error:
                    print(f"   セレクタエラー: {selector_error}")
                    continue
            
            if fullsize_urls:
                all_image_urls.extend(fullsize_urls)
                print(f"🎯 フルサイズURL取得完了: {len(fullsize_urls)}個")
        
        except Exception as click_error:
            print(f"画像クリック処理エラー: {click_error}")
        
        # 7. URL クリーンアップと重複除去
        cleaned_urls = []
        
        for url in all_image_urls:
            # URL文字列のクリーンアップ
            clean_url = url.split('&quot;')[0]  # 不要文字列除去
            clean_url = clean_url.split('); tran')[0]  # CSS部分除去
            clean_url = clean_url.strip()
            
            # 有効なURLのみ追加
            if clean_url.startswith('https://lh') and 'googleusercontent.com' in clean_url:
                cleaned_urls.append(clean_url)
        
        # 重複除去
        unique_urls = list(set(cleaned_urls))
        
        # プロフィール画像やサムネイルを除外、フルサイズのみ選別
        fullsize_filtered_urls = []
        
        for url in unique_urls:
            # プロフィール画像除外
            if '/a/' in url:
                continue
            
            # サイズ情報が含まれる場合、大きなサイズのみ選択
            if '=w' in url:
                try:
                    width_part = url.split('=w')[1].split('-')[0]
                    width = int(width_part)
                    
                    # 幅が1000px以上のもののみ採用（フルサイズまたは大サイズ）
                    if width >= 1000:
                        fullsize_filtered_urls.append(url)
                        print(f"   ✅ 採用: w{width}px")
                    else:
                        print(f"   🚫 除外: w{width}px (小さすぎる)")
                        
                except (ValueError, IndexError):
                    # サイズ解析失敗時は採用
                    fullsize_filtered_urls.append(url)
            else:
                # サイズ情報がない場合も採用
                fullsize_filtered_urls.append(url)
        
        # 最終的なフィルタリング済みURL
        filtered_urls = fullsize_filtered_urls
        
        print(f"\n📊 結果:")
        print(f"   抽出URL総数: {len(all_image_urls)}")
        print(f"   ユニークURL: {len(unique_urls)}")
        print(f"   フィルタ後: {len(filtered_urls)}")
        
        return filtered_urls
        
    except Exception as e:
        print(f"❌ Seleniumエラー: {e}")
        return []
    
    finally:
        if driver:
            print("🔚 WebDriverを終了中...")
            driver.quit()

def main():
    print("🤖 Selenium Google Photos フルサイズURL抽出")
    print("=" * 60)
    print("注意: WebDriverダウンロード＋自動ブラウザ操作を実行します")
    
    test_url = "https://photos.app.goo.gl/qctTRRMsqWvjHaPKA"
    
    # Seleniumで動的URL抽出
    extracted_urls = extract_fullsize_urls_with_selenium(test_url)
    
    if extracted_urls:
        print(f"\n✅ {len(extracted_urls)}個のフルサイズ画像URLを抽出成功！")
        
        print(f"\n📋 抽出されたフルサイズURL:")
        print("=" * 50)
        
        for i, url in enumerate(extracted_urls, 1):
            print(f"{i:2d}. {url}")
        
        print(f"\n📝 記事用Markdown:")
        print("=" * 30)
        
        for i, url in enumerate(extracted_urls, 1):
            print(f"![画像{i}]({url})")
        
    else:
        print(f"\n❌ フルサイズ画像URLの抽出に失敗")
        print("手動での対応をお勧めします")

if __name__ == "__main__":
    main()