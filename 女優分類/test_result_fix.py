# -*- coding: utf-8 -*-
"""
測試 Result 物件處理修正
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.container import Container

def test_get_all_videos_result():
    """測試 get_all_videos 回傳 Result 物件的處理"""
    try:
        # 建立容器
        container = Container()
        container.config.from_dict({
            'database': {'path': 'test.db'},
            'directories': {'video_path': 'test_videos'},
            'search': {'delay': 1, 'timeout': 30}
        })
        container.wire(modules=[__name__])
        
        # 測試資料庫管理器
        db_manager = container.db_manager()
        result = db_manager.get_all_videos()
        
        print(f"get_all_videos() 回傳類型: {type(result)}")
        print(f"是否成功: {result.success}")
        print(f"資料類型: {type(result.data) if result.success else 'N/A'}")
        print(f"資料長度: {len(result.data) if result.success else 'N/A'}")
        
        # 測試正確的使用方式
        if result.success:
            codes = {v["code"] for v in result.data}
            print(f"成功提取到 {len(codes)} 個程式碼")
        else:
            print(f"查詢失敗: {result.error}")
        
        return True
        
    except Exception as e:
        print(f"測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== 測試 Result 物件處理修正 ===")
    success = test_get_all_videos_result()
    print(f"測試結果: {'成功' if success else '失敗'}")
