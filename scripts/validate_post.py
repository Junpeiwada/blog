#!/usr/bin/env python3
"""
記事作成・更新時の検証スクリプト
使用方法: python scripts/validate_post.py [記事ファイルパス]
"""

import sys
import re
import yaml
from pathlib import Path
import argparse

class PostValidator:
    def __init__(self):
        self.blog_root = Path(__file__).parent.parent
        self.content_dir = self.blog_root / 'content' / 'posts'
        self.images_dir = self.blog_root / 'images'
        self.errors = []
        self.warnings = []
        
    def error(self, message):
        """エラーを記録"""
        self.errors.append(f"❌ エラー: {message}")
        
    def warning(self, message):
        """警告を記録"""
        self.warnings.append(f"⚠️  警告: {message}")
        
    def success(self, message):
        """成功メッセージを記録"""
        print(f"✅ {message}")
    
    def validate_filename(self, filepath):
        """ファイル名の検証"""
        filename = filepath.name
        
        # ファイル名パターン: YYYY-MM-DD-title.md
        pattern = r'^\d{4}-\d{2}-\d{2}-.+\.md$'
        if not re.match(pattern, filename):
            self.error(f"ファイル名が規則に従っていません: {filename}")
            self.error("正しい形式: YYYY-MM-DD-title.md")
            return False
            
        # 日付部分の妥当性チェック
        date_part = filename[:10]
        try:
            from datetime import datetime
            datetime.strptime(date_part, '%Y-%m-%d')
            self.success(f"ファイル名形式: {filename}")
        except ValueError:
            self.error(f"無効な日付形式: {date_part}")
            return False
            
        return True
    
    def validate_frontmatter(self, content):
        """フロントマターの検証"""
        if not content.startswith('---'):
            self.error("フロントマターが見つかりません")
            return None
            
        # フロントマター部分を抽出
        parts = content.split('---', 2)
        if len(parts) < 3:
            self.error("フロントマターが正しく閉じられていません")
            return None
            
        try:
            frontmatter = yaml.safe_load(parts[1])
        except yaml.YAMLError as e:
            self.error(f"フロントマターのYAML構文エラー: {e}")
            return None
            
        # 必須フィールドのチェック
        required_fields = ['title', 'date', 'category', 'description']
        for field in required_fields:
            if field not in frontmatter:
                self.error(f"必須フィールドが不足: {field}")
            elif not frontmatter[field]:
                self.error(f"空の必須フィールド: {field}")
                
        # カテゴリの確認
        if 'category' in frontmatter:
            category = frontmatter['category']
            valid_categories = ['mountain-guide', 'mountain', 'tech', 'travel', 'life', 'gear', 'sea']
            if category not in valid_categories:
                self.warning(f"未知のカテゴリ: {category}")
                self.warning(f"推奨カテゴリ: {', '.join(valid_categories)}")
                
        # 日付形式の確認
        if 'date' in frontmatter:
            date_str = str(frontmatter['date'])
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                self.error(f"日付形式が正しくありません: {date_str} (YYYY-MM-DD形式を使用)")
                
        # tagsフィールドの確認
        if 'tags' in frontmatter:
            if not isinstance(frontmatter['tags'], list):
                self.error("tagsフィールドはリスト形式で指定してください")
                
        self.success("フロントマター形式")
        return frontmatter
    
    def validate_images(self, content):
        """画像パスの検証"""
        # 画像参照パターンを検索
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(image_pattern, content)
        
        for alt_text, image_path in matches:
            # 相対パス形式の確認
            if not image_path.startswith('../images/'):
                self.error(f"画像パスが正しくありません: {image_path}")
                self.error("正しい形式: ../images/filename.ext")
                continue
                
            # 実際のファイル存在確認
            actual_path = self.images_dir / image_path.replace('../images/', '')
            if not actual_path.exists():
                self.error(f"画像ファイルが見つかりません: {actual_path}")
            else:
                self.success(f"画像ファイル: {image_path}")
                
            # altテキストの確認
            if not alt_text.strip():
                self.warning("altテキストが空です")
                
    def validate_content(self, content):
        """コンテンツの基本検証"""
        lines = content.split('\n')
        
        # フロントマター後の最初のH1チェック
        in_frontmatter = False
        frontmatter_ended = False
        found_h1 = False
        
        for line in lines:
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                else:
                    frontmatter_ended = True
                continue
                    
            if frontmatter_ended and line.startswith('# '):
                found_h1 = True
                break
                
        # H1見出しはテンプレートのタイトルがあるため不要
        # if not found_h1:
        #     self.warning("記事にH1見出し（# タイトル）がありません")
            
        # 最低限のコンテンツ長チェック
        content_without_frontmatter = content.split('---', 2)[2] if '---' in content else content
        if len(content_without_frontmatter.strip()) < 100:
            self.warning("記事の内容が短すぎる可能性があります")
            
        self.success("基本コンテンツ形式")
    
    def validate_post(self, filepath):
        """記事ファイル全体の検証"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            self.error(f"ファイルが見つかりません: {filepath}")
            return False
            
        print(f"\n📝 記事検証開始: {filepath.name}")
        print("=" * 50)
        
        # ファイル名検証
        self.validate_filename(filepath)
        
        # ファイル内容読み込み
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.error(f"ファイル読み込みエラー: {e}")
            return False
            
        # フロントマター検証
        self.validate_frontmatter(content)
        
        # 画像パス検証
        self.validate_images(content)
        
        # コンテンツ検証
        self.validate_content(content)
        
        # 結果表示
        print("\n" + "=" * 50)
        
        if self.warnings:
            print("\n⚠️  警告:")
            for warning in self.warnings:
                print(f"  {warning}")
                
        if self.errors:
            print("\n❌ エラー:")
            for error in self.errors:
                print(f"  {error}")
            print(f"\n💥 検証失敗: {len(self.errors)}個のエラーがあります")
            return False
        else:
            if self.warnings:
                print(f"\n⚠️  検証完了: {len(self.warnings)}個の警告があります")
            else:
                print("\n🎉 検証成功: 問題は見つかりませんでした")
            return True
    
    def get_post_display_info(self, filepath):
        """記事の表示情報を取得"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                category = frontmatter.get('category', 'unknown')
                
                print(f"\n📋 表示予測:")
                if category == 'mountain':
                    print("  🚫 この記事はインデックスページに表示されません（個別山岳記事）")
                else:
                    print("  ✅ この記事はインデックスページにカード表示されます")
                    
                print(f"  📂 カテゴリ: {category}")
                print(f"  🏷️  タグ: {', '.join(frontmatter.get('tags', []))}")
                
        except Exception as e:
            print(f"表示情報取得エラー: {e}")

def main():
    parser = argparse.ArgumentParser(description='ブログ記事の検証')
    parser.add_argument('filepath', help='検証する記事ファイルのパス')
    parser.add_argument('--info', action='store_true', help='記事の表示情報も表示')
    
    args = parser.parse_args()
    
    validator = PostValidator()
    success = validator.validate_post(args.filepath)
    
    if args.info:
        validator.get_post_display_info(args.filepath)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()