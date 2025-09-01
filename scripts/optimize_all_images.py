#!/usr/bin/env python3
"""
全記事の画像を極限圧縮し、オリジナルファイルを削除
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

def optimize_image(input_path, quality=45, max_width=800):
    """
    記事表示サイズ用の極限圧縮最適化
    """
    try:
        # 元ファイルサイズ記録
        original_size = input_path.stat().st_size
        
        # 一時ファイルに最適化
        temp_path = input_path.with_suffix('.optimized' + input_path.suffix.lower())
        
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
            str(temp_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if temp_path.exists():
            # 最適化サイズ記録
            optimized_size = temp_path.stat().st_size
            reduction = (1 - optimized_size / original_size) * 100 if original_size > 0 else 0
            
            # 元ファイルを最適化版で置き換え
            shutil.move(temp_path, input_path)
            
            print(f"  {original_size / 1024 / 1024:.1f}MB → {optimized_size / 1024 / 1024:.1f}MB ({reduction:.1f}% 削減)")
            return True, original_size, optimized_size
        else:
            print(f"  失敗: 最適化ファイルが作成されませんでした")
            return False, original_size, original_size
        
    except subprocess.CalledProcessError as e:
        print(f"  エラー: {e}")
        # 一時ファイルが存在する場合は削除
        if temp_path.exists():
            temp_path.unlink()
        return False, input_path.stat().st_size, input_path.stat().st_size
    except Exception as e:
        print(f"  予期しないエラー: {e}")
        return False, input_path.stat().st_size, input_path.stat().st_size

def find_all_images(image_dir):
    """
    全ての画像ファイルを検索
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.heic'}
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(image_dir.glob(f"*{ext}"))
        image_files.extend(image_dir.glob(f"*{ext.upper()}"))
    
    return sorted(image_files)

def cleanup_backups(image_dir):
    """
    バックアップファイルとディレクトリを削除
    """
    backup_dir = image_dir.parent / "images_backup"
    
    if backup_dir.exists():
        print(f"\n🗑️  バックアップディレクトリを削除: {backup_dir}")
        shutil.rmtree(backup_dir)
        print("✅ バックアップディレクトリ削除完了")
    
    # .imagemagick.bakファイルも削除
    backup_files = list(image_dir.glob("*.imagemagick.bak"))
    if backup_files:
        print(f"\n🗑️  .imagemagick.bakファイルを削除: {len(backup_files)}個")
        for backup_file in backup_files:
            backup_file.unlink()
            print(f"  削除: {backup_file.name}")
        print("✅ バックアップファイル削除完了")

def main():
    print("🚀 全記事画像の極限圧縮最適化 + オリジナル削除")
    print("=" * 60)
    print("設定: 品質45%, 最大幅800px, 極限圧縮")
    print("注意: この操作は不可逆です。オリジナルファイルは完全に削除されます。")
    print()
    
    # プロジェクトディレクトリ設定
    project_root = Path(__file__).parent.parent
    image_dir = project_root / "images"
    
    if not image_dir.exists():
        print(f"❌ 画像ディレクトリが存在しません: {image_dir}")
        return False
    
    # 全画像ファイル検索
    all_images = find_all_images(image_dir)
    
    if not all_images:
        print("❌ 最適化対象の画像が見つかりません")
        return False
    
    print(f"📸 対象画像: {len(all_images)}枚")
    print(f"📁 画像ディレクトリ: {image_dir}")
    print()
    
    # 最適化実行
    success_count = 0
    total_original_size = 0
    total_optimized_size = 0
    failed_files = []
    
    for i, image_path in enumerate(all_images, 1):
        print(f"[{i}/{len(all_images)}] {image_path.name}")
        
        success, original_size, optimized_size = optimize_image(image_path)
        
        total_original_size += original_size
        total_optimized_size += optimized_size
        
        if success:
            success_count += 1
        else:
            failed_files.append(image_path.name)
    
    # 結果サマリー
    print()
    print("=" * 60)
    print("📊 最適化結果")
    print("=" * 60)
    print(f"✅ 処理成功: {success_count}/{len(all_images)} 枚")
    print(f"📉 合計サイズ: {total_original_size / 1024 / 1024:.1f}MB → {total_optimized_size / 1024 / 1024:.1f}MB")
    
    if total_original_size > 0:
        total_reduction = (1 - total_optimized_size / total_original_size) * 100
        print(f"🎯 全体削減率: {total_reduction:.1f}%")
        print(f"💾 節約容量: {(total_original_size - total_optimized_size) / 1024 / 1024:.1f}MB")
    
    if failed_files:
        print(f"\n❌ 失敗したファイル ({len(failed_files)}個):")
        for failed_file in failed_files:
            print(f"  - {failed_file}")
    
    # オリジナルファイル削除
    print()
    print("🗑️  オリジナルファイル削除処理")
    print("=" * 30)
    cleanup_backups(image_dir)
    
    print()
    print("✅ 全画像最適化 + オリジナル削除が完了しました！")
    print("🌐 次のステップ: サイト再ビルド・公開")
    
    return success_count == len(all_images)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)