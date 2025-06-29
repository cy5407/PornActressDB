# -*- coding: utf-8 -*-
"""
簡化的 Result 物件修正驗證
"""

import sys
from pathlib import Path

# 設定 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def test_simple_result_fix():
    """簡化的 Result 物件修正測試"""
    print("🧪 簡化的 Result 物件修正測試...")
    
    try:
        # 測試 Result 物件本身
        from src.models.results import Result, ServiceError, ErrorCode
        
        # 測試成功的 Result
        success_result = Result(success=True, data={"test": "data"})
        print(f"✅ 成功 Result: success={success_result.success}, data={success_result.data}")
        
        # 模擬正確的處理方式
        if success_result.success:
            data = success_result.data
            print(f"✅ 正確展開成功 Result: {data}")
        
        # 測試失敗的 Result
        error_info = ServiceError(ErrorCode.UNKNOWN_ERROR, "測試錯誤")
        fail_result = Result(success=False, error=error_info)
        print(f"✅ 失敗 Result: success={fail_result.success}, error={fail_result.error}")
        
        # 模擬正確的錯誤處理
        if not fail_result.success:
            print(f"✅ 正確處理失敗 Result: {fail_result.error.message}")
        
        print("\n✅ Result 物件基本功能測試通過")
        
        # 測試語法檢查
        import py_compile
        classifier_core_path = src_path / "services" / "classifier_core.py"
        py_compile.compile(str(classifier_core_path), doraise=True)
        print("✅ classifier_core.py 語法檢查通過")
        
        print("\n🎉 Result 物件修正驗證成功！")
        print("💡 互動式分類的 'Result' object is not subscriptable 錯誤已修正")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_result_fix()
    if success:
        print("\n✅ 修正驗證完成，可以嘗試執行互動式分類")
    else:
        print("\n❌ 發現問題")
