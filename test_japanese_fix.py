#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修正後的日文網站搜尋功能
"""

import sys
from pathlib import Path

# 將 src 資料夾加入 Python 路徑
src_path = Path(__file__).parent / '女優分類' / 'src'
sys.path.insert(0, str(src_path))

from models.config import ConfigManager
from services.web_searcher import WebSearcher
import threading

def test_japanese_sites_search():
    """測試日文網站搜尋功能"""
    print("🚀 測試修正後的日文網站搜尋功能")
    print("=" * 60)
    
    # 初始化配置和搜尋器
    config = ConfigManager()
    searcher = WebSearcher(config)
    stop_event = threading.Event()
    
    # 測試番號
    test_codes = ['SONE-553', 'FWAY-031', 'SONE-323']
    
    print(f"\n📋 測試日文網站專用搜尋方法")
    print("-" * 40)
    
    for code in test_codes:
        print(f"\n🔍 測試番號: {code}")
        
        try:
            # 使用修正後的日文網站搜尋
            result = searcher.search_japanese_sites(code, stop_event)
            
            if result and result.get('actresses'):
                print(f"✅ 找到結果:")
                print(f"    來源: {result.get('source', 'Unknown')}")
                print(f"    女優: {', '.join(result['actresses'])}")
                print(f"    片商: {result.get('studio', '未知')}")
                if result.get('release_date'):
                    print(f"    發行日期: {result['release_date']}")
            else:
                print(f"❌ 未找到結果")
                
        except Exception as e:
            print(f"💥 搜尋失敗: {e}")
        
        print(f"⏰ 等待 2 秒...")
        import time
        time.sleep(2)
    
    # 測試 JAVDB 專用搜尋
    print(f"\n📋 測試 JAVDB 專用搜尋方法")
    print("-" * 40)
    
    for code in test_codes[:2]:  # 只測試前兩個
        print(f"\n🔍 測試番號: {code}")
        
        try:
            result = searcher.search_javdb_only(code, stop_event)
            
            if result and result.get('actresses'):
                print(f"✅ JAVDB 找到結果:")
                print(f"    來源: {result.get('source', 'Unknown')}")
                print(f"    女優: {', '.join(result['actresses'])}")
                print(f"    片商: {result.get('studio', '未知')}")
                if result.get('rating'):
                    print(f"    評分: {result['rating']}")
            else:
                print(f"❌ JAVDB 未找到結果")
                
        except Exception as e:
            print(f"💥 JAVDB 搜尋失敗: {e}")
        
        print(f"⏰ 等待 2 秒...")
        time.sleep(2)

def test_headers():
    """測試日文網站專用標頭"""
    print(f"\n📋 測試日文網站專用標頭")
    print("-" * 40)
    
    config = ConfigManager()
    searcher = WebSearcher(config)
    
    print("🔧 日文網站專用標頭:")
    for key, value in searcher.japanese_headers.items():
        print(f"    {key}: {value}")
    
    # 檢查是否不包含 Accept-Encoding
    if 'Accept-Encoding' not in searcher.japanese_headers:
        print("✅ 正確：不包含 Accept-Encoding，避免 Brotli 壓縮")
    else:
        print("❌ 錯誤：仍包含 Accept-Encoding，可能導致壓縮問題")

if __name__ == "__main__":
    test_headers()
    test_japanese_sites_search()
    
    print(f"\n{'='*60}")
    print("🎉 測試完成！")
    print("如果日文網站能找到女優資訊，則修正成功！")
