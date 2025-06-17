#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版 chiba-f.net 搜尋測試
"""

import requests
import re
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any


def test_single_search(code: str):
    """測試單個番號搜尋"""
    print(f"🔍 測試搜尋: {code}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:        # 嘗試不同的搜尋方式
        search_urls = [
            f"https://chiba-f.net/search/?keyword={code}",
            f"https://chiba-f.net/search/?keyword={code.upper()}",
            f"https://chiba-f.net/search/?keyword={code.lower()}",
            f"https://chiba-f.net/details/?pno={code.lower().replace('-', '')}",
        ]
        
        for i, url in enumerate(search_urls):
            print(f"  嘗試 URL {i+1}: {url}")
            
            try:
                response = requests.get(url, headers=headers, timeout=15)
                print(f"    狀態碼: {response.status_code}")
                
                if response.status_code == 200:
                    # 檢查內容是否包含相關資訊
                    if code.upper() in response.text.upper():
                        print(f"    ✅ 找到 {code} 相關內容!")
                        # 簡單解析
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # 查找女優名稱
                        actress_spans = soup.find_all('span', class_='fw-bold')
                        if actress_spans:
                            for span in actress_spans:
                                print(f"    女優: {span.text.strip()}")
                        
                        # 查找系列
                        series_links = soup.find_all('a', href=re.compile(r'series/'))
                        if series_links:
                            for link in series_links:
                                print(f"    系列: {link.text.strip()}")
                        
                        # 查找日期
                        date_spans = soup.find_all('span', class_='start_date')
                        if date_spans:
                            for span in date_spans:
                                print(f"    日期: {span.text.strip()}")
                        
                        return True
                    else:
                        print(f"    ❌ 未找到 {code} 相關內容")
                else:
                    print(f"    ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"    ❌ 請求錯誤: {str(e)}")
        
        return False
        
    except Exception as e:
        print(f"❌ 測試 {code} 時發生錯誤: {str(e)}")
        return False


def main():
    """主測試函數"""
    print("🚀 簡化版 chiba-f.net 搜尋測試")
    print("=" * 50)
    
    # 測試一些具體的番號
    test_codes = [
        "EBWH-226",  # 您提到的有資料的番號
        "PPPE-353",  # 之前測試中有找到的
        "SDJS-303",  # 之前測試中有找到的
        "TZ-150",    # 測試失敗的
        "MUKD-536",  # 有多個版本的
    ]
    
    found_count = 0
    
    for code in test_codes:
        print(f"\n{'='*30}")
        if test_single_search(code):
            found_count += 1
        print()
    
    print(f"\n📊 結果: {found_count}/{len(test_codes)} 找到資料")


if __name__ == "__main__":
    main()
