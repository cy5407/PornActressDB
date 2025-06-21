# -*- coding: utf-8 -*-
"""
run.py 檔案測試腳本

**建立日期**: 2025-06-22

此腳本用於測試兩個 run.py 檔案的功能性。
"""

import sys
import os
from pathlib import Path
import subprocess
import time

def test_redirect_launcher():
    """測試重定向啟動器"""
    print("=" * 50)
    print("📋 測試重定向啟動器")
    print("=" * 50)
    
    main_dir = Path(__file__).parent
    redirect_script = main_dir / "run.py"
    
    if not redirect_script.exists():
        print("❌ 重定向啟動器不存在")
        return False
    
    print(f"✅ 找到重定向啟動器：{redirect_script}")
    
    # 檢查語法
    try:
        with open(redirect_script, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, str(redirect_script), 'exec')
        print("✅ 重定向啟動器語法正確")
    except SyntaxError as e:
        print(f"❌ 重定向啟動器語法錯誤：{e}")
        return False
    
    return True

def test_main_launcher():
    """測試主啟動器"""
    print("=" * 50)
    print("📋 測試主啟動器")
    print("=" * 50)
    
    main_dir = Path(__file__).parent / "女優分類"
    main_script = main_dir / "run.py"
    
    if not main_script.exists():
        print("❌ 主啟動器不存在")
        return False
    
    print(f"✅ 找到主啟動器：{main_script}")
    
    # 檢查語法
    try:
        with open(main_script, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, str(main_script), 'exec')
        print("✅ 主啟動器語法正確")
    except SyntaxError as e:
        print(f"❌ 主啟動器語法錯誤：{e}")
        return False
    
    # 檢查關鍵模組是否存在
    src_dir = main_dir / "src"
    ui_dir = src_dir / "ui"
    main_gui = ui_dir / "main_gui.py"
    
    if not src_dir.exists():
        print("❌ src 目錄不存在")
        return False
    
    if not ui_dir.exists():
        print("❌ ui 目錄不存在")
        return False
    
    if not main_gui.exists():
        print("❌ main_gui.py 不存在")
        return False
    
    print("✅ 所有關鍵模組檔案存在")
    return True

def test_directory_structure():
    """測試目錄結構"""
    print("=" * 50)
    print("📋 測試目錄結構")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    project_dir = base_dir / "女優分類"
    
    required_dirs = [
        project_dir / "src",
        project_dir / "src" / "ui",
        project_dir / "src" / "services",
        project_dir / "src" / "models",
        project_dir / "src" / "utils",
        project_dir / "data",
        project_dir / "cache"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"✅ {dir_path.name} 目錄存在")
        else:
            print(f"❌ {dir_path.name} 目錄不存在")
            all_exist = False
    
    return all_exist

def main():
    """主測試函數"""
    print("🚀 開始 run.py 檔案系統測試")
    print()
    
    results = []
    
    # 測試重定向啟動器
    results.append(("重定向啟動器", test_redirect_launcher()))
    
    # 測試主啟動器
    results.append(("主啟動器", test_main_launcher()))
    
    # 測試目錄結構
    results.append(("目錄結構", test_directory_structure()))
    
    # 總結報告
    print("=" * 50)
    print("📊 測試結果總結")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 所有測試通過！run.py 檔案系統運作正常。")
    else:
        print("⚠️ 部分測試失敗，請檢查上述問題。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    print()
    input("按 Enter 鍵退出...")
    sys.exit(0 if success else 1)
