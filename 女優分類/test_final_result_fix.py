# -*- coding: utf-8 -*-
"""
驗證最終的 Result 物件修正
"""

import sys
from pathlib import Path

# 設定 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def test_final_result_fix():
    """測試最終的 Result 物件修正"""
    print("🔧 驗證最終 Result 物件修正...")
    
    try:
        # 導入相關模組
        from src.container import Container
        
        # 建立容器
        container = Container()
        
        print("✅ 依賴注入容器建立成功")
        
        # 測試 classifier_core
        classifier_core = container.unified_classifier_core()
        print("✅ classifier_core 載入成功")
        
        # 模擬一個簡單的測試，看看是否還有 Result 物件處理問題
        test_path = str(Path(__file__).parent)
        
        # 測試 interactive_move_files（這是出現錯誤的方法）
        result = classifier_core.interactive_move_files(test_path)
        print(f"✅ interactive_move_files 執行成功: {result['status']}")
        
        print("\n🎉 最終 Result 物件修正驗證成功！")
        print("💡 'Result' object is not subscriptable 錯誤應該已完全修正")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_final_result_fix()
    if success:
        print("\n✅ 最終修正驗證完成，現在可以安全使用互動式分類功能")
    else:
        print("\n❌ 仍有問題需要進一步檢查")
