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
            print(f"Error checking git status: {output}")
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
            
        print(f"Installing missing packages: {', '.join(packages)}")
        cmd = f"pip install {' '.join(packages)}"
        success, output = self.run_command(cmd)
        
        if success:
            print("Dependencies installed successfully")
            return True
        else:
            print(f"Error installing dependencies: {output}")
            return False
    
    def build_site(self):
        """Build the blog site"""
        print("Building blog site...")
        try:
            self.builder.build_all(clean=True)
            print("Site build completed successfully")
            return True
        except Exception as e:
            print(f"Error building site: {e}")
            return False
    
    def commit_changes(self, message=None):
        """Commit changes to git"""
        if message is None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"Deploy blog site - {timestamp}"
        
        print("Committing changes...")
        
        # Add all changes
        success, output = self.run_command('git add .')
        if not success:
            print(f"Error adding changes: {output}")
            return False
        
        # Commit changes
        success, output = self.run_command(f'git commit -m "{message}"')
        if not success:
            if "nothing to commit" in output:
                print("No changes to commit")
                return True
            else:
                print(f"Error committing changes: {output}")
                return False
        
        print("Changes committed successfully")
        return True
    
    def push_changes(self):
        """Push changes to remote repository"""
        print("Pushing changes to remote repository...")
        
        success, output = self.run_command('git push origin main')
        if not success:
            print(f"Error pushing changes: {output}")
            return False
        
        print("Changes pushed successfully")
        return True
    
    def deploy(self, commit=True, push=True, commit_message=None):
        """Full deployment process"""
        print("Starting blog deployment...")
        
        # Check dependencies
        missing_deps = self.check_dependencies()
        if missing_deps:
            print(f"Missing dependencies: {', '.join(missing_deps)}")
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
                print(f"Found {len(changes)} changed files:")
                for change in changes[:10]:  # Show first 10 changes
                    print(f"  {change}")
                if len(changes) > 10:
                    print(f"  ... and {len(changes) - 10} more files")
                
                # Commit changes
                if not self.commit_changes(commit_message):
                    return False
                
                if push:
                    # Push changes
                    if not self.push_changes():
                        return False
            else:
                print("No changes to commit")
        
        print("\nDeployment completed successfully!")
        print(f"Site will be available at: https://junpeiwada.github.io/blog/")
        print("Note: GitHub Pages may take a few minutes to update")
        
        return True
    
    def status(self):
        """Show deployment status"""
        print("Blog deployment status:")
        print(f"Root directory: {self.root_dir}")
        print(f"Content directory: {self.builder.content_dir}")
        print(f"Docs directory: {self.builder.docs_dir}")
        
        # Count markdown files
        md_files = list(self.builder.content_dir.glob('*.md'))
        print(f"Markdown files: {len(md_files)}")
        
        # Count HTML files
        html_files = list(self.builder.posts_dir.glob('*.html'))
        print(f"Generated HTML files: {len(html_files)}")
        
        # Check git status
        success, changes = self.check_git_status()
        if success:
            if changes:
                print(f"Uncommitted changes: {len(changes)} files")
            else:
                print("Git status: clean")
        
        # Check dependencies
        missing_deps = self.check_dependencies()
        if missing_deps:
            print(f"Missing dependencies: {', '.join(missing_deps)}")
        else:
            print("Dependencies: all installed")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy blog to GitHub Pages')
    parser.add_argument('--build-only', action='store_true', help='Only build, don\'t commit or push')
    parser.add_argument('--no-push', action='store_true', help='Commit but don\'t push')
    parser.add_argument('--message', '-m', help='Commit message')
    parser.add_argument('--status', action='store_true', help='Show deployment status')
    
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