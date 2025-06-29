#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
檢查當前程式碼版本的快速驗證腳本
"""

import sys
from pathlib import Path

# 設定路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def verify_fixes():
    """驗證所有修正是否已生效"""
    
    print("🔍 驗證 Result 物件修正狀態...")
    
    try:
        # 強制重新載入模組
        for module_name in list(sys.modules.keys()):
            if module_name.startswith('src.'):
                del sys.modules[module_name]
        
        print("✅ 清除模組快取")
        
        # 重新導入
        from src.services.classifier_core import UnifiedClassifierCore
        import inspect
        
        # 檢查方法源碼
        method = UnifiedClassifierCore.process_and_search_japanese_sites
        source_lines = inspect.getsourcelines(method)[0]
        
        print("🔍 檢查 process_and_search_japanese_sites 方法...")
        
        # 檢查關鍵行
        has_scan_result = False
        has_success_check = False
        has_data_assignment = False
        
        for line in source_lines:
            line_clean = line.strip()
            if 'scan_result = self.file_scanner.scan_directory' in line_clean:
                has_scan_result = True
                print("✅ 找到: scan_result 賦值")
            elif 'if not scan_result.success:' in line_clean:
                has_success_check = True
                print("✅ 找到: success 檢查")
            elif 'video_files = scan_result.data' in line_clean:
                has_data_assignment = True
                print("✅ 找到: data 賦值")
        
        # 檢查結果
        if has_scan_result and has_success_check and has_data_assignment:
            print("\n🎉 所有修正都已正確應用！")
            return True
        else:
            print("\n❌ 發現問題:")
            if not has_scan_result:
                print("  - 缺少 scan_result 賦值")
            if not has_success_check:
                print("  - 缺少 success 檢查")
            if not has_data_assignment:
                print("  - 缺少 data 賦值")
            return False
            
    except Exception as e:
        print(f"❌ 驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if verify_fixes():
        print("\n💡 修正已生效，請重新啟動女優分類系統進行測試。")
    else:
        print("\n⚠️  發現問題，需要重新檢查程式碼。")
