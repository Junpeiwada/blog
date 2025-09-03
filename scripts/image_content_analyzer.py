#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像コンテンツ分析ツール
Google Photos抽出済みURLからEXIF分析・記事構成提案

使用方法:
  python image_content_analyzer.py url1 url2 url3 ...
  python image_content_analyzer.py url1 url2 --topic "花火大会" --suggest-structure

機能:
1. 複数画像URLからのEXIF情報取得
2. 撮影時刻による自動ソート
3. 記事構成提案（時系列・内容別）
4. Markdown形式出力
5. ブログ記事作成支援
"""

import sys
import requests
import io
from datetime import datetime, timedelta, date, time as dtime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import json
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import csv
import yaml


class ImageContentAnalyzer:
    def __init__(self, topic_hint="", verbose=True):
        self.topic_hint = topic_hint
        self.verbose = verbose
        # captions: {url or index(str): caption str}
        self.captions = {}
        
    def get_exif_data(self, image_url):
        """単一画像からEXIF情報を取得"""
        try:
            if self.verbose:
                print(f"📷 分析中: {image_url[:60]}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # PILでイメージを開く
            image = Image.open(io.BytesIO(response.content))
            
            if self.verbose:
                print(f"   ✅ サイズ: {image.size[0]}×{image.size[1]}px, 形式: {image.format}")
            
            # EXIFデータを取得
            exif_data = image.getexif()
            
            if not exif_data:
                return {
                    'url': image_url,
                    'size': image.size,
                    'format': image.format,
                    'datetime': None,
                    'camera_make': None,
                    'camera_model': None,
                    'gps_info': None,
                    'has_exif': False
                }
            
            # EXIFデータを解析
            exif_dict = {}
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                exif_dict[tag_name] = value
            
            # EXIFデータオブジェクトも保持（IFDアクセス用）
            exif_dict['_raw_exif'] = exif_data
            
            # GPS情報を解析
            gps_info = self._extract_gps_info(exif_dict)
            
            # 撮影日時の解析（改良版）
            datetime_obj = self._extract_datetime_enhanced(exif_data, exif_dict)
            
            # ISO、絞り、シャッタースピードなど
            camera_settings = self._extract_camera_settings(exif_dict)
            
            result = {
                'url': image_url,
                'size': image.size,
                'format': image.format,
                'datetime': datetime_obj,
                'datetime_str': exif_dict.get('DateTimeOriginal') or exif_dict.get('DateTime'),
                'camera_make': exif_dict.get('Make'),
                'camera_model': exif_dict.get('Model'),
                'gps_info': gps_info,
                'camera_settings': camera_settings,
                'has_exif': True,
                'exif_raw': exif_dict
            }
            
            if self.verbose and datetime_obj:
                print(f"   📅 撮影: {datetime_obj.strftime('%Y-%m-%d %H:%M:%S')}")
            if self.verbose and gps_info:
                print(f"   🌍 GPS: {gps_info['latitude']:.4f}, {gps_info['longitude']:.4f}")
                
            return result
            
        except Exception as e:
            if self.verbose:
                print(f"   ❌ エラー: {e}")
            return {
                'url': image_url,
                'error': str(e),
                'has_exif': False
            }
    
    def _extract_gps_info(self, exif_dict):
        """GPS情報を抽出"""
        if 'GPSInfo' not in exif_dict:
            return None
            
        gps_data = exif_dict['GPSInfo']
        gps_dict = {}
        for key in gps_data.keys():
            name = GPSTAGS.get(key, key)
            gps_dict[name] = gps_data[key]
        
        if 'GPSLatitude' in gps_dict and 'GPSLongitude' in gps_dict:
            lat = self._convert_gps_coordinate(gps_dict['GPSLatitude'], gps_dict.get('GPSLatitudeRef', 'N'))
            lon = self._convert_gps_coordinate(gps_dict['GPSLongitude'], gps_dict.get('GPSLongitudeRef', 'E'))
            return {'latitude': lat, 'longitude': lon}
        
        return None
    
    def _convert_gps_coordinate(self, coord, ref):
        """GPS座標を度数に変換"""
        try:
            degrees = float(coord[0])
            minutes = float(coord[1])
            seconds = float(coord[2])
            
            decimal = degrees + minutes/60 + seconds/3600
            
            if ref in ['S', 'W']:
                decimal = -decimal
                
            return decimal
        except:
            return None
    
    def _extract_datetime(self, exif_dict):
        """撮影日時を抽出（DateTimeOriginalを優先的に取得）"""
        # まず通常のEXIFから確認
        datetime_str = exif_dict.get('DateTimeOriginal') or exif_dict.get('DateTime')
        
        # DateTimeOriginalが見つからない場合、IFDから直接取得
        if not datetime_str and hasattr(exif_dict, 'get_ifd'):
            try:
                exif_ifd = exif_dict.get_ifd(0x8769)  # Exif IFD
                if exif_ifd:
                    datetime_str = exif_ifd.get(36867)  # DateTimeOriginal tag ID
                    if not datetime_str:
                        datetime_str = exif_ifd.get(36868)  # DateTimeDigitized tag ID
            except:
                pass
        
        if datetime_str:
            try:
                return datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
            except:
                pass
        return None
    
    def _extract_datetime_enhanced(self, exif_data, exif_dict):
        """撮影日時の拡張取得（IFDから直接取得を含む）"""
        # Method 1: 通常のEXIFから確認
        datetime_str = exif_dict.get('DateTimeOriginal') or exif_dict.get('DateTime')
        
        # Method 2: IFDから直接取得（Google Photos対応）
        if not datetime_str and hasattr(exif_data, 'get_ifd'):
            try:
                exif_ifd = exif_data.get_ifd(0x8769)  # Exif IFD
                if exif_ifd:
                    # DateTimeOriginal (36867)
                    datetime_str = exif_ifd.get(36867)
                    if not datetime_str:
                        # DateTimeDigitized (36868)
                        datetime_str = exif_ifd.get(36868)
                    if not datetime_str:
                        # DateTime (306) - 最後の手段
                        datetime_str = exif_ifd.get(306)
            except Exception as e:
                if self.verbose:
                    print(f"   ⚠️ IFD取得エラー: {e}")
        
        # Method 3: すべてのEXIFタグから日時関連を探す
        if not datetime_str:
            datetime_tags = [36867, 36868, 306]  # DateTimeOriginal, DateTimeDigitized, DateTime
            for tag_id in datetime_tags:
                if tag_id in exif_data:
                    datetime_str = exif_data[tag_id]
                    break
        
        # 文字列をdatetimeオブジェクトに変換
        if datetime_str:
            try:
                dt = datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
                if self.verbose:
                    print(f"   📅 撮影日時: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                return dt
            except Exception as e:
                if self.verbose:
                    print(f"   ⚠️ 日時解析エラー: {datetime_str} - {e}")
        
        return None
    
    def _extract_camera_settings(self, exif_dict):
        """カメラ設定情報を抽出"""
        settings = {}
        
        # ISO感度
        if 'ISOSpeedRatings' in exif_dict:
            settings['iso'] = exif_dict['ISOSpeedRatings']
        
        # 絞り値
        if 'FNumber' in exif_dict:
            try:
                f_num = float(exif_dict['FNumber'])
                settings['aperture'] = f"f/{f_num:.1f}"
            except:
                pass
        
        # シャッタースピード
        if 'ExposureTime' in exif_dict:
            try:
                exp_time = float(exif_dict['ExposureTime'])
                if exp_time >= 1:
                    settings['shutter_speed'] = f"{exp_time:.1f}s"
                else:
                    settings['shutter_speed'] = f"1/{int(1/exp_time)}s"
            except:
                pass
        
        # 焦点距離
        if 'FocalLength' in exif_dict:
            try:
                focal = float(exif_dict['FocalLength'])
                settings['focal_length'] = f"{focal:.0f}mm"
            except:
                pass
        
        return settings
    
    def analyze_multiple_images(self, urls, parallel=True, max_workers=5):
        """複数画像の並行分析"""
        print(f"🔍 {len(urls)}枚の画像を分析開始...")
        
        results = []
        
        if parallel and len(urls) > 1:
            # 並行処理
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {executor.submit(self.get_exif_data, url): url for url in urls}
                
                for future in as_completed(future_to_url):
                    result = future.result()
                    results.append(result)
        else:
            # 順次処理
            for url in urls:
                result = self.get_exif_data(url)
                results.append(result)
                time.sleep(0.5)  # レート制限対策
        # 既定では撮影時刻でソート。ただし外側で手動割当を行う場合に並び替えたいケースがあるため、
        # 呼び出し側で必要に応じて再ソート（または入力順へ再配置）してください。
        def sort_key(item):
            if 'error' in item or not item.get('datetime'):
                return datetime.max
            return item['datetime']
        results.sort(key=sort_key)
        
        success_count = len([r for r in results if 'error' not in r])
        print(f"✅ 分析完了: {success_count}/{len(urls)}枚成功")
        
        return results
    
    def suggest_blog_structure(self, analyzed_images):
        """記事構成を提案"""
        print(f"\n📝 記事構成を分析中...")
        
        # 有効な画像を抽出
        valid_images = [img for img in analyzed_images if 'error' not in img]
        
        if not valid_images:
            print("❌ 分析できる画像がありません")
            return None
        
        # 時系列のある画像を抽出
        timed_images = [img for img in valid_images if img.get('datetime')]
        
        if not timed_images:
            return self._suggest_basic_structure(valid_images)
        
        # 撮影時刻に基づく構成提案
        return self._suggest_time_based_structure(timed_images, valid_images)
    
    def _suggest_time_based_structure(self, timed_images, all_images):
        """時系列に基づく構成提案"""
        start_time = timed_images[0]['datetime']
        end_time = timed_images[-1]['datetime']
        duration = (end_time - start_time).total_seconds() / 3600  # 時間
        
        structure = {
            'type': 'time_based',
            'suggested_date': start_time.strftime('%Y-%m-%d'),
            'time_range': f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}",
            'duration_hours': round(duration, 2),
            'total_images': len(all_images),
            'timed_images': len(timed_images),
            'sections': []
        }
        
        # 時間帯でグループ化
        if duration <= 1:
            # 1時間以内: 短時間イベント
            groups = self._group_by_short_intervals(timed_images)
        elif duration <= 4:
            # 4時間以内: 中時間イベント  
            groups = self._group_by_medium_intervals(timed_images)
        else:
            # それ以上: 長時間イベント
            groups = self._group_by_long_intervals(timed_images)
        
        # セクション生成
        for group_name, images in groups.items():
            section = {
                'title': self._generate_section_title(group_name, images),
                'time': f"{images[0]['datetime'].strftime('%H:%M')}頃",
                'images': [img['url'] for img in images],
                'image_count': len(images),
                'duration': self._calculate_group_duration(images)
            }
            structure['sections'].append(section)
        
        return structure
    
    def _group_by_short_intervals(self, images):
        """短時間イベント用グループ化（30分間隔）"""
        if len(images) <= 3:
            return {"メイン": images}
        
        start_time = images[0]['datetime']
        groups = {}
        
        for img in images:
            elapsed = (img['datetime'] - start_time).total_seconds() / 60  # 分
            
            if elapsed < 15:
                group = "開始"
            elif elapsed < 30:
                group = "前半"
            elif elapsed < 45:
                group = "後半"
            else:
                group = "終了"
            
            if group not in groups:
                groups[group] = []
            groups[group].append(img)
        
        return groups
    
    def _group_by_medium_intervals(self, images):
        """中時間イベント用グループ化（1時間間隔）"""
        start_time = images[0]['datetime']
        groups = {}
        
        for img in images:
            elapsed = (img['datetime'] - start_time).total_seconds() / 3600  # 時間
            
            if elapsed < 0.5:
                group = "準備・開始"
            elif elapsed < 1.5:
                group = "前半"
            elif elapsed < 2.5:
                group = "中盤"
            elif elapsed < 3.5:
                group = "後半"
            else:
                group = "終了・片付け"
            
            if group not in groups:
                groups[group] = []
            groups[group].append(img)
        
        return groups
    
    def _group_by_long_intervals(self, images):
        """長時間イベント用グループ化（2時間間隔）"""
        start_time = images[0]['datetime']
        groups = {}
        
        for img in images:
            elapsed = (img['datetime'] - start_time).total_seconds() / 3600
            
            if elapsed < 1:
                group = "開始"
            elif elapsed < 3:
                group = "午前中"
            elif elapsed < 6:
                group = "午後前半"
            elif elapsed < 9:
                group = "午後後半"
            else:
                group = "終了"
            
            if group not in groups:
                groups[group] = []
            groups[group].append(img)
        
        return groups
    
    def _suggest_basic_structure(self, images):
        """基本構成提案（時系列情報なし）"""
        image_count = len(images)
        
        if image_count <= 3:
            sections = ["導入", "メイン", "まとめ"]
        elif image_count <= 6:
            sections = ["準備", "前半", "後半", "まとめ"]
        else:
            sections = ["導入", "展開", "クライマックス", "結末"]
        
        structure = {
            'type': 'basic',
            'suggested_date': datetime.now().strftime('%Y-%m-%d'),
            'time_range': '時刻情報なし',
            'total_images': image_count,
            'sections': []
        }
        
        # 画像を均等配分
        images_per_section = image_count // len(sections)
        remainder = image_count % len(sections)
        
        start_idx = 0
        for i, section_name in enumerate(sections):
            count = images_per_section + (1 if i < remainder else 0)
            section_images = images[start_idx:start_idx + count]
            
            structure['sections'].append({
                'title': section_name,
                'time': '時刻不明',
                'images': [img['url'] for img in section_images],
                'image_count': len(section_images)
            })
            
            start_idx += count
        
        return structure
    
    def _generate_section_title(self, group_name, images):
        """グループ名とトピックに基づいてセクションタイトルを生成"""
        if self.topic_hint:
            topic_keywords = {
                '花火': {'開始': '会場到着・準備', '前半': '花火開始', '中盤': 'ワイドスターマイン', '後半': 'フィナーレ'},
                '登山': {'開始': '登山開始', '前半': '序盤の登り', '中盤': '中腹', '後半': '山頂・下山'},
                '旅行': {'開始': '出発・移動', '前半': '到着・散策', '中盤': '観光・体験', '後半': '帰路'},
                'キャンプ': {'開始': '設営', '前半': '準備・食事', '中盤': '活動', '後半': '撤収'}
            }
            
            for keyword, mapping in topic_keywords.items():
                if keyword in self.topic_hint:
                    return mapping.get(group_name, f"{group_name}の様子")
        
        return f"{group_name}の様子"
    
    def _calculate_group_duration(self, images):
        """グループ内の撮影時間幅を計算"""
        if len(images) < 2 or not all(img.get('datetime') for img in images):
            return "時間不明"
        
        times = [img['datetime'] for img in images if img.get('datetime')]
        if len(times) < 2:
            return "瞬間"
        
        duration = (max(times) - min(times)).total_seconds() / 60  # 分
        
        if duration < 1:
            return "瞬間"
        elif duration < 60:
            return f"{int(duration)}分間"
        else:
            hours = int(duration // 60)
            minutes = int(duration % 60)
            return f"{hours}時間{minutes}分間"
    
    def generate_markdown_report(self, analyzed_images, structure=None):
        """Markdown形式のレポート生成"""
        output = []
        output.append("# 画像分析レポート\n")
        
        # 基本統計
        valid_images = [img for img in analyzed_images if 'error' not in img]
        timed_images = [img for img in valid_images if img.get('datetime')]
        gps_images = [img for img in valid_images if img.get('gps_info')]
        
        output.append(f"**総画像数**: {len(analyzed_images)}枚")
        output.append(f"**分析成功**: {len(valid_images)}枚")
        output.append(f"**撮影時刻あり**: {len(timed_images)}枚")
        output.append(f"**GPS情報あり**: {len(gps_images)}枚\n")
        
        if structure:
            output.append(f"**推奨記事日付**: {structure['suggested_date']}")
            output.append(f"**撮影時間帯**: {structure['time_range']}")
            if structure.get('duration_hours'):
                output.append(f"**撮影時間**: {structure['duration_hours']}時間\n")
        
        # 記事構成提案
        if structure and structure.get('sections'):
            output.append("## 📝 推奨記事構成\n")
            for i, section in enumerate(structure['sections'], 1):
                output.append(f"### {i}. {section['title']} ({section['time']})")
                output.append(f"- 画像数: {section['image_count']}枚")
                if section.get('duration'):
                    output.append(f"- 撮影時間幅: {section['duration']}")
                output.append("- 使用画像:")
                for j, img_url in enumerate(section['images'], 1):
                    output.append(f"  {j}. `![{section['title']}{j}]({img_url})`")
                output.append("")
        
        # 詳細画像情報
        output.append("## 📷 画像詳細情報\n")
        for i, img in enumerate(analyzed_images, 1):
            if 'error' in img:
                output.append(f"### 画像 {i} ❌")
                output.append(f"- **URL**: {img['url']}")
                output.append(f"- **エラー**: {img['error']}\n")
                continue
            
            output.append(f"### 画像 {i}")
            output.append(f"- **URL**: `{img['url']}`")
            output.append(f"- **サイズ**: {img['size'][0]}×{img['size'][1]}px")
            output.append(f"- **形式**: {img['format']}")
            
            if img.get('datetime'):
                dt = img['datetime']
                output.append(f"- **撮影日時**: {dt.strftime('%Y年%m月%d日 %H時%M分%S秒')}")
            elif img.get('assumed_datetime'):
                dt = img['assumed_datetime']
                output.append(f"- **仮撮影日時**: {dt.strftime('%Y年%m月%d日 %H時%M分%S秒')}")
            
            if img.get('camera_make') and img.get('camera_model'):
                output.append(f"- **カメラ**: {img['camera_make']} {img['camera_model']}")
            
            if img.get('camera_settings'):
                settings = img['camera_settings']
                setting_str = []
                if 'iso' in settings:
                    setting_str.append(f"ISO{settings['iso']}")
                if 'aperture' in settings:
                    setting_str.append(settings['aperture'])
                if 'shutter_speed' in settings:
                    setting_str.append(settings['shutter_speed'])
                if 'focal_length' in settings:
                    setting_str.append(settings['focal_length'])
                
                if setting_str:
                    output.append(f"- **撮影設定**: {' / '.join(setting_str)}")
            
            if img.get('gps_info'):
                gps = img['gps_info']
                output.append(f"- **GPS座標**: {gps['latitude']:.6f}, {gps['longitude']:.6f}")
                output.append(f"- **Google Maps**: [地図で確認](https://www.google.com/maps?q={gps['latitude']},{gps['longitude']})")
            
            # キャプション
            if img.get('caption'):
                output.append(f"- **キャプション**: {img['caption']}")
            
            output.append("")
        
        return "\n".join(output)

    # ========= ここから EXIFなし前提の拡張ユーティリティ =========
    def load_captions(self, captions_path):
        """CSVまたはYAMLからキャプションを読み込み、self.captionsに格納"""
        mapping = {}
        if not captions_path:
            return mapping
        try:
            if captions_path.lower().endswith(('.yml', '.yaml')):
                with open(captions_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                if isinstance(data, dict):
                    # {url or index: caption}
                    for k, v in data.items():
                        mapping[str(k)] = v
                elif isinstance(data, list):
                    # - {url: ..., caption: ...}
                    for item in data:
                        if not isinstance(item, dict):
                            continue
                        if 'url' in item and 'caption' in item:
                            mapping[item['url']] = item['caption']
                        elif 'index' in item and 'caption' in item:
                            mapping[str(item['index'])] = item['caption']
            elif captions_path.lower().endswith('.csv'):
                with open(captions_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # columns: url, caption OR index, caption
                        if row.get('url') and row.get('caption'):
                            mapping[row['url']] = row['caption']
                        elif row.get('index') and row.get('caption'):
                            mapping[str(row['index'])] = row['caption']
            else:
                # プレーンテキスト: 行ごとキャプション、indexベース
                with open(captions_path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f, 1):
                        caption = line.strip()
                        if caption:
                            mapping[str(i)] = caption
        except Exception as e:
            if self.verbose:
                print(f"   ⚠️ キャプション読み込み失敗: {e}")
        self.captions = mapping
        return mapping

    def apply_captions(self, images_in_order):
        """self.captionsをimagesへ付与。URL優先、なければindex(1-based)で照合"""
        for idx, img in enumerate(images_in_order, 1):
            cap = self.captions.get(img.get('url')) or self.captions.get(str(idx))
            if cap:
                img['caption'] = cap

    def parse_sequential_time(self, arg_value):
        """--sequential-time 形式 'start=HH:MM,step=5m' を解析"""
        if not arg_value:
            return None, None
        pairs = [p.strip() for p in arg_value.split(',') if p.strip()]
        start_s = None
        step_s = None
        for p in pairs:
            if '=' in p:
                k, v = p.split('=', 1)
                k = k.strip()
                v = v.strip()
                if k == 'start':
                    start_s = v
                elif k == 'step':
                    step_s = v
            else:
                # 位置引数的に start, step の順とみなす
                if not start_s:
                    start_s = p
                elif not step_s:
                    step_s = p
        start_time = None
        if start_s:
            try:
                hh, mm = start_s.split(':')
                start_time = dtime(hour=int(hh), minute=int(mm))
            except Exception:
                pass
        step_td = None
        if step_s:
            # 例: 5m, 30s, 2h
            try:
                unit = step_s[-1].lower()
                num = int(step_s[:-1])
                if unit == 'm':
                    step_td = timedelta(minutes=num)
                elif unit == 's':
                    step_td = timedelta(seconds=num)
                elif unit == 'h':
                    step_td = timedelta(hours=num)
            except Exception:
                pass
        return start_time, step_td

    def parse_breakpoints(self, arg_value):
        """--breakpoints '3,7,12' → [3,7,12] (1-based index, その位置で区切る)"""
        if not arg_value:
            return []
        try:
            arr = [int(x.strip()) for x in arg_value.split(',') if x.strip()]
            return [x for x in arr if x > 0]
        except Exception:
            return []

    def assign_sequential_datetimes(self, images_in_order, assume_date=None, start_time=None, step=None):
        """日時が無い画像に対して順次に仮日時を割当てる"""
        if assume_date is None:
            base_date = date.today()
        else:
            base_date = assume_date
        if start_time is None:
            start_time = dtime(hour=12, minute=0)
        if step is None:
            step = timedelta(minutes=1)
        base_dt = datetime.combine(base_date, start_time)
        i_missing = 0
        for idx, img in enumerate(images_in_order):
            if not img.get('datetime'):
                assigned = base_dt + step * i_missing
                img['datetime'] = assigned
                img['assumed_datetime'] = assigned
                img['datetime_str'] = assigned.strftime('%Y:%m:%d %H:%M:%S')
                i_missing += 1

    def _suggest_manual_structure(self, images_in_order, n_sections=None, breakpoints=None):
        """手動セクション分割。breakpoints優先。n_sectionsは均等割り。"""
        total = len(images_in_order)
        if total == 0:
            return None
        sections = []
        # 決定ロジック
        if breakpoints:
            sorted_bp = sorted([bp for bp in breakpoints if 0 < bp < total])
            indices = [0] + sorted_bp + [total]
            ranges = [(indices[i], indices[i+1]) for i in range(len(indices)-1)]
        elif n_sections and n_sections > 0:
            q, r = divmod(total, n_sections)
            ranges = []
            start = 0
            for i in range(n_sections):
                count = q + (1 if i < r else 0)
                end = start + count
                ranges.append((start, end))
                start = end
        else:
            # フォールバック: 既存の基本構成に委ねる
            return self._suggest_basic_structure(images_in_order)

        for i, (s, e) in enumerate(ranges, 1):
            imgs = images_in_order[s:e]
            if not imgs:
                continue
            # 時刻表示
            times = [im.get('datetime') for im in imgs if im.get('datetime')]
            if times:
                tlabel = f"{min(times).strftime('%H:%M')}頃"
                duration = self._calculate_group_duration(imgs)
            else:
                tlabel = '時刻不明'
                duration = None
            sections.append({
                'title': f'セクション{i}',
                'time': tlabel,
                'images': [im['url'] for im in imgs],
                'image_count': len(imgs),
                'duration': duration
            })

        structure = {
            'type': 'manual',
            'suggested_date': (images_in_order[0].get('datetime') or datetime.now()).strftime('%Y-%m-%d'),
            'time_range': self._compute_time_range(images_in_order),
            'total_images': total,
            'sections': sections
        }
        return structure

    def _compute_time_range(self, images):
        times = [img.get('datetime') for img in images if img.get('datetime')]
        if len(times) >= 2:
            return f"{min(times).strftime('%H:%M')} - {max(times).strftime('%H:%M')}"
        return '時刻情報なし'
    
    def generate_blog_template(self, structure, topic=""):
        """ブログ記事のテンプレート生成"""
        if not structure:
            return "# 記事構成情報が不足しています"
        
        output = []
        output.append("---")
        output.append(f'title: "{topic} - [タイトルを編集してください]"')
        output.append(f'date: {structure["suggested_date"]}')
        output.append('category: travel  # 適切なカテゴリに変更')
        output.append('tags: [タグ1, タグ2, タグ3]  # 適切なタグを設定')
        output.append(f'description: "{topic}の体験記。{structure["time_range"]}に撮影した{structure["total_images"]}枚の写真とともに紹介します。"')
        output.append("---\n")
        
        output.append(f"<!-- 元のGoogle Photosリンク: [ここに元URLを記載] -->\n")
        
        output.append(f"{topic}に行ってきました。{structure['time_range']}の時間帯で撮影した写真とともに、体験をお伝えします。\n")
        
        for section in structure.get('sections', []):
            output.append(f"## {section['title']}\n")
            output.append(f"{section['time']}の様子です。\n")
            
            for j, img_url in enumerate(section['images'], 1):
                output.append(f"![{section['title']}{j}]({img_url})\n")
            
            output.append("[ここに説明文を追加してください]\n")
        
        output.append("## まとめ\n")
        output.append(f"{topic}は良い体験でした。また機会があれば訪れたいと思います。\n")
        
        return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description='Google Photos画像のコンテンツ分析ツール')
    parser.add_argument('urls', nargs='+', help='分析する画像URL（複数指定可能）')
    parser.add_argument('--topic', default='', help='記事のトピック/テーマ')
    parser.add_argument('--suggest-structure', action='store_true', help='記事構成を提案')
    parser.add_argument('--generate-template', action='store_true', help='ブログテンプレートを生成')
    parser.add_argument('--output', choices=['markdown', 'json'], default='markdown', help='出力形式')
    parser.add_argument('--parallel', action='store_true', default=True, help='並行処理を使用')
    parser.add_argument('--quiet', action='store_true', help='詳細出力を抑制')
    # D) EXIF無し前提のオプション
    parser.add_argument('--assume-date', help='撮影日を仮定 (YYYY-MM-DD)')
    parser.add_argument('--sequential-time', help="入力順に仮時刻を割当て (例: 'start=09:00,step=5m')")
    parser.add_argument('--sections', type=int, help='セクション数で均等分割')
    parser.add_argument('--breakpoints', help="手動区切り位置 (1-based, 例: '3,7,12')")
    parser.add_argument('--captions', help='キャプション定義ファイル (CSV/YAML/テキスト)')
    
    args = parser.parse_args()
    
    if not args.urls:
        print("❌ 画像URLが指定されていません")
        return 1
    
    print("=" * 60)
    print("🔍 画像コンテンツ分析ツール")
    print("=" * 60)
    
    # 分析器を初期化
    analyzer = ImageContentAnalyzer(
        topic_hint=args.topic,
        verbose=not args.quiet
    )
    
    try:
        # キャプションの読み込み（任意）
        if args.captions:
            analyzer.load_captions(args.captions)

        # 画像分析
        results = analyzer.analyze_multiple_images(args.urls, parallel=args.parallel)

        # 入力順へ再配置（キャプションや手動分割・仮時刻のため）
        url_to_item = {r.get('url'): r for r in results}
        images_in_order = [url_to_item.get(u, {'url': u, 'error': 'missing result'}) for u in args.urls]

        # 仮日付/仮時刻割当
        assume_dt = None
        if args.assume_date:
            try:
                assume_dt = datetime.strptime(args.assume_date, '%Y-%m-%d').date()
            except Exception:
                print('⚠️ --assume-date は YYYY-MM-DD 形式で指定してください（例: 2023-08-15）')
        start_time, step_td = analyzer.parse_sequential_time(args.sequential_time) if args.sequential_time else (None, None)
        if assume_dt or start_time or step_td:
            analyzer.assign_sequential_datetimes(images_in_order, assume_date=assume_dt, start_time=start_time, step=step_td)

        # キャプション付与
        analyzer.apply_captions(images_in_order)
        
        # 記事構成提案
        structure = None
        if args.suggest_structure:
            if args.breakpoints or args.sections:
                bps = analyzer.parse_breakpoints(args.breakpoints) if args.breakpoints else []
                structure = analyzer._suggest_manual_structure(images_in_order, n_sections=args.sections, breakpoints=bps)
            else:
                structure = analyzer.suggest_blog_structure(results)
        
        # 出力生成
        if args.output == 'json':
            output_data = {
                'images': images_in_order,
                'structure': structure
            }
            print(json.dumps(output_data, indent=2, ensure_ascii=False, default=str))
        else:
            # Markdownレポート（入力順）
            report = analyzer.generate_markdown_report(images_in_order, structure)
            print("\n" + "=" * 60)
            print("📋 分析結果")
            print("=" * 60)
            print(report)
            
            # ブログテンプレート
            if args.generate_template and structure:
                template = analyzer.generate_blog_template(structure, args.topic)
                print("\n" + "=" * 60)
                print("📝 ブログ記事テンプレート")
                print("=" * 60)
                print(template)
        
        success_count = len([r for r in results if 'error' not in r])
        print(f"\n✅ 処理完了: {success_count}/{len(args.urls)}枚の画像を分析しました")
        
        return 0
        
    except Exception as e:
        print(f"❌ 処理エラー: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによって中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        sys.exit(1)
