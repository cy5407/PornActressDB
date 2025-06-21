# -*- coding: utf-8 -*-
"""
女優分類系統 - 完整版 v5.1 (包含片商分類功能)
作者：Assistant
更新日期：2025-06-15

主要功能：
1. [原有] 掃描與搜尋：建立影片與女優資料庫
2. [原有] 互動式移動：多女優共演時可選擇個人偏好
3. [原有] 標準移動：使用第一位女優進行快速分類
4. [新增] 片商分類：將女優資料夾按片商歸類整理 ⭐
"""
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import threading
import time
import re
import logging
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote
import concurrent.futures
import configparser
import sqlite3
from pathlib import Path

# ===== 設定日誌系統 =====
log_file_path = Path("unified_classifier.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== 修正 sqlite3 DeprecationWarning =====
sqlite3.register_adapter(datetime, lambda val: val.isoformat())
sqlite3.register_converter("timestamp", lambda val: datetime.fromisoformat(val.decode()))

# ===== 設定管理器 =====
class ConfigManager:
    """設定檔管理器"""
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        if self.config_file.exists():
            self.config.read(self.config_file, encoding='utf-8')
        db_path = Path.home() / "Documents" / "ActressClassifier" / "actress_database.db"
        defaults = {
            'database': {'database_path': str(db_path)},
            'paths': {'default_input_dir': '.'},
            'search': {'batch_size': '10', 'thread_count': '5', 'batch_delay': '2.0', 'request_timeout': '20'},
            'classification': {'mode': 'interactive', 'auto_apply_preferences': 'true'}
        }
        needs_saving = not self.config_file.exists()
        for section, options in defaults.items():
            if not self.config.has_section(section):
                self.config.add_section(section); needs_saving = True
            for option, value in options.items():
                if not self.config.has_option(section, option):
                    self.config.set(section, option, value); needs_saving = True
        if needs_saving: self.save_config()

    def save_config(self):
        try:
            with self.config_file.open('w', encoding='utf-8') as f: self.config.write(f)
        except IOError as e: logger.error(f"儲存設定檔失敗: {e}")

    def get(self, section: str, key: str, fallback=None): return self.config.get(section, key, fallback=fallback)
    def getint(self, section: str, key: str, fallback=0): return self.config.getint(section, key, fallback=fallback)
    def getfloat(self, section: str, key: str, fallback=0.0): return self.config.getfloat(section, key, fallback=fallback)
    def getboolean(self, section: str, key: str, fallback=False): return self.config.getboolean(section, key, fallback=fallback)

# ===== 偏好管理器 =====
class PreferenceManager:
    """使用者偏好管理器 - 包含片商分類設定"""
    def __init__(self, preference_file: str = "user_preferences.json"):
        self.preference_file = Path(preference_file)
        self.preferences = self.load_preferences()

    def load_preferences(self) -> Dict:
        """載入使用者偏好設定 - 包含片商分類設定"""
        try:
            if self.preference_file.exists():
                with self.preference_file.open('r', encoding='utf-8') as f:
                    prefs = json.load(f)
                    
                # 確保新設定項目存在（向後相容）
                if 'solo_folder_name' not in prefs:
                    prefs['solo_folder_name'] = '單體企劃女優'
                if 'studio_classification' not in prefs:
                    prefs['studio_classification'] = {
                        'confidence_threshold': 60.0,
                        'auto_create_studio_folders': True,
                        'backup_before_move': True
                    }
                
                return prefs
                
        except Exception as e:
            logger.warning(f"載入偏好設定失敗: {e}")
        
        # 預設設定
        return {
            'favorite_actresses': [],
            'priority_actresses': [],
            'collaboration_preferences': {},
            'classification_strategy': 'interactive',
            'auto_tag_filenames': True,
            'skip_single_actress': False,
            
            # 🆕 片商分類設定
            'solo_folder_name': '單體企劃女優',
            'studio_classification': {
                'confidence_threshold': 60.0,
                'auto_create_studio_folders': True,
                'backup_before_move': True
            }
        }

    def save_preferences(self):
        """儲存偏好設定"""
        try:
            with self.preference_file.open('w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=2)
            logger.info("偏好設定已儲存")
        except Exception as e:
            logger.error(f"儲存偏好設定失敗: {e}")

    def get_preferred_actress(self, actresses: List[str]) -> Optional[str]:
        """根據偏好選擇分類女優"""
        if not actresses:
            return None
        
        # 檢查是否有記住的共演偏好
        actresses_key = "+".join(sorted(actresses))
        if actresses_key in self.preferences['collaboration_preferences']:
            return self.preferences['collaboration_preferences'][actresses_key]
        
        # 優先級1：最愛女優
        for actress in actresses:
            if actress in self.preferences['favorite_actresses']:
                return actress
        
        # 優先級2：優先女優
        for actress in actresses:
            if actress in self.preferences['priority_actresses']:
                return actress
        
        return None

    def save_collaboration_preference(self, actresses: List[str], chosen: str):
        """儲存共演組合的偏好設定"""
        actresses_key = "+".join(sorted(actresses))
        self.preferences['collaboration_preferences'][actresses_key] = chosen
        self.save_preferences()
        logger.info(f"已記住組合偏好: {actresses_key} -> {chosen}")

    # 🆕 片商分類相關方法
    def get_solo_folder_name(self) -> str:
        """取得單體企劃女優資料夾名稱"""
        return self.preferences.get('solo_folder_name', '單體企劃女優')

    def set_solo_folder_name(self, folder_name: str):
        """設定單體企劃女優資料夾名稱"""
        self.preferences['solo_folder_name'] = folder_name
        self.save_preferences()

    def get_confidence_threshold(self) -> float:
        """取得片商信心度門檻"""
        return self.preferences.get('studio_classification', {}).get('confidence_threshold', 60.0)

    def set_confidence_threshold(self, threshold: float):
        """設定片商信心度門檻"""
        if 'studio_classification' not in self.preferences:
            self.preferences['studio_classification'] = {}
        self.preferences['studio_classification']['confidence_threshold'] = threshold
        self.save_preferences()

    def should_backup_before_move(self) -> bool:
        """是否在移動前備份"""
        return self.preferences.get('studio_classification', {}).get('backup_before_move', True)

    def should_auto_create_studio_folders(self) -> bool:
        """是否自動建立片商資料夾"""
        return self.preferences.get('studio_classification', {}).get('auto_create_studio_folders', True)

# ===== SQLite 資料庫管理器 =====
class SQLiteDBManager:
    def __init__(self, db_path: str):
        if not db_path: raise ValueError("資料庫路徑不能為空。請檢查您的 config.ini 檔案。")
        self.db_path = Path(db_path); self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_schema()
    def _get_connection(self): return sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    def _create_schema(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE, original_filename TEXT, file_path TEXT, studio TEXT, search_method TEXT, last_updated TIMESTAMP)')
            cursor.execute('CREATE TABLE IF NOT EXISTS actresses (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)')
            cursor.execute('CREATE TABLE IF NOT EXISTS video_actress_link (video_id INTEGER, actress_id INTEGER, PRIMARY KEY (video_id, actress_id), FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE, FOREIGN KEY (actress_id) REFERENCES actresses(id) ON DELETE CASCADE)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_code ON videos(code)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_actress_name ON actresses(name)')
            conn.commit()
    def add_or_update_video(self, code: str, info: Dict):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM videos WHERE code = ?", (code,))
            video_row = cursor.fetchone()
            if video_row:
                video_id = video_row[0]
                cursor.execute("UPDATE videos SET original_filename=?, file_path=?, studio=?, search_method=?, last_updated=? WHERE id=?", (info.get('original_filename'), str(info.get('file_path')), info.get('studio'), info.get('search_method'), datetime.now(), video_id))
            else:
                cursor.execute("INSERT INTO videos (code, original_filename, file_path, studio, search_method, last_updated) VALUES (?, ?, ?, ?, ?, ?)", (code, info.get('original_filename'), str(info.get('file_path')), info.get('studio'), info.get('search_method'), datetime.now()))
                video_id = cursor.lastrowid
            actress_names = info.get('actresses', [])
            if not actress_names: conn.commit(); return
            actress_ids = []
            for name in actress_names:
                cursor.execute("INSERT OR IGNORE INTO actresses (name) VALUES (?)", (name,))
                cursor.execute("SELECT id FROM actresses WHERE name = ?", (name,))
                actress_id_row = cursor.fetchone()
                if actress_id_row: actress_ids.append(actress_id_row[0])
            cursor.execute("DELETE FROM video_actress_link WHERE video_id = ?", (video_id,))
            if actress_ids:
                link_data = [(video_id, actress_id) for actress_id in actress_ids]
                cursor.executemany("INSERT OR IGNORE INTO video_actress_link (video_id, actress_id) VALUES (?, ?)", link_data)
            conn.commit()
    def get_video_info(self, code: str) -> Optional[Dict]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos WHERE code = ?", (code,))
            video_row = cursor.fetchone()
            if not video_row: return None
            video_id, code_val, *video_data = video_row
            cursor.execute("SELECT a.name FROM actresses a JOIN video_actress_link va ON a.id = va.actress_id WHERE va.video_id = ?", (video_id,))
            actresses = [row[0] for row in cursor.fetchall()]
            return {'code': code_val, 'original_filename': video_data[0], 'file_path': video_data[1], 'studio': video_data[2], 'search_method': video_data[3], 'last_updated': video_data[4], 'actresses': actresses}
    def get_all_videos(self) -> List[Dict]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row; cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos")
            return [dict(row) for row in cursor.fetchall()]

# ===== 核心類別：統一程式碼提取器 =====
class UnifiedCodeExtractor:
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts', '.m2ts']
        self.skip_prefixes = ["FC2", "FC2PPV", "FC2-PPV"]
        # 🆕 增強的番號模式，按優先級排序
        self.code_patterns = [
            (r'([A-Z]{2,6}-\d{3,5})', '標準格式'),
            (r'([A-Z]{2,6}-\d{3,5})[A-Z]*', '標準格式帶後綴'),  # 🆕 處理 STARS-707CH → STARS-707
            (r'([A-Z]{2,6}\d{3,5})', '無橫槓格式'),
            (r'([A-Z]{2,6}[._]\d{3,5})', '特殊分隔符格式'),    # 🆕 處理 STARS_707, STARS.707
            (r'(\d{6}[-_]\d{3})', '數字格式')
        ]
    
    def extract_code(self, filename: str) -> Optional[str]:  # 從檔案名稱提取番號
        base_name = Path(filename).stem  # 取得不含副檔名的檔案名稱
        
        # 檢查跳過前綴
        for prefix in self.skip_prefixes:
            if base_name.upper().startswith(prefix): 
                return None
        
        # 🆕 增強的檔名清理邏輯
        cleaned_name = base_name
        
        # 移除括號內容 [H265], (1080p), {字幕組} 等
        cleaned_name = re.sub(r'\[.*?\]|\(.*?\)|\{.*?\}', '', cleaned_name)
        
        # 🆕 移除常見的品質和編碼標記
        cleaned_name = re.sub(r'[-_]?[CHch]\d*$', '', cleaned_name)  # 移除 -C, CH, -C1 等結尾
        cleaned_name = re.sub(r'\.H265$', '', cleaned_name, flags=re.IGNORECASE)  # 移除 .H265
        cleaned_name = re.sub(r'[-_]?(1080p|720p|4K|HDR|HEVC|AVC|X264|X265)', '', cleaned_name, flags=re.IGNORECASE)
        
        # 移除版本標記 -c, -C 等（但保留在番號中間的）
        cleaned_name = re.sub(r'[-_ ]?c\d*$', '', cleaned_name, flags=re.IGNORECASE)
        
        # 移除網站標記
        cleaned_name = re.sub(r'^(hhd800\.com@|xxx\.com-)', '', cleaned_name, flags=re.IGNORECASE)
        
        # 🆕 移除多餘的空白和連字符
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()
        cleaned_name = re.sub(r'-+', '-', cleaned_name)  # 將多個連字符合併為一個
        
        # 使用增強的模式進行匹配
        for pattern, format_name in self.code_patterns:
            match = re.search(pattern, cleaned_name, re.IGNORECASE)
            if match:
                code = match.group(1).upper()
                
                # 🆕 標準化分隔符（將 . _ 轉換為 -）
                code = re.sub(r'[._]', '-', code)
                
                # 如果沒有分隔符，添加標準的 - 分隔符
                if '-' not in code and re.match(r'^[A-Z]+[0-9]+', code):
                    letters = ''.join(filter(str.isalpha, code))  # 提取字母部分
                    numbers = ''.join(filter(str.isdigit, code))  # 提取數字部分
                    code = f"{letters}-{numbers}"
                
                # 🆕 驗證番號的合理性
                if self._validate_code(code):
                    return code
        
        return None
    
    def _validate_code(self, code: str) -> bool:  # 🆕 驗證番號的合理性
        """驗證番號格式是否合理"""
        if not code or len(code) < 4:
            return False
        
        # 檢查是否包含字母和數字
        has_letter = re.search(r'[A-Z]', code)
        has_number = re.search(r'\d', code)
        if not (has_letter and has_number):
            return False
        
        # 檢查長度是否合理（4-15字符）
        if len(code) > 15:
            return False
        
        # 🆕 檢查是否符合常見番號格式
        valid_patterns = [
            r'^[A-Z]{2,6}-\d{3,5}$',     # STARS-707
            r'^[A-Z]{2,6}\d{3,5}$',      # STARS707
            r'^\d{6}-\d{3}$'             # 240101-001
        ]
        
        for pattern in valid_patterns:
            if re.match(pattern, code):
                return True
        
        return False

# ===== 核心類別：統一檔案掃描器 =====
class UnifiedFileScanner:
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts', '.m2ts']
    def scan_directory(self, path: str, recursive: bool = True) -> List[Path]:
        video_files = []
        scan_path = Path(path)
        if not scan_path.is_dir(): logger.error(f"掃描路徑非資料夾: {path}"); return []
        try:
            patterns = [f'*{ext}' for ext in self.supported_formats]
            if recursive:
                for p in patterns: video_files.extend(scan_path.rglob(p))
            else:
                for p in patterns: video_files.extend(scan_path.glob(p))
            return list(set(video_files))
        except Exception as e:
            logger.error(f"掃描目錄失敗: {e}"); return []

# ===== 核心類別：片商識別器 =====
class StudioIdentifier:
    def __init__(self, rules_file: str = "studios.json"):
        self.rules_file = Path(rules_file)
        self.studio_patterns = self._load_rules()
    def _load_rules(self) -> Dict:
        if not self.rules_file.exists():
            logger.warning(f"片商規則檔案 {self.rules_file} 不存在，將建立預設檔案。")
            default_rules = {'S1': ['SSIS', 'SSNI', 'STARS'], 'MOODYZ': ['MIRD', 'MIDD', 'MIDV'], 'PREMIUM': ['IPX', 'IPZ', 'IPZZ'], 'WANZ': ['WANZ'], 'FALENO': ['FSDSS']}
            try:
                with self.rules_file.open('w', encoding='utf-8') as f: json.dump(default_rules, f, ensure_ascii=False, indent=4)
                return default_rules
            except IOError as e: logger.error(f"無法建立預設片商規則檔案: {e}"); return {}
        try:
            with self.rules_file.open('r', encoding='utf-8') as f: return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"讀取片商規則檔案失敗: {e}, 將使用空規則。"); return {}
    def identify_studio(self, code: str) -> str:
        if not code: return 'UNKNOWN'
        prefix_match = re.match(r'([A-Z]+)', code.upper())
        if prefix_match:
            prefix = prefix_match.group(1)
            for studio, prefixes in self.studio_patterns.items():
                if prefix in prefixes: return studio
        return 'UNKNOWN'

# ===== 網路搜尋器 =====
class WebSearcher:
    """增強版搜尋器 - 支援搜尋結果頁面"""
    def __init__(self, config: ConfigManager):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
        self.search_cache = {}
        self.batch_size = config.getint('search', 'batch_size', fallback=10)
        self.thread_count = config.getint('search', 'thread_count', fallback=5)
        self.batch_delay = config.getfloat('search', 'batch_delay', fallback=2.0)
        self.timeout = config.getint('search', 'request_timeout', fallback=20)

    def search_info(self, code: str, stop_event: threading.Event) -> Optional[Dict]:
        if stop_event.is_set(): return None
        if code in self.search_cache: return self.search_cache[code]
        
        search_url = f"https://av-wiki.net/?s={quote(code)}&post_type=product"
        try:
            with httpx.Client(headers=self.headers, timeout=self.timeout) as client:
                response = client.get(search_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                
                actress_elements = soup.find_all(class_="actress-name")
                actresses = [actress.text.strip() for actress in actress_elements if actress.text.strip()]
                
                if not actresses:
                    page_text = soup.get_text()
                    lines = [line.strip() for line in page_text.split('\n') if line.strip()]
                    for i, line in enumerate(lines):
                        if code in line:
                            for j in range(max(0, i-3), min(len(lines), i+1)):
                                potential_name = lines[j].strip()
                                if potential_name and self._is_actress_name(potential_name):
                                    if potential_name not in actresses: actresses.append(potential_name)
                
                if actresses:
                    result = {'source': 'AV-WIKI (增強版)', 'actresses': actresses}
                    self.search_cache[code] = result
                    logger.info(f"番號 {code} 透過 {result['source']} 找到: {', '.join(result['actresses'])}")
                    return result

        except httpx.RequestError as e:
            logger.error(f"AV-WIKI 搜尋 {code} 時發生網路錯誤: {e}")
        except Exception as e:
            logger.error(f"AV-WIKI 解析 {code} 時發生未知錯誤: {e}", exc_info=True)
            
        logger.warning(f"番號 {code} 未在 AV-WIKI 中找到女優資訊。")
        return None

    def _is_actress_name(self, text: str) -> bool:
        """判斷文字是否可能是女優名稱"""
        if not text or len(text) < 2 or len(text) > 20: return False
        exclude_keywords = ['SOD', 'STARS', 'FANZA', 'MGS', 'MIDV', 'SSIS', 'IPX', 'IPZZ', '続きを読む', '検索', '件', '特典', '映像', '付き', 'star', 'SOKMIL', 'Menu', 'セール', '限定', '最大']
        if any(keyword in text for keyword in exclude_keywords): return False
        import re
        if re.match(r'^\d+$', text) or len(re.findall(r'\d', text)) > len(text) // 2: return False
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text): return True
        return False

    def batch_search(self, items: List, task_func, stop_event: threading.Event, progress_callback=None) -> Dict:
        results = {}
        total_batches = (len(items) + self.batch_size - 1) // self.batch_size
        for i in range(0, len(items), self.batch_size):
            if stop_event.is_set(): logger.info("任務被使用者中止。"); break
            batch = items[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            if progress_callback: progress_callback(f"處理批次 {batch_num}/{total_batches}...\n")
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_count) as executor:
                future_to_item = {executor.submit(task_func, item, stop_event): item for item in batch}
                for future in concurrent.futures.as_completed(future_to_item):
                    if stop_event.is_set(): break
                    item = future_to_item[future]
                    try:
                        result = future.result()
                        results[item] = result
                        if progress_callback:
                            if result and result.get('actresses'): progress_callback(f"✅ {item}: 找到資料\n")
                            else: progress_callback(f"❌ {item}: 未找到結果\n")
                    except Exception as e:
                        logger.error(f"批次處理 {item} 時發生錯誤: {e}")
                        if progress_callback: progress_callback(f"💥 {item}: 處理失敗 - {e}\n")
            if i + self.batch_size < len(items) and total_batches > 1: time.sleep(self.batch_delay)
        return results

# ===== 🆕 片商分類核心功能 =====
class StudioClassificationCore:
    """片商分類核心類別"""
    
    def __init__(self, db_manager, code_extractor, studio_identifier, preference_manager):
        self.db_manager = db_manager
        self.code_extractor = code_extractor
        self.studio_identifier = studio_identifier
        self.preference_manager = preference_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.supported_formats = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.ts', '.m2ts']

    def classify_actresses_by_studio(self, root_path: str, progress_callback=None) -> Dict:
        """按片商分類女優資料夾的主要功能"""
        try:
            root_folder = Path(root_path)
            
            if progress_callback:
                progress_callback(f"🏢 開始片商分類：{root_path}\n")
                progress_callback("=" * 60 + "\n")
            
            # 第一步：掃描所有女優資料夾
            actress_folders = self._scan_actress_folders(root_folder, progress_callback)
            if not actress_folders:
                if progress_callback:
                    progress_callback("🤷 未找到任何女優資料夾\n")
                return {'status': 'success', 'message': '未找到女優資料夾'}
            
            if progress_callback:
                progress_callback(f"📁 發現 {len(actress_folders)} 個女優資料夾\n\n")
            
            # 第二步：重新掃描並更新統計資料
            updated_stats = self._update_actress_statistics(actress_folders, progress_callback)
            
            # 第三步：按片商分類移動
            move_stats = self._move_actresses_by_studio(
                root_folder, updated_stats, progress_callback
            )
            
            return {
                'status': 'success',
                'total_actresses': len(actress_folders),
                'updated_count': len(updated_stats),
                'move_stats': move_stats
            }
            
        except Exception as e:
            self.logger.error(f"片商分類過程中發生錯誤: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    def _scan_actress_folders(self, root_folder: Path, progress_callback=None) -> List[Path]:
        """遞迴掃描所有女優資料夾"""
        actress_folders = []
        
        if progress_callback:
            progress_callback("🔍 正在遞迴掃描女優資料夾...\n")
        
        try:
            for item in root_folder.rglob('*'):
                if item.is_dir() and self._is_actress_folder(item):
                    actress_folders.append(item)
                    
            return actress_folders
            
        except Exception as e:
            self.logger.error(f"掃描女優資料夾失敗: {e}")
            return []

    def _is_actress_folder(self, folder_path: Path) -> bool:
        """判斷是否為女優資料夾"""
        folder_name = folder_path.name
        
        # 排除明顯的片商資料夾名稱
        studio_folders = {
            'S1', 'MOODYZ', 'PREMIUM', 'WANZ', 'FALENO', 'ATTACKERS', 
            'E-BODY', 'KAWAII', 'FITCH', 'MADONNA', 'PRESTIGE', 'SOD',
            '單體企劃女優', 'SOLO_ACTRESS', 'INDEPENDENT'
        }
        
        if folder_name.upper() in studio_folders:
            return False
        
        # 檢查資料夾內是否有影片檔案
        try:
            for file_path in folder_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                    return True
        except PermissionError:
            return False
        
        return False

    def _update_actress_statistics(self, actress_folders: List[Path], progress_callback=None) -> Dict[str, Dict]:
        """重新掃描女優資料夾並更新片商統計"""
        updated_stats = {}
        
        if progress_callback:
            progress_callback("📊 正在重新統計女優片商分佈...\n")
        
        for i, actress_folder in enumerate(actress_folders, 1):
            actress_name = actress_folder.name
            
            try:
                # 掃描該女優資料夾中的影片檔案
                video_files = []
                for file_path in actress_folder.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                        video_files.append(file_path)
                
                if not video_files:
                    continue
                
                # 統計片商分佈
                studio_stats = self._calculate_studio_distribution(video_files)
                
                if studio_stats:
                    # 計算主要片商和信心度
                    main_studio, confidence = self._determine_main_studio(studio_stats)
                    
                    updated_stats[actress_name] = {
                        'folder_path': actress_folder,
                        'studio_stats': studio_stats,
                        'main_studio': main_studio,
                        'confidence': confidence,
                        'total_videos': len(video_files)
                    }
                    
                    if progress_callback and i % 10 == 0:
                        progress_callback(f"   處理進度: {i}/{len(actress_folders)}\n")
                
            except Exception as e:
                self.logger.error(f"處理女優 {actress_name} 時發生錯誤: {e}")
                continue
        
        if progress_callback:
            progress_callback(f"✅ 完成統計更新，處理了 {len(updated_stats)} 位女優\n\n")
        
        return updated_stats

    def _calculate_studio_distribution(self, video_files: List[Path]) -> Dict[str, int]:
        """計算影片檔案的片商分佈"""
        studio_stats = defaultdict(int)
        
        for video_file in video_files:
            # 提取番號
            code = self.code_extractor.extract_code(video_file.name)
            if code:
                # 識別片商
                studio = self.studio_identifier.identify_studio(code)
                if studio and studio != 'UNKNOWN':
                    studio_stats[studio] += 1
        
        return dict(studio_stats)

    def _determine_main_studio(self, studio_stats: Dict[str, int]) -> Tuple[str, float]:
        """決定主要片商和信心度"""
        if not studio_stats:
            return 'UNKNOWN', 0.0
        
        total_videos = sum(studio_stats.values())
        if total_videos == 0:
            return 'UNKNOWN', 0.0
        
        # 找出影片數最多的片商
        main_studio = max(studio_stats.items(), key=lambda x: x[1])
        studio_name, video_count = main_studio
        
        # 計算信心度
        confidence = round((video_count / total_videos) * 100, 1)
        
        return studio_name, confidence

    def _move_actresses_by_studio(self, root_folder: Path, actress_stats: Dict[str, Dict], 
                                 progress_callback=None) -> Dict:
        """根據片商統計移動女優資料夾"""
        move_stats = {
            'moved': 0,           # 成功移動到片商資料夾
            'exists': 0,          # 目標已存在
            'solo_artist': 0,     # 移動到單體企劃女優
            'failed': 0           # 移動失敗
        }
        
        # 取得單體企劃女優資料夾名稱
        solo_folder_name = self.preference_manager.get_solo_folder_name()
        confidence_threshold = self.preference_manager.get_confidence_threshold()
        
        if progress_callback:
            progress_callback("🚚 開始按片商移動女優資料夾...\n")
        
        for actress_name, stats in actress_stats.items():
            try:
                source_folder = stats['folder_path']
                main_studio = stats['main_studio']
                confidence = stats['confidence']
                
                # 決定目標片商資料夾
                if confidence >= confidence_threshold and main_studio != 'UNKNOWN':
                    target_studio_folder = root_folder / main_studio
                    category = 'studio'
                else:
                    target_studio_folder = root_folder / solo_folder_name
                    category = 'solo'
                
                # 建立目標片商資料夾
                target_studio_folder.mkdir(exist_ok=True)
                
                # 目標女優資料夾路徑
                target_actress_folder = target_studio_folder / actress_name
                
                # 檢查是否已存在
                if target_actress_folder.exists():
                    move_stats['exists'] += 1
                    if progress_callback:
                        progress_callback(f"⚠️ 已存在: {target_studio_folder.name}/{actress_name}\n")
                    continue
                
                # 執行移動
                shutil.move(str(source_folder), str(target_actress_folder))
                
                if category == 'solo':
                    move_stats['solo_artist'] += 1
                    if progress_callback:
                        progress_callback(f"🎭 {actress_name} → {solo_folder_name}/ (信心度: {confidence}%)\n")
                else:
                    move_stats['moved'] += 1
                    if progress_callback:
                        progress_callback(f"✅ {actress_name} → {main_studio}/ (信心度: {confidence}%)\n")
                
            except Exception as e:
                move_stats['failed'] += 1
                self.logger.error(f"移動女優 {actress_name} 失敗: {e}")
                if progress_callback:
                    progress_callback(f"❌ {actress_name}: 移動失敗 - {str(e)}\n")
        
        return move_stats

    def get_classification_summary(self, total_actresses: int, move_stats: Dict) -> str:
        """生成片商分類結果摘要"""
        solo_folder_name = self.preference_manager.get_solo_folder_name()
        
        return (f"📊 片商分類完成！\n\n"
               f"  📁 掃描女優總數: {total_actresses}\n"
               f"  ✅ 移動到片商資料夾: {move_stats['moved']}\n"
               f"  🎭 移動到{solo_folder_name}: {move_stats['solo_artist']}\n"
               f"  ⚠️ 目標已存在: {move_stats['exists']}\n"
               f"  ❌ 移動失敗: {move_stats['failed']}\n")

# ===== 互動式分類器 =====
class InteractiveClassifier:
    """互動式分類器 - 處理多女優共演的偏好選擇"""
    def __init__(self, preference_manager: PreferenceManager, gui_parent=None):
        self.preference_manager = preference_manager
        self.gui_parent = gui_parent
        self.pending_decisions = {}

    def get_classification_choice(self, code: str, actresses: List[str]) -> Tuple[str, bool]:
        """取得分類選擇 - 返回 (選擇的女優, 是否記住偏好)"""
        
        if len(actresses) == 1:
            return actresses[0], False
        
        # 檢查已有偏好
        preferred = self.preference_manager.get_preferred_actress(actresses)
        if preferred:
            return preferred, False
        
        # 需要使用者選擇
        if self.gui_parent:
            return self._show_gui_choice_dialog(code, actresses)
        else:
            return self._show_console_choice(code, actresses)

    def _show_gui_choice_dialog(self, code: str, actresses: List[str]) -> Tuple[str, bool]:
        """顯示 GUI 選擇對話框"""
        
        result = {'choice': None, 'remember': False}
        
        dialog = tk.Toplevel(self.gui_parent)
        dialog.title(f"選擇分類偏好 - {code}")
        dialog.geometry("450x400")
        dialog.resizable(False, False)
        
        # 置中顯示
        dialog.transient(self.gui_parent)
        dialog.grab_set()
        
        # 標題
        title_frame = ttk.Frame(dialog)
        title_frame.pack(pady=15)
        ttk.Label(title_frame, text=f"🎬 影片 {code} 包含多位女優", font=("Arial", 14, "bold")).pack()
        ttk.Label(title_frame, text="請選擇要分類到哪位女優的資料夾：", font=("Arial", 10)).pack(pady=5)
        
        # 選擇區域
        choice_frame = ttk.LabelFrame(dialog, text="女優選擇", padding=10)
        choice_frame.pack(pady=10, padx=20, fill="x")
        
        selected_actress = tk.StringVar()
        
        # 女優選項
        for i, actress in enumerate(actresses):
            rb = ttk.Radiobutton(choice_frame, text=f"{i+1}. {actress}", 
                               variable=selected_actress, value=actress)
            rb.pack(anchor="w", pady=2)
            if i == 0:
                rb.invoke()
        
        # 特殊選項
        ttk.Separator(choice_frame, orient='horizontal').pack(fill='x', pady=5)
        ttk.Radiobutton(choice_frame, text=f"{len(actresses)+1}. 放到「多人共演」資料夾", 
                       variable=selected_actress, value="多人共演").pack(anchor="w", pady=2)
        ttk.Radiobutton(choice_frame, text=f"{len(actresses)+2}. 跳過此檔案", 
                       variable=selected_actress, value="SKIP").pack(anchor="w", pady=2)
        
        # 記住偏好選項
        remember_frame = ttk.Frame(dialog)
        remember_frame.pack(pady=10)
        remember_var = tk.BooleanVar()
        ttk.Checkbutton(remember_frame, text="🧠 記住此組合的偏好設定 (下次自動分類)", 
                       variable=remember_var).pack()
        
        # 按鈕區域
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        
        def confirm_choice():
            choice = selected_actress.get()
            if choice:
                result['choice'] = choice
                result['remember'] = remember_var.get()
                dialog.destroy()
        
        def skip_all():
            result['choice'] = "SKIP_ALL"
            result['remember'] = False
            dialog.destroy()
        
        ttk.Button(button_frame, text="✅ 確認選擇", command=confirm_choice).pack(side="left", padx=5)
        ttk.Button(button_frame, text="⏭️ 全部跳過", command=skip_all).pack(side="left", padx=5)
        ttk.Button(button_frame, text="❌ 取消", command=dialog.destroy).pack(side="left", padx=5)
        
        # 等待使用者選擇
        dialog.wait_window()
        
        choice = result.get('choice')
        if not choice:
            return "SKIP", False
        
        remember = result.get('remember', False)
        return choice, remember

    def _show_console_choice(self, code: str, actresses: List[str]) -> Tuple[str, bool]:
        """顯示控制台選擇介面"""
        
        print(f"\n🎬 影片 {code} 包含以下女優：")
        for i, actress in enumerate(actresses, 1):
            print(f"  {i}. {actress}")
        
        print(f"  {len(actresses) + 1}. 放到「多人共演」資料夾")
        print(f"  {len(actresses) + 2}. 跳過此檔案")
        print(f"  0. 跳過所有後續選擇")
        
        while True:
            try:
                choice = input("請選擇 (輸入數字): ").strip()
                
                if choice == "0":
                    return "SKIP_ALL", False
                
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(actresses):
                    chosen = actresses[choice_num - 1]
                    
                    remember_input = input(f"是否記住 {', '.join(actresses)} 的分類偏好到 {chosen}？(y/n): ").strip().lower()
                    remember = remember_input in ['y', 'yes', '是']
                    
                    return chosen, remember
                    
                elif choice_num == len(actresses) + 1:
                    return "多人共演", False
                    
                elif choice_num == len(actresses) + 2:
                    return "SKIP", False
                    
                else:
                    print("❌ 無效選擇，請重新輸入")
                    
            except ValueError:
                print("❌ 請輸入有效的數字")
            except KeyboardInterrupt:
                print("\n⏹️ 使用者中斷操作")
                return "SKIP_ALL", False

# ===== 核心業務邏輯類別 =====
class UnifiedClassifierCore:
    """核心業務邏輯類別 - 包含片商分類功能"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.db_manager = SQLiteDBManager(config.get('database', 'database_path'))
        self.code_extractor = UnifiedCodeExtractor()
        self.file_scanner = UnifiedFileScanner()
        self.studio_identifier = StudioIdentifier()
        self.web_searcher = WebSearcher(config)
        self.preference_manager = PreferenceManager()
        self.interactive_classifier = None
        
        # 🆕 新增片商分類功能
        self.studio_classifier = StudioClassificationCore(
            self.db_manager,
            self.code_extractor,
            self.studio_identifier,
            self.preference_manager
        )
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def set_interactive_classifier(self, interactive_classifier: InteractiveClassifier):
        """設定互動式分類器"""
        self.interactive_classifier = interactive_classifier

    # 🆕 新增片商分類相關方法
    def classify_actresses_by_studio(self, folder_path: str, progress_callback=None):
        """按片商分類女優資料夾"""
        return self.studio_classifier.classify_actresses_by_studio(folder_path, progress_callback)

    def get_actress_studio_distribution(self, actress_name: str) -> Dict:
        """取得指定女優的片商分佈統計"""
        # 這裡可以根據需要實作具體的查詢邏輯
        pass

    def preview_studio_classification(self, folder_path: str) -> Dict:
        """預覽片商分類結果（不實際移動檔案）"""
        try:
            root_folder = Path(folder_path)
            
            # 掃描女優資料夾
            actress_folders = self.studio_classifier._scan_actress_folders(root_folder)
            
            # 更新統計（但不移動檔案）
            updated_stats = self.studio_classifier._update_actress_statistics(actress_folders)
            
            # 分析分類結果
            preview_result = {
                'total_actresses': len(actress_folders),
                'studio_distribution': defaultdict(list),
                'solo_artists': [],
                'unknown_actresses': []
            }
            
            solo_folder_name = self.preference_manager.get_solo_folder_name()
            confidence_threshold = self.preference_manager.get_confidence_threshold()
            
            for actress_name, stats in updated_stats.items():
                confidence = stats['confidence']
                main_studio = stats['main_studio']
                
                if confidence >= confidence_threshold and main_studio != 'UNKNOWN':
                    preview_result['studio_distribution'][main_studio].append(actress_name)
                else:
                    preview_result['solo_artists'].append(actress_name)
            
            return {
                'status': 'success',
                'preview': preview_result,
                'solo_folder_name': solo_folder_name,
                'confidence_threshold': confidence_threshold
            }
            
        except Exception as e:
            self.logger.error(f"預覽片商分類失敗: {e}")
            return {'status': 'error', 'message': str(e)}

    def process_and_search(self, folder_path: str, stop_event: threading.Event, progress_callback=None):
        try:
            if progress_callback: progress_callback("🔍 開始掃描資料夾...\n")
            video_files = self.file_scanner.scan_directory(folder_path)
            if not video_files:
                if progress_callback: progress_callback("🤷 未發現任何影片檔案。\n")
                return {'status': 'success', 'message': '未發現影片檔案'}
            if progress_callback: progress_callback(f"📁 發現 {len(video_files)} 個影片檔案。\n")
            
            codes_in_db = {v['code'] for v in self.db_manager.get_all_videos()}
            new_code_file_map = {}
            for file_path in video_files:
                code = self.code_extractor.extract_code(file_path.name)
                if code and code not in codes_in_db:
                    if code not in new_code_file_map: new_code_file_map[code] = []
                    new_code_file_map[code].append(file_path)
            if progress_callback:
                progress_callback(f"✅ 資料庫中已存在 {len(codes_in_db)} 個影片的番號記錄。\n")
                progress_callback(f"🎯 需要搜尋 {len(new_code_file_map)} 個新番號。\n\n")
            if not new_code_file_map:
                if progress_callback: progress_callback("🎉 所有影片都已在資料庫中！\n")
                return {'status': 'success', 'message': '所有番號都已存在於資料庫中'}
            search_results = self.web_searcher.batch_search(list(new_code_file_map.keys()), self.web_searcher.search_info, stop_event, progress_callback)
            success_count = 0
            for code, result in search_results.items():
                if result and result.get('actresses'):
                    success_count += 1
                    for file_path in new_code_file_map[code]:
                        info = {'actresses': result['actresses'], 'original_filename': file_path.name, 'file_path': str(file_path), 'studio': self.studio_identifier.identify_studio(code), 'search_method': result.get('source', 'AV-WIKI')}
                        self.db_manager.add_or_update_video(code, info)
            return {'status': 'success', 'total_files': len(video_files), 'new_codes': len(new_code_file_map), 'success': success_count}
        except Exception as e:
            self.logger.error(f"搜尋過程中發生錯誤: {e}", exc_info=True); return {'status': 'error', 'message': str(e)}
    
    def interactive_move_files(self, folder_path_str: str, progress_callback=None):
        """互動式檔案移動 - 支援多女優共演的偏好選擇"""
        try:
            folder_path = Path(folder_path_str)
            if progress_callback: progress_callback(f"🔍 開始掃描 {folder_path} 並準備互動式移動...\n")
            video_files = self.file_scanner.scan_directory(folder_path_str, recursive=False)
            if not video_files:
                if progress_callback: progress_callback("🤷 目標資料夾中沒有影片檔案可移動。\n")
                return {'status': 'success', 'message': '目標資料夾中沒有影片檔案可移動。'}
            
            move_stats = {'success': 0, 'exists': 0, 'no_data': 0, 'failed': 0, 'skipped': 0}
            skip_all = False
            
            # 分析需要互動選擇的檔案
            collaboration_files = []
            single_files = []
            
            for file_path in video_files:
                code = self.code_extractor.extract_code(file_path.name)
                if not code: continue
                info = self.db_manager.get_video_info(code)
                if not info or not info.get('actresses'):
                    continue
                
                actresses = info['actresses']
                if len(actresses) > 1:
                    collaboration_files.append((file_path, code, actresses, info))
                else:
                    single_files.append((file_path, code, actresses, info))
            
            if progress_callback:
                progress_callback(f"📊 分析結果: {len(single_files)} 個單人作品, {len(collaboration_files)} 個多人共演作品\n")
                if collaboration_files:
                    progress_callback("🤝 開始處理多人共演作品的分類選擇...\n\n")
            
            # 處理所有檔案
            all_files = single_files + collaboration_files
            
            for i, (file_path, code, actresses, info) in enumerate(all_files, 1):
                if skip_all:
                    move_stats['skipped'] += 1
                    continue
                
                try:
                    # 決定分類目標
                    if len(actresses) == 1:
                        target_actress = actresses[0]
                        remember = False
                    else:
                        if not self.interactive_classifier:
                            target_actress = actresses[0]
                            remember = False
                        else:
                            choice, remember = self.interactive_classifier.get_classification_choice(code, actresses)
                            
                            if choice == "SKIP_ALL":
                                skip_all = True
                                move_stats['skipped'] += 1
                                if progress_callback: progress_callback(f"⏭️ 使用者選擇跳過所有後續檔案\n")
                                continue
                            elif choice == "SKIP":
                                move_stats['skipped'] += 1
                                if progress_callback: progress_callback(f"⏭️ [{i}/{len(all_files)}] 跳過: {file_path.name}\n")
                                continue
                            
                            target_actress = choice
                    
                    # 記住偏好設定
                    if remember and len(actresses) > 1:
                        self.preference_manager.save_collaboration_preference(actresses, target_actress)
                        if progress_callback: progress_callback(f"🧠 已記住組合偏好: {', '.join(actresses)} → {target_actress}\n")
                    
                    # 建立目標資料夾
                    target_folder = folder_path / target_actress
                    target_folder.mkdir(exist_ok=True)
                    
                    # 決定檔案名稱
                    if len(actresses) > 1 and self.preference_manager.preferences.get('auto_tag_filenames', True):
                        actresses_tag = f" ({', '.join(actresses)})"
                        base_name = file_path.stem
                        new_filename = f"{base_name}{actresses_tag}{file_path.suffix}"
                    else:
                        new_filename = file_path.name
                    
                    target_path = target_folder / new_filename
                    
                    # 檢查檔案是否已存在
                    if target_path.exists():
                        move_stats['exists'] += 1
                        if progress_callback: progress_callback(f"⚠️ [{i}/{len(all_files)}] 已存在: {target_actress}/{new_filename}\n")
                        continue
                    
                    # 執行移動
                    shutil.move(str(file_path), str(target_path))
                    move_stats['success'] += 1
                    
                    if len(actresses) > 1:
                        actresses_display = f" (共演: {', '.join(actresses)})"
                    else:
                        actresses_display = ""
                    
                    if progress_callback: progress_callback(f"✅ [{i}/{len(all_files)}] {file_path.name} → {target_actress}/{new_filename}{actresses_display}\n")
                    
                except Exception as e:
                    move_stats['failed'] += 1
                    logger.error(f"移動檔案 {file_path.name} 失敗: {e}")
                    if progress_callback: progress_callback(f"❌ [{i}/{len(all_files)}] {file_path.name}: 移動失敗 - {str(e)}\n")
            
            return {'status': 'success', 'total_files': len(video_files), 'stats': move_stats}
            
        except Exception as e:
            self.logger.error(f"互動式檔案移動過程中發生錯誤: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    def move_files(self, folder_path_str: str, progress_callback=None):
        """標準檔案移動 - 使用第一位女優分類"""
        try:
            folder_path = Path(folder_path_str)
            if progress_callback: progress_callback(f"🔍 開始掃描 {folder_path} 並準備移動...\n")
            video_files = self.file_scanner.scan_directory(folder_path_str, recursive=False)
            if not video_files:
                if progress_callback: progress_callback("🤷 目標資料夾中沒有影片檔案可移動。\n")
                return {'status': 'success', 'message': '目標資料夾中沒有影片檔案可移動。'}
            move_stats = {'success': 0, 'exists': 0, 'no_data': 0, 'failed': 0}
            for i, file_path in enumerate(video_files, 1):
                code = self.code_extractor.extract_code(file_path.name)
                if not code: continue 
                info = self.db_manager.get_video_info(code)
                if not info or not info.get('actresses'):
                    move_stats['no_data'] += 1
                    if progress_callback: progress_callback(f"❓ [{i}/{len(video_files)}] {file_path.name}: 資料庫中無資料\n")
                    continue
                main_actress = info['actresses'][0]; target_folder = folder_path / main_actress; target_folder.mkdir(exist_ok=True)
                target_path = target_folder / file_path.name
                if target_path.exists():
                    move_stats['exists'] += 1
                    if progress_callback: progress_callback(f"⚠️ [{i}/{len(video_files)}] {file_path.name}: 檔案已存在於目標資料夾\n")
                    continue
                try:
                    shutil.move(str(file_path), str(target_path)); move_stats['success'] += 1
                    if progress_callback: progress_callback(f"✅ [{i}/{len(video_files)}] {file_path.name} → {main_actress}/\n")
                except Exception as e:
                    move_stats['failed'] += 1; logger.error(f"移動檔案 {file_path.name} 失敗: {e}")
                    if progress_callback: progress_callback(f"❌ [{i}/{len(video_files)}] {file_path.name}: 移動失敗\n")
            return {'status': 'success', 'total_files': len(video_files), 'stats': move_stats}
        except Exception as e:
            self.logger.error(f"檔案移動過程中發生錯誤: {e}", exc_info=True); return {'status': 'error', 'message': str(e)}

# ===== 🆕 偏好設定對話框 =====
class PreferenceDialog:
    """偏好設定對話框 - 包含片商分類設定"""
    def __init__(self, parent, preference_manager: PreferenceManager):
        self.parent = parent
        self.preference_manager = preference_manager
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()

    def setup_dialog(self):
        self.dialog.title("⚙️ 偏好設定")
        self.dialog.geometry("650x550")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # 標題
        ttk.Label(main_frame, text="⚙️ 個人化偏好設定", font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # 筆記本容器
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 15))
        
        # 女優偏好頁面
        self._setup_actress_preferences_tab(notebook)
        
        # 分類選項頁面
        self._setup_classification_options_tab(notebook)
        
        # 🆕 片商分類頁面
        self._setup_studio_classification_tab(notebook)
        
        # 共演記錄頁面
        self._setup_collaboration_tab(notebook)
        
        # 按鈕區域
        self._setup_buttons(main_frame)
        
        # 載入當前設定
        self.load_current_preferences()

    def _setup_actress_preferences_tab(self, notebook):
        """設定女優偏好頁面"""
        actress_frame = ttk.Frame(notebook, padding="10")
        notebook.add(actress_frame, text="👩 女優偏好")
        
        # 最愛女優設定
        ttk.Label(actress_frame, text="⭐ 最愛女優（最高優先級）", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 5))
        fav_frame = ttk.Frame(actress_frame)
        fav_frame.pack(fill="x", pady=(0, 15))
        
        self.favorite_listbox = tk.Listbox(fav_frame, height=4)
        self.favorite_listbox.pack(side="left", fill="both", expand=True)
        
        fav_btn_frame = ttk.Frame(fav_frame)
        fav_btn_frame.pack(side="right", fill="y", padx=(10, 0))
        ttk.Button(fav_btn_frame, text="新增", command=lambda: self.add_actress('favorite')).pack(fill="x", pady=1)
        ttk.Button(fav_btn_frame, text="移除", command=lambda: self.remove_actress('favorite')).pack(fill="x", pady=1)
        
        # 優先女優設定
        ttk.Label(actress_frame, text="🔸 優先女優（次要優先級）", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 5))
        priority_frame = ttk.Frame(actress_frame)
        priority_frame.pack(fill="x", pady=(0, 15))
        
        self.priority_listbox = tk.Listbox(priority_frame, height=4)
        self.priority_listbox.pack(side="left", fill="both", expand=True)
        
        priority_btn_frame = ttk.Frame(priority_frame)
        priority_btn_frame.pack(side="right", fill="y", padx=(10, 0))
        ttk.Button(priority_btn_frame, text="新增", command=lambda: self.add_actress('priority')).pack(fill="x", pady=1)
        ttk.Button(priority_btn_frame, text="移除", command=lambda: self.remove_actress('priority')).pack(fill="x", pady=1)

    def _setup_classification_options_tab(self, notebook):
        """設定分類選項頁面"""
        options_frame = ttk.Frame(notebook, padding="10")
        notebook.add(options_frame, text="🔧 分類選項")
        
        # 檔名標籤選項
        ttk.Label(options_frame, text="📝 檔案命名選項", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        self.auto_tag_var = tk.BooleanVar(value=self.preference_manager.preferences.get('auto_tag_filenames', True))
        ttk.Checkbutton(options_frame, text="自動標籤化檔名（在多人共演檔案名稱中標記所有女優）", 
                       variable=self.auto_tag_var).pack(anchor="w", pady=2)
        
        # 跳過選項
        ttk.Label(options_frame, text="⏭️ 跳過選項", font=("Arial", 11, "bold")).pack(anchor="w", pady=(20, 10))
        
        self.skip_single_var = tk.BooleanVar(value=self.preference_manager.preferences.get('skip_single_actress', False))
        ttk.Checkbutton(options_frame, text="跳過單人作品的確認（單人作品直接分類，不詢問）", 
                       variable=self.skip_single_var).pack(anchor="w", pady=2)

    def _setup_studio_classification_tab(self, notebook):
        """設定片商分類頁面"""
        studio_frame = ttk.Frame(notebook, padding="10")
        notebook.add(studio_frame, text="🏢 片商分類")
        
        # 資料夾命名設定
        ttk.Label(studio_frame, text="📁 資料夾命名設定", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        # 單體企劃女優資料夾名稱
        solo_name_frame = ttk.Frame(studio_frame)
        solo_name_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(solo_name_frame, text="單體企劃女優資料夾名稱：").pack(side="left")
        self.solo_folder_var = tk.StringVar(value=self.preference_manager.get_solo_folder_name())
        solo_entry = ttk.Entry(solo_name_frame, textvariable=self.solo_folder_var, width=20)
        solo_entry.pack(side="left", padx=(10, 0))
        
        # 說明文字
        solo_desc = ttk.Label(studio_frame, 
                             text="💡 說明：信心度不足60%或跨多片商的女優將歸類到此資料夾", 
                             font=("Arial", 9), 
                             foreground="gray")
        solo_desc.pack(anchor="w", pady=(0, 20))
        
        # 分類規則設定
        ttk.Label(studio_frame, text="📊 分類規則設定", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        # 信心度門檻設定
        threshold_frame = ttk.Frame(studio_frame)
        threshold_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(threshold_frame, text="片商信心度門檻：").pack(side="left")
        self.confidence_var = tk.DoubleVar(value=self.preference_manager.get_confidence_threshold())
        confidence_spinbox = ttk.Spinbox(threshold_frame, 
                                       from_=50.0, to=100.0, increment=5.0,
                                       textvariable=self.confidence_var, 
                                       width=10, format="%.1f")
        confidence_spinbox.pack(side="left", padx=(10, 5))
        ttk.Label(threshold_frame, text="%").pack(side="left")
        
        # 門檻說明
        threshold_desc = ttk.Label(studio_frame,
                                  text="💡 說明：女優在某片商的影片占比超過此門檻時，歸類到該片商資料夾",
                                  font=("Arial", 9),
                                  foreground="gray")
        threshold_desc.pack(anchor="w", pady=(0, 20))
        
        # 其他選項
        ttk.Label(studio_frame, text="🔧 其他選項", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        # 自動建立片商資料夾
        self.auto_create_var = tk.BooleanVar(value=self.preference_manager.should_auto_create_studio_folders())
        ttk.Checkbutton(studio_frame, 
                       text="自動建立片商資料夾（如果不存在）", 
                       variable=self.auto_create_var).pack(anchor="w", pady=2)
        
        # 移動前備份
        self.backup_before_var = tk.BooleanVar(value=self.preference_manager.should_backup_before_move())
        ttk.Checkbutton(studio_frame, 
                       text="移動前建立備份記錄", 
                       variable=self.backup_before_var).pack(anchor="w", pady=2)

    def _setup_collaboration_tab(self, notebook):
        """設定共演記錄頁面"""
        collaboration_frame = ttk.Frame(notebook, padding="10")
        notebook.add(collaboration_frame, text="🤝 共演記錄")
        
        ttk.Label(collaboration_frame, text="🤝 已記住的共演組合偏好", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        # 共演記錄列表
        collab_list_frame = ttk.Frame(collaboration_frame)
        collab_list_frame.pack(fill="both", expand=True)
        
        # 創建 Treeview 來顯示共演記錄
        columns = ('組合', '選擇的女優')
        self.collab_tree = ttk.Treeview(collab_list_frame, columns=columns, show='headings', height=10)
        self.collab_tree.heading('組合', text='共演組合')
        self.collab_tree.heading('選擇的女優', text='分類到')
        self.collab_tree.column('組合', width=300)
        self.collab_tree.column('選擇的女優', width=150)
        
        collab_scrollbar = ttk.Scrollbar(collab_list_frame, orient="vertical", command=self.collab_tree.yview)
        self.collab_tree.configure(yscrollcommand=collab_scrollbar.set)
        
        self.collab_tree.pack(side="left", fill="both", expand=True)
        collab_scrollbar.pack(side="right", fill="y")
        
        # 共演記錄按鈕
        collab_btn_frame = ttk.Frame(collaboration_frame)
        collab_btn_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(collab_btn_frame, text="🗑️ 清除選中記錄", command=self.remove_collaboration).pack(side="left", padx=(0, 5))
        ttk.Button(collab_btn_frame, text="🗑️ 清除全部記錄", command=self.clear_all_collaborations).pack(side="left")

    def _setup_buttons(self, main_frame):
        """設定按鈕區域"""
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="💾 儲存設定", command=self.save_preferences).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="❌ 取消", command=self.dialog.destroy).pack(side="right")
        ttk.Button(button_frame, text="🔄 重設為預設值", command=self.reset_preferences).pack(side="left")

    def load_current_preferences(self):
        """載入當前偏好設定"""
        # 載入最愛女優
        self.favorite_listbox.delete(0, tk.END)
        for actress in self.preference_manager.preferences.get('favorite_actresses', []):
            self.favorite_listbox.insert(tk.END, actress)
        
        # 載入優先女優
        self.priority_listbox.delete(0, tk.END)
        for actress in self.preference_manager.preferences.get('priority_actresses', []):
            self.priority_listbox.insert(tk.END, actress)
        
        # 載入共演記錄
        self.collab_tree.delete(*self.collab_tree.get_children())
        for combination, chosen in self.preference_manager.preferences.get('collaboration_preferences', {}).items():
            actresses = combination.replace('+', ' & ')
            self.collab_tree.insert('', 'end', values=(actresses, chosen))
        
        # 🆕 載入片商分類設定
        if hasattr(self, 'solo_folder_var'):
            self.solo_folder_var.set(self.preference_manager.get_solo_folder_name())
        
        if hasattr(self, 'confidence_var'):
            self.confidence_var.set(self.preference_manager.get_confidence_threshold())
        
        if hasattr(self, 'auto_create_var'):
            self.auto_create_var.set(self.preference_manager.should_auto_create_studio_folders())
        
        if hasattr(self, 'backup_before_var'):
            self.backup_before_var.set(self.preference_manager.should_backup_before_move())

    def add_actress(self, category: str):
        """新增女優到指定分類"""
        import tkinter.simpledialog as simpledialog
        actress_name = simpledialog.askstring("新增女優", f"請輸入要新增到{'最愛' if category == 'favorite' else '優先'}女優的名稱：")
        if actress_name and actress_name.strip():
            actress_name = actress_name.strip()
            listbox = self.favorite_listbox if category == 'favorite' else self.priority_listbox
            
            # 檢查是否已存在
            current_items = [listbox.get(i) for i in range(listbox.size())]
            if actress_name not in current_items:
                listbox.insert(tk.END, actress_name)
            else:
                messagebox.showwarning("重複項目", f"女優 '{actress_name}' 已在清單中！")

    def remove_actress(self, category: str):
        """從指定分類移除女優"""
        listbox = self.favorite_listbox if category == 'favorite' else self.priority_listbox
        selection = listbox.curselection()
        if selection:
            listbox.delete(selection[0])
        else:
            messagebox.showinfo("未選擇項目", "請先選擇要移除的女優！")

    def remove_collaboration(self):
        """移除選中的共演記錄"""
        selection = self.collab_tree.selection()
        if selection:
            for item in selection:
                self.collab_tree.delete(item)
        else:
            messagebox.showinfo("未選擇項目", "請先選擇要移除的共演記錄！")

    def clear_all_collaborations(self):
        """清除所有共演記錄"""
        if messagebox.askyesno("確認清除", "確定要清除所有共演記錄嗎？此操作無法復原。"):
            self.collab_tree.delete(*self.collab_tree.get_children())

    def reset_preferences(self):
        """重設為預設值"""
        if messagebox.askyesno("確認重設", "確定要重設所有偏好設定為預設值嗎？此操作無法復原。"):
            # 清空所有列表
            self.favorite_listbox.delete(0, tk.END)
            self.priority_listbox.delete(0, tk.END)
            self.collab_tree.delete(*self.collab_tree.get_children())
            
            # 重設選項
            self.auto_tag_var.set(True)
            self.skip_single_var.set(False)
            
            # 🆕 重設片商分類設定
            if hasattr(self, 'solo_folder_var'):
                self.solo_folder_var.set('單體企劃女優')
            if hasattr(self, 'confidence_var'):
                self.confidence_var.set(60.0)
            if hasattr(self, 'auto_create_var'):
                self.auto_create_var.set(True)
            if hasattr(self, 'backup_before_var'):
                self.backup_before_var.set(True)

    def save_preferences(self):
        """儲存偏好設定 - 包含片商分類設定"""
        try:
            # 收集最愛女優
            favorite_actresses = [self.favorite_listbox.get(i) for i in range(self.favorite_listbox.size())]
            
            # 收集優先女優
            priority_actresses = [self.priority_listbox.get(i) for i in range(self.priority_listbox.size())]
            
            # 收集共演記錄
            collaboration_preferences = {}
            for item in self.collab_tree.get_children():
                values = self.collab_tree.item(item)['values']
                if len(values) >= 2:
                    combination_display = values[0]
                    chosen = values[1]
                    combination_key = combination_display.replace(' & ', '+')
                    collaboration_preferences[combination_key] = chosen
            
            # 🆕 收集片商分類設定
            solo_folder_name = self.solo_folder_var.get().strip()
            if not solo_folder_name:
                solo_folder_name = '單體企劃女優'
            
            confidence_threshold = self.confidence_var.get()
            auto_create_folders = self.auto_create_var.get()
            backup_before_move = self.backup_before_var.get()
            
            # 更新偏好設定
            self.preference_manager.preferences.update({
                'favorite_actresses': favorite_actresses,
                'priority_actresses': priority_actresses,
                'collaboration_preferences': collaboration_preferences,
                'auto_tag_filenames': self.auto_tag_var.get(),
                'skip_single_actress': self.skip_single_var.get(),
                
                # 🆕 新增片商分類設定
                'solo_folder_name': solo_folder_name,
                'studio_classification': {
                    'confidence_threshold': confidence_threshold,
                    'auto_create_studio_folders': auto_create_folders,
                    'backup_before_move': backup_before_move
                }
            })
            
            # 儲存到檔案
            self.preference_manager.save_preferences()
            
            messagebox.showinfo("設定已儲存", "偏好設定已成功儲存！")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("儲存失敗", f"儲存偏好設定時發生錯誤：\n{str(e)}")

# ===== 主GUI介面類別 =====
class UnifiedActressClassifierGUI:
    """整合版圖形介面 - 包含片商分類功能"""
    def __init__(self, root):
        self.root = root
        self.root.title("女優分類系統 - v5.1 (包含片商分類功能)")
        self.root.geometry("900x750")
        self.is_running = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.config_manager = ConfigManager()
        self.core = UnifiedClassifierCore(self.config_manager)
        
        # 設定互動式分類器
        self.interactive_classifier = InteractiveClassifier(self.core.preference_manager, self.root)
        self.core.set_interactive_classifier(self.interactive_classifier)
        
        self.selected_path = tk.StringVar(value=self.config_manager.get('paths', 'default_input_dir', '.'))
        self.stop_event = threading.Event()
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # 標題區域
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(title_frame, text="🎬 女優分類系統 v5.1", font=("Arial", 16, "bold")).pack()
        ttk.Label(title_frame, text="互動式分類版 - 支援多女優共演的個人偏好選擇 + 片商分類功能", font=("Arial", 10)).pack()
        
        # 路徑選擇區域
        path_frame = ttk.LabelFrame(main_frame, text="📁 目標資料夾", padding="10")
        path_frame.pack(fill="x", pady=5)
        path_entry = ttk.Entry(path_frame, textvariable=self.selected_path, font=("Arial", 10))
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.browse_btn = ttk.Button(path_frame, text="瀏覽...", command=self.browse_folder)
        self.browse_btn.pack(side="left")
        
        # 功能按鈕區域
        button_frame = ttk.LabelFrame(main_frame, text="🔧 功能選擇", padding="10")
        button_frame.pack(fill="x", pady=5)
        
        # 第一排按鈕
        row1_frame = ttk.Frame(button_frame)
        row1_frame.pack(fill="x", pady=(0, 5))
        row1_frame.columnconfigure((0, 1), weight=1)
        
        self.search_btn = ttk.Button(row1_frame, text="🔍 掃描與搜尋", command=self.start_search)
        self.search_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew", ipady=5)
        
        self.settings_btn = ttk.Button(row1_frame, text="⚙️ 偏好設定", command=self.show_preferences)
        self.settings_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew", ipady=5)
        
        # 第二排按鈕 - 🆕 包含片商分類按鈕
        row2_frame = ttk.Frame(button_frame)
        row2_frame.pack(fill="x", pady=(0, 5))
        row2_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        self.interactive_move_btn = ttk.Button(row2_frame, text="🤝 互動式移動", command=self.start_interactive_move)
        self.interactive_move_btn.grid(row=0, column=0, padx=(0, 2), sticky="ew", ipady=5)
        
        self.standard_move_btn = ttk.Button(row2_frame, text="📁 標準移動", command=self.start_standard_move)
        self.standard_move_btn.grid(row=0, column=1, padx=2, sticky="ew", ipady=5)
        
        # 🆕 新增片商分類按鈕
        self.studio_classify_btn = ttk.Button(row2_frame, text="🏢 片商分類", command=self.start_studio_classification)
        self.studio_classify_btn.grid(row=0, column=2, padx=2, sticky="ew", ipady=5)
        
        self.stop_btn = ttk.Button(row2_frame, text="🛑 中止任務", command=self.stop_task, state="disabled")
        self.stop_btn.grid(row=0, column=3, padx=(2, 0), sticky="ew", ipady=5)
        
        # 結果顯示區域
        result_frame = ttk.LabelFrame(main_frame, text="📋 執行結果", padding="10")
        result_frame.pack(fill="both", expand=True, pady=5)
        
        self.result_text = tk.Text(result_frame, wrap="word", font=("Consolas", 9), height=25, relief="flat", padx=5, pady=5)
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        self.result_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 狀態列
        self.status_var = tk.StringVar(value="就緒")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=2)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.show_welcome_message()

    def show_welcome_message(self):
        """顯示歡迎訊息"""
        welcome_text = """🎬 女優分類系統 v5.1 - 互動式分類版
========================================

✨ 功能總覽：
• 🔍 掃描與搜尋：建立影片與女優資料庫
• 🤝 互動式移動：多女優共演時可選擇個人偏好
• 📁 標準移動：使用第一位女優進行快速分類
• 🏢 片商分類：將女優資料夾按片商歸類整理 ⭐ 新功能

🎯 建議使用流程：
1. 選擇包含影片檔案的資料夾
2. 點擊「掃描與搜尋」建立影片資料庫
3. 使用「互動式移動」進行個人化分類
4. 使用「片商分類」整理女優資料夾到片商結構

🏢 片商分類功能特色：
• 自動分析女優的片商分佈統計
• 信心度≥60%歸類到主片商資料夾
• 信心度<60%歸類到「單體企劃女優」資料夾
• 可在偏好設定中自訂分類規則

準備好開始了嗎？請選擇資料夾並開始您的分類之旅！
"""
        self.result_text.insert(tk.END, welcome_text)

    def show_preferences(self):
        """顯示偏好設定對話框"""
        PreferenceDialog(self.root, self.core.preference_manager)

    def on_closing(self):
        self.is_running = False
        self.stop_event.set()
        self.root.destroy()

    def browse_folder(self):
        initial_dir = self.selected_path.get()
        if not Path(initial_dir).is_dir(): initial_dir = str(Path.home())
        folder_path = filedialog.askdirectory(title="選擇目標資料夾", initialdir=initial_dir)
        if folder_path:
            self.selected_path.set(folder_path)
            self.config_manager.config.set('paths', 'default_input_dir', folder_path)
            self.config_manager.save_config()

    def clear_results(self):
        if self.is_running and self.result_text.winfo_exists():
            self.result_text.delete(1.0, tk.END)

    def update_progress(self, message: str):
        if self.is_running and self.root.winfo_exists():
            self.root.after(0, self._insert_text, message)

    def _insert_text(self, message: str):
        if self.is_running and self.result_text.winfo_exists():
            self.result_text.insert(tk.END, message)
            self.result_text.see(tk.END)

    def _toggle_buttons(self, is_task_running: bool):
        if not self.is_running: return
        search_state = 'disabled' if is_task_running else 'normal'
        stop_state = 'normal' if is_task_running else 'disabled'
        
        # 🆕 更新按鈕列表，包含片商分類按鈕
        buttons = [
            self.browse_btn, self.search_btn, self.interactive_move_btn, 
            self.standard_move_btn, self.studio_classify_btn, self.settings_btn
        ]
        
        for btn in buttons:
            if btn.winfo_exists(): btn.config(state=search_state)
        if self.stop_btn.winfo_exists(): self.stop_btn.config(state=stop_state)

    def _run_task(self, task_func, *args):
        if self.is_running: self.root.after(0, self._toggle_buttons, True)
        try: task_func(*args)
        finally:
            if self.is_running: self.root.after(0, self._toggle_buttons, False)

    def stop_task(self):
        self.update_progress("\n⚠️ 正在中止任務，請稍候...\n")
        self.stop_event.set()

    def start_search(self):
        path = self.selected_path.get()
        if not Path(path).is_dir(): messagebox.showerror("錯誤", "請選擇一個有效的資料夾！"); return
        self.clear_results(); self.update_progress(f"目標資料夾: {path}\n{'='*60}\n")
        self.stop_event.clear()
        threading.Thread(target=self._run_task, args=(self._search_worker, path), daemon=True).start()

    def _search_worker(self, path):
        self.status_var.set("執行中：掃描與搜尋...")
        result = self.core.process_and_search(path, self.stop_event, self.update_progress)
        if self.is_running:
            if self.stop_event.is_set():
                self.update_progress(f"\n🛑 任務已由使用者中止。\n"); self.status_var.set("任務已中止")
            elif result['status'] == 'success':
                self.update_progress(f"\n{'='*60}\n🎉 搜尋任務完成！\n"); self.status_var.set("就緒")
            else:
                self.update_progress(f"\n💥 錯誤: {result['message']}\n"); self.status_var.set(f"錯誤: {result.get('message', '未知錯誤')}")

    def start_interactive_move(self):
        path = self.selected_path.get()
        if not Path(path).is_dir(): messagebox.showerror("錯誤", "請選擇一個有效的資料夾！"); return
        
        confirm_text = f"""確定要進行互動式分類嗎？

📁 目標資料夾: {path}

🤝 互動式分類特色：
• 遇到多女優共演時會彈出選擇對話框
• 可選擇您偏好的女優進行分類
• 自動記住您的選擇偏好
• 檔名會標記所有參演女優資訊

⚠️ 注意：只會移動此資料夾根目錄下的檔案"""
        
        if not messagebox.askyesno("確認互動式移動", confirm_text): return
        self.clear_results(); self.update_progress(f"🤝 互動式分類模式\n目標資料夾: {path}\n{'='*60}\n")
        threading.Thread(target=self._run_task, args=(self._interactive_move_worker, path), daemon=True).start()

    def _interactive_move_worker(self, path):
        self.status_var.set("執行中：互動式檔案移動...")
        result = self.core.interactive_move_files(path, self.update_progress)
        if self.is_running:
            if result.get('status') == 'success' and 'stats' in result:
                stats = result['stats']
                summary = (f"\n{'='*60}\n🤝 互動式分類完成！\n\n"
                          f"  ✅ 成功移動: {stats['success']}\n"
                          f"  ⚠️ 已存在: {stats['exists']}\n"
                          f"  ❓ 無資料: {stats['no_data']}\n"
                          f"  ⏭️ 跳過: {stats['skipped']}\n"
                          f"  ❌ 失敗: {stats['failed']}\n")
                self.update_progress(summary); self.status_var.set("就緒")
            else:
                self.update_progress(f"\n💥 錯誤: {result.get('message', '未知錯誤')}\n")
                self.status_var.set(f"錯誤: {result.get('message', '未知錯誤')}")

    def start_standard_move(self):
        path = self.selected_path.get()
        if not Path(path).is_dir(): messagebox.showerror("錯誤", "請選擇一個有效的資料夾！"); return
        if not messagebox.askyesno("確認標準移動", f"確定要將 '{path}' 資料夾中的影片，根據資料庫分類到對應的女優子資料夾嗎？\n\n（使用第一位女優進行分類，只會移動此資料夾根目錄下的檔案）"): return
        self.clear_results(); self.update_progress(f"📁 標準分類模式\n目標資料夾: {path}\n{'='*60}\n")
        threading.Thread(target=self._run_task, args=(self._standard_move_worker, path), daemon=True).start()

    def _standard_move_worker(self, path):
        self.status_var.set("執行中：標準檔案移動...")
        result = self.core.move_files(path, self.update_progress)
        if self.is_running:
            if result.get('status') == 'success' and 'stats' in result:
                stats = result['stats']
                summary = (f"\n{'='*60}\n📁 標準分類完成！\n\n"
                          f"  ✅ 成功: {stats['success']}\n"
                          f"  ⚠️ 已存在: {stats['exists']}\n"
                          f"  ❓ 無資料: {stats['no_data']}\n"
                          f"  ❌ 失敗: {stats['failed']}\n")
                self.update_progress(summary); self.status_var.set("就緒")
            else:
                self.update_progress(f"\n💥 錯誤: {result.get('message', '未知錯誤')}\n")
                self.status_var.set(f"錯誤: {result.get('message', '未知錯誤')}")

    # 🆕 新增片商分類功能
    def start_studio_classification(self):
        """開始片商分類功能"""
        path = self.selected_path.get()
        if not Path(path).is_dir():
            messagebox.showerror("錯誤", "請選擇一個有效的資料夾！")
            return
        
        # 確認對話框
        solo_folder_name = self.core.preference_manager.get_solo_folder_name()
        confidence_threshold = self.core.preference_manager.get_confidence_threshold()
        
        confirm_text = f"""確定要進行片商分類嗎？

📁 目標資料夾: {path}

🏢 片商分類規則：
• 信心度 ≥ {confidence_threshold}%：歸類到主片商資料夾
• 信心度 < {confidence_threshold}%：歸類到「{solo_folder_name}」資料夾

⚠️ 注意事項：
• 會遞迴掃描所有子資料夾中的女優資料夾
• 會重新統計女優的片商分佈（確保資料準確）
• 移動操作無法復原，建議先備份重要資料

是否繼續執行？"""
        
        if not messagebox.askyesno("確認片商分類", confirm_text):
            return
        
        self.clear_results()
        self.update_progress(f"🏢 片商分類模式\n目標資料夾: {path}\n{'='*60}\n")
        
        # 在背景執行片商分類
        threading.Thread(target=self._run_task, args=(self._studio_classification_worker, path), daemon=True).start()

    def _studio_classification_worker(self, path):
        """片商分類工作執行緒"""
        self.status_var.set("執行中：片商分類...")
        
        try:
            result = self.core.classify_actresses_by_studio(path, self.update_progress)
            
            if self.is_running:
                if result.get('status') == 'success':
                    # 顯示結果摘要
                    move_stats = result.get('move_stats', {})
                    total_actresses = result.get('total_actresses', 0)
                    
                    summary = self.core.studio_classifier.get_classification_summary(total_actresses, move_stats)
                    self.update_progress(f"\n{'='*60}\n{summary}")
                    
                    self.status_var.set("就緒")
                else:
                    error_msg = result.get('message', '未知錯誤')
                    self.update_progress(f"\n💥 錯誤: {error_msg}\n")
                    self.status_var.set(f"錯誤: {error_msg}")
                    
        except Exception as e:
            if self.is_running:
                self.update_progress(f"\n💥 片商分類發生未預期錯誤: {str(e)}\n")
                self.status_var.set(f"錯誤: {str(e)}")

# ===== 主程式 =====
def main():
    """主程式入口"""
    try:
        logger.info("🚀 啟動女優分類系統 - 完整版 v5.1...")
        root = tk.Tk()
        
        # 嘗試使用 ttkbootstrap 美化主題
        try:
            import ttkbootstrap as tb
            style = tb.Style(theme='litera')
            root = style.master
        except ImportError:
            pass
        
        app = UnifiedActressClassifierGUI(root)
        root.mainloop()
        logger.info("✅ 程式正常結束。")
        
    except Exception as e:
        logger.error(f"❌ 程式啟動失敗: {e}", exc_info=True)
        messagebox.showerror("致命錯誤", f"程式發生無法處理的錯誤，請查看日誌檔案 'unified_classifier.log'。\n\n錯誤: {e}")

if __name__ == "__main__":
    main()