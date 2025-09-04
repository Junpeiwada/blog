#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Photos画像URL取得ツール
共有リンクから全ての画像URLを自動取得

使用方法:
  python google_photos_extractor.py "https://photos.app.goo.gl/YOUR_URL"
  python google_photos_extractor.py "https://photos.app.goo.gl/YOUR_URL" --headless

オプション:
  --headless   ブラウザウィンドウを表示せずに実行（推奨）
               * 大量画像（15個以上）のアルバムではより安定
               * サーバー環境での実行に最適
               * stale element reference エラーの回避

必要な依存関係:
  pip install selenium webdriver-manager

実行例:
  # 通常実行（ブラウザ画面が表示される）
  python google_photos_extractor.py "https://photos.app.goo.gl/abc123"
  
  # ヘッドレス実行（推奨、安定動作）
  python google_photos_extractor.py "https://photos.app.goo.gl/abc123" --headless
"""

import time
import re
import sys
from datetime import datetime, timedelta
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


# 待機時間設定
HDR_WAIT_TIME = 2      # 画像処理用の固定待機時間（秒）


def create_progress_bar(current, total, width=40):
    """プログレスバーを作成"""
    percent = (current / total) * 100
    filled = int((current / total) * width)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {percent:.1f}% ({current}/{total})"


def format_time_duration(seconds):
    """秒数を読みやすい時間形式に変換"""
    if seconds < 60:
        return f"{int(seconds)}秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}分{secs}秒"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}時間{minutes}分"


def print_progress_report(current, total, successful, failed, start_time):
    """進捗状況を詳細に報告"""
    progress_bar = create_progress_bar(current, total)
    
    # 経過時間とETA計算
    elapsed = time.time() - start_time
    if current > 0:
        avg_time_per_item = elapsed / current
        remaining_items = total - current
        eta_seconds = avg_time_per_item * remaining_items
        eta_str = format_time_duration(eta_seconds)
    else:
        eta_str = "計算中..."
    
    elapsed_str = format_time_duration(elapsed)
    success_rate = (successful / current * 100) if current > 0 else 0
    
    # 進捗報告を表示
    print(f"\n📊 === 進捗状況レポート ===")
    print(f"   {progress_bar}")
    print(f"   ✅ 成功: {successful}個  ❌ 失敗: {failed}個  📈 成功率: {success_rate:.1f}%")
    print(f"   ⏱️ 経過時間: {elapsed_str}  🎯 残り予想時間: {eta_str}")
    print(f"   {'=' * 50}")


def setup_driver(headless=False):
    """WebDriverの初期化とセットアップ"""
    print("ChromeDriverをセットアップ中...")
    
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    
    if headless:
        options.add_argument('--headless')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ ChromeDriver起動成功")
    
    return driver


def scroll_and_load_all_images(driver, max_attempts=10):
    """スクロールして全ての画像を遅延読み込み"""
    print("📜 スクロールによる全画像読み込み開始...")
    
    previous_count = 0
    attempts = 0
    
    while attempts < max_attempts:
        attempts += 1
        print(f"🔄 スクロール試行 {attempts}/{max_attempts}")
        
        # 現在の画像数をカウント
        google_bg_divs = driver.find_elements(By.CSS_SELECTOR, "div[style*='googleusercontent.com']")
        current_count = len(google_bg_divs)
        
        print(f"   現在の画像数: {current_count}個")
        
        # 画像が見つかり、増加が止まったら終了
        if current_count > 0 and current_count == previous_count and attempts >= 3:
            print(f"✅ {current_count}個の画像を検出！")
            return google_bg_divs
        
        # 前回から増えていない場合、より積極的にスクロール
        if current_count == previous_count:
            print("   📏 ページ下部まで大きくスクロール")
            # ページの最下部までスクロール
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # 少し上に戻る
            driver.execute_script("window.scrollBy(0, -200);")
            time.sleep(2)
            
            # また下にスクロール
            driver.execute_script("window.scrollBy(0, 400);")
            time.sleep(3)
        else:
            print("   📏 通常のスクロール")
            # 通常のスクロール
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)
        
        # トップに戻って全体を確認
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        previous_count = current_count
    
    print(f"⚠️ 最大試行回数に達しました。最終検出数: {current_count}個")
    return google_bg_divs






def extract_background_image_url(element):
    """背景画像のURLを抽出"""
    try:
        style = element.get_attribute('style')
        if 'background-image' in style:
            match = re.search(r'url\("([^"]+)"\)', style)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"背景画像URL抽出エラー: {e}")
    return None


def click_and_get_full_url(driver, element, index):
    """画像をクリックして拡大表示、フルサイズURLを取得（HDR対応）"""
    print(f"🖱️ 画像 {index} をクリック中...")
    
    try:
        # 元のURLを取得
        original_url = extract_background_image_url(element)
        
        # 要素が見える位置までスクロール
        driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(1)
        
        # JavaScriptクリック実行（より確実な高解像度読み込み）
        driver.execute_script("arguments[0].click();", element)
        
        # HDR画像処理待機（固定7秒）
        print(f"   ⏰ HDR画像処理待機中: {HDR_WAIT_TIME}秒")
        time.sleep(HDR_WAIT_TIME)
        print(f"   ✅ 待機完了")
        
        # 拡大表示された画像を取得
        full_image_url = None
        
        try:
            # 新しく表示されたimg要素を探す
            full_images = driver.find_elements(By.CSS_SELECTOR, "img[src*='googleusercontent.com']")
            for img in full_images:
                src = img.get_attribute('src')
                size = img.size
                if src and size['width'] > 500:  # 大きな画像を探す
                    full_image_url = src
                    print(f"   📸 フル画像サイズ: {size['width']}x{size['height']}")
                    break
        except Exception as e:
            print(f"   ⚠️ フル画像取得エラー: {e}")
        
        # ESCで拡大表示を閉じる
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(1)
        
        return full_image_url if full_image_url else original_url
        
    except Exception as e:
        print(f"   ❌ クリック処理エラー: {e}")
        return extract_background_image_url(element)


def normalize_image_url(url, target_size="s1621"):
    """画像URLのサイズパラメータを正規化"""
    if not url:
        return url
    
    try:
        if '=' in url:
            base_url = url.split('=')[0]
            return f"{base_url}={target_size}?authuser=0"
        else:
            return f"{url}={target_size}?authuser=0"
    except Exception as e:
        print(f"URL正規化エラー: {e}")
        return url


def extract_google_photos_urls(share_url, headless=False):
    """Google Photos共有URLから全画像URLを取得"""
    driver = None
    
    try:
        print("=" * 60)
        print("🚀 Google Photos画像URL取得開始")
        print("=" * 60)
        
        # WebDriver起動
        driver = setup_driver(headless)
        
        # ページアクセス
        print(f"📱 アクセス: {share_url}")
        driver.get(share_url)
        
        # 基本的なページ読み込み待機
        wait = WebDriverWait(driver, 30)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(5)
        
        # スクロールして全画像を読み込み
        image_elements = scroll_and_load_all_images(driver)
        
        if len(image_elements) == 0:
            print(f"⚠️ 画像が検出されませんでした")
        
        # 全ての画像を処理
        total_images = len(image_elements)
        print(f"\n🎯 全{total_images}個の画像を処理開始")
        
        # 進捗追跡用変数
        extracted_urls = []
        successful_count = 0
        failed_count = 0
        start_time = time.time()
        
        for i, element in enumerate(image_elements, 1):
            try:
                print(f"\n--- 画像 {i}/{total_images} ---")
                
                # クリックしてフルサイズURL取得
                full_url = click_and_get_full_url(driver, element, i)
                
                if full_url:
                    # URL正規化
                    normalized_url = normalize_image_url(full_url)
                    extracted_urls.append(normalized_url)
                    successful_count += 1
                    
                    print(f"✅ URL取得成功")
                    print(f"🔗 {normalized_url}")
                else:
                    failed_count += 1
                    print(f"❌ URL取得失敗")
                
                # 5個ごとに進捗報告
                if i % 5 == 0 or i == total_images:
                    print_progress_report(i, total_images, successful_count, failed_count, start_time)
                
                time.sleep(2)  # 次の画像処理前に待機
                
            except Exception as e:
                failed_count += 1
                print(f"❌ 画像 {i} 処理エラー: {e}")
                
                # エラーでも進捗報告
                if i % 5 == 0 or i == total_images:
                    print_progress_report(i, total_images, successful_count, failed_count, start_time)
                continue
        
        # 最終結果表示
        total_time = time.time() - start_time
        total_time_str = format_time_duration(total_time)
        final_success_rate = (successful_count / total_images * 100) if total_images > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"🎉 全処理完了！")
        print("=" * 60)
        print(f"📊 最終統計:")
        print(f"   📸 処理画像数: {total_images}個")
        print(f"   ✅ 成功: {successful_count}個")
        print(f"   ❌ 失敗: {failed_count}個")
        print(f"   📈 最終成功率: {final_success_rate:.1f}%")
        print(f"   ⏱️ 総処理時間: {total_time_str}")
        print(f"   ⚡ 平均処理時間/画像: {total_time/total_images:.1f}秒" if total_images > 0 else "")
        print("=" * 60)
        
        print(f"\n📋 取得成功URL一覧 ({len(extracted_urls)}個):")
        for i, url in enumerate(extracted_urls, 1):
            print(f"{i:2d}. {url}")
        
        return extracted_urls
        
    except Exception as e:
        print(f"❌ メイン処理エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return []
        
    finally:
        if driver:
            if not headless:
                print("\n👀 結果確認のため5秒待機...")
                time.sleep(5)
            driver.quit()
            print("🔚 WebDriver終了")


def main():
    """メイン関数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python google_photos_extractor.py <Google Photos共有URL>")
        print("  python google_photos_extractor.py <Google Photos共有URL> --headless")
        print("")
        print("オプション:")
        print("  --headless   ブラウザを表示せずに実行（推奨）")
        print("")
        print("例:")
        print("  python google_photos_extractor.py 'https://photos.app.goo.gl/...'")
        print("  python google_photos_extractor.py 'https://photos.app.goo.gl/...' --headless")
        print("")
        print("推奨:")
        print("  大量画像（15個以上）のアルバムでは --headless オプションを使用")
        print("")
        print("必要な依存関係:")
        print("  pip install selenium webdriver-manager")
        return 1
    
    share_url = sys.argv[1]
    
    # ヘッドレスモードの指定
    headless = "--headless" in sys.argv
    
    # URL取得実行
    urls = extract_google_photos_urls(share_url, headless)
    
    # 成功判定
    if len(urls) > 0:
        print(f"\n✅ 成功！{len(urls)}個のURL取得完了")
        return 0
    else:
        print(f"\n❌ 失敗：URL取得できませんでした")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによって中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        sys.exit(1)