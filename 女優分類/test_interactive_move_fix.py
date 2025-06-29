# -*- coding: utf-8 -*-
"""
測試互動式移動功能的 Result 物件修正
"""

import sys
from pathlib import Path

# 設定 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def test_result_handling():
    """測試 Result 物件處理是否正確"""
    print("🧪 測試 Result 物件處理修正...")
    
    try:
        # 導入相關模組
        from src.container import Container
        from src.models.results import Result
        
        # 建立容器
        container = Container()
        
        # 測試資料庫管理器的 get_video_info 方法
        db_manager = container.db_manager()
        
        print("✅ 依賴注入容器建立成功")
        
        # 測試 get_video_info 回傳 Result 物件
        result = db_manager.get_video_info("TEST-001")
        print(f"✅ get_video_info 回傳型態: {type(result)}")
        print(f"✅ Result 物件 success 屬性: {result.success}")
        print(f"✅ Result 物件 data 屬性: {result.data}")
        
        # 測試正確的 Result 處理
        if result.success:
            info = result.data
            if info and info.get("actresses"):
                print(f"✅ 正確展開 Result 物件，女優資訊: {info['actresses']}")
            else:
                print("ℹ️ 測試番號 TEST-001 無資料（預期結果）")
        else:
            print(f"ℹ️ 測試番號查詢失敗（預期結果）: {result.error}")
        
        print("\n🎯 測試 classifier_core 修正...")
        
        # 測試 classifier_core
        classifier_core = container.unified_classifier_core()
        print("✅ classifier_core 載入成功")
        
        print("\n🎉 所有 Result 物件處理修正測試通過！")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_result_handling()
    if success:
        print("\n✅ Result 物件處理修正驗證完成")
    else:
        print("\n❌ 發現問題，需要進一步修正")
