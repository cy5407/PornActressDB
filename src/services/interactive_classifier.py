# -*- coding: utf-8 -*-
"""
互動式分類器模組
"""
import tkinter as tk
from tkinter import ttk
import logging
from typing import List, Tuple

from models.config import PreferenceManager

logger = logging.getLogger(__name__)


class InteractiveClassifier:
    """互動式分類器 - 處理多女優共演的偏好選擇"""
    
    def __init__(self, preference_manager: PreferenceManager, gui_parent=None):
        self.preference_manager = preference_manager
        self.gui_parent = gui_parent
        self.pending_decisions = {}

    def get_classification_choice(self, code: str, actresses: List[str]) -> Tuple[str, bool]:
        """取得分類選擇 - 返回 (選擇的女優, 是否記住偏好)"""
        
        if len(actresses) == 1:
            return actresses[0], False
        
        # 檢查已有偏好
        preferred = self.preference_manager.get_preferred_actress(actresses)
        if preferred:
            return preferred, False
        
        # 需要使用者選擇
        if self.gui_parent:
            return self._show_gui_choice_dialog(code, actresses)
        else:
            return self._show_console_choice(code, actresses)

    def _show_gui_choice_dialog(self, code: str, actresses: List[str]) -> Tuple[str, bool]:
        """顯示 GUI 選擇對話框"""
        
        result = {'choice': None, 'remember': False}
        
        dialog = tk.Toplevel(self.gui_parent)
        dialog.title(f"選擇分類偏好 - {code}")
        dialog.geometry("450x400")
        dialog.resizable(False, False)
        
        # 置中顯示
        dialog.transient(self.gui_parent)
        dialog.grab_set()
        
        # 標題
        title_frame = ttk.Frame(dialog)
        title_frame.pack(pady=15)
        ttk.Label(title_frame, text=f"🎬 影片 {code} 包含多位女優", font=("Arial", 14, "bold")).pack()
        ttk.Label(title_frame, text="請選擇要分類到哪位女優的資料夾：", font=("Arial", 10)).pack(pady=5)
        
        # 選擇區域
        choice_frame = ttk.LabelFrame(dialog, text="女優選擇", padding=10)
        choice_frame.pack(pady=10, padx=20, fill="x")
        
        selected_actress = tk.StringVar()
        
        # 女優選項
        for i, actress in enumerate(actresses):
            rb = ttk.Radiobutton(choice_frame, text=f"{i+1}. {actress}", 
                               variable=selected_actress, value=actress)
            rb.pack(anchor="w", pady=2)
            if i == 0:
                rb.invoke()
        
        # 特殊選項
        ttk.Separator(choice_frame, orient='horizontal').pack(fill='x', pady=5)
        ttk.Radiobutton(choice_frame, text=f"{len(actresses)+1}. 放到「多人共演」資料夾", 
                       variable=selected_actress, value="多人共演").pack(anchor="w", pady=2)
        ttk.Radiobutton(choice_frame, text=f"{len(actresses)+2}. 跳過此檔案", 
                       variable=selected_actress, value="SKIP").pack(anchor="w", pady=2)
        
        # 記住偏好選項
        remember_frame = ttk.Frame(dialog)
        remember_frame.pack(pady=10)
        remember_var = tk.BooleanVar()
        ttk.Checkbutton(remember_frame, text="🧠 記住此組合的偏好設定 (下次自動分類)", 
                       variable=remember_var).pack()
        
        # 按鈕區域
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=15)
        
        def confirm_choice():
            choice = selected_actress.get()
            if choice:
                result['choice'] = choice
                result['remember'] = remember_var.get()
                dialog.destroy()
        
        def skip_all():
            result['choice'] = "SKIP_ALL"
            result['remember'] = False
            dialog.destroy()
        
        ttk.Button(button_frame, text="✅ 確認選擇", command=confirm_choice).pack(side="left", padx=5)
        ttk.Button(button_frame, text="⏭️ 全部跳過", command=skip_all).pack(side="left", padx=5)
        ttk.Button(button_frame, text="❌ 取消", command=dialog.destroy).pack(side="left", padx=5)
        
        # 等待使用者選擇
        dialog.wait_window()
        
        choice = result.get('choice')
        if not choice:
            return "SKIP", False
        
        remember = result.get('remember', False)
        return choice, remember

    def _show_console_choice(self, code: str, actresses: List[str]) -> Tuple[str, bool]:
        """顯示控制台選擇介面"""
        
        print(f"\n🎬 影片 {code} 包含以下女優：")
        for i, actress in enumerate(actresses, 1):
            print(f"  {i}. {actress}")
        
        print(f"  {len(actresses) + 1}. 放到「多人共演」資料夾")
        print(f"  {len(actresses) + 2}. 跳過此檔案")
        print(f"  0. 跳過所有後續選擇")
        
        while True:
            try:
                choice = input("請選擇 (輸入數字): ").strip()
                
                if choice == "0":
                    return "SKIP_ALL", False
                
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(actresses):
                    chosen = actresses[choice_num - 1]
                    
                    remember_input = input(f"是否記住 {', '.join(actresses)} 的分類偏好到 {chosen}？(y/n): ").strip().lower()
                    remember = remember_input in ['y', 'yes', '是']
                    
                    return chosen, remember
                    
                elif choice_num == len(actresses) + 1:
                    return "多人共演", False
                    
                elif choice_num == len(actresses) + 2:
                    return "SKIP", False
                    
                else:
                    print("❌ 無效選擇，請重新輸入")
                    
            except ValueError:
                print("❌ 請輸入有效的數字")
            except KeyboardInterrupt:
                print("\n⏹️ 使用者中斷操作")
                return "SKIP_ALL", False
