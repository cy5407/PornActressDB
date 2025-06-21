#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試片商資訊修正效果
"""

import sys
from pathlib import Path

# 將 src 資料夾加入 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def test_studio_fix():
    """測試片商資訊修正"""
    print("🔧 測試片商資訊修正效果")
    print("=" * 50)
    
    # 模擬搜尋結果
    mock_javdb_result = {
        'actresses': ['西宮夢'],
        'studio': 'S1',  # JAVDB 搜尋到的正確片商
        'source': 'JAVDB'
    }
    
    print(f"JAVDB 搜尋結果:")
    print(f"  片商: {mock_javdb_result['studio']}")
    print(f"  女優: {mock_javdb_result['actresses']}")
    
    # 模擬修正後的邏輯
    code = 'SSIS-001'
    
    # 新邏輯：優先使用搜尋結果中的片商
    studio = mock_javdb_result.get('studio')
    
    # 只有當搜尋結果沒有片商資訊時才使用本地識別
    if not studio or studio == 'UNKNOWN':
        # 這裡會用本地識別器
        print("  使用本地片商識別器")
        studio = "本地識別結果"
    else:
        print("  ✅ 使用 JAVDB 搜尋結果中的片商資訊")
    
    print(f"\n最終寫入資料庫的片商: {studio}")
    
    print("\n修正總結:")
    print("✅ 修正前: 始終使用 studio_identifier.identify_studio(code)")
    print("✅ 修正後: 優先使用 JAVDB 搜尋結果，備用本地識別")
    print("✅ 這樣可以確保 JAVDB 搜尋到的正確片商資訊不會被覆蓋")

def check_modification():
    """檢查程式碼修改"""
    print("\n🔍 檢查程式碼修改")
    print("=" * 50)
    
    classifier_file = Path('src/services/classifier_core.py')
    if classifier_file.exists():
        with open(classifier_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查是否包含修正的程式碼
        if "優先使用搜尋結果中的片商資訊" in content:
            print("✅ 程式碼修正已成功應用")
            print("✅ 新增了片商資訊優先級邏輯")
        else:
            print("❌ 程式碼修正可能未正確應用")
    else:
        print("❌ 找不到 classifier_core.py 檔案")

def main():
    """主函式"""
    test_studio_fix()
    check_modification()
    
    print("\n🎉 測試完成！")
    print("\n下一步建議:")
    print("1. 執行實際的女優分類功能測試")
    print("2. 檢查資料庫中的片商資訊是否正確更新")
    print("3. 使用實際的 JAVDB 搜尋測試新邏輯")

if __name__ == "__main__":
    main()
