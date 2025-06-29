#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 WebSearcher 和 Result 物件處理的修正
"""
import threading
import sys
import os

# 將專案根目錄加入 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.config import ConfigManager
from src.services.web_searcher import WebSearcher
from src.services.classifier_core import UnifiedClassifierCore
from src.models.extractor import UnifiedCodeExtractor
from src.models.database import SQLiteDBManager

def test_javdb_search():
    """測試 WebSearcher.search_javdb_only 方法回傳 Result 物件處理"""
    print("開始測試 JAVDB 搜尋處理...")
    
    # 初始化配置
    config = ConfigManager()
    
    # 初始化 WebSearcher
    web_searcher = WebSearcher(config)
    
    # 建立測試用的中止事件
    stop_event = threading.Event()
    
    # 測試單一代碼搜尋
    code = "STARS-224"
    print(f"搜尋代碼: {code}")
    result = web_searcher.search_javdb_only(code, stop_event)
    
    # 驗證結果正確處理
    print(f"返回型別: {type(result)}")
    print(f"是否成功: {result.success}")
    
    # 檢查結果是否為 Result 物件且正確處理
    if result.success:
        print("成功獲取結果!")
        print(f"資料型別: {type(result.data)}")
        
        # 測試資料存取
        if result.data and "actresses" in result.data:
            print(f"女優: {result.data['actresses']}")
            print(f"片商: {result.data.get('studio', '無片商資訊')}")
        else:
            print("無女優資料")
    else:
        print(f"搜尋失敗: {result.error.message if result.error else '未知錯誤'}")
    
    # 測試 batch_search
    print("\n測試批次搜尋...")
    codes = ["STARS-224", "SSNI-650", "IPX-999"]
    results = web_searcher.batch_search(codes, web_searcher.search_javdb_only, stop_event)
    
    # 驗證批次結果
    print(f"返回型別: {type(results)}")
    print(f"結果數量: {len(results)}")
    
    # 顯示所有結果
    for code, result_obj in results.items():
        print(f"\n代碼: {code}")
        print(f"是否成功: {result_obj.success}")
        
        if result_obj.success and result_obj.data:
            print(f"女優: {result_obj.data.get('actresses', ['無資料'])}")
        else:
            print(f"錯誤: {result_obj.error.message if result_obj.error else '未知錯誤'}")
    
    print("\n測試完成!")

if __name__ == "__main__":
    test_javdb_search()
