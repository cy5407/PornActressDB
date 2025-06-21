"""
女優分類系統 - 主進入點
"""

import sys
from pathlib import Path

# 將 src 資料夾加入 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    import tkinter as tk
    from tkinter import messagebox
    import logging
    
    # 設定日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('unified_classifier.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🚀 啟動女優分類系統 - 完整版 v5.3 (JAVDB 優化版)...")
        
        # 初始化安全搜尋器設定
        logger.info("🛡️ 初始化安全搜尋功能...")
        
        # 建立必要的資料夾
        from pathlib import Path
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        cache_dir = Path('cache')
        cache_dir.mkdir(exist_ok=True)
        
        logger.info("📁 已建立必要的資料夾")
        
        root = tk.Tk()
        
        # 嘗試使用 ttkbootstrap 美化主題
        try:
            import ttkbootstrap as tb
            style = tb.Style(theme='litera')
            root = style.master
            logger.info("✨ 已載入 ttkbootstrap 美化主題")
        except ImportError:
            logger.info("📋 使用預設 tkinter 主題")
        
        # 匯入並啟動主介面
        from ui.main_gui import UnifiedActressClassifierGUI
        app = UnifiedActressClassifierGUI(root)
        
        logger.info("🎬 GUI 介面已啟動")
        root.mainloop()
        logger.info("✅ 程式正常結束。")
        
    except Exception as e:
        logger.error(f"❌ 程式啟動失敗: {e}", exc_info=True)
        try:
            messagebox.showerror(
                "致命錯誤", 
                f"程式發生無法處理的錯誤，請查看日誌檔案 'unified_classifier.log'。\n\n錯誤: {e}"
            )
        except:
            print(f"致命錯誤: {e}")
