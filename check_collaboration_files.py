# -*- coding: utf-8 -*-
"""
檢查多人共演影片在資料庫中的女優記錄
"""
import sys
from pathlib import Path

# 加入專案根目錄到 Python 路徑
current_dir = Path(__file__).parent
project_root = current_dir / "女優分類"
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from models.database import SQLiteDBManager
from models.config import ConfigManager

def check_actresses_in_db():
    """檢查指定影片番號在資料庫中的女優記錄"""
    
    # 從檔案名稱提取的多人共演番號
    test_codes = [
        'HOIZ-146',
        'STCVS-020', 
        'SVSHA-030',
        'BANK-201',
        'UMD-939',
        'MIMK-203',
        'REAL-887',
        'START-276',
        'MKMP-611',
        'STCV-537',
        'MKMP-628',
        'PFES-091',
        'HJMO-651',
        'PRIN-024'
    ]
    
    config = ConfigManager()
    db_manager = SQLiteDBManager(config.get('database', 'database_path'))
    
    print("🔍 檢查多人共演影片在資料庫中的女優記錄：\n")
    
    for code in test_codes:
        info = db_manager.get_video_info(code)
        if info and info.get('actresses'):
            actresses = info['actresses']
            print(f"📼 {code}:")
            print(f"   資料庫中女優數量: {len(actresses)}")
            print(f"   女優列表: {', '.join(actresses)}")
            print()
        else:
            print(f"❌ {code}: 資料庫中無記錄")
            print()
    
    print("="*60)
    print("🤔 分析結果：")
    print("如果這些影片在資料庫中只有一位女優記錄，")
    print("但檔案名稱顯示為多人共演，可能需要：")
    print("1. 重新搜尋這些番號的完整資訊")
    print("2. 或者修改判斷邏輯，同時檢查檔案名稱中的女優標記")

if __name__ == "__main__":
    try:
        check_actresses_in_db()
    except Exception as e:
        print(f"❌ 檢查過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
