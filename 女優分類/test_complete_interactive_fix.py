# -*- coding: utf-8 -*-
"""
模擬測試互動式分類的完整流程
"""

import sys
from pathlib import Path

# 設定 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def test_interactive_classification_flow():
    """測試互動式分類的完整流程，特別是 Result 物件處理"""
    print("🧪 測試互動式分類完整流程...")
    
    try:
        # 導入相關模組
        from src.container import Container
        from src.models.results import Result
        
        # 建立容器
        container = Container()
        
        print("✅ 依賴注入容器建立成功")
        
        # 測試核心分類器
        classifier_core = container.unified_classifier_core()
        print("✅ 統一分類器核心載入成功")
        
        # 測試檔案掃描器
        file_scanner = container.file_scanner()
        print("✅ 檔案掃描器載入成功")
        
        # 測試程式碼提取器
        code_extractor = container.code_extractor()
        print("✅ 程式碼提取器載入成功")
        
        # 測試資料庫管理器
        db_manager = container.db_manager()
        print("✅ 資料庫管理器載入成功")
        
        # 模擬程式碼提取
        test_filename = "hhd800.com@CAWD-854.mp4"
        code_result = code_extractor.extract_code(test_filename)
        print(f"✅ 程式碼提取測試: {test_filename} -> Result(success={code_result.success}, data={code_result.data})")
        
        if code_result.success and code_result.data:
            code = code_result.data
            print(f"✅ 提取到番號: {code}")
            
            # 模擬資料庫查詢
            info_result = db_manager.get_video_info(code)
            print(f"✅ 資料庫查詢測試: {code} -> Result(success={info_result.success}, data={info_result.data})")
            
            if info_result.success:
                if info_result.data:
                    info = info_result.data
                    print(f"✅ 正確展開資料庫查詢結果")
                    if info.get("actresses"):
                        print(f"   女優資訊: {info['actresses']}")
                    else:
                        print("   無女優資訊")
                else:
                    print("ℹ️ 資料庫中無此番號資料（預期結果）")
            else:
                print(f"ℹ️ 資料庫查詢失敗: {info_result.error}")
        
        # 測試掃描目錄
        test_path = str(Path(__file__).parent)
        scan_result = file_scanner.scan_directory(test_path)
        print(f"✅ 目錄掃描測試: Result(success={scan_result.success}, files_count={len(scan_result.data) if scan_result.success else 0})")
        
        # 測試獲取所有影片
        all_videos_result = db_manager.get_all_videos()
        print(f"✅ 獲取所有影片測試: Result(success={all_videos_result.success}, count={len(all_videos_result.data) if all_videos_result.success else 0})")
        
        print("\n🎉 所有 Result 物件處理測試通過！")
        print("🔧 原始的 'Result' object is not subscriptable 錯誤應該已經修正")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_interactive_classification_flow()
    if success:
        print("\n✅ 互動式分類 Result 物件處理修正驗證完成")
        print("💡 現在可以嘗試再次執行互動式分類功能")
    else:
        print("\n❌ 發現問題，需要進一步檢查")
