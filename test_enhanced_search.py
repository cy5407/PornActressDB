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
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

try:
    from models.config import ConfigManager
    from models.database import SQLiteDBManager
    from services.web_searcher import WebSearcher
except ImportError as e:
    print(f"❌ 導入模組失敗: {e}")
    print("💡 請確認您在正確的專案目錄中執行此程式")
    print(f"📁 當前目錄: {Path.cwd()}")
    print(f"📁 專案根目錄: {project_root}")
    print(f"📁 src 目錄: {src_path}")
    sys.exit(1)


def demonstrate_enhanced_search():
    """展示增強版搜尋功能"""
    print("🔍 女優分類系統 - 搜尋功能展示")
    print("=" * 50)
    
    try:
        # 初始化配置與元件
        print("📋 正在初始化系統元件...")
        config = ConfigManager('config.ini')
        
        # 使用測試資料庫路徑
        test_db_path = Path('data') / 'test_database.db'
        test_db_path.parent.mkdir(exist_ok=True)
        
        db_manager = SQLiteDBManager(str(test_db_path))
        web_searcher = WebSearcher(config)
        print("✅ 系統元件初始化完成")
        
    except Exception as e:
        print(f"❌ 系統初始化失敗: {e}")
        print("💡 請檢查 config.ini 檔案是否正確設定")
        return
    
    # 測試番號列表（範例）
    test_codes = [
        "SSIS-123",  # S1 片商
        "MIDV-456",  # MOODYZ 片商
    ]
    
    stop_event = threading.Event()
    
    print("\n📝 測試搜尋與資料庫寫入功能：")
    print("-" * 30)
    print("⚠️  注意：此為線上搜尋測試，需要網路連線")
    
    # 詢問是否繼續
    try:
        user_input = input("\n是否繼續執行線上搜尋測試？(y/N): ").strip().lower()
        if user_input not in ['y', 'yes']:
            print("⏹️  跳過線上搜尋測試")
            # 改為展示離線功能
            demonstrate_offline_features(db_manager)
            return
    except KeyboardInterrupt:
        print("\n⏹️  使用者中斷")
        return
    
    for code in test_codes:
        print(f"\n🔍 搜尋番號：{code}")
        
        try:
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
                print(f"  ❌ 搜尋失敗或無資料")
                
        except Exception as e:
            print(f"  ❌ 搜尋過程發生錯誤：{e}")
    
    # 展示資料庫統計
    demonstrate_database_stats(db_manager)


def demonstrate_offline_features(db_manager):
    """展示離線功能"""
    print("\n📊 展示離線資料庫功能：")
    print("-" * 30)
    
    # 新增一些測試資料
    test_data = [
        {
            'code': 'SSIS-999',
            'info': {
                'original_filename': 'SSIS-999.mp4',
                'file_path': '/test/SSIS-999.mp4',
                'actresses': ['測試女優A'],
                'studio': 'S1',
                'studio_code': 'SSIS',
                'release_date': '2024-01-01',
                'search_method': 'Manual Test'
            }
        },
        {
            'code': 'MIDV-888',
            'info': {
                'original_filename': 'MIDV-888.mp4',
                'file_path': '/test/MIDV-888.mp4',
                'actresses': ['測試女優B', '測試女優C'],
                'studio': 'MOODYZ',
                'studio_code': 'MIDV',
                'release_date': '2024-02-01',
                'search_method': 'Manual Test'
            }
        }
    ]
    
    print("📝 新增測試資料...")
    for test_item in test_data:
        try:
            db_manager.add_or_update_video(test_item['code'], test_item['info'])
            print(f"  ✅ 已新增：{test_item['code']}")
        except Exception as e:
            print(f"  ❌ 新增失敗：{e}")
    
    # 展示統計功能
    demonstrate_database_stats(db_manager)


def demonstrate_database_stats(db_manager):
    """展示資料庫統計功能"""
    print("\n📊 資料庫統計資訊：")
    print("-" * 30)
    
    try:
        # 女優統計
        actress_stats = db_manager.get_actress_statistics()
        print(f"📝 女優總數：{len(actress_stats)}")
        for stat in actress_stats[:5]:  # 只顯示前5筆
            print(f"  👩 {stat['actress_name']}：{stat['video_count']} 部影片")
            if stat['studios']:
                studios = [s for s in stat['studios'] if s]  # 過濾空值
                if studios:
                    print(f"     🏢 片商：{', '.join(studios)}")
        
        # 片商統計
        studio_stats = db_manager.get_studio_statistics()
        print(f"\n🏢 片商總數：{len(studio_stats)}")
        for stat in studio_stats[:5]:  # 只顯示前5筆
            studio_display = f"{stat['studio']}"
            if stat['studio_code']:
                studio_display += f" ({stat['studio_code']})"
            print(f"  🏢 {studio_display}：{stat['video_count']} 部影片，{stat['actress_count']} 位女優")
            
    except Exception as e:
        print(f"❌ 統計資訊取得失敗：{e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ 展示完成！")
    print("💡 提示：這展示了優化後的搜尋功能如何同步處理女優與片商資訊。")


if __name__ == "__main__":
    try:
        demonstrate_enhanced_search()
    except KeyboardInterrupt:
        print("\n⏹️  使用者中斷展示")
    except Exception as e:
        print(f"\n❌ 展示過程發生錯誤：{e}")
        import traceback
        traceback.print_exc()
