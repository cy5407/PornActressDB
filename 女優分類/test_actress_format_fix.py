#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試單人作品資料格式一致性修正
"""

import sys
import os
from pathlib import Path

# 加入專案根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.container import Container

def test_single_actress_format_consistency():
    """測試單人作品的資料格式是否一致"""
    print("🔧 開始測試單人作品資料格式一致性...")
    
    try:
        # 初始化容器
        container = Container()
        container.init_resources()
        
        # 取得 classifier_core
        classifier_core = container.unified_classifier_core()
        
        # 建立測試資料夾
        test_path = project_root / "test_single_actress"
        test_path.mkdir(exist_ok=True)
        
        # 建立一個單人作品測試檔案
        test_file = test_path / "PRED-456.mp4"  # 一般是單人作品
        test_file.touch()
        
        print(f"📁 建立測試路徑: {test_path}")
        print(f"📄 建立測試檔案: {test_file}")
        
        # 測試 interactive_move_files 方法處理單人作品的資料格式
        print("🎯 呼叫 interactive_move_files 方法...")
        result = classifier_core.interactive_move_files(str(test_path))
        
        print(f"✅ interactive_move_files 執行完成")
        print(f"📊 結果: {result}")
        
        # 清理測試檔案
        if test_file.exists():
            test_file.unlink()
        if test_path.exists():
            test_path.rmdir()
        
        print("🧹 已清理測試檔案")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        print(f"🔍 錯誤類型: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_move_files_consistency():
    """測試 move_files 方法的一致性"""
    print("\n🔧 開始測試 move_files 方法一致性...")
    
    try:
        # 初始化容器
        container = Container()
        container.init_resources()
        
        # 取得 classifier_core
        classifier_core = container.unified_classifier_core()
        
        # 建立測試資料夾
        test_path = project_root / "test_move_files_consistency"
        test_path.mkdir(exist_ok=True)
        
        # 建立測試檔案
        test_file = test_path / "MIDV-123.mp4"
        test_file.touch()
        
        print(f"📁 建立測試路徑: {test_path}")
        print(f"📄 建立測試檔案: {test_file}")
        
        # 測試 move_files 方法
        print("🎯 呼叫 move_files 方法...")
        result = classifier_core.move_files(str(test_path))
        
        print(f"✅ move_files 執行完成")
        print(f"📊 結果: {result}")
        
        # 清理測試檔案
        if test_file.exists():
            test_file.unlink()
        if test_path.exists():
            test_path.rmdir()
        
        print("🧹 已清理測試檔案")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        print(f"🔍 錯誤類型: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 單人作品資料格式一致性測試")
    print("=" * 80)
    
    success1 = test_single_actress_format_consistency()
    success2 = test_move_files_consistency()
    
    print("\n" + "=" * 80)
    if success1 and success2:
        print("🎉 所有測試通過！單人作品資料格式一致性修正成功。")
    else:
        print("⚠️ 部分測試失敗，需要進一步檢查。")
    print("=" * 80)
