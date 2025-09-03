#!/usr/bin/env python3
"""
Blog site builder for GitHub Pages
Converts Markdown files to HTML using templates
"""

import os
import re
import json
import yaml
import markdown
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

class BlogBuilder:
    def __init__(self, root_dir=None):
        if root_dir is None:
            root_dir = Path(__file__).parent.parent
        else:
            root_dir = Path(root_dir)
            
        self.root_dir = root_dir
        self.content_dir = root_dir / "content" / "posts"
        self.docs_dir = root_dir / "docs"
        self.posts_dir = root_dir / "docs" / "posts"
        self.templates_dir = root_dir / "templates"
        
        # Create directories if they don't exist
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
        
        # Setup Markdown processor
        self.markdown_processor = markdown.Markdown(
            extensions=[
                'meta',
                'codehilite',
                'fenced_code',
                'tables',
                'toc',
                'footnotes'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True
                },
                'toc': {
                    'permalink': True
                }
            }
        )
    
    def parse_markdown_file(self, filepath):
        """Parse a markdown file and extract frontmatter and content"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split frontmatter and content
        if content.startswith('---'):
            try:
                _, frontmatter, body = content.split('---', 2)
                metadata = yaml.safe_load(frontmatter.strip())
            except ValueError:
                # No frontmatter found
                metadata = {}
                body = content
        else:
            metadata = {}
            body = content
        
        # Convert markdown to HTML
        html_content = self.markdown_processor.convert(body.strip())
        
        # Get markdown metadata (if no frontmatter was found)
        if not metadata and hasattr(self.markdown_processor, 'Meta'):
            for key, value in self.markdown_processor.Meta.items():
                if isinstance(value, list) and len(value) == 1:
                    metadata[key] = value[0]
                else:
                    metadata[key] = value
        
        # Extract filename info
        filename = filepath.stem
        
        # Try to parse date from filename (YYYY-MM-DD-title format)
        date_match = re.match(r'^(\d{4}-\d{2}-\d{2})-(.+)$', filename)
        if date_match:
            date_str, title_slug = date_match.groups()
            if 'date' not in metadata:
                metadata['date'] = date_str
            if 'title' not in metadata:
                metadata['title'] = title_slug.replace('-', ' ').title()
        
        # Ensure required fields have defaults
        metadata.setdefault('title', filename.replace('-', ' ').title())
        metadata.setdefault('date', datetime.now().strftime('%Y-%m-%d'))
        metadata.setdefault('category', 'uncategorized')
        metadata.setdefault('tags', [])
        metadata.setdefault('description', '')
        metadata.setdefault('featured_image', '')
        
        # Ensure tags is a list
        if isinstance(metadata['tags'], str):
            metadata['tags'] = [tag.strip() for tag in metadata['tags'].split(',')]
        
        return {
            'metadata': metadata,
            'content': html_content,
            'filename': filename + '.html',
            'source_path': filepath
        }
    
    def build_post(self, post_data):
        """Build individual post HTML file"""
        template = self.jinja_env.get_template('post.html')
        
        # Prepare template data
        template_data = {
            'post': {
                'title': post_data['metadata']['title'],
                'date': post_data['metadata']['date'],
                'category': post_data['metadata']['category'],
                'tags': post_data['metadata']['tags'],
                'description': post_data['metadata']['description'],
                'content': post_data['content']
            }
        }
        
        # Render template
        html_content = template.render(template_data)
        
        # Write to file
        output_path = self.posts_dir / post_data['filename']
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Built post: {post_data['filename']}")
        return output_path
    
    def build_index(self, posts_data):
        """Build index page with all posts"""
        template = self.jinja_env.get_template('index.html')
        
        # Sort posts by date (newest first)
        def get_date_key(post):
            date_val = post['metadata']['date']
            # Convert to string if it's a date object
            if hasattr(date_val, 'strftime'):
                return date_val.strftime('%Y-%m-%d')
            return str(date_val)
        
        sorted_posts = sorted(
            posts_data,
            key=get_date_key,
            reverse=True
        )
        
        # Generate category statistics
        category_stats = self.generate_category_stats(posts_data)
        
        # Prepare posts data for template
        posts_for_template = []
        for post in sorted_posts:
            posts_for_template.append({
                'title': post['metadata']['title'],
                'date': post['metadata']['date'],
                'category': post['metadata']['category'],
                'tags': post['metadata']['tags'],
                'description': post['metadata']['description'],
                'featured_image': post['metadata']['featured_image'],
                'url': f"posts/{post['filename']}.html",
                'filename': post['filename']
            })
        
        # Render template
        template_data = {
            'posts': posts_for_template,
            'category_stats': category_stats
        }
        html_content = template.render(template_data)
        
        # Write to file
        output_path = self.docs_dir / 'index.html'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Built index page with {len(posts_for_template)} posts")
        self.print_category_stats(category_stats)
        return output_path

    def generate_category_stats(self, posts_data):
        """Generate category statistics"""
        stats = {}
        for post in posts_data:
            category = post['metadata']['category']
            stats[category] = stats.get(category, 0) + 1
        
        return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))
    
    def print_category_stats(self, category_stats):
        """Print category statistics to console"""
        print("\n📊 カテゴリ別記事数統計:")
        for category, count in category_stats.items():
            print(f"   {category}: {count}記事")
        print()
        
        # Check for consistency with CATEGORY_GUIDE.md
        expected_categories = {
            '海・潜水', '釣り', '登山・クライミング', 
            '旅行記', 'ギア・道具', 'クラフト・DIY', '山岳ガイド'
        }
        actual_categories = set(category_stats.keys())
        
        if actual_categories - expected_categories:
            print("⚠️  標準外カテゴリが見つかりました:")
            for cat in actual_categories - expected_categories:
                print(f"   - {cat}")
            print("   → docs/CATEGORY_GUIDE.mdを確認してください")
            print()
    
    def clean_docs_dir(self):
        """Clean the docs directory"""
        if self.docs_dir.exists():
            # Remove all HTML files in docs/posts/
            for html_file in self.posts_dir.glob('*.html'):
                html_file.unlink()
            
            # Remove index.html
            index_file = self.docs_dir / 'index.html'
            if index_file.exists():
                index_file.unlink()
        
        print("Cleaned docs directory")
    
    def build_all(self, clean=True):
        """Build all posts and index page"""
        print("Starting blog build process...")
        
        if clean:
            self.clean_docs_dir()
        
        # Find all markdown files
        md_files = list(self.content_dir.glob('*.md'))
        if not md_files:
            print("No markdown files found in content/posts/")
            return
        
        print(f"Found {len(md_files)} markdown files")
        
        # Parse all posts
        posts_data = []
        for md_file in md_files:
            try:
                post_data = self.parse_markdown_file(md_file)
                posts_data.append(post_data)
                print(f"Parsed: {md_file.name}")
            except Exception as e:
                print(f"Error parsing {md_file.name}: {e}")
                continue
        
        if not posts_data:
            print("No valid posts found")
            return
        
        # Build individual posts
        print("\nBuilding individual posts...")
        for post_data in posts_data:
            try:
                self.build_post(post_data)
            except Exception as e:
                print(f"Error building post {post_data['filename']}: {e}")
        
        # Build index page
        print("\nBuilding index page...")
        try:
            self.build_index(posts_data)
        except Exception as e:
            print(f"Error building index page: {e}")
        
        
        # Copy images directory to docs
        self.copy_images()
        
        # Copy assets directory to docs
        self.copy_assets()
        
        print(f"\nBuild complete! Generated {len(posts_data)} posts")
        print(f"Output directory: {self.docs_dir}")
    
    def copy_images(self):
        """Copy images directory to docs"""
        import shutil
        
        images_src = self.root_dir / "images"
        images_dest = self.docs_dir / "images"
        
        if images_src.exists():
            if images_dest.exists():
                shutil.rmtree(images_dest)
            shutil.copytree(images_src, images_dest)
            print(f"Copied images from {images_src} to {images_dest}")
        else:
            print("No images directory found to copy")
    
    def copy_assets(self):
        """Copy assets directory to docs"""
        import shutil
        
        assets_src = self.root_dir / "assets"
        assets_dest = self.docs_dir / "assets"
        
        if assets_src.exists():
            if assets_dest.exists():
                shutil.rmtree(assets_dest)
            shutil.copytree(assets_src, assets_dest)
            print(f"Copied assets from {assets_src} to {assets_dest}")
        else:
            print("No assets directory found to copy")
    
    def serve_local(self, port=8000):
        """Serve the site locally for testing"""
        import http.server
        import socketserver
        import webbrowser
        import threading
        import time
        
        os.chdir(self.docs_dir)
        
        Handler = http.server.SimpleHTTPRequestHandler
        
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"Serving at http://localhost:{port}")
            
            # Open browser after a short delay
            def open_browser():
                time.sleep(1)
                webbrowser.open(f'http://localhost:{port}')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down server...")
                httpd.shutdown()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Build blog site')
    parser.add_argument('--serve', action='store_true', help='Serve site locally after building')
    parser.add_argument('--port', type=int, default=8000, help='Port for local server')
    parser.add_argument('--no-clean', action='store_true', help='Don\'t clean docs directory before building')
    
    args = parser.parse_args()
    
    builder = BlogBuilder()
    builder.build_all(clean=not args.no_clean)
    
    if args.serve:
        builder.serve_local(port=args.port)

if __name__ == '__main__':
    main()