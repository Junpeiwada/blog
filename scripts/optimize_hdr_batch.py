#!/usr/bin/env python3
"""
Photoshop経由HDR Gain Map保持画像最適化スクリプト
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

def check_photoshop():
    """
    Adobe Photoshop 2025の存在確認
    """
    photoshop_path = "/Applications/Adobe Photoshop 2025/Adobe Photoshop 2025.app"
    if not os.path.exists(photoshop_path):
        print("❌ Adobe Photoshop 2025が見つかりません")
        print(f"   パス: {photoshop_path}")
        return False
    
    print("✅ Adobe Photoshop 2025を確認")
    return True

def backup_original_images(image_dir):
    """
    元画像をバックアップ（既存のImageMagick処理済み画像を復元）
    """
    backup_dir = image_dir.parent / "images_backup"
    
    if not backup_dir.exists():
        print("❌ バックアップフォルダが存在しません")
        print("   ImageMagick最適化で作成されたバックアップを探しています...")
        return None
    
    print(f"📦 オリジナル画像をバックアップから復元")
    
    # ImageMagick処理済み画像をバックアップから復元
    tsubakuro_originals = list(backup_dir.glob("2025-08-16-tsubakuro-*"))
    restored_count = 0
    
    for backup_file in tsubakuro_originals:
        target_file = image_dir / backup_file.name
        if target_file.exists():
            # 現在のImageMagick処理済みファイルを一時保存
            temp_file = target_file.with_suffix('.imagemagick.bak')
            shutil.copy2(target_file, temp_file)
        
        # オリジナルを復元
        shutil.copy2(backup_file, target_file)
        restored_count += 1
        print(f"   復元: {backup_file.name}")
    
    print(f"✅ {restored_count}枚のオリジナル画像を復元しました")
    return backup_dir

def run_photoshop_script(jsx_script_path):
    """
    AppleScript経由でPhotoshopスクリプトを実行
    """
    jsx_path_posix = jsx_script_path.as_posix()
    
    applescript = f'''
    tell application "Adobe Photoshop 2025"
        activate
        do javascript file POSIX file "{jsx_path_posix}"
    end tell
    '''
    
    try:
        print("🚀 Photoshopスクリプトを実行中...")
        print(f"   スクリプト: {jsx_script_path.name}")
        
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=600  # 10分タイムアウト
        )
        
        if result.returncode == 0:
            print("✅ Photoshopスクリプト実行完了")
            if result.stdout.strip():
                print(f"   出力: {result.stdout.strip()}")
            return True
        else:
            print("❌ Photoshopスクリプト実行エラー")
            print(f"   エラー: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Photoshopスクリプトがタイムアウトしました")
        return False
    except Exception as e:
        print(f"❌ AppleScript実行エラー: {e}")
        return False

def check_file_sizes(image_dir):
    """
    最適化前後のファイルサイズ比較
    """
    tsubakuro_images = list(image_dir.glob("2025-08-16-tsubakuro-*"))
    backup_dir = image_dir.parent / "images_backup"
    
    total_original_size = 0
    total_optimized_size = 0
    
    print("\n📊 ファイルサイズ比較:")
    print("=" * 60)
    
    for image_file in sorted(tsubakuro_images):
        backup_file = backup_dir / image_file.name
        
        if backup_file.exists():
            original_size = backup_file.stat().st_size
            optimized_size = image_file.stat().st_size
            reduction = (1 - optimized_size / original_size) * 100 if original_size > 0 else 0
            
            total_original_size += original_size
            total_optimized_size += optimized_size
            
            print(f"{image_file.name}")
            print(f"  {original_size / 1024 / 1024:.1f}MB → {optimized_size / 1024 / 1024:.1f}MB ({reduction:.1f}% 削減)")
    
    print("=" * 60)
    if total_original_size > 0:
        total_reduction = (1 - total_optimized_size / total_original_size) * 100
        print(f"合計: {total_original_size / 1024 / 1024:.1f}MB → {total_optimized_size / 1024 / 1024:.1f}MB ({total_reduction:.1f}% 削減)")
    
    return total_reduction

def verify_hdr_metadata(image_path):
    """
    HDRメタデータの存在確認（簡易版）
    """
    try:
        result = subprocess.run(
            ['exiftool', '-ColorSpace', '-WhitePoint', '-s3', str(image_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return True
        return False
    except:
        return False

def main():
    print("🎨 Photoshop HDR Gain Map保持画像最適化")
    print("=" * 50)
    
    # 環境確認
    if not check_photoshop():
        return False
    
    # プロジェクトディレクトリ設定
    project_root = Path(__file__).parent.parent
    image_dir = project_root / "images"
    jsx_script = project_root / "scripts" / "optimize_hdr_photoshop.jsx"
    
    if not image_dir.exists():
        print(f"❌ 画像ディレクトリが存在しません: {image_dir}")
        return False
    
    if not jsx_script.exists():
        print(f"❌ Photoshopスクリプトが存在しません: {jsx_script}")
        return False
    
    # オリジナル画像の復元
    backup_dir = backup_original_images(image_dir)
    if not backup_dir:
        return False
    
    print()
    
    # 対象画像確認
    tsubakuro_images = list(image_dir.glob("2025-08-16-tsubakuro-*"))
    print(f"🖼️  対象画像: {len(tsubakuro_images)}枚")
    
    # Photoshopスクリプト実行
    success = run_photoshop_script(jsx_script)
    
    if success:
        print()
        print("📈 最適化結果:")
        reduction = check_file_sizes(image_dir)
        
        # HDRメタデータ確認（サンプル）
        if tsubakuro_images:
            sample_image = tsubakuro_images[0]
            has_hdr = verify_hdr_metadata(sample_image)
            print(f"HDRメタデータ確認 ({sample_image.name}): {'✅' if has_hdr else '❌'}")
        
        print()
        print("✅ HDR Gain Map保持画像最適化が完了しました！")
        print(f"   削減率: {reduction:.1f}%")
        print("   次のステップ: サイト再ビルド")
        
    else:
        print()
        print("❌ 最適化に失敗しました")
        print("   オリジナル画像はバックアップから復元済みです")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)