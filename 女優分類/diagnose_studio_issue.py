#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
片商資訊 UNKNOWN 問題診斷工具
追蹤從 JAVDB 搜尋到資料庫儲存的完整流程
"""
import sys
from pathlib import Path
import logging

# 將 src 資料夾加入 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# 設定日誌
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def diagnose_studio_unknown_issue():
    """完整診斷片商資訊流程"""
    
    print("🔍 開始診斷片商資訊 UNKNOWN 問題...")
    print("=" * 60)
    
    try:
        from services.safe_javdb_searcher import SafeJAVDBSearcher
        from services.web_searcher import WebSearcher
        from models.database import SQLiteDBManager
        from models.config import ConfigManager
        
        # 使用實際的資料庫路徑
        db_path = r"C:\Users\cy540\Documents\ActressClassifier\actress_database.db"
        
        if not Path(db_path).exists():
            print(f"❌ 資料庫檔案不存在: {db_path}")
            print("💡 請先執行主程式進行影片搜尋來建立資料庫")
            return
        
        # 1. 測試 JAVDB 搜尋器
        print("\n🧪 第一步：測試 JAVDB 搜尋器")
        print("-" * 40)
        
        javdb_searcher = SafeJAVDBSearcher()
        test_codes = ["FNS-033", "EBWH-194", "MGOLD-038"]
        
        javdb_results = {}
        for code in test_codes:
            result = javdb_searcher.search_javdb(code)
            javdb_results[code] = result
            
            if result:
                print(f"✅ {code}: 找到片商 '{result.get('studio')}' (代碼: {result.get('studio_code')})")
            else:
                print(f"❌ {code}: 未找到結果")
        
        # 2. 測試整合搜尋器
        print("\n🧪 第二步：測試整合搜尋器 (WebSearcher)")
        print("-" * 40)
        
        config = ConfigManager()
        web_searcher = WebSearcher(config)
        
        import threading
        stop_event = threading.Event()
        
        web_results = {}
        for code in test_codes:
            result = web_searcher.search_info(code, stop_event)
            web_results[code] = result
            
            if result:
                print(f"✅ {code}: WebSearcher 找到片商 '{result.get('studio')}' (來源: {result.get('source')})")
            else:
                print(f"❌ {code}: WebSearcher 未找到結果")
        
        # 3. 模擬資料庫寫入流程
        print("\n🧪 第三步：模擬資料庫寫入流程")
        print("-" * 40)
        
        db_manager = SQLiteDBManager(db_path)
        
        for code in test_codes:
            if web_results.get(code):
                result = web_results[code]
                
                # 模擬完整的影片資訊
                video_info = {
                    'code': code,
                    'actresses': result.get('actresses', []),
                    'studio': result.get('studio'),
                    'studio_code': result.get('studio_code'),
                    'release_date': result.get('release_date'),
                    'original_filename': f'{code}_test.mp4',
                    'file_path': Path(f'/test/{code}'),
                    'search_method': result.get('source', 'test')
                }
                
                print(f"💾 準備寫入 {code}:")
                print(f"   片商: {video_info['studio']}")
                print(f"   片商代碼: {video_info['studio_code']}")
                print(f"   女優: {video_info['actresses']}")
                
                # 寫入資料庫
                db_manager.add_or_update_video(code, video_info)
                
                # 立即讀取驗證
                stored_info = db_manager.get_video_info(code)
                if stored_info:
                    print(f"✅ 寫入成功 - 儲存的片商: {stored_info.get('studio')}")
                else:
                    print(f"❌ 寫入失敗或讀取失敗")
        
        # 4. 檢查片商分類系統的影響
        print("\n🧪 第四步：檢查片商分類系統")
        print("-" * 40)
        
        # 檢查是否有女優資料夾分析會覆蓋片商資訊
        for code in test_codes:
            video_info = db_manager.get_video_info(code)
            if video_info:
                actresses = video_info.get('actresses', [])
                for actress in actresses:
                    # 檢查該女優的片商分析結果
                    analysis = db_manager.analyze_actress_primary_studio(actress)
                    print(f"👤 女優 {actress} 的片商分析:")
                    print(f"   主要片商: {analysis.get('primary_studio')}")
                    print(f"   信心度: {analysis.get('confidence')}%")
                    print(f"   建議: {analysis.get('recommendation')}")
        
        # 5. 檢查可能的覆蓋來源
        print("\n🧪 第五步：查找可能的資料覆蓋來源")
        print("-" * 40)
        
        # 檢查所有 UNKNOWN 的影片
        all_videos = db_manager.get_all_videos()
        unknown_count = 0
        unknown_samples = []
        
        for video in all_videos:
            if not video.get('studio') or video.get('studio') in ['UNKNOWN', 'Unknown', '']:
                unknown_count += 1
                if len(unknown_samples) < 5:
                    unknown_samples.append(video.get('code'))
        
        print(f"📊 資料庫統計:")
        print(f"   總影片數: {len(all_videos)}")
        print(f"   UNKNOWN 片商數: {unknown_count}")
        print(f"   UNKNOWN 比例: {unknown_count/len(all_videos)*100:.1f}%")
        print(f"   範例: {unknown_samples}")
        
        # 6. 建議解決方案
        print("\n💡 解決方案建議")
        print("-" * 40)
        
        if unknown_count > 0:
            print("1. 執行片商資訊更新工具:")
            print("   python update_studio_info.py")
            print()
            print("2. 檢查片商分類邏輯是否錯誤覆蓋資料")
            print("3. 確認資料庫寫入順序和邏輯")
        else:
            print("✅ 未發現 UNKNOWN 片商問題")
        
    except Exception as e:
        print(f"❌ 診斷過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_studio_unknown_issue()
