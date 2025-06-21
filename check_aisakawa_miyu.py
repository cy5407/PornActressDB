# -*- coding: utf-8 -*-
"""
逢沢みゆ資料庫記錄檢查腳本

**建立日期**: 2025-06-22

檢查逢沢みゆ在資料庫中的記錄，特別是S1作品。
"""

import sqlite3
import os

def check_actress_records():
    """檢查逢沢みゆ的資料庫記錄"""
    db_path = r"C:\Users\cy540\Documents\ActressClassifier\actress_database.db"
    
    print("=" * 70)
    print("🔍 檢查逢沢みゆ的資料庫記錄")
    print("=" * 70)
    
    # 檢查資料庫檔案是否存在
    if not os.path.exists(db_path):
        print(f"❌ 資料庫檔案不存在: {db_path}")
        
        # 檢查資料夾內的其他檔案
        db_dir = os.path.dirname(db_path)
        if os.path.exists(db_dir):
            print(f"📁 資料夾內容: {db_dir}")
            for file in os.listdir(db_dir):
                if file.endswith('.db'):
                    print(f"  • {file}")
        return
    
    print(f"✅ 找到資料庫: {db_path}")
    
    try:
        # 連接資料庫
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查詢女優表
        print("\n📊 檢查女優記錄...")
        cursor.execute("SELECT id, name FROM actresses WHERE name LIKE '%逢沢%' OR name LIKE '%みゆ%'")
        actresses = cursor.fetchall()
        
        if not actresses:
            print("❌ 未找到逢沢みゆ的記錄")
            
            # 檢查相似名稱
            cursor.execute("SELECT DISTINCT name FROM actresses WHERE name LIKE '%逢%' OR name LIKE '%沢%' OR name LIKE '%みゆ%' LIMIT 10")
            similar = cursor.fetchall()
            if similar:
                print("🔍 找到相似名稱:")
                for name in similar:
                    print(f"  • {name[0]}")
        else:
            print("✅ 找到女優記錄:")
            for actress_id, name in actresses:
                print(f"  ID: {actress_id}, 姓名: {name}")
                
                # 查詢該女優的影片記錄
                print(f"\n🎬 檢查 {name} 的影片記錄...")
                cursor.execute("""
                    SELECT v.code, v.studio, v.studio_code, va.file_association_type
                    FROM videos v
                    JOIN video_actress_link va ON v.id = va.video_id
                    WHERE va.actress_id = ?
                    ORDER BY v.studio, v.code
                """, (actress_id,))
                
                videos = cursor.fetchall()
                
                if not videos:
                    print(f"❌ 沒有找到 {name} 的影片記錄")
                else:
                    print(f"✅ 找到 {len(videos)} 部影片:")
                    
                    # 按片商分組統計
                    studio_stats = {}
                    s1_videos = []
                    
                    for code, studio, studio_code, association_type in videos:
                        if studio not in studio_stats:
                            studio_stats[studio] = 0
                        studio_stats[studio] += 1
                        
                        # 特別記錄S1作品
                        if studio == 'S1' or studio_code == 'S1':
                            s1_videos.append((code, studio, studio_code, association_type))
                        
                        print(f"    • {code} - {studio} ({association_type})")
                    
                    print(f"\n📊 片商統計:")
                    for studio, count in sorted(studio_stats.items()):
                        is_major = studio in ['E-BODY', 'FALENO', 'S1', 'SOD', 'PRESTIGE', 'MOODYZ', 'MADONNA', 'IdeaPocket', 'KAWAII']
                        marker = "🎯" if is_major else "📁"
                        print(f"    {marker} {studio}: {count} 部")
                    
                    if s1_videos:
                        print(f"\n🎯 S1作品詳細:")
                        for code, studio, studio_code, association_type in s1_videos:
                            print(f"    • {code} - {studio} ({association_type})")
                    else:
                        print(f"\n❌ 沒有找到S1作品記錄")
                        
                    # 模擬分析邏輯
                    print(f"\n🧮 分析邏輯模擬:")
                    if studio_stats:
                        # 找主要片商
                        main_studio = max(studio_stats.items(), key=lambda x: x[1])
                        total_videos = sum(studio_stats.values())
                        confidence = (main_studio[1] / total_videos) * 100
                        
                        print(f"    主要片商: {main_studio[0]} ({main_studio[1]} 部)")
                        print(f"    信心度: {confidence:.1f}%")
                        print(f"    總影片數: {total_videos}")
                        
                        # 大片商檢查
                        major_studios = {'E-BODY', 'FALENO', 'S1', 'SOD', 'PRESTIGE', 'MOODYZ', 'MADONNA', 'IdeaPocket', 'KAWAII'}
                        is_major = main_studio[0] in major_studios
                        
                        print(f"    是否大片商: {'✅ 是' if is_major else '❌ 否'}")
                        
                        if is_major and confidence >= 50:
                            recommendation = "studio_classification"
                            result = f"歸類到 {main_studio[0]}/"
                        else:
                            recommendation = "solo_artist"
                            result = "歸類到 單體企劃女優/"
                        
                        print(f"    推薦分類: {recommendation}")
                        print(f"    預期結果: {result}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 資料庫查詢錯誤: {e}")

if __name__ == "__main__":
    check_actress_records()
    input("按 Enter 鍵退出...")
