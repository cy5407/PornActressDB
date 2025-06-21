#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試互動式對話框的可調整大小功能
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# 將 src 資料夾加入 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def test_resizable_dialog():
    """測試可調整大小的對話框"""
    
    # 建立測試用的主視窗
    root = tk.Tk()
    root.title("測試主視窗")
    root.geometry("400x300")
    
    try:
        # 匯入互動式分類器
        from models.config import PreferenceManager
        from services.interactive_classifier import InteractiveClassifier
        
        # 建立偏好管理器（簡化版）
        class TestPreferenceManager:
            def get_preferred_actress(self, actresses):
                return None
                
        preference_manager = TestPreferenceManager()
        classifier = InteractiveClassifier(preference_manager, root)
        
        # 建立測試按鈕
        def test_dialog():
            test_actresses = ['小正のあん', 'さつき芽衣', '松本いちか', '美谷朱里', '百瀬あすか', 
                            '水原みその', '逢見リカ', '美波もも', '結城りの', '安住亜沙美', '飯別つまき']
            result = classifier.get_classification_choice("DAZD-217", test_actresses)
            print(f"測試結果: {result}")
        
        test_btn = tk.Button(root, text="測試可調整大小對話框", command=test_dialog, 
                           font=("Arial", 12), pady=10)
        test_btn.pack(expand=True)
        
        info_label = tk.Label(root, text="點擊按鈕測試對話框\n現在應該可以調整大小了！", 
                            font=("Arial", 10), fg="blue")
        info_label.pack(pady=20)
        
        print("🔧 互動式對話框修正測試")
        print("=" * 40)
        print("✅ 修正項目:")
        print("  - 視窗可調整大小 (resizable=True)")
        print("  - 設定最小尺寸 (minsize)")
        print("  - 改善佈局和滾動支援")
        print("  - 添加滾輪支援")
        print("\n點擊測試按鈕來體驗修正效果...")
        
        root.mainloop()
        
    except ImportError as e:
        print(f"匯入錯誤: {e}")
        print("請確認 src/ 資料夾結構正確")
    except Exception as e:
        print(f"測試錯誤: {e}")

if __name__ == "__main__":
    test_resizable_dialog()
