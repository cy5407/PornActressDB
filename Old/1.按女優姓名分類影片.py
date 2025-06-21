import os  # 提供操作系統功能，用於文件和目錄操作
import re  # 提供正則表達式功能，用於字符串匹配和替換
import threading  # 提供多線程功能，加速處理過程
from tkinter import filedialog  # 提供文件選擇對話框
from urllib.parse import quote  # 提供URL編碼功能，轉換特殊字符

import requests  #提供HTTP請求功能，用於訪問網頁
from bs4 import BeautifulSoup #提供HTML解析功能，用於提取網頁信息
import csv  # 提供CSV檔案處理功能
import configparser  # 提供配置文件讀寫功能
import argparse  # 提供命令行參數解析功能

# 設定最大線程數量，避免過多線程導致系統負載過大
MAX_THREADS = 10
# 建立一個線程信號量，控制並發線程數量
semaphore = threading.Semaphore(MAX_THREADS)

# 建立一個線程鎖，確保多線程操作共享數據時的安全性
thread_lock = threading.Lock()

# 用於存儲已處理的演員和對應的文件名
actress_data = {}


def clean_filename(filename):
    """去除檔名中的後綴、副檔名和字幕組標記"""
    base_name, _ = os.path.splitext(filename)  # 分離檔名和副檔名
    # 移除字幕組標記 (移除 @ 及其之前的所有內容)
    base_name = re.sub(r'^.*?@', '', base_name)
    # 移除已定義的後綴，如CH、-c等標識符
    return re.sub(r'(CH|-c|-C|-ch|-CH|\[H265\]|\[HEVC\]|\[1080p\]|\[720p\]|\[4K\]|\[HDR\])', '', base_name)

def get_actress_names(search_url, filename):
    """搜尋檔名並擷取演員姓名
    
    參數:
    search_url - 搜尋網站的基本URL
    filename - 要搜尋的檔案名稱
    
    返回:
    包含演員姓名的列表
    """

    # 檢查檔名是否以 FC2、FC2PPV 或 FC2-PPV 開頭，這些是某些特定格式的視頻
    if filename.startswith(("FC2", "FC2PPV", "FC2-PPV")):
        print(f"跳過檔案：{filename} (以 FC2 開頭)")  # 可選擇性地印出跳過的檔案
        return []  # 如果跳過，直接返回一個空列表

    try:
        encoded_filename = quote(filename)  # URL編碼檔名，處理特殊字元
        search_url = f"{search_url}{encoded_filename}"  # 構建完整的搜尋URL
        response = requests.get(search_url, timeout=10)  # 發送HTTP請求，設置超時時間
        response.raise_for_status()  # 如果請求不成功則拋出異常

        soup = BeautifulSoup(response.content, "html.parser")  # 解析HTML內容
        actress_elements = soup.find_all(class_="actress-name")  # 找出所有演員名稱元素
        return [actress.text.strip() for actress in actress_elements if actress.text.strip()]  # 返回所有有效的演員名稱

    except Exception as e:
        print(f"搜尋 {filename} 時發生錯誤 ({type(e).__name__}): {e}")  # 印出錯誤信息
        return []  # 發生錯誤時返回空列表

def process_file(filename, folder_path, search_url):
    """處理單個檔案
    
    參數:
    filename - 要處理的檔案名稱
    folder_path - 檔案所在的資料夾路徑
    search_url - 搜尋網站的基本URL
    """
    global actress_data  # 使用全局變數存儲演員數據

    clean_name = clean_filename(filename)  # 清理檔名
    actress_names = get_actress_names(search_url, clean_name)  # 獲取演員名稱

    with thread_lock:  # 使用線程鎖確保數據安全
        for actress_name in actress_names:
            if actress_name in actress_data:
                actress_data[actress_name].append(filename)  # 如果演員已存在，添加檔名到列表
            else:
                actress_data[actress_name] = [filename]  # 如果演員不存在，創建新列表

            # 建立資料夾並移動檔案
            actress_folder = os.path.join(folder_path, actress_name)  # 構建演員資料夾路徑
            os.makedirs(actress_folder, exist_ok=True)  # 創建資料夾，如果已存在則不報錯
            src_path = os.path.join(folder_path, filename)  # 原檔案路徑
            dst_path = os.path.join(actress_folder, filename)  # 目標檔案路徑
            if os.path.exists(dst_path):
                print(f"檔案已存在，跳過移動: {dst_path}")  # 如果目標檔案已存在，則跳過
            else:
                os.rename(src_path, dst_path)  # 移動檔案
            break  # 只移動到第一個找到的演員的資料夾，以避免將同一個檔案移動到多個演員的資料夾


