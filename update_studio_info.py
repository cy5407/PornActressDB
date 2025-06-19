#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新資料庫中的片商資訊
"""
import sys
import re
from pathlib import Path

# 將 src 資料夾加入 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from models.database import SQLiteDBManager
from models.studio import StudioIdentifier

def extract_studio_code_from_code(code):
    """從番號提取片商代碼"""
    if not code:
        return None
    
    # 提取前綴字母部分
    match = re.match(r'^([A-Z]+)', code.upper())
    if match:
        return match.group(1)
    return None

def update_unknown_studios():
    """更新資料庫中片商為 UNKNOWN 的記錄"""
    
    try:
        # 直接使用指定的資料庫路徑
        db_path = r"C:\Users\cy540\Documents\ActressClassifier\actress_database.db"
        
        print(f"📂 使用資料庫路徑: {db_path}")
        
        # 檢查資料庫檔案是否存在
        if not Path(db_path).exists():
            print(f"❌ 資料庫檔案不存在: {db_path}")
            print("💡 請先執行影片搜尋功能來建立資料庫")
            return
        
        # 初始化資料庫和片商識別器
        db_manager = SQLiteDBManager(db_path)
        studio_identifier = StudioIdentifier()
        
        print("🔍 開始查找需要更新的影片...")
        
        # 獲取所有影片
        all_videos = db_manager.get_all_videos()
        
        if not all_videos:
            print("❌ 資料庫中沒有找到任何影片記錄")
            return
        
        print(f"📊 資料庫中共有 {len(all_videos)} 部影片")
        
        # 找出需要更新的影片
        needs_update = []
        for video in all_videos:
            if not video.get('studio') or video.get('studio') in ['UNKNOWN', 'Unknown', '']:
                needs_update.append(video)
        
        print(f"🎯 找到 {len(needs_update)} 部需要更新片商資訊的影片")
        
        if not needs_update:
            print("✅ 所有影片都已有片商資訊，無需更新")
            return
        
        # 開始更新
        updated_count = 0
        identified_count = 0
        
        for i, video in enumerate(needs_update, 1):
            code = video.get('code')
            if not code:
                continue
                
            # 識別片商
            studio = studio_identifier.identify_studio(code)
            studio_code = extract_studio_code_from_code(code)
            
            if studio and studio != 'UNKNOWN':
                # 更新資料庫
                try:
                    with db_manager._get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE videos 
                            SET studio = ?, studio_code = ?, last_updated = CURRENT_TIMESTAMP 
                            WHERE code = ?
                        """, (studio, studio_code, code))
                        conn.commit()
                    
                    identified_count += 1
                    print(f"✅ {i:3d}/{len(needs_update)} - {code} → {studio} ({studio_code})")
                    
                except Exception as e:
                    print(f"❌ 更新 {code} 失敗: {e}")
                    continue
            else:
                print(f"⚠️ {i:3d}/{len(needs_update)} - {code} → 仍無法識別")
            
            updated_count += 1
            
            # 每處理10個顯示進度
            if i % 10 == 0:
                print(f"📈 進度: {i}/{len(needs_update)} ({i/len(needs_update)*100:.1f}%)")
        
        print(f"\n🎉 更新完成！")
        print(f"   📊 處理總數: {updated_count}")
        print(f"   ✅ 成功識別: {identified_count}")
        print(f"   ❓ 仍未識別: {updated_count - identified_count}")
        print(f"   📈 識別率: {identified_count/updated_count*100:.1f}%")
        
        # 顯示更新後的片商統計
        print(f"\n📊 更新後的片商統計:")
        studio_stats = db_manager.get_studio_statistics()
        for stat in studio_stats[:10]:  # 顯示前10個片商
            print(f"   {stat['studio']}: {stat['video_count']} 部影片")
        
        if len(studio_stats) > 10:
            print(f"   ... 還有 {len(studio_stats) - 10} 個片商")
            
    except Exception as e:
        print(f"❌ 更新過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_unknown_studios()