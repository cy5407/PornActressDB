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
            if i + self.batch_size < len(items) and total_batches > 1: 
                time.sleep(self.batch_delay)
        return results
