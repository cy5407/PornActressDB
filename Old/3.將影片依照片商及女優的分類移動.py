import os  # 提供操作系統功能，用於文件和目錄操作
import shutil  # 提供高階文件操作功能，如複製和移動整個目錄
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

def read_csv_file(csv_file):
    """
    讀取CSV文件，建立女優名稱到片商代號的映射
    
    參數:
    csv_file - CSV文件路徑
    
    返回:
    包含女優名稱到片商代號映射的字典
    """
    folder_map = {}  # 用於存儲女優名稱到片商代號的映射
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 跳過標題行
        for row in reader:
            company, actress = row  # 解析CSV行，提取片商代號和女優名稱
            folder_map[actress] = company  # 建立映射關係
    return folder_map

def move_actress_folders(source_folder, target_base_folder, folder_map):
    """
    根據映射表移動女優資料夾到對應的片商資料夾
    
    參數:
    source_folder - 包含女優資料夾的源目錄
    target_base_folder - 目標基礎目錄，將在其下建立片商資料夾
    folder_map - 女優名稱到片商代號的映射字典
    """
    for actress_folder in os.listdir(source_folder):  # 遍歷源目錄下的所有項目
        actress_path = os.path.join(source_folder, actress_folder)  # 構建女優資料夾的完整路徑
        if os.path.isdir(actress_path) and actress_folder in folder_map:  # 確認是目錄且在映射表中有對應的片商
            company = folder_map[actress_folder]  # 獲取對應的片商代號
            target_folder = os.path.join(target_base_folder, company)  # 構建目標片商資料夾的完整路徑
            os.makedirs(target_folder, exist_ok=True)  # 確保目標片商資料夾存在，如果不存在則創建
            target_path = os.path.join(target_folder, actress_folder)  # 構建目標女優資料夾的完整路徑
            if os.path.exists(target_path):  # 如果目標路徑已存在，先刪除它
                shutil.rmtree(target_path)
            shutil.move(actress_path, target_folder)  # 移動女優資料夾到對應的片商資料夾
            print(f"已移動 {actress_folder} 至 {target_folder}")  # 顯示移動信息

if __name__ == "__main__":
    # 程式入口點，當腳本被直接執行時運行
    output_file_path = 'actress_names_with_codes.csv'  # 映射表文件路徑
    folder_map = read_csv_file(output_file_path)  # 讀取映射表

    print("請選擇資料夾，裡面有以女優姓名作為資料夾名的資料夾")
    source_folder = select_folder("選擇女優資料夾來源")  # 讓使用者選擇源目錄
    print("請選擇目標資料夾，將女優資料夾放入對應的片商資料夾中")
    target_base_folder = select_folder("選擇目標資料夾")  # 讓使用者選擇目標基礎目錄

    move_actress_folders(source_folder, target_base_folder, folder_map)  # 根據映射表移動資料夾
    print("所有資料夾已完成移動！")  # 顯示完成信息