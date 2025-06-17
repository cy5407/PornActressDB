#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜尋功能測試範例 - 展示片商資訊同步搜尋功能

此範例展示優化後的搜尋功能如何：
1. 搜尋女優資訊
2. 同步提取片商資訊
3. 將完整資訊寫入資料庫
"""

import sys
import threading
from pathlib import Path

# 新增專案根目錄到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models.config import ConfigManager
from src.models.database import SQLiteDBManager
from src.services.web_searcher import WebSearcher


def demonstrate_enhanced_search():
    """展示增強版搜尋功能"""
    print("🔍 女優分類系統 - 搜尋功能展示")
    print("=" * 50)
    
    # 初始化配置與元件
    config = ConfigManager('config.ini')
    db_manager = SQLiteDBManager('data/test_database.db')
    web_searcher = WebSearcher(config)
    
    # 測試番號列表（範例）
    test_codes = [
        "SSIS-123",  # S1 片商
        "MIDV-456",  # MOODYZ 片商
        "IPX-789",   # IdeaPocket 片商
    ]
    
    stop_event = threading.Event()
    
    print("\n📝 測試搜尋與資料庫寫入功能：")
    print("-" * 30)
    
    for code in test_codes:
        print(f"\n🔍 搜尋番號：{code}")
        
        # 執行搜尋
        result = web_searcher.search_info(code, stop_event)
        
        if result:
            print(f"  ✅ 搜尋成功！")
            print(f"  👩 女優：{', '.join(result.get('actresses', []))}")
            print(f"  🏢 片商：{result.get('studio', '未知')}")
            print(f"  🏷️  片商代碼：{result.get('studio_code', '未知')}")
            print(f"  📅 發行日期：{result.get('release_date', '未知')}")
            
            # 準備資料庫寫入資料
            video_info = {
                'original_filename': f"{code}.mp4",
                'file_path': f"/test/videos/{code}.mp4",
                'actresses': result.get('actresses', []),
                'studio': result.get('studio'),
                'studio_code': result.get('studio_code'),
                'release_date': result.get('release_date'),
                'search_method': result.get('source', 'Unknown')
            }
            
            # 寫入資料庫
            try:
                db_manager.add_or_update_video(code, video_info)
                print(f"  💾 已寫入資料庫")
            except Exception as e:
                print(f"  ❌ 資料庫寫入失敗：{e}")
                
        else:
            print(f"  ❌ 搜尋失敗")
    
    # 展示資料庫統計
    print("\n📊 資料庫統計資訊：")
    print("-" * 30)
    
    try:
        # 女優統計
        actress_stats = db_manager.get_actress_statistics()
        print(f"📝 女優總數：{len(actress_stats)}")
        for stat in actress_stats[:3]:  # 只顯示前3筆
            print(f"  👩 {stat['actress_name']}：{stat['video_count']} 部影片")
            if stat['studios']:
                print(f"     🏢 片商：{', '.join(stat['studios'])}")
        
        # 片商統計
        studio_stats = db_manager.get_studio_statistics()
        print(f"\n🏢 片商總數：{len(studio_stats)}")
        for stat in studio_stats[:3]:  # 只顯示前3筆
            print(f"  🏢 {stat['studio']} ({stat['studio_code']})：{stat['video_count']} 部影片，{stat['actress_count']} 位女優")
            
    except Exception as e:
        print(f"❌ 統計資訊取得失敗：{e}")
    
    print("\n✅ 展示完成！")
    print("💡 提示：這是測試展示，實際使用時請確保網路連線正常。")


if __name__ == "__main__":
    try:
        demonstrate_enhanced_search()
    except KeyboardInterrupt:
        print("\n⏹️  使用者中斷展示")
    except Exception as e:
        print(f"\n❌ 展示過程發生錯誤：{e}")
        import traceback
        traceback.print_exc()
