# -*- coding: utf-8 -*-
"""
測試 Result 物件修正
"""
import sys
from pathlib import Path

# 將 src 資料夾加入 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from src.container import Container
from src.models.results import Result

def test_result_fixes():
    """測試 Result 物件處理修正"""
    print("🧪 開始測試 Result 物件修正...")
    
    try:
        # 初始化容器
        container = Container()
        
        # 測試各種服務的 Result 返回
        print("1. 測試檔案掃描器...")
        file_scanner = container.file_scanner()
        
        # 測試掃描一個不存在的目錄
        result = file_scanner.scan_directory("./non_existent_directory")
        print(f"   掃描結果類型: {type(result)}")
        print(f"   掃描結果成功: {result.success}")
        if result.success:
            print(f"   掃描結果資料: {type(result.data)}")
        else:
            print(f"   掃描錯誤: {result.error}")
        
        print("2. 測試資料庫管理器...")
        db_manager = container.db_manager()
        
        # 測試取得所有影片
        result = db_manager.get_all_videos()
        print(f"   資料庫結果類型: {type(result)}")
        print(f"   資料庫結果成功: {result.success}")
        if result.success:
            print(f"   影片資料類型: {type(result.data)}")
            print(f"   影片數量: {len(result.data) if result.data else 0}")
        else:
            print(f"   資料庫錯誤: {result.error}")
        
        print("3. 測試核心分類器...")
        core = container.unified_classifier_core()
        print(f"   核心分類器初始化: 成功")
        
        print("✅ 所有 Result 物件修正測試完成！")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_result_fixes()
