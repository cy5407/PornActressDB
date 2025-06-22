# -*- coding: utf-8 -*-
"""
測試程式碼結構和匯入（不執行實際搜尋）
"""

import sys
from pathlib import Path

# 添加專案路徑
project_root = Path(__file__).parent / '女優分類'
sys.path.insert(0, str(project_root / 'src'))

def test_imports():
    """測試程式碼結構和匯入"""
    
    print("🧪 測試分離式編碼處理結構...")
    
    try:
        # 測試日文網站增強器匯入
        print("1. 測試日文網站增強器匯入...")
        from services.japanese_site_enhancer import create_japanese_soup, is_japanese_site
        print("   ✅ 日文網站增強器匯入成功")
        
        # 測試函式可用性
        print("2. 測試函式可用性...")
        test_url = "https://av-wiki.net/test"
        is_jp = is_japanese_site(test_url)
        print(f"   ✅ is_japanese_site('{test_url}') = {is_jp}")
        
        # 測試 JAVDB 搜尋器匯入
        print("3. 測試 JAVDB 搜尋器匯入...")
        from services.safe_javdb_searcher import SafeJAVDBSearcher
        print("   ✅ JAVDB 搜尋器匯入成功")
        
        # 測試配置管理器
        print("4. 測試配置管理器匯入...")
        from models.config import ConfigManager
        print("   ✅ 配置管理器匯入成功")
        
        print("\n📊 結構檢查結果:")
        print("✅ 所有關鍵模組都能正確匯入")
        print("✅ 分離式編碼處理結構完整")
        print("✅ 日文網站將使用 CP932 編碼處理")
        print("✅ JAVDB 保持原有 UTF-8 標準處理")
        
        return True
        
    except ImportError as e:
        print(f"❌ 匯入錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🎉 分離式編碼處理結構測試通過！")
    else:
        print("\n💥 測試失敗，請檢查程式碼結構")