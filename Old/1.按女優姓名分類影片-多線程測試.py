import os  # 提供操作系統功能，用於文件和目錄操作
import re  # 提供正則表達式功能，用於字符串匹配和替換
import threading  # 提供多線程功能，加速處理過程
from concurrent.futures import ThreadPoolExecutor  # 更現代的線程池管理
from tkinter import filedialog  # 提供文件選擇對話框
from urllib.parse import quote  # 提供URL編碼功能，轉換特殊字符
import time  # 提供時間相關功能，用於重試機制
import functools  # 提供函數工具，用於緩存裝飾器

import requests  # 提供HTTP請求功能，用於訪問網頁
from bs4 import BeautifulSoup  # 提供HTML解析功能，用於提取網頁信息
import csv  # 提供CSV檔案處理功能
import configparser  # 提供配置文件讀寫功能
import argparse  # 提供命令行參數解析功能

# 設定參數
MAX_WORKERS = 10  # 線程池最大工作線程數
MAX_RETRIES = 3  # 最大重試次數
RETRY_DELAY = 2  # 重試延遲時間（秒）
REQUEST_TIMEOUT = 10  # 請求超時時間（秒）

# 建立一個線程鎖，確保多線程操作共享數據時的安全性
thread_lock = threading.Lock()

# 用於存儲已處理的演員和對應的文件名
actress_data = {}

# 建立請求快取，避免重複請求相同的檔名
request_cache = {}


# 使用 functools.lru_cache 裝飾器實現記憶體快取
@functools.lru_cache(maxsize=1000)
def clean_filename(filename):
    """去除檔名中的後綴、副檔名和字幕組標記，並使用快取優化效能"""
    base_name, _ = os.path.splitext(filename)  # 分離檔名和副檔名
    # 移除字幕組標記 (移除 @ 及其之前的所有內容)
    base_name = re.sub(r'^.*?@', '', base_name)
    # 移除已定義的後綴，如CH、-c等標識符
    return re.sub(r'(CH|-c|-C|-ch|-CH|\[H265\]|\[HEVC\]|\[1080p\]|\[720p\]|\[4K\]|\[HDR\])', '', base_name)


def retry_on_error(max_retries=MAX_RETRIES, delay=RETRY_DELAY):
    """重試裝飾器，處理網路請求失敗的情況"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:  # 如果不是最後一次嘗試，則等待後重試
                        time.sleep(delay)
            # 所有重試都失敗後，印出最後一個異常
            print(f"在 {max_retries} 次嘗試後仍然失敗: {last_exception}")
            return []  # 返回空列表表示沒有找到演員
        return wrapper
    return decorator


@retry_on_error()
def get_actress_names(search_url, filename):
    """搜尋檔名並擷取演員姓名，增加重試機制和快取
    
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

    # 檢查快取
    if filename in request_cache:
        return request_cache[filename]

    try:
        encoded_filename = quote(filename)  # URL編碼檔名，處理特殊字元
        search_url = f"{search_url}{encoded_filename}"  # 構建完整的搜尋URL
        
        # 使用 Session 而不是單獨的 requests.get() 可以重用連接
        session = requests.Session()
        response = session.get(search_url, timeout=REQUEST_TIMEOUT)  # 發送HTTP請求，設置超時時間
        response.raise_for_status()  # 如果請求不成功則拋出異常

        soup = BeautifulSoup(response.content, "html.parser")  # 解析HTML內容
        actress_elements = soup.find_all(class_="actress-name")  # 找出所有演員名稱元素
        result = [actress.text.strip() for actress in actress_elements if actress.text.strip()]  # 返回所有有效的演員名稱
        
        # 存入快取
        request_cache[filename] = result
        return result

    except Exception as e:
        print(f"搜尋 {filename} 時發生錯誤 ({type(e).__name__}): {e}")  # 印出錯誤信息
        raise  # 重新拋出異常以供重試裝飾器捕獲