def save_to_csv(csv_filename, actress_data):
    """將 actress_data 保存到 CSV 文件
    
    參數:
    csv_filename - CSV檔案名稱
    actress_data - 要保存的演員數據字典
    """
    if not actress_data:
        print("沒有資料可保存到 CSV 文件。")
        return

    max_files = max([len(files) for files in actress_data.values()])  # 找出擁有最多文件的演員

    with open(csv_filename, 'a', newline='', encoding='utf-8-sig') as csvfile:  # 使用utf-8-sig編碼以支持中文
        writer = csv.writer(csvfile)  # 創建CSV寫入器
        # 如果文件不存在，寫入標題行
        if not os.path.isfile(csv_filename):
            header = ['女優名字'] + [f'檔案 {i+1}' for i in range(max_files)]  # 創建標題行
            writer.writerow(header)

        for actress, file_list in actress_data.items():
            row = [actress] + file_list + [''] * (max_files - len(file_list))  # 填充空單元格確保每行長度一致
            writer.writerow(row)  # 寫入一行數據


def process_file_wrapper(filename, folder_path, search_url, semaphore):
    """處理單個檔案的包裝函數，處理完釋放信號量
    
    參數:
    filename - 要處理的檔案名稱
    folder_path - 檔案所在的資料夾路徑
    search_url - 搜尋網站的基本URL
    semaphore - 線程信號量，用於控制並發
    """
    try:
        process_file(filename, folder_path, search_url)  # 處理檔案
    finally:
        semaphore.release()  # 釋放信號量，無論處理成功或失敗


def main():
    """主函數，程式入口點"""
    global actress_data  # 使用全局變數存儲演員數據

    parser = argparse.ArgumentParser(description="處理視頻檔案並將演員數據保存到CSV。")  # 創建命令行參數解析器
    parser.add_argument('--config', type=str, help='配置文件路徑', default='config.ini')  # 添加配置文件參數
    args = parser.parse_args()  # 解析命令行參數

    config = configparser.ConfigParser()  # 創建配置解析器
    config.read(args.config)  # 讀取配置文件

    folder_path = filedialog.askdirectory(title="選擇資料夾")  # 彈出對話框讓用戶選擇資料夾
    if not folder_path:
        print("未選擇資料夾，程式結束。")
        return

    search_url = config.get('Settings', 'search_url', fallback="https://av-wiki.net/search/")  # 從配置讀取搜尋URL，如果沒有則使用默認值
    csv_filename = config.get('Settings', 'csv_filename', fallback=os.path.join(folder_path, "actress_files.csv"))  # 從配置讀取CSV檔名

    threads = []  # 存儲所有線程
    for filename in os.listdir(folder_path):  # 遍歷資料夾中的所有檔案
        if filename.endswith((".mp4", ".mkv", ".avi", ".mov")):  # 只處理視頻檔案
            semaphore.acquire()  # 獲取信號量，如果達到最大線程數則等待
            thread = threading.Thread(target=process_file_wrapper, args=(filename, folder_path, search_url, semaphore))  # 創建處理線程
            threads.append(thread)  # 添加到線程列表
            thread.start()  # 啟動線程

    for thread in threads:
        thread.join()  # 等待所有線程完成

    # 保存結果到 CSV 文件
    save_to_csv(csv_filename, actress_data)  # 將處理結果保存到CSV

    print(f"已將結果儲存至 {csv_filename}")  # 顯示完成信息

    # 創建預設配置文件（如果不存在）
    if not os.path.exists('config.ini'):
        config = configparser.ConfigParser()  # 創建配置解析器
        config['Settings'] = {'search_url': 'https://av-wiki.net/search/', 'csv_filename': 'actress_files.csv'}  # 設置默認配置
        with open('config.ini', 'w') as configfile:
            config.write(configfile)  # 寫入配置文件


if __name__ == "__main__":
    main()  # 如果是直接執行此腳本，則調用主函數