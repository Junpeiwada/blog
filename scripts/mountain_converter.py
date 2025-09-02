#!/usr/bin/env python3
"""
Mountain info converter for blog
Converts mountain info from 山登り directory to blog posts
"""

import os
import re
import json
import yaml
from pathlib import Path
from datetime import datetime
import shutil

class MountainConverter:
    def __init__(self, source_dir=None, blog_dir=None):
        if source_dir is None:
            # Assuming script is run from blog directory
            source_dir = Path("../../AISandbox/山登り")
        if blog_dir is None:
            blog_dir = Path(__file__).parent.parent
        
        self.source_dir = Path(source_dir)
        self.blog_dir = Path(blog_dir)
        self.content_dir = self.blog_dir / "content" / "posts"
        self.images_dir = self.blog_dir / "docs" / "assets" / "images" / "mountains"
        
        # Create directories if they don't exist
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        # Mountain data storage
        self.mountains_data = []
        
        # All mountains will be converted - removed priority system
        self.date_counter = 5  # Starting from 2024-09-05
    
    def find_mountain_files(self):
        """Find all mountain markdown files"""
        md_files = []
        for area in ['北アルプス', '中央アルプス', '南アルプス']:
            area_path = self.source_dir / area
            if area_path.exists():
                md_files.extend(area_path.glob('**/*.md'))
        
        # Filter out requirement spec file
        return [f for f in md_files if 'mount要求仕様' not in str(f)]
    
    def parse_mountain_file(self, file_path):
        """Parse individual mountain markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract mountain name from file path or content
            mountain_name = file_path.stem
            if mountain_name == file_path.parent.name:
                # File name matches directory name
                pass
            else:
                # Try to extract from first line
                first_line = content.split('\n')[0]
                if first_line.startswith('# '):
                    mountain_name = first_line[2:].strip()
            
            # Parse content for key information
            mountain_data = self.extract_mountain_info(content, mountain_name, file_path)
            return mountain_data
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def extract_mountain_info(self, content, mountain_name, file_path):
        """Extract structured information from mountain content"""
        data = {
            'name': mountain_name,
            'source_path': file_path,
            'content': content,
            'area': self.get_mountain_area(file_path),
            'elevation': self.extract_elevation(content),
            'elevation_gain': self.extract_elevation_gain(content),
            'is_hyakumeizan': self.is_hyakumeizan(content),
            'difficulty': self.extract_difficulty(content),
            'duration': self.extract_duration(content),
            'prefecture': self.extract_prefecture(content)
        }
        
        return data
    
    def get_mountain_area(self, file_path):
        """Determine mountain area from file path"""
        path_str = str(file_path)
        if '北アルプス' in path_str:
            return '北アルプス'
        elif '中央アルプス' in path_str:
            return '中央アルプス'
        elif '南アルプス' in path_str:
            return '南アルプス'
        return '未分類'
    
    def extract_elevation(self, content):
        """Extract elevation from content"""
        elevation_match = re.search(r'標高.*?(\d{1,4})m', content)
        if elevation_match:
            return int(elevation_match.group(1))
        return None
    
    def extract_elevation_gain(self, content):
        """Extract elevation gain from content"""
        # Look for 獲得標高: XXXm pattern
        elevation_gain_match = re.search(r'獲得標高.*?(\d{1,4})m', content)
        if elevation_gain_match:
            return int(elevation_gain_match.group(1))
        
        # Look for pattern like (登山口XXXm→山頂XXXm)
        range_match = re.search(r'(\d{1,4})m.*?→.*?(\d{1,4})m', content)
        if range_match:
            start_elevation = int(range_match.group(1))
            end_elevation = int(range_match.group(2))
            return end_elevation - start_elevation
        
        return None
    
    def is_hyakumeizan(self, content):
        """Check if mountain is 日本百名山"""
        return '日本百名山.*はい' in content or '百名山' in content
    
    def extract_difficulty(self, content):
        """Extract difficulty rating"""
        # Look for star ratings
        difficulty_match = re.search(r'技術的難易度.*?(★+)', content)
        if difficulty_match:
            return len(difficulty_match.group(1))
        return None
    
    def extract_duration(self, content):
        """Extract duration information"""
        duration_match = re.search(r'標準コースタイム.*?(\d+.*?[時日])', content)
        if duration_match:
            return duration_match.group(1)
        return None
    
    def extract_prefecture(self, content):
        """Extract prefecture information"""
        pref_match = re.search(r'所在地.*?([^、\n]+)', content)
        if pref_match:
            return pref_match.group(1).strip()
        return None
    
    def create_blog_post(self, mountain_data, individual_post=False):
        """Create blog post from mountain data"""
        mountain_name = mountain_data['name']
        
        if individual_post:
            # Create individual detailed post for all mountains
            date = f"2024-09-{self.date_counter:02d}"
            self.date_counter += 1
            filename = f"{date}-{self.slugify(mountain_name)}-guide.md"
            tags = ['登山', mountain_data['area']]
            if mountain_data['is_hyakumeizan']:
                tags.append('百名山')
            tags.append(mountain_name)
            
            frontmatter = {
                'title': f"{mountain_name}完全ガイド - {mountain_data['area']}の名峰",
                'date': date,
                'category': 'mountain',
                'tags': tags,
                'description': f"{mountain_name}への登山ルート、アクセス、装備を詳しく解説。{mountain_data['area']}の代表的な山岳です。"
            }
            
            # Enhanced content for individual posts
            content = self.enhance_individual_content(mountain_data)
            
        else:
            # Create summary for index post
            return self.create_mountain_summary(mountain_data)
        
        # Generate full markdown content
        full_content = self.generate_markdown_post(frontmatter, content)
        
        # Write to file
        output_path = self.content_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"Created blog post: {filename}")
        return output_path
    
    def create_mountain_summary(self, mountain_data):
        """Create summary data for index post"""
        # Generate the expected filename for the individual post
        slugified_name = self.slugify(mountain_data['name'])
        # We need to assign a date to match the individual post
        # For now, use a temporary counter - this will be fixed in convert_all
        filename = f"PLACEHOLDER-{slugified_name}-guide.html"
        
        return {
            'name': mountain_data['name'],
            'area': mountain_data['area'],
            'elevation': mountain_data['elevation'] or '不明',
            'elevation_gain': mountain_data['elevation_gain'] or '不明',
            'prefecture': mountain_data['prefecture'] or '不明',
            'hyakumeizan': '○' if mountain_data['is_hyakumeizan'] else '',
            'difficulty': '★' * (mountain_data['difficulty'] or 0) if mountain_data['difficulty'] else '不明',
            'duration': mountain_data['duration'] or '不明',
            'filename': filename  # Add filename for linking
        }
    
    def enhance_individual_content(self, mountain_data):
        """Enhance content for individual posts"""
        original_content = mountain_data['content']
        
        # Add blog-specific enhancements
        enhanced_content = f"""
{original_content}

