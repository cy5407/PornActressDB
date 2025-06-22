# -*- coding: utf-8 -*-
"""
日文網站編碼增強器 - 專門處理 av-wiki.net 和 chiba-f.net
"""

import logging
from typing import Tuple, Optional
from bs4 import BeautifulSoup
import httpx

logger = logging.getLogger(__name__)

class JapaneseSiteEnhancer:
    """日文網站編碼增強器 - 專為 av-wiki.net 和 chiba-f.net 設計"""
    
    def __init__(self):
        # 日文網站的編碼優先順序
        self.encoding_priority = [
            'cp932',      # 日文 Windows 編碼（最適合）
            'shift_jis',  # 日文編碼
            'euc-jp',     # 日文 Unix 編碼
            'utf-8',      # 作為最後備選
        ]
        
        # 支援的日文網站
        self.supported_domains = [
            'av-wiki.net',
            'chiba-f.net'
        ]
    
    def is_japanese_site(self, url: str) -> bool:
        """檢查是否為支援的日文網站"""
        return any(domain in url for domain in self.supported_domains)
    
    def create_enhanced_soup(self, response: httpx.Response, url: str = "") -> BeautifulSoup:
        """
        為日文網站創建經過編碼優化的 BeautifulSoup 物件
        
        Args:
            response: httpx.Response 物件
            url: 來源 URL
            
        Returns:
            BeautifulSoup 物件
        """
        if not self.is_japanese_site(url):
            # 如果不是日文網站，使用標準處理
            return BeautifulSoup(response.content, "html.parser")
        
        content_bytes = response.content
        if not content_bytes:
            return BeautifulSoup("", "html.parser")
        
        best_soup = None
        best_encoding = 'utf-8'
        min_replacement_ratio = float('inf')
        
        for encoding in self.encoding_priority:
            try:
                decoded = content_bytes.decode(encoding, errors='replace')
                
                # 計算替換字符比例
                replacement_count = decoded.count('\ufffd')
                replacement_ratio = replacement_count / len(decoded) if decoded else 1.0
                
                if replacement_ratio < min_replacement_ratio:
                    min_replacement_ratio = replacement_ratio
                    best_encoding = encoding
                    best_soup = BeautifulSoup(decoded, "html.parser")
                    
                    # 如果替換字符很少，就使用這個編碼
                    if replacement_ratio < 0.05:  # 5% 以下
                        break
                        
            except (UnicodeDecodeError, LookupError) as e:
                logger.debug(f"編碼 {encoding} 解碼失敗: {e}")
                continue
        
        if best_soup is None:
            # 如果所有編碼都失敗，使用標準處理
            logger.warning(f"所有編碼嘗試都失敗，使用標準處理: {url}")
            return BeautifulSoup(response.content, "html.parser")
        
        logger.info(f"[{url}] 日文網站使用最佳編碼: {best_encoding} (替換比例: {min_replacement_ratio:.3f})")
        return best_soup
    
    def smart_decode_response(self, response: httpx.Response, url: str = "") -> Tuple[str, str]:
        """
        智慧解碼日文網站的 HTTP 回應內容
        
        Args:
            response: httpx.Response 物件
            url: 來源 URL
            
        Returns:
            (decoded_content, best_encoding)
        """
        if not self.is_japanese_site(url):
            # 如果不是日文網站，使用標準處理
            return response.text, response.encoding or 'utf-8'
        
        content_bytes = response.content
        if not content_bytes:
            return "", "utf-8"
        
        best_content = ""
        best_encoding = 'utf-8'
        min_replacement_ratio = float('inf')
        
        for encoding in self.encoding_priority:
            try:
                decoded = content_bytes.decode(encoding, errors='replace')
                
                # 計算替換字符比例
                replacement_count = decoded.count('\ufffd')
                replacement_ratio = replacement_count / len(decoded) if decoded else 1.0
                
                if replacement_ratio < min_replacement_ratio:
                    min_replacement_ratio = replacement_ratio
                    best_encoding = encoding
                    best_content = decoded
                    
                    # 如果替換字符很少，就使用這個編碼
                    if replacement_ratio < 0.05:  # 5% 以下
                        break
                        
            except (UnicodeDecodeError, LookupError) as e:
                logger.debug(f"編碼 {encoding} 解碼失敗: {e}")
                continue
        
        if not best_content:
            # 如果所有編碼都失敗，使用原始回應
            logger.warning(f"所有編碼嘗試都失敗，使用原始內容: {url}")
            return response.text, response.encoding or 'utf-8'
        
        logger.info(f"[{url}] 日文網站解碼結果: {best_encoding} (替換比例: {min_replacement_ratio:.3f})")
        return best_content, best_encoding

# 創建全域實例
japanese_enhancer = JapaneseSiteEnhancer()

# 便捷函式
def create_japanese_soup(response: httpx.Response, url: str = "") -> BeautifulSoup:
    """便捷函式：為日文網站創建增強的 BeautifulSoup"""
    return japanese_enhancer.create_enhanced_soup(response, url)

def decode_japanese_response(response: httpx.Response, url: str = "") -> Tuple[str, str]:
    """便捷函式：智慧解碼日文網站回應"""
    return japanese_enhancer.smart_decode_response(response, url)
