# -*- coding: utf-8 -*-
"""
網路搜尋器模組
"""
import re
import time
import logging
import threading
import concurrent.futures
from typing import Dict, List, Optional
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote

from models.config import ConfigManager
from .safe_searcher import SafeSearcher, RequestConfig
from .safe_javdb_searcher import SafeJAVDBSearcher
from .japanese_site_enhancer import create_japanese_soup, is_japanese_site

logger = logging.getLogger(__name__)


class WebSearcher:
    """增強版搜尋器 - 支援搜尋結果頁面"""
    
    def __init__(self, config: ConfigManager):
        # 初始化一般搜尋器配置（用於 JAVDB）
        safe_config = RequestConfig(
            min_interval=config.getfloat('search', 'min_interval', fallback=1.0),
            max_interval=config.getfloat('search', 'max_interval', fallback=3.0),
            enable_cache=config.getboolean('search', 'enable_cache', fallback=True),
            cache_duration=config.getint('search', 'cache_duration', fallback=86400),
            max_retries=config.getint('search', 'max_retries', fallback=3),
            backoff_factor=config.getfloat('search', 'backoff_factor', fallback=2.0),
            rotate_headers=config.getboolean('search', 'rotate_headers', fallback=True)
        )
        
        # 初始化日文網站專用配置（較快速，因為比較不會擋爬蟲）
        japanese_config = RequestConfig(
            min_interval=config.getfloat('search', 'japanese_min_interval', fallback=0.5),
            max_interval=config.getfloat('search', 'japanese_max_interval', fallback=1.5),
            enable_cache=config.getboolean('search', 'enable_cache', fallback=True),
            cache_duration=config.getint('search', 'cache_duration', fallback=86400),
            max_retries=config.getint('search', 'max_retries', fallback=3),
            backoff_factor=config.getfloat('search', 'backoff_factor', fallback=1.5),
            rotate_headers=config.getboolean('search', 'rotate_headers', fallback=True)
        )
        
        # 初始化搜尋器
        self.safe_searcher = SafeSearcher(safe_config)  # 用於一般搜尋
        self.japanese_searcher = SafeSearcher(japanese_config)  # 專用於日文網站
        
        # 初始化 JAVDB 安全搜尋器
        cache_dir = config.get('search', 'cache_dir', fallback=None)
        self.javdb_searcher = SafeJAVDBSearcher(cache_dir)
        
        # 保留原有配置以向下相容
        self.headers = self.safe_searcher.get_headers()
        self.search_cache = {}
        self.batch_size = config.getint('search', 'batch_size', fallback=10)
        self.thread_count = config.getint('search', 'thread_count', fallback=5)
        self.batch_delay = config.getfloat('search', 'batch_delay', fallback=2.0)
        self.timeout = config.getint('search', 'request_timeout', fallback=20)
        
        logger.info("🛡️ 已啟用安全搜尋器功能")
        logger.info("🇯🇵 已啟用日文網站快速搜尋功能")
        logger.info("🎬 已啟用 JAVDB 安全搜尋功能")

    def search_info(self, code: str, stop_event: threading.Event) -> Optional[Dict]:
        """多層級搜尋策略 - AV-WIKI -> chiba-f.net -> JAVDB"""
        if stop_event.is_set(): 
            return None
        if code in self.search_cache: 
            return self.search_cache[code]
        
        try:
            # 第一層：原有的 AV-WIKI 搜尋
            logger.debug(f"🔍 第一層搜尋 - AV-WIKI: {code}")
            result = self._search_av_wiki(code, stop_event)
            if result and result.get('actresses'):
                self.search_cache[code] = result
                return result
            
            # 第二層：chiba-f.net 搜尋  
            if not stop_event.is_set():
                logger.debug(f"🔍 第二層搜尋 - chiba-f.net: {code}")
                result = self._search_chiba_f_net(code, stop_event)
                if result and result.get('actresses'):
                    self.search_cache[code] = result
                    return result
            
            # 第三層：使用安全的 JAVDB 搜尋
            if not stop_event.is_set():
                logger.debug(f"🔍 第三層搜尋 - JAVDB: {code}")
                javdb_result = self.javdb_searcher.search_javdb(code)
                if javdb_result and javdb_result.get('actresses'):
                    # 轉換為統一格式
                    result = {
                        'source': javdb_result['source'],
                        'actresses': javdb_result['actresses'],
                        'studio': javdb_result.get('studio'),
                        'studio_code': javdb_result.get('studio_code'),
                        'release_date': javdb_result.get('release_date'),
                        'title': javdb_result.get('title'),
                        'duration': javdb_result.get('duration'),
                        'director': javdb_result.get('director'),
                        'series': javdb_result.get('series'),
                        'rating': javdb_result.get('rating'),
                        'categories': javdb_result.get('categories', [])
                    }
                    self.search_cache[code] = result
                    
                    # 豐富的日誌輸出
                    log_parts = [f"番號 {code} 透過 {result['source']} 找到:"]
                    log_parts.append(f"女優: {', '.join(result['actresses'])}")
                    log_parts.append(f"片商: {result.get('studio', '未知')}")
                    
                    if result.get('rating'):
                        log_parts.append(f"評分: {result['rating']}")
                    if result.get('categories'):
                        categories_str = ', '.join(result['categories'][:3])  # 只顯示前3個類別
                        if len(result['categories']) > 3:
                            categories_str += f" 等{len(result['categories'])}個類別"
                        log_parts.append(f"類別: {categories_str}")
                    
                    logger.info(" | ".join(log_parts))
                    return result
            
            logger.warning(f"番號 {code} 未在所有搜尋源中找到女優資訊。")
            return None
            
        except Exception as e:
            logger.error(f"搜尋番號 {code} 時發生錯誤: {e}", exc_info=True)
            return None

    def _search_av_wiki(self, code: str, stop_event: threading.Event) -> Optional[Dict]:
        """AV-WIKI 搜尋方法 - 使用日文編碼增強"""
        if stop_event.is_set():
            return None
            
        search_url = f"https://av-wiki.net/?s={quote(code)}&post_type=product"
        
        # 使用日文網站專用搜尋器進行請求
        def make_request(url, **kwargs):
            with httpx.Client(timeout=self.timeout, **kwargs) as client:
                response = client.get(url)
                response.raise_for_status()
                # 使用日文網站編碼增強器
                return create_japanese_soup(response, url)
        
        try:
            # 使用日文網站專用搜尋器（較短延遲）
            soup = self.japanese_searcher.safe_request(make_request, search_url)
            
            if soup is None:
                logger.warning(f"無法獲取 {code} 的 AV-WIKI 搜尋頁面")
                return None
                
            actress_elements = soup.find_all(class_="actress-name")
            actresses = [actress.text.strip() for actress in actress_elements if actress.text.strip()]
            
            # 搜尋片商資訊
            studio_info = self._extract_studio_info(soup, code)
            
            if not actresses:
                page_text = soup.get_text()
                lines = [line.strip() for line in page_text.split('\n') if line.strip()]
                for i, line in enumerate(lines):
                    if code in line:
                        for j in range(max(0, i-3), min(len(lines), i+1)):
                            potential_name = lines[j].strip()
                            if potential_name and self._is_actress_name(potential_name):
                                if potential_name not in actresses: 
                                    actresses.append(potential_name)                
            if actresses:
                result = {
                    'source': 'AV-WIKI (安全增強版)', 
                    'actresses': actresses,
                    'studio': studio_info.get('studio'),
                    'studio_code': studio_info.get('studio_code'),
                    'release_date': studio_info.get('release_date')
                }
                logger.info(f"番號 {code} 透過 {result['source']} 找到: {', '.join(result['actresses'])}, 片商: {result.get('studio', '未知')}")
                return result

        except Exception as e:
            logger.error(f"AV-WIKI 搜尋 {code} 時發生錯誤: {e}", exc_info=True)
        
        return None

    def _is_actress_name(self, text: str) -> bool:
        """判斷文字是否可能是女優名稱"""
        if not text or len(text) < 2 or len(text) > 20: 
            return False
        exclude_keywords = [
            'SOD', 'STARS', 'FANZA', 'MGS', 'MIDV', 'SSIS', 'IPX', 'IPZZ', 
            '続きを読む', '検索', '件', '特典', '映像', '付き', 'star', 'SOKMIL', 
            'Menu', 'セール', '限定', '最大'
        ]
        if any(keyword in text for keyword in exclude_keywords): 
            return False
        if re.match(r'^\d+$', text) or len(re.findall(r'\d', text)) > len(text) // 2: 
            return False
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text): 
            return True
        return False

    def batch_search(self, items: List, task_func, stop_event: threading.Event, progress_callback=None) -> Dict:
        results = {}
        total_batches = (len(items) + self.batch_size - 1) // self.batch_size
        for i in range(0, len(items), self.batch_size):
            if stop_event.is_set(): 
                logger.info("任務被使用者中止。")
                break
            batch = items[i:i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            if progress_callback: 
                progress_callback(f"處理批次 {batch_num}/{total_batches}...\n")
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_count) as executor:
                future_to_item = {executor.submit(task_func, item, stop_event): item for item in batch}
                for future in concurrent.futures.as_completed(future_to_item):
                    if stop_event.is_set(): 
                        break
                    item = future_to_item[future]
                    try:
                        result = future.result()
                        results[item] = result
                        if progress_callback:
                            if result and result.get('actresses'): 
                                progress_callback(f"✅ {item}: 找到資料\n")
                            else: 
                                progress_callback(f"❌ {item}: 未找到結果\n")
                    except Exception as e:
                        logger.error(f"批次處理 {item} 時發生錯誤: {e}")
                        if progress_callback: 
                            progress_callback(f"💥 {item}: 處理失敗 - {e}\n")
            if i + self.batch_size < len(items) and total_batches > 1:                time.sleep(self.batch_delay)
        return results
    
    def _search_chiba_f_net(self, code: str, stop_event: threading.Event) -> Optional[Dict]:
        """使用 chiba-f.net 搜尋女優資訊 - 使用日文編碼增強"""
        if stop_event.is_set():
            return None
            
        search_url = f"https://chiba-f.net/search/?keyword={quote(code)}"
        
        # 使用日文網站專用搜尋器進行請求
        def make_request(url, **kwargs):
            with httpx.Client(timeout=self.timeout, **kwargs) as client:
                response = client.get(url)
                response.raise_for_status()
                # 使用日文網站編碼增強器
                return create_japanese_soup(response, url)
        
        try:
            # 使用日文網站專用搜尋器（較短延遲）
            soup = self.japanese_searcher.safe_request(make_request, search_url)
            
            if soup is None:
                logger.warning(f"無法獲取 {code} 的 chiba-f.net 搜尋頁面")
                return None
                
            # 查找產品區塊
            product_divs = soup.find_all('div', class_='product-div')
                
            for product_div in product_divs:
                # 檢查番號是否匹配
                pno_element = product_div.find('div', class_='pno')
                if pno_element and code.upper() in pno_element.text.upper():
                    return self._extract_chiba_product_info(product_div, code)
            
            # 如果沒有找到完全匹配，嘗試模糊匹配
            for product_div in product_divs:
                product_text = product_div.get_text()
                if code.upper() in product_text.upper():
                    return self._extract_chiba_product_info(product_div, code)
                        
        except Exception as e:
            logger.error(f"chiba-f.net 搜尋 {code} 時發生錯誤: {e}", exc_info=True)
            
        logger.debug(f"番號 {code} 未在 chiba-f.net 中找到女優資訊。")
        return None
    
    def _extract_chiba_product_info(self, product_div, code: str) -> Dict:
        """從 chiba-f.net 產品區塊提取資訊"""
        result = {
            'source': 'chiba-f.net (安全增強版)',
            'actresses': [],
            'studio': None,
            'studio_code': None,
            'release_date': None
        }
        
        try:
            # 提取女優名稱
            actress_span = product_div.find('span', class_='fw-bold')
            if actress_span:
                result['actresses'] = [actress_span.text.strip()]
            
            # 提取系列/片商資訊
            series_link = product_div.find('a', href=re.compile(r'../series/'))
            if series_link:
                result['studio'] = series_link.text.strip()
                # 從 href 提取片商代碼
                href = series_link.get('href', '')
                if '../series/' in href:
                    result['studio_code'] = href.replace('../series/', '').strip()
            
            # 提取發行日期
            date_span = product_div.find('span', class_='start_date')
            if date_span:
                result['release_date'] = date_span.text.strip()
            
            # 如果沒有找到片商，嘗試從番號推測
            if not result['studio_code']:
                result['studio_code'] = self._extract_studio_code_from_number(code)
            
            if result['actresses']:
                self.search_cache[code] = result
                logger.info(f"番號 {code} 透過 {result['source']} 找到: {', '.join(result['actresses'])}, 片商: {result.get('studio', '未知')}")
                
        except Exception as e:
            logger.warning(f"提取 {code} 從 chiba-f.net 資訊時發生部分錯誤: {str(e)}")
        
        return result if result.get('actresses') else None
    
    def _extract_studio_info(self, soup: BeautifulSoup, code: str) -> Dict:
        """從網頁中提取片商資訊"""
        studio_info = {
            'studio': None,
            'studio_code': None,
            'release_date': None
        }
        
        try:
            # 方法1: 嘗試從番號中提取片商代碼
            studio_code = self._extract_studio_code_from_number(code)
            if studio_code:
                studio_info['studio_code'] = studio_code
                studio_info['studio'] = self._get_studio_name_by_code(studio_code)
            
            # 方法2: 從網頁內容中搜尋片商資訊
            page_text = soup.get_text()
            
            # 搜尋常見的片商名稱和模式
            studio_patterns = [
                # 直接片商名稱匹配
                (r'(S1|SOD|MOODYZ|PREMIUM|WANZ|FALENO|ATTACKERS|E-BODY|KAWAII|FITCH|MADONNA|PRESTIGE)', r'\1'),
                # 製作公司/發行商模式
                (r'製作[：:]\s*([^\n\r]+)', r'\1'),
                (r'發行[：:]\s*([^\n\r]+)', r'\1'),
                (r'メーカー[：:]\s*([^\n\r]+)', r'\1'),
                # 番號前綴模式 
                (r'品番[：:]\s*([A-Z]+)-?\d+', r'\1'),
            ]
            
            for pattern, replacement in studio_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    extracted_studio = match.group(1).strip()
                    if extracted_studio and len(extracted_studio) < 50:  # 合理長度限制
                        if not studio_info['studio']:
                            studio_info['studio'] = extracted_studio
                        if not studio_info['studio_code'] and len(extracted_studio) <= 10:
                            studio_info['studio_code'] = extracted_studio
                        break
            
            # 方法3: 嘗試提取發行日期
            date_patterns = [
                r'發售日[：:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
                r'(\d{4}\.\d{1,2}\.\d{1,2})'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, page_text)
                if match:
                    studio_info['release_date'] = match.group(1)
                    break                    
        except Exception as e:
            logger.warning(f"提取片商資訊時發生錯誤: {e}")
        
        return studio_info
    
    def _extract_studio_code_from_number(self, code: str) -> Optional[str]:
        """從番號中提取片商代碼"""
        if not code:
            return None
            
        # 提取字母部分作為片商代碼
        match = re.match(r'^([A-Z]+)', code.upper())
        if match:
            return match.group(1)
        return None
    
    def _get_studio_name_by_code(self, studio_code: str) -> Optional[str]:
        """根據片商代碼獲取片商名稱（從 studios.json 載入）"""
        try:
            import json
            from pathlib import Path
            
            # 載入 studios.json 檔案
            studios_file = Path(__file__).parent.parent.parent / 'studios.json'
            if studios_file.exists():
                with open(studios_file, 'r', encoding='utf-8') as f:
                    studios_data = json.load(f)
                
                # 反向查找：從代碼找到片商
                studio_code_upper = studio_code.upper()
                for studio_name, codes in studios_data.items():
                    if studio_code_upper in [code.upper() for code in codes]:
                        return studio_name
        except Exception as e:
            logger.warning(f"載入 studios.json 失敗: {e}")
        
        # 回退到內建對應表
        studio_mapping = {
            'STAR': 'SOD',
            'STARS': 'SOD', 
            'SDJS': 'SOD',
            'SSIS': 'S1',
            'SSNI': 'S1',
            'IPX': 'IdeaPocket',
            'IPZZ': 'IdeaPocket',
            'MIDV': 'MOODYZ',
            'MIAA': 'MOODYZ',
            'WANZ': 'WANZ FACTORY',
            'FSDSS': 'FALENO',
            'PRED': 'PREMIUM',
            'ABW': 'Prestige',
            'BF': 'BeFree',
            'CAWD': 'kawaii',
            'JUFD': 'Fitch',
            'JUL': 'MADONNA',
            'JUY': 'MADONNA',
        }
        
        return studio_mapping.get(studio_code.upper(), studio_code)
    
    def get_safe_searcher_stats(self) -> Dict:
        """獲取安全搜尋器統計資訊"""
        return self.safe_searcher.get_stats()
    
    def clear_cache(self):
        """清空快取"""
        self.search_cache.clear()
        self.safe_searcher.clear_cache()
        logger.info("🧹 已清空所有搜尋快取")
    
    def configure_safe_searcher(self, **kwargs):
        """動態配置安全搜尋器"""
        self.safe_searcher.configure(**kwargs)
        # 更新本地標頭
        self.headers = self.safe_searcher.get_headers()
    
    def get_javdb_stats(self) -> Dict:
        """獲取 JAVDB 搜尋器統計資訊"""
        return self.javdb_searcher.get_stats()
    
    def get_all_search_stats(self) -> Dict:
        """獲取所有搜尋器的統計資訊"""
        return {
            'safe_searcher': self.get_safe_searcher_stats(),
            'javdb_searcher': self.get_javdb_stats(),
            'local_cache_entries': len(self.search_cache)
        }
    
    def clear_all_cache(self):
        """清空所有搜尋快取"""
        self.search_cache.clear()
        self.safe_searcher.clear_cache()
        self.javdb_searcher.clear_cache()
        logger.info("🧹 已清空所有搜尋快取 (包含 JAVDB)")
