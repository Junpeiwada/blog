#!/usr/bin/env python3
"""
Blog deployment script for GitHub Pages
Builds the site and optionally commits/pushes changes
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from build import BlogBuilder

class BlogDeployer:
    def __init__(self, root_dir=None):
        if root_dir is None:
            root_dir = Path(__file__).parent.parent
        else:
            root_dir = Path(root_dir)
            
        self.root_dir = root_dir
        self.builder = BlogBuilder(root_dir)
        
    def run_command(self, cmd, cwd=None):
        """Run a shell command and return success status"""
        if cwd is None:
            cwd = self.root_dir
            
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
    
    def check_git_status(self):
        """Check if there are uncommitted changes"""
        success, output = self.run_command('git status --porcelain')
        if not success:
            print(f"Git状態の確認でエラー: {output}")
            return False, []
        
        changes = [line.strip() for line in output.split('\n') if line.strip()]
        return True, changes
    
    def check_dependencies(self):
        """Check if required Python packages are installed"""
        required_packages = [
            'jinja2',
            'markdown',
            'pyyaml',
            'pygments'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        return missing_packages
    
    def install_dependencies(self, packages):
        """Install missing Python packages"""
        if not packages:
            return True
            
        print(f"不足しているパッケージをインストール中: {', '.join(packages)}")
        cmd = f"pip install {' '.join(packages)}"
        success, output = self.run_command(cmd)
        
        if success:
            print("依存関係のインストール完了")
            return True
        else:
            print(f"依存関係のインストールでエラー: {output}")
            return False
    
    def build_site(self):
        """Build the blog site"""
        print("ブログサイトをビルド中...")
        try:
            self.builder.build_all(clean=True)
            print("サイトビルドが正常に完了しました")
            return True
        except Exception as e:
            print(f"サイトビルドでエラー: {e}")
            return False
    
    def commit_changes(self, message=None):
        """Commit changes to git"""
        if message is None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"ブログサイトデプロイ - {timestamp}"
        
        print("変更をコミット中...")
        
        # Add all changes
        success, output = self.run_command('git add .')
        if not success:
            print(f"変更の追加でエラー: {output}")
            return False
        
        # Commit changes
        success, output = self.run_command(f'git commit -m "{message}"')
        if not success:
            if "nothing to commit" in output:
                print("コミットする変更がありません")
                return True
            else:
                print(f"変更のコミットでエラー: {output}")
                return False
        
        print("変更のコミットが完了しました")
        return True
    
    def push_changes(self):
        """Push changes to remote repository"""
        print("リモートリポジトリに変更をプッシュ中...")
        
        success, output = self.run_command('git push origin main')
        if not success:
            print(f"変更のプッシュでエラー: {output}")
            return False
        
        print("変更のプッシュが完了しました")
        return True
    
    def deploy(self, commit=True, push=True, commit_message=None):
        """Full deployment process"""
        print("ブログデプロイを開始...")
        
        # Check dependencies
        missing_deps = self.check_dependencies()
        if missing_deps:
            print(f"不足している依存関係: {', '.join(missing_deps)}")
            if not self.install_dependencies(missing_deps):
                return False
        
        # Build site
        if not self.build_site():
            return False
        
        if commit:
            # Check git status
            success, changes = self.check_git_status()
            if not success:
                return False
            
            if changes:
                print(f"{len(changes)}個の変更ファイルを発見:")
                for change in changes[:10]:  # Show first 10 changes
                    print(f"  {change}")
                if len(changes) > 10:
                    print(f"  ... 他 {len(changes) - 10} ファイル")
                
                # Commit changes
                if not self.commit_changes(commit_message):
                    return False
                
                if push:
                    # Push changes
                    if not self.push_changes():
                        return False
            else:
                print("コミットする変更がありません")
        
        print("\nデプロイが正常に完了しました！")
        print(f"サイトURL: https://junpeiwada.github.io/blog/")
        print("注意: GitHub Pagesの更新には数分かかる場合があります")
        
        return True
    
    def status(self):
        """Show deployment status"""
        print("ブログデプロイ状態:")
        print(f"ルートディレクトリ: {self.root_dir}")
        print(f"記事ディレクトリ: {self.builder.content_dir}")
        print(f"出力ディレクトリ: {self.builder.docs_dir}")
        
        # Count markdown files
        md_files = list(self.builder.content_dir.glob('*.md'))
        print(f"Markdownファイル数: {len(md_files)}個")
        
        # Count HTML files
        html_files = list(self.builder.posts_dir.glob('*.html'))
        print(f"生成HTMLファイル数: {len(html_files)}個")
        
        # Check git status
        success, changes = self.check_git_status()
        if success:
            if changes:
                print(f"未コミット変更: {len(changes)}ファイル")
            else:
                print("Git状態: クリーン")
        
        # Check dependencies
        missing_deps = self.check_dependencies()
        if missing_deps:
            print(f"不足している依存関係: {', '.join(missing_deps)}")
        else:
            print("依存関係: すべてインストール済み")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='ブログをGitHub Pagesにデプロイ')
    parser.add_argument('--build-only', action='store_true', help='ビルドのみ実行（コミット・プッシュしない）')
    parser.add_argument('--no-push', action='store_true', help='コミットするがプッシュしない')
    parser.add_argument('--message', '-m', help='コミットメッセージ')
    parser.add_argument('--status', action='store_true', help='デプロイ状態を表示')
    
    args = parser.parse_args()
    
    deployer = BlogDeployer()
    
    if args.status:
        deployer.status()
        return
    
    if args.build_only:
        success = deployer.deploy(commit=False, push=False)
    elif args.no_push:
        success = deployer.deploy(commit=True, push=False, commit_message=args.message)
    else:
        success = deployer.deploy(commit=True, push=True, commit_message=args.message)
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()