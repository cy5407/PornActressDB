# -*- coding: utf-8 -*-
"""
重現原始錯誤的測試腳本
"""

import sys
from pathlib import Path

# 添加 src 路徑
sys.path.insert(0, str(Path(__file__).parent / '女優分類' / 'src'))

from models.config import ConfigManager
from services.classifier_core import UnifiedClassifierCore
from models.config import PreferenceManager
import threading
import tempfile
import os

def test_search_functionality():
    """測試搜尋功能"""
    print("🧪 開始測試搜尋功能...")
    
    # 建立暫時測試資料夾
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 建立一些測試檔案
        test_files = [
            'SONE-467.mp4',
            'SONE-240.mp4',
            'SIVR-370.mp4'
        ]
        
        for filename in test_files:
            test_file = temp_path / filename
            test_file.write_text("test content")
        
        print(f"📁 建立測試資料夾: {temp_path}")
        print(f"📄 建立測試檔案: {test_files}")
        
        # 初始化系統
        config = ConfigManager()
        core = UnifiedClassifierCore(config)
        
        # 設定偏好管理器
        preference_manager = PreferenceManager()
        core.set_preference_manager(preference_manager)
        
        # 測試日文網站搜尋
        stop_event = threading.Event()
        
        def progress_callback(message):
            print(f"📝 {message.strip()}")
        
        try:
            print("\n🇯🇵 測試日文網站搜尋...")
            result = core.process_and_search_japanese_sites(
                str(temp_path), 
                stop_event, 
                progress_callback
            )
            print(f"✅ 日文網站搜尋結果: {result['status']}")
            
        except AttributeError as e:
            if 'add_video' in str(e):
                print(f"❌ 發現 add_video 錯誤: {e}")
                return False
            else:
                print(f"❌ 其他錯誤: {e}")
                return False
        except Exception as e:
            print(f"❌ 測試失敗: {e}")
            return False
        
        try:
            print("\n📊 測試 JAVDB 搜尋...")
            result = core.process_and_search_javdb(
                str(temp_path), 
                stop_event, 
                progress_callback
            )
            print(f"✅ JAVDB 搜尋結果: {result['status']}")
            
        except AttributeError as e:
            if 'add_video' in str(e):
                print(f"❌ 發現 add_video 錯誤: {e}")
                return False
            else:
                print(f"❌ 其他錯誤: {e}")
                return False
        except Exception as e:
            print(f"❌ 測試失敗: {e}")
            return False
    
    print("🧪 所有測試完成，沒有 add_video 錯誤")
    return True

if __name__ == "__main__":
    test_search_functionality()
