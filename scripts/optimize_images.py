#!/usr/bin/env python3
"""
画像最適化スクリプト - UltraHDR保持版
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def optimize_image(input_path, output_path, quality=45, max_width=800):
    """
    UltraHDR情報を保持したまま画像を最適化
    """
    try:
        # 記事表示サイズ用の極限圧縮最適化
        cmd = [
            'magick',
            str(input_path),
            '-resize', f'{max_width}x>',  # 記事表示サイズに縮小
            '-quality', str(quality),
            '-interlace', 'plane',  # Progressive JPEG
            '-strip',  # 全メタデータ除去
            '-sampling-factor', '4:2:0',  # クロマサブサンプリング
            '-define', 'jpeg:dct-method=float',  # 高効率DCT
            '-define', 'jpeg:optimize-coding=true',  # ハフマンテーブル最適化
            '-blur', '0.5x0.5',  # 軽微なブラー（圧縮効率向上）
            '-unsharp', '0x0.5+0.5+0.008',  # アンシャープマスク（品質補償）
            '-colorspace', 'sRGB',  # 標準色空間
            str(output_path)
        ]
        
        print(f"最適化中: {input_path.name}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # ファイルサイズ比較
        original_size = input_path.stat().st_size
        optimized_size = output_path.stat().st_size
        reduction = (1 - optimized_size / original_size) * 100
        
        print(f"  {original_size / 1024 / 1024:.1f}MB → {optimized_size / 1024 / 1024:.1f}MB ({reduction:.1f}% 削減)")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"エラー: {input_path.name} の最適化に失敗")
        print(f"  {e}")
        return False

def backup_original_images(image_dir):
    """
    元画像をバックアップ
    """
    backup_dir = image_dir.parent / "images_backup"
    backup_dir.mkdir(exist_ok=True)
    
    print(f"バックアップディレクトリ作成: {backup_dir}")
    
    # 燕岳関連画像のみバックアップ
    for image_file in image_dir.glob("2025-08-16-tsubakuro-*"):
        backup_path = backup_dir / image_file.name
        if not backup_path.exists():
            shutil.copy2(image_file, backup_path)
            print(f"バックアップ: {image_file.name}")
    
    return backup_dir

def optimize_tsubakuro_images():
    """
    燕岳記事の画像を最適化
    """
    # プロジェクトのimagesディレクトリ
    project_root = Path(__file__).parent.parent
    image_dir = project_root / "images"
    
    if not image_dir.exists():
        print(f"エラー: {image_dir} が存在しません")
        return False
    
    # バックアップ作成
    backup_dir = backup_original_images(image_dir)
    print()
    
    # 燕岳関連画像を取得
    tsubakuro_images = list(image_dir.glob("2025-08-16-tsubakuro-*"))
    
    if not tsubakuro_images:
        print("燕岳関連の画像が見つかりません")
        return False
    
    print(f"{len(tsubakuro_images)}枚の画像を最適化します")
    print(f"設定: 品質45%, 最大幅800px (記事表示サイズ最適化)")
    print()
    
    success_count = 0
    total_original_size = 0
    total_optimized_size = 0
    
    for image_path in sorted(tsubakuro_images):
        # 元のファイルサイズを記録
        total_original_size += image_path.stat().st_size
        
        # 一時ファイルに最適化
        temp_path = image_path.with_suffix('.tmp.jpg')
        
        if optimize_image(image_path, temp_path):
            # 成功した場合、元ファイルを置き換え
            total_optimized_size += temp_path.stat().st_size
            shutil.move(temp_path, image_path)
            success_count += 1
        else:
            # 失敗した場合、一時ファイル削除
            if temp_path.exists():
                temp_path.unlink()
    
    print()
    print("=== 最適化結果 ===")
    print(f"処理済み: {success_count}/{len(tsubakuro_images)} 枚")
    print(f"合計サイズ: {total_original_size / 1024 / 1024:.1f}MB → {total_optimized_size / 1024 / 1024:.1f}MB")
    
    if total_original_size > 0:
        total_reduction = (1 - total_optimized_size / total_original_size) * 100
        print(f"全体削減率: {total_reduction:.1f}%")
    
    print(f"バックアップ場所: {backup_dir}")
    
    return success_count == len(tsubakuro_images)

if __name__ == "__main__":
    print("🖼️  UltraHDR画像最適化スクリプト")
    print("=" * 40)
    
    if optimize_tsubakuro_images():
        print()
        print("✅ 最適化が完了しました！")
        print("   サイトを再ビルドしてください: python scripts/build.py")
    else:
        print()
        print("❌ 一部の画像で最適化に失敗しました")
        sys.exit(1)