# -*- coding: utf-8 -*-
"""
測試資料庫方法是否正確運作
"""

import sys
from pathlib import Path

# 添加 src 路徑
sys.path.insert(0, str(Path(__file__).parent / '女優分類' / 'src'))

from models.config import ConfigManager
from models.database import SQLiteDBManager

def test_database_methods():
    """測試資料庫方法"""
    print("🧪 開始測試資料庫方法...")
    
    # 初始化配置
    config = ConfigManager()
    
    # 初始化資料庫管理器
    db_manager = SQLiteDBManager('test_database.db')
    
    # 測試 add_or_update_video 方法
    test_info = {
        'actresses': ['測試女優'],
        'original_filename': 'TEST-001.mp4',
        'file_path': '/test/path/TEST-001.mp4',
        'studio': '測試片商',
        'studio_code': 'TEST',
        'release_date': '2025-06-22',
        'search_method': '測試方法'
    }
    
    try:
        db_manager.add_or_update_video('TEST-001', test_info)
        print("✅ add_or_update_video 方法運作正常")
        
        # 測試是否能檢索資料
        retrieved_info = db_manager.get_video_info('TEST-001')
        if retrieved_info:
            print(f"✅ 成功檢索資料: {retrieved_info['code']}")
            print(f"   女優: {retrieved_info['actresses']}")
            print(f"   片商: {retrieved_info['studio']}")
        else:
            print("❌ 無法檢索資料")
            
    except AttributeError as e:
        if 'add_video' in str(e):
            print(f"❌ 發現 add_video 錯誤: {e}")
            print("需要檢查程式碼中是否還有對 add_video 的呼叫")
        else:
            print(f"❌ 其他屬性錯誤: {e}")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
    
    print("🧪 測試完成")

if __name__ == "__main__":
    test_database_methods()
