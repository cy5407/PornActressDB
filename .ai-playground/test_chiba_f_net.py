#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新增 chiba-f.net 搜尋網站功能
"""

import asyncio
import httpx
import re
import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

# 添加專案路徑
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.extractor import UnifiedCodeExtractor


class ChibaFNetSearcher:
    """chiba-f.net 搜尋器"""
    
    def __init__(self):
        self.base_url = "https://chiba-f.net"
        self.search_url = f"{self.base_url}/search/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def search_actress_info(self, code: str) -> Optional[Dict[str, Any]]:
        """搜尋女優資訊"""
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
                # 構建搜尋 URL
                search_url = f"{self.search_url}?q={code}"
                
                print(f"🔍 搜尋 {code} 於 chiba-f.net...")
                response = await client.get(search_url)
                
                if response.status_code == 200:
                    return self._parse_search_results(response.text, code)
                else:
                    print(f"❌ HTTP {response.status_code} for {code}")
                    return None
                    
        except Exception as e:
            print(f"❌ 搜尋 {code} 時發生錯誤: {str(e)}")
            return None
    
    def _parse_search_results(self, html_content: str, code: str) -> Optional[Dict[str, Any]]:
        """解析搜尋結果"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 尋找產品區塊
            product_divs = soup.find_all('div', class_='product-div')
            
            for product_div in product_divs:
                # 檢查番號是否匹配
                pno_element = product_div.find('div', class_='pno')
                if pno_element and code.upper() in pno_element.text.upper():
                    return self._extract_product_info(product_div, code)
            
            # 如果沒有找到完全匹配，嘗試模糊匹配
            for product_div in product_divs:
                product_text = product_div.get_text()
                if code.upper() in product_text.upper():
                    return self._extract_product_info(product_div, code)
            
            print(f"❌ 在 chiba-f.net 中未找到 {code}")
            return None
            
        except Exception as e:
            print(f"❌ 解析 {code} 搜尋結果時發生錯誤: {str(e)}")
            return None
    
    def _extract_product_info(self, product_div, code: str) -> Dict[str, Any]:
        """從產品區塊提取資訊"""
        result = {
            'code': code,
            'actresses': [],
            'studio': None,
            'studio_code': None,
            'release_date': None,
            'title': None,
            'source': 'chiba-f.net'
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
            
            # 提取標題
            title_div = product_div.find('div', class_='card-title')
            if title_div:
                result['title'] = title_div.text.strip()
            
            # 如果沒有找到片商，嘗試從番號推測
            if not result['studio_code']:
                result['studio_code'] = self._extract_studio_from_code(code)
            
        except Exception as e:
            print(f"⚠️ 提取 {code} 資訊時發生部分錯誤: {str(e)}")
        
        return result
    
    def _extract_studio_from_code(self, code: str) -> Optional[str]:
        """從番號提取片商代碼"""
        # 提取字母部分作為片商代碼
        match = re.match(r'^([A-Z]+)', code.upper())
        return match.group(1) if match else None


async def test_chiba_f_net_search():
    """測試 chiba-f.net 搜尋功能"""
    
    print("🚀 測試 chiba-f.net 搜尋功能")
    print("=" * 60)
    
    # 測試檔案列表
    test_files = [
        # hhd800.com@ 前綴檔案
        "hhd800.com@420HOI-343.mp4",
        "hhd800.com@DOCS-081.mp4", 
        "hhd800.com@EBWH-226.mp4",
        "hhd800.com@FNS-026.mp4",
        "hhd800.com@FNS-033.mp4",
        "hhd800.com@MIDA-123.mp4",
        "hhd800.com@MUKD-536.mp4",
        "hhd800.com@PKPD-372.mp4",
        "hhd800.com@PPPE-353.mp4",
        "hhd800.com@SDJS-303.mp4",
        "hhd800.com@STZY-017.mp4",
        
        # 其他一般檔案
        "4k2.com@mida-139.mp4",
        "FILE250426-153747F.MP4",
        "MUKD-536_AV1.mp4",
        "MUKD-536_H265.mp4", 
        "sdde-746.mp4",
        "sdjs-318.mp4",
        "tek-102.mp4",
        "TZ-150.mp4",
        "YUJ-036ch.mp4"
    ]
    
    extractor = UnifiedCodeExtractor()
    searcher = ChibaFNetSearcher()
    
    found_count = 0
    total_count = 0
    
    for filename in test_files:
        print(f"\n📁 處理檔案: {filename}")
        
        # 提取番號
        code = extractor.extract_code(filename)
        if not code:
            print(f"⚠️ 無法提取番號")
            continue
        
        print(f"📋 提取番號: {code}")
        total_count += 1
        
        # 搜尋女優資訊
        result = await searcher.search_actress_info(code)
        
        if result and result.get('actresses'):
            found_count += 1
            print(f"✅ 找到資訊:")
            print(f"   女優: {', '.join(result['actresses'])}")
            if result.get('studio'):
                print(f"   片商: {result['studio']}")
            if result.get('studio_code'):
                print(f"   片商代碼: {result['studio_code']}")
            if result.get('release_date'):
                print(f"   發行日期: {result['release_date']}")
            if result.get('title'):
                print(f"   標題: {result['title'][:50]}...")
        else:
            print(f"❌ 未找到資訊")
    
    print(f"\n📊 統計結果:")
    print(f"總共處理: {total_count} 個番號")
    print(f"找到資訊: {found_count} 個")
    print(f"成功率: {found_count/total_count*100:.1f}%" if total_count > 0 else "N/A")


if __name__ == "__main__":
    asyncio.run(test_chiba_f_net_search())