---

<div class="mt-4 mb-4 p-3 bg-light border-left border-primary">
    <h5><i class="bi bi-arrow-left-circle"></i> 日本アルプス登山完全ガイドに戻る</h5>
    <p class="mb-2">この記事は日本アルプス全山ガイドの詳細版です。</p>
    <a href="../2024-09-04-japanese-alps-complete-guide.html" class="btn btn-primary">
        <i class="bi bi-mountain"></i> 全山ガイドに戻る
    </a>
</div>

## 登山の安全について

### 最新情報の確認
登山前には必ず以下の情報を確認してください：
- 気象情報・天気予報
- 登山道の状況
- 山小屋の営業状況
- 交通アクセスの状況

### 緊急時の連絡先
- **遭難時**: 110番（警察）
- **山域別救助隊**: 各県警山岳救助隊

**参考リンク**:
- [山岳関係気象情報](https://www.jma.go.jp/bosai/#pattern=rain_snow)
- [山と高原地図](https://www.yamakei.co.jp/)
- [長野県警山岳情報](https://www.pref.nagano.lg.jp/police/)
"""
        
        return enhanced_content
    
    def generate_markdown_post(self, frontmatter, content):
        """Generate complete markdown post"""
        yaml_content = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)
        return f"---\n{yaml_content}---\n\n{content}"
    
    def create_index_post(self):
        """Create main index post with all mountains"""
        mountains_summary = [self.create_mountain_summary(m) for m in self.mountains_data]
        
        # Sort by elevation (descending)
        mountains_summary.sort(key=lambda x: x['elevation'] if isinstance(x['elevation'], int) else 0, reverse=True)
        
        frontmatter = {
            'title': '日本アルプス登山完全ガイド - 全山制覇への道',
            'date': '2024-09-04',
            'category': 'mountain',
            'tags': ['登山', '日本アルプス', '百名山', '山岳ガイド'],
            'description': '日本アルプス全54山の完全ガイド。北アルプス、中央アルプス、南アルプスの全山を網羅した登山情報データベース。'
        }
        
        content = self.generate_index_content(mountains_summary)
        full_content = self.generate_markdown_post(frontmatter, content)
        
        output_path = self.content_dir / "2024-09-04-japanese-alps-complete-guide.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"Created index post: 2024-09-04-japanese-alps-complete-guide.md")
        return output_path
    
    def create_index_post_with_links(self, mountains_summary):
        """Create main index post with correct links to individual mountains"""
        frontmatter = {
            'title': '日本アルプス登山完全ガイド - 全山制覇への道',
            'date': '2024-09-04',
            'category': 'mountain-guide',
            'tags': ['登山', '日本アルプス', '百名山', '山岳ガイド'],
            'description': f'日本アルプス全{len(mountains_summary)}山の完全ガイド。北アルプス、中央アルプス、南アルプスの全山を網羅した登山情報データベース。',
            'featured': True
        }
        
        content = self.generate_index_content(mountains_summary)
        full_content = self.generate_markdown_post(frontmatter, content)
        
        output_path = self.content_dir / "2024-09-04-japanese-alps-complete-guide.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"Created index post with links: 2024-09-04-japanese-alps-complete-guide.md")
        return output_path
    
    def generate_index_content(self, mountains_summary):
        """Generate content for index post"""
        content = f"""# 日本アルプス登山完全ガイド

日本アルプス（北アルプス、中央アルプス、南アルプス）の全{len(mountains_summary)}山を網羅した完全ガイドです。
各山の基本情報、難易度、アクセスなどを一覧で確認できます。

## 山域別概要

### 北アルプス（飛騨山脈）
日本アルプスの中で最も人気が高く、3,000m級の山々が連なる山域。
槍ヶ岳、穂高岳、剱岳など、登山者憧れの名峰が揃っています。

### 中央アルプス（木曽山脈）
コンパクトながら美しい山容を持つ山域。木曽駒ヶ岳を中心とした山々。
千畳敷カールなど、アクセスしやすい絶景スポットも多数。

### 南アルプス（赤石山脈）
日本第2位の高峰・北岳をはじめとする静寂な山域。
深い山懐と豊富な高山植物が魅力です。

## 全山一覧表

<div class="mountain-filters mb-3">
    <button class="btn btn-primary filter-btn" data-filter="all">すべて</button>
    <button class="btn btn-outline-primary filter-btn" data-filter="北アルプス">北アルプス</button>
    <button class="btn btn-outline-primary filter-btn" data-filter="中央アルプス">中央アルプス</button>
    <button class="btn btn-outline-primary filter-btn" data-filter="南アルプス">南アルプス</button>
    <button class="btn btn-outline-success filter-btn" data-filter="hyakumeizan">百名山のみ</button>
</div>

<div class="table-responsive">
    <table class="table table-striped" id="mountainTable">
        <thead>
            <tr>
                <th>山名</th>
                <th>標高</th>
                <th>獲得標高</th>
                <th>山域</th>
                <th>所在地</th>
                <th>百名山</th>
                <th>難易度</th>
                <th>所要時間</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for mountain in mountains_summary:
            # Create link to individual mountain page (same directory)
            mountain_link = f'<a href="{mountain["filename"]}" class="text-decoration-none"><strong>{mountain["name"]}</strong></a>'
            # Format elevation and elevation gain
            elevation = f"{mountain['elevation']}m" if mountain['elevation'] != '不明' else '不明'
            elevation_gain = f"{mountain['elevation_gain']}m" if mountain['elevation_gain'] != '不明' else '不明'
            
            content += f"""            <tr data-area="{mountain['area']}" data-hyakumeizan="{mountain['hyakumeizan']}">
                <td>{mountain_link}</td>
                <td>{elevation}</td>
                <td>{elevation_gain}</td>
                <td><span class="badge bg-secondary">{mountain['area']}</span></td>
                <td>{mountain['prefecture']}</td>
                <td>{mountain['hyakumeizan']}</td>
                <td>{mountain['difficulty']}</td>
                <td>{mountain['duration']}</td>
            </tr>
"""
        
        content += """        </tbody>
    </table>
</div>

## 登山計画のポイント

### 難易度について
- ★☆☆☆☆: 初心者向け
- ★★☆☆☆: 初級者向け
- ★★★☆☆: 中級者向け
- ★★★★☆: 上級者向け
- ★★★★★: エキスパート向け

### 装備チェックリスト
#### 基本装備
- 登山靴（トレッキングブーツ）
- ザック（日帰り30-40L、宿泊50-70L）
- レインウェア上下
- 防寒着（フリース・ダウンなど）
- ヘッドランプ + 予備電池
- 地図・コンパス（GPS）
- 救急用品

#### 宿泊装備（山小屋泊以外）
- テント・シュラフ
- 調理器具・食料
- 水（浄水器具）

### 安全登山のために
1. **登山計画書の提出**: 必ず家族や関係機関に提出
2. **天候確認**: 気象情報を必ずチェック
3. **体力と技術の確認**: 無理のない計画を
4. **装備の点検**: 事前に必ず確認・メンテナンス
5. **緊急時の準備**: 連絡手段と避難計画

## 人気の山（個別ガイドあり）

以下の山については、詳細な個別ガイド記事をご用意しています：

- [槍ヶ岳完全ガイド](../2024-09-05-槍ヶ岳-guide.html) - 北アルプスの盟主
- [穂高岳完全ガイド](../2024-09-06-穂高岳-guide.html) - 日本のマッターホルン
- [剱岳完全ガイド](../2024-09-07-剱岳-guide.html) - 岩と雪の殿堂

## まとめ

日本アルプスは日本の登山における最高峰の山域です。
しっかりとした準備と計画で、安全で楽しい山行を心がけてください。

**関連リンク**:
- [山岳関係気象情報](https://www.jma.go.jp/)
- [山と高原地図](https://www.yamakei.co.jp/)
- [日本山岳会](https://www.jac.or.jp/)

<script>
// Mountain table filtering
document.addEventListener('DOMContentLoaded', function() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const tableRows = document.querySelectorAll('#mountainTable tbody tr');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update button states
            filterButtons.forEach(btn => {
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-outline-primary');
            });
            this.classList.remove('btn-outline-primary');
            this.classList.add('btn-primary');
            
            const filter = this.dataset.filter;
            
            tableRows.forEach(row => {
                const area = row.dataset.area;
                const isHyakumeizan = row.dataset.hyakumeizan === '○';
                
                let show = false;
                if (filter === 'all') {
                    show = true;
                } else if (filter === 'hyakumeizan') {
                    show = isHyakumeizan;
                } else {
                    show = area === filter;
                }
                
                row.style.display = show ? '' : 'none';
            });
        });
    });
});
</script>
"""
        
        return content
    
    def slugify(self, text):
        """Convert text to URL-friendly slug"""
        # Simple slugify for Japanese text
        return re.sub(r'[^\w\-_]', '-', text.lower()).strip('-')
    
    def copy_images(self):
        """Copy mountain images to blog assets"""
        # Look for image files in mountain directories
        source_images_dir = self.source_dir / "docs"
        if source_images_dir.exists():
            for img_file in source_images_dir.glob("**/*.{png,jpg,jpeg,gif,svg}"):
                dest_path = self.images_dir / img_file.name
                try:
                    shutil.copy2(img_file, dest_path)
                    print(f"Copied image: {img_file.name}")
                except Exception as e:
                    print(f"Error copying {img_file.name}: {e}")
    
    def convert_all(self):
        """Convert all mountain data to blog posts"""
        print("Starting mountain info conversion...")
        
        # Find and parse all mountain files
        mountain_files = self.find_mountain_files()
        print(f"Found {len(mountain_files)} mountain files")
        
        for file_path in mountain_files:
            mountain_data = self.parse_mountain_file(file_path)
            if mountain_data:
                self.mountains_data.append(mountain_data)
        
        print(f"Parsed {len(self.mountains_data)} mountains")
        
        # Create individual posts for ALL mountains and collect filenames
        individual_count = 0
        mountain_to_filename = {}
        
        for mountain_data in self.mountains_data:
            mountain_name = mountain_data['name']
            date = f"2024-09-{self.date_counter:02d}"
            slugified_name = self.slugify(mountain_name)
            filename = f"{date}-{slugified_name}-guide.html"
            mountain_to_filename[mountain_name] = filename
            
            self.create_blog_post(mountain_data, individual_post=True)
            individual_count += 1
        
        print(f"Created {individual_count} individual posts")
        
        # Update mountain summaries with correct filenames
        mountains_summary = []
        for mountain_data in self.mountains_data:
            summary = self.create_mountain_summary(mountain_data)
            # Replace placeholder with actual filename
            mountain_name = mountain_data['name']
            summary['filename'] = mountain_to_filename[mountain_name]
            mountains_summary.append(summary)
        
        # Sort by elevation (descending)
        mountains_summary.sort(key=lambda x: x['elevation'] if isinstance(x['elevation'], int) else 0, reverse=True)
        
        # Create index post with correct links
        self.create_index_post_with_links(mountains_summary)
        
        # Copy images
        self.copy_images()
        
        print("Mountain conversion completed!")
        
        # Return summary
        return {
            'total_mountains': len(self.mountains_data),
            'individual_posts': individual_count,
            'index_post': True,
            'images_copied': True
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert mountain info to blog posts')
    parser.add_argument('--source', help='Source directory (山登り directory)')
    parser.add_argument('--blog', help='Blog directory')
    
    args = parser.parse_args()
    
    converter = MountainConverter(source_dir=args.source, blog_dir=args.blog)
    result = converter.convert_all()
    
    print("\nConversion Summary:")
    print(f"Total mountains processed: {result['total_mountains']}")
    print(f"Individual posts created: {result['individual_posts']}")
    print(f"Index post created: {result['index_post']}")
    print(f"Images copied: {result['images_copied']}")

if __name__ == '__main__':
    main()