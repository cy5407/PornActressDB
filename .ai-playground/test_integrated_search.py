#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試整合後的搜尋功能
"""

import sys
import os
import threading
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.web_searcher import WebSearcher
from models.config import ConfigManager

def test_integrated_search():
    """測試整合後的搜尋功能"""
    print("🚀 測試整合後的搜尋功能")
    print("=" * 50)
    
    # 初始化配置和搜尋器
    config = ConfigManager()
    searcher = WebSearcher(config)
    stop_event = threading.Event()
    
    # 測試番號列表
    test_codes = [
        "EBWH-226",  # chiba-f.net 有資料的
        "PPPE-353",  # AV-WIKI 可能有的
        "SDJS-303",  # AV-WIKI 可能有的
        "TZ-150",    # 測試備用搜尋
        "NONEXIST-999"  # 測試都找不到的情況
    ]
    
    for code in test_codes:
        print(f"\n🔍 測試番號: {code}")
        print("-" * 30)
        
        start_time = time.time()
        result = searcher.search_info(code, stop_event)
        end_time = time.time()
        
        if result:
            print(f"✅ 找到結果 (耗時: {end_time-start_time:.2f}秒)")
            print(f"   來源: {result.get('source', '未知')}")
            print(f"   女優: {', '.join(result.get('actresses', []))}")
            if result.get('studio'):
                print(f"   片商: {result.get('studio')}")
            if result.get('studio_code'):
                print(f"   片商代碼: {result.get('studio_code')}")
            if result.get('release_date'):
                print(f"   發行日期: {result.get('release_date')}")
        else:
            print(f"❌ 未找到結果 (耗時: {end_time-start_time:.2f}秒)")
        
        # 避免請求過於頻繁
        time.sleep(1)

if __name__ == "__main__":
    test_integrated_search()
