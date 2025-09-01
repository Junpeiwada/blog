#!/usr/bin/env python3
"""
単一ファイルでHDRテスト
"""

import subprocess
import sys
from pathlib import Path

def test_single_image():
    """
    単一の画像でPhotoshopスクリプトをテスト
    """
    project_root = Path(__file__).parent.parent
    test_image = project_root / "images" / "2025-08-16-tsubakuro-01.jpg"
    jsx_script = project_root / "scripts" / "optimize_hdr_photoshop.jsx"
    
    if not test_image.exists():
        print(f"❌ テスト画像が見つかりません: {test_image}")
        return False
    
    print(f"🧪 テスト画像: {test_image.name}")
    
    # ファイルサイズ確認
    original_size = test_image.stat().st_size
    print(f"元サイズ: {original_size / 1024 / 1024:.1f}MB")
    
    applescript = f'''
    tell application "Adobe Photoshop 2025"
        activate
        delay 2
        do javascript file POSIX file "{jsx_script.as_posix()}" with arguments {{"{test_image.as_posix()}"}}
    end tell
    '''
    
    try:
        print("🚀 Photoshopでテスト実行中...")
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            new_size = test_image.stat().st_size
            reduction = (1 - new_size / original_size) * 100
            print(f"✅ 成功!")
            print(f"新サイズ: {new_size / 1024 / 1024:.1f}MB ({reduction:.1f}% 削減)")
            return True
        else:
            print(f"❌ エラー: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 実行エラー: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Photoshop HDR単一ファイルテスト")
    print("=" * 40)
    print("注意: Adobe Photoshop 2025を事前に起動してください")
    
    input("Photoshopが起動したら Enter を押してください...")
    
    success = test_single_image()
    sys.exit(0 if success else 1)