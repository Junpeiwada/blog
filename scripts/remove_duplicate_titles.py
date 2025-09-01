#!/usr/bin/env python3
"""
記事内の重複H1タイトルを自動除去するスクリプト
フロントマターのtitleと同じ内容のH1タイトルを削除します
"""

import os
import re
import yaml
from pathlib import Path

def parse_frontmatter_and_content(file_path):
    """Markdownファイルのフロントマターと本文を分離"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # フロントマターの抽出
    if content.startswith('---\n'):
        parts = content.split('---\n', 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2]
            return frontmatter, body
    
    return {}, content

def remove_duplicate_h1_title(file_path, dry_run=False):
    """重複するH1タイトルを除去"""
    try:
        frontmatter, body = parse_frontmatter_and_content(file_path)
        
        if 'title' not in frontmatter:
            return False, "フロントマターにtitleが見つかりません"
        
        title = frontmatter['title']
        
        # H1タイトルのパターンを検索（行の最初の # で始まるもの）
        h1_pattern = r'^# (.+)$'
        lines = body.split('\n')
        
        modified = False
        new_lines = []
        
        for line in lines:
            h1_match = re.match(h1_pattern, line.strip())
            if h1_match:
                h1_title = h1_match.group(1).strip()
                # フロントマターのtitleと一致する場合は除去
                if h1_title == title:
                    modified = True
                    print(f"  除去: {h1_title}")
                    continue
            new_lines.append(line)
        
        if modified and not dry_run:
            # ファイルを書き戻し
            new_body = '\n'.join(new_lines)
            new_content = f"---\n{yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)}---\n{new_body}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        
        return modified, "成功" if modified else "変更なし"
        
    except Exception as e:
        return False, f"エラー: {str(e)}"

def main():
    """メイン処理"""
    script_dir = Path(__file__).parent
    content_dir = script_dir.parent / "content" / "posts"
    
    if not content_dir.exists():
        print(f"エラー: {content_dir} が見つかりません")
        return
    
    print("記事内の重複H1タイトル除去を開始...")
    print(f"対象ディレクトリ: {content_dir}")
    print()
    
    # 最初はドライランで確認
    print("=== ドライラン（変更プレビュー） ===")
    modified_files = []
    
    for md_file in sorted(content_dir.glob("*.md")):
        print(f"チェック中: {md_file.name}")
        modified, message = remove_duplicate_h1_title(md_file, dry_run=True)
        if modified:
            modified_files.append(md_file)
        print(f"  → {message}")
    
    if not modified_files:
        print("\n除去対象のH1タイトルは見つかりませんでした。")
        return
    
    print(f"\n{len(modified_files)}個のファイルに変更が必要です。")
    
    # 実際の変更を実行するか確認
    response = input("\n実際に変更を適用しますか？ (y/N): ")
    if response.lower() != 'y':
        print("キャンセルしました。")
        return
    
    print("\n=== 実際の変更を適用中 ===")
    success_count = 0
    
    for md_file in modified_files:
        print(f"修正中: {md_file.name}")
        modified, message = remove_duplicate_h1_title(md_file, dry_run=False)
        if modified:
            success_count += 1
        print(f"  → {message}")
    
    print(f"\n完了: {success_count}個のファイルを修正しました。")
    print("\n次のステップ:")
    print("1. npm run build または python scripts/build.py でサイトを再ビルド")
    print("2. 修正結果を確認")

if __name__ == "__main__":
    main()