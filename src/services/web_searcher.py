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

logger = logging.getLogger(__name__)


class WebSearcher:
    """增強版搜尋器 - 支援搜尋結果頁面"""
    
    def __init__(self, config: ConfigManager):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
        self.search_cache = {}
        self.batch_size = config.getint('search', 'batch_size', fallback=10)
        self.thread_count = config.getint('search', 'thread_count', fallback=5)
        self.batch_delay = config.getfloat('search', 'batch_delay', fallback=2.0)
        self.timeout = config.getint('search', 'request_timeout', fallback=20)

    def search_info(self, code: str, stop_event: threading.Event) -> Optional[Dict]:
        if stop_event.is_set(): 
            return None
        if code in self.search_cache: 
            return self.search_cache[code]
        
        search_url = f"https://av-wiki.net/?s={quote(code)}&post_type=product"
        try:
            with httpx.Client(headers=self.headers, timeout=self.timeout) as client:
                response = client.get(search_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                
                actress_elements = soup.find_all(class_="actress-name")
                actresses = [actress.text.strip() for actress in actress_elements if actress.text.strip()]
                
                # 新增：搜尋片商資訊
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
                        'source': 'AV-WIKI (增強版)', 
                        'actresses': actresses,
                        'studio': studio_info.get('studio'),
                        'studio_code': studio_info.get('studio_code'),
                        'release_date': studio_info.get('release_date')
                    }
                    self.search_cache[code] = result
                    logger.info(f"番號 {code} 透過 {result['source']} 找到: {', '.join(result['actresses'])}, 片商: {result.get('studio', '未知')}")
                    return result

        except httpx.RequestError as e:
            logger.error(f"AV-WIKI 搜尋 {code} 時發生網路錯誤: {e}")
        except Exception as e:
            logger.error(f"AV-WIKI 解析 {code} 時發生未知錯誤: {e}", exc_info=True)
        
        # 如果 AV-WIKI 沒找到，嘗試 chiba-f.net
        logger.debug(f"AV-WIKI 未找到 {code}，嘗試 chiba-f.net...")
        chiba_result = self._search_chiba_f_net(code, stop_event)
        if chiba_result:
            return chiba_result
            
        logger.warning(f"番號 {code} 未在所有搜尋源中找到女優資訊。")
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
        """使用 chiba-f.net 搜尋女優資訊"""
        if stop_event.is_set():
            return None
            
        search_url = f"https://chiba-f.net/search/?keyword={quote(code)}"
        try:
            with httpx.Client(headers=self.headers, timeout=self.timeout) as client:
                response = client.get(search_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                
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
                        
        except httpx.RequestError as e:
            logger.error(f"chiba-f.net 搜尋 {code} 時發生網路錯誤: {e}")
        except Exception as e:
            logger.error(f"chiba-f.net 解析 {code} 時發生未知錯誤: {e}", exc_info=True)
            
        logger.debug(f"番號 {code} 未在 chiba-f.net 中找到女優資訊。")
        return None
    
    def _extract_chiba_product_info(self, product_div, code: str) -> Dict:
        """從 chiba-f.net 產品區塊提取資訊"""
        result = {
            'source': 'chiba-f.net',
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
