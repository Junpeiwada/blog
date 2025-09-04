#!/usr/bin/env python3
"""
ファビコン生成スクリプト
JP.pngから複数サイズのファビコンを生成します
"""

from PIL import Image
import os

def create_favicons(input_path, output_dir):
    """複数サイズのファビコンを生成"""
    
    # 必要なファビコンサイズ
    sizes = [
        (16, 16, 'favicon-16x16.png'),
        (32, 32, 'favicon-32x32.png'),
        (48, 48, 'favicon-48x48.png'),
        (180, 180, 'apple-touch-icon.png'),  # iOS用
        (192, 192, 'android-chrome-192x192.png'),  # Android用
        (512, 512, 'android-chrome-512x512.png'),  # Android用
    ]
    
    # 元画像を読み込み
    try:
        original = Image.open(input_path)
        print(f"✅ 元画像読み込み成功: {input_path}")
        print(f"   サイズ: {original.size}")
        print(f"   モード: {original.mode}")
        
        # 出力ディレクトリを作成
        os.makedirs(output_dir, exist_ok=True)
        
        # 各サイズのファビコンを生成
        for width, height, filename in sizes:
            # リサイズ（高品質）
            resized = original.resize((width, height), Image.Resampling.LANCZOS)
            
            # 透明背景を維持するためRGBAモードを確認
            if original.mode == 'RGBA':
                resized = resized.convert('RGBA')
            
            # 出力パス
            output_path = os.path.join(output_dir, filename)
            
            # 保存
            resized.save(output_path, 'PNG', optimize=True)
            print(f"✅ 生成完了: {filename} ({width}x{height})")
        
        # favicon.icoファイルも生成（複数サイズを含む）
        ico_sizes = [(16, 16), (32, 32), (48, 48)]
        ico_images = []
        
        for width, height in ico_sizes:
            resized = original.resize((width, height), Image.Resampling.LANCZOS)
            if original.mode == 'RGBA':
                # ICOファイルのため透明度をサポート
                resized = resized.convert('RGBA')
            ico_images.append(resized)
        
        # favicon.icoを保存
        ico_path = os.path.join(output_dir, 'favicon.ico')
        ico_images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in ico_images])
        print(f"✅ 生成完了: favicon.ico (複数サイズ含む)")
        
        print(f"\n🎉 ファビコン生成完了！")
        print(f"📁 出力先: {output_dir}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False
    
    return True

def main():
    input_path = 'images/JP.png'
    output_dir = 'assets/favicons'
    
    print("=" * 50)
    print("🎨 ファビコン生成開始")
    print("=" * 50)
    
    if not os.path.exists(input_path):
        print(f"❌ 元画像が見つかりません: {input_path}")
        return
    
    success = create_favicons(input_path, output_dir)
    
    if success:
        print("\n📋 生成されたファイル:")
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                filepath = os.path.join(root, file)
                size = os.path.getsize(filepath)
                print(f"   {file} ({size:,} bytes)")

if __name__ == "__main__":
    main()