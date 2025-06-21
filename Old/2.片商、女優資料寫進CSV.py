import os  # 提供操作系統功能，用於文件和目錄操作
import csv  # 提供CSV檔案處理功能
import tkinter as tk  # 提供GUI介面功能
from tkinter import filedialog  # 提供文件選擇對話框

def select_folder(prompt):
    """
    開啟資料夾選擇對話框，讓使用者選擇目錄
    
    參數:
    prompt - 對話框的標題提示
    
    返回:
    選擇的資料夾路徑
    """
    root = tk.Tk()  # 建立Tkinter根視窗
    root.withdraw()  # 隱藏根視窗，只顯示對話框
    return filedialog.askdirectory(title=prompt)  # 顯示資料夾選擇對話框並返回選擇結果

def collect_actress_names_with_code(base_folder, output_file):
    """
    收集所有片商目錄下的女優資料夾，並寫入CSV文件
    
    參數:
    base_folder - 基礎資料夾路徑，包含多個片商資料夾
    output_file - 輸出的CSV文件路徑
    """
    existing_entries = set()  # 用於存儲已有的條目，避免重複

    # 如果輸出文件已存在，先讀取已有的條目
    if os.path.isfile(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # 跳過標題行
            for row in reader:
                existing_entries.add(tuple(row))  # 將每行轉為元組並添加到集合中

    entries = []  # 用於存儲新的條目
    for studio_code in os.listdir(base_folder):  # 遍歷基礎資料夾下的所有項目（片商代號）
        studio_path = os.path.join(base_folder, studio_code)  # 構建片商資料夾的完整路徑
        if os.path.isdir(studio_path):  # 確認是目錄而非文件
            for actress in os.listdir(studio_path):  # 遍歷片商資料夾下的所有項目（女優名稱）
                actress_path = os.path.join(studio_path, actress)  # 構建女優資料夾的完整路徑
                if os.path.isdir(actress_path):  # 確認是目錄而非文件
                    entry = (studio_code, actress)  # 創建片商-女優對
                    if entry not in existing_entries:  # 如果這個組合不在已有條目中
                        entries.append(entry)  # 添加到新條目列表
                        existing_entries.add(entry)  # 同時添加到已有條目集合中，避免重複

    # 附加模式打開CSV文件，保留原有內容
    with open(output_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not os.path.isfile(output_file):  # 如果文件不存在，寫入標題行
            writer.writerow(['Studio Code', 'Actress Name'])
        writer.writerows(entries)  # 寫入所有新增的條目

    print(f"已完成，女優資料夾與代號已儲存至 {output_file}")  # 顯示完成信息

if __name__ == "__main__":
    # 程式入口點，當腳本被直接執行時運行
    print("請選擇片商資料夾")
    base_folder_path = select_folder("選擇片商資料夾")  # 讓使用者選擇片商資料夾
    output_file_path = 'actress_names_with_codes.csv'  # 設定輸出文件名

    collect_actress_names_with_code(base_folder_path, output_file_path)  # 收集資料並寫入CSV
    print("女優資料夾與代號已儲存至 actress_names_with_codes.csv")  # 顯示完成信息