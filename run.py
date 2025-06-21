# -*- coding: utf-8 -*-
"""
女優分類系統 - 啟動腳本（重定向版本）

**建立日期**: 2025-06-22

此檔案會自動重定向到正確的專案位置並啟動主程式。
"""

import sys
import os
from pathlib import Path

# 設定終端機編碼
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

def main():
    """主啟動函數"""
    print("[重定向] 啟動女優分類專案...")
    
    # 重定向到正確的專案位置
    project_root = Path(__file__).parent / "女優分類"
    
    if not project_root.exists():
        print("[錯誤] 找不到女優分類專案資料夾")
        print(f"預期位置：{project_root}")
        print("請確認專案結構是否正確")
        input("按 Enter 鍵退出...")
        return
    
    main_script = project_root / 'run.py'
    if not main_script.exists():
        print("[錯誤] 找不到主啟動腳本")
        print(f"預期位置：{main_script}")
        input("按 Enter 鍵退出...")
        return
    
    print(f"[成功] 找到專案位置：{project_root}")
    print("[啟動] 女優分類系統...")
      # 切換到專案目錄
    original_cwd = os.getcwd()
    try:
        os.chdir(str(project_root))
        
        # 添加 src 目錄到 Python 路徑
        src_path = project_root / 'src'
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        # 執行主要的 run.py
        with open(main_script, 'r', encoding='utf-8') as f:
            exec(f.read())
        
    except Exception as e:
        print(f"[錯誤] 啟動失敗：{e}")
        input("按 Enter 鍵退出...")
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    main()