def process_file(filename, folder_path, search_url):
    """處理單個檔案
    
    參數:
    filename - 要處理的檔案名稱
    folder_path - 檔案所在的資料夾路徑
    search_url - 搜尋網站的基本URL
    
    返回:
    布爾值，表示處理是否成功
    """
    global actress_data  # 使用全局變數存儲演員數據

    # 檢查檔案是否為視頻檔案
    if not filename.endswith((".mp4", ".mkv", ".avi", ".mov")):
        return False  # 如果不是視頻檔案，則跳過

    # 檢查原始檔案是否仍然存在（可能已被其他線程處理）
    src_path = os.path.join(folder_path, filename)
    if not os.path.exists(src_path):
        return False

    clean_name = clean_filename(filename)  # 清理檔名
    actress_names = get_actress_names(search_url, clean_name)  # 獲取演員名稱

    if not actress_names:
        return False  # 如果沒有找到演員，則返回

    with thread_lock:  # 使用線程鎖確保數據安全
        for actress_name in actress_names:
            if actress_name in actress_data:
                actress_data[actress_name].append(filename)  # 如果演員已存在，添加檔名到列表
            else:
                actress_data[actress_name] = [filename]  # 如果演員不存在，創建新列表

            # 建立資料夾並移動檔案
            actress_folder = os.path.join(folder_path, actress_name)  # 構建演員資料夾路徑
            os.makedirs(actress_folder, exist_ok=True)  # 創建資料夾，如果已存在則不報錯
            
            dst_path = os.path.join(actress_folder, filename)  # 目標檔案路徑
            
            if os.path.exists(dst_path):
                print(f"檔案已存在，跳過移動: {dst_path}")  # 如果目標檔案已存在，則跳過
            else:
                try:
                    os.rename(src_path, dst_path)  # 移動檔案
                except FileNotFoundError:
                    print(f"檔案 {src_path} 不存在，可能已被其他線程處理")
                    return False
                except PermissionError:
                    print(f"無法移動檔案 {src_path}，權限被拒絕")
                    return False
            break  # 只移動到第一個找到的演員的資料夾，以避免將同一個檔案移動到多個演員的資料夾

    return True


def save_to_csv(csv_filename, actress_data):
    """將 actress_data 保存到 CSV 文件
    
    參數:
    csv_filename - CSV檔案名稱
    actress_data - 要保存的演員數據字典
    """
    if not actress_data:
        print("沒有資料可保存到 CSV 文件。")
        return

    max_files = max([len(files) for files in actress_data.values()], default=0)  # 找出擁有最多文件的演員，使用 default 預防空列表

    # 決定是否需要寫入標題行
    write_header = not os.path.exists(csv_filename)

    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:  # 使用utf-8-sig編碼以支持中文，使用 'w' 模式而非 'a' 模式
        writer = csv.writer(csvfile)  # 創建CSV寫入器
        
        # 如果文件不存在，寫入標題行
        if write_header:
            header = ['女優名字'] + [f'檔案 {i+1}' for i in range(max_files)]  # 創建標題行
            writer.writerow(header)

        # 按演員名稱排序，使結果更有條理
        for actress, file_list in sorted(actress_data.items()):
            row = [actress] + file_list + [''] * (max_files - len(file_list))  # 填充空單元格確保每行長度一致
            writer.writerow(row)  # 寫入一行數據


def batch_process_files(folder_path, search_url, max_workers=MAX_WORKERS):
    """使用線程池批量處理檔案
    
    參數:
    folder_path - 檔案所在的資料夾路徑
    search_url - 搜尋網站的基本URL
    max_workers - 最大工作線程數
    """
    # 獲取所有視頻檔案
    video_files = [
        f for f in os.listdir(folder_path) 
        if os.path.isfile(os.path.join(folder_path, f)) and 
        f.endswith((".mp4", ".mkv", ".avi", ".mov"))
    ]
    
    if not video_files:
        print(f"在 {folder_path} 中未找到視頻檔案")
        return

    print(f"找到 {len(video_files)} 個視頻檔案，開始處理...")

    # 使用線程池處理檔案
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 創建一個任務列表，每個任務處理一個檔案
        tasks = [
            executor.submit(process_file, filename, folder_path, search_url)
            for filename in video_files
        ]
        
        # 顯示進度
        total = len(tasks)
        completed = 0
        
        for future in tasks:
            future.result()  # 等待任務完成
            completed += 1
            if completed % 5 == 0 or completed == total:  # 每處理5個檔案或完成所有檔案時顯示進度
                print(f"進度: {completed}/{total} ({completed*100/total:.1f}%)")


def main():
    """主函數，程式入口點"""
    global actress_data  # 使用全局變數存儲演員數據

    parser = argparse.ArgumentParser(description="處理視頻檔案並將演員數據保存到CSV。")  # 創建命令行參數解析器
    parser.add_argument('--config', type=str, help='配置文件路徑', default='config.ini')  # 添加配置文件參數
    parser.add_argument('--dir', type=str, help='要處理的資料夾路徑（可選，如不提供則會彈出選擇對話框）')  # 添加資料夾路徑參數
    parser.add_argument('--workers', type=int, help='最大工作線程數', default=MAX_WORKERS)  # 添加最大工作線程數參數
    args = parser.parse_args()  # 解析命令行參數

    # 讀取配置
    config = configparser.ConfigParser()  # 創建配置解析器
    
    # 如果配置文件存在則讀取
    if os.path.exists(args.config):
        config.read(args.config)
    else:
        # 創建預設配置文件
        config['Settings'] = {
            'search_url': 'https://av-wiki.net/search/', 
            'csv_filename': 'actress_files.csv',
            'max_workers': str(MAX_WORKERS),
            'max_retries': str(MAX_RETRIES),
            'retry_delay': str(RETRY_DELAY),
            'request_timeout': str(REQUEST_TIMEOUT)
        }
        with open(args.config, 'w') as configfile:
            config.write(configfile)

    # 確定資料夾路徑
    folder_path = args.dir if args.dir else filedialog.askdirectory(title="選擇資料夾")
    if not folder_path:
        print("未選擇資料夾，程式結束。")
        return

    # 從配置讀取設置
    search_url = config.get('Settings', 'search_url', fallback="https://av-wiki.net/search/")
    csv_filename = config.get('Settings', 'csv_filename', fallback=os.path.join(folder_path, "actress_files.csv"))
    
    # 如果 csv_filename 不是絕對路徑，則將其轉換為相對於 folder_path 的路徑
    if not os.path.isabs(csv_filename):
        csv_filename = os.path.join(folder_path, csv_filename)
    
    # 使用命令行參數覆蓋配置文件中的設置
    max_workers = args.workers

    # 開始處理
    start_time = time.time()  # 記錄開始時間
    
    try:
        batch_process_files(folder_path, search_url, max_workers)
        
        # 保存結果到 CSV 文件
        save_to_csv(csv_filename, actress_data)
        
        # 計算並顯示處理時間
        elapsed_time = time.time() - start_time
        minutes, seconds = divmod(elapsed_time, 60)
        
        # 顯示統計信息
        total_actresses = len(actress_data)
        total_files = sum(len(files) for files in actress_data.values())
        
        print(f"\n處理完成！")
        print(f"處理時間: {int(minutes)}分 {seconds:.1f}秒")
        print(f"處理了 {total_files} 個檔案，找到 {total_actresses} 位演員")
        print(f"已將結果儲存至 {csv_filename}")
        
    except KeyboardInterrupt:
        print("\n程式被使用者中斷")
        # 即使中斷，也嘗試保存已處理的數據
        if actress_data:
            save_to_csv(csv_filename, actress_data)
            print(f"已將部分結果儲存至 {csv_filename}")
    except Exception as e:
        print(f"處理過程中發生錯誤: {e}")
        # 嘗試保存已處理的數據
        if actress_data:
            save_to_csv(csv_filename, actress_data)
            print(f"已將部分結果儲存至 {csv_filename}")


if __name__ == "__main__":
    main()  # 如果是直接執行此腳本，則調用主函數