# -*- coding: utf-8 -*-
"""
女優資料庫記錄檢查腳本

**建立日期**: 2025-06-22

檢查特定女優在資料庫中的片商記錄。
"""

import sys
from pathlib import Path

# 設定路徑
src_path = Path(__file__).parent / '女優分類' / 'src'
sys.path.insert(0, str(src_path))

def check_actress_records(actress_name):
    """檢查女優的資料庫記錄"""
    try:
        from models.database import SQLiteDBManager
        
        # 使用預設資料庫路徑
        db_path = Path('女優分類') / 'actress_videos.db'
        if not db_path.exists():
            print(f"❌ 資料庫檔案不存在: {db_path}")
            return
            
        db = SQLiteDBManager(str(db_path))
        
        print("=" * 70)
        print(f"🔍 檢查女優資料庫記錄: {actress_name}")
        print("=" * 70)
        
        # 檢查女優是否存在
        with db._get_connection() as conn:
            cursor = conn.cursor()
            
            # 搜尋女優
            cursor.execute("""
                SELECT id, name FROM actresses 
                WHERE name LIKE ? OR name = ?
            """, (f'%{actress_name}%', actress_name))
            
            actresses = cursor.fetchall()
            if not actresses:
                print(f"❌ 未找到女優: {actress_name}")
                return
            
            print(f"📋 找到女優記錄:")
            for actress_id, name in actresses:
                print(f"  ID: {actress_id}, 姓名: {name}")
                
                # 查詢該女優的所有影片記錄
                cursor.execute("""
                    SELECT 
                        v.code,
                        v.studio,
                        v.studio_code,
                        va.file_association_type,
                        v.title
                    FROM videos v
                    JOIN video_actress_link va ON v.id = va.video_id
                    WHERE va.actress_id = ?
                    ORDER BY v.studio, v.code
                """, (actress_id,))
                
                videos = cursor.fetchall()
                if not videos:
                    print(f"  ❌ 該女優沒有影片記錄")
                    continue
                
                print(f"\n📊 影片記錄 (共 {len(videos)} 部):")
                
                # 按片商分組
                studio_stats = {}
                s1_videos = []
                
                for code, studio, studio_code, assoc_type, title in videos:
                    if studio not in studio_stats:
                        studio_stats[studio] = {'primary': 0, 'collaboration': 0}
                    
                    if assoc_type == 'primary':
                        studio_stats[studio]['primary'] += 1
                    else:
                        studio_stats[studio]['collaboration'] += 1
                    
                    # 特別記錄S1作品
                    if studio == 'S1':
                        s1_videos.append((code, title, assoc_type))
                
                print("\n🏢 片商分佈:")
                for studio, stats in studio_stats.items():
                    total = stats['primary'] + stats['collaboration']
                    print(f"  • {studio}: {total}部 (主演: {stats['primary']}, 合作: {stats['collaboration']})")
                
                # 特別顯示S1作品
                if s1_videos:
                    print(f"\n🎯 S1作品詳細:")
                    for code, title, assoc_type in s1_videos:
                        print(f"  • {code}: {title} ({assoc_type})")
                else:
                    print(f"\n❌ 未找到S1作品記錄")
                
                # 測試分析函式
                print(f"\n🧪 測試分析結果:")
                major_studios = {
                    'E-BODY', 'FALENO', 'S1', 'SOD', 'PRESTIGE', 
                    'MOODYZ', 'MADONNA', 'IdeaPocket', 'KAWAII'
                }
                
                result = db.analyze_actress_primary_studio(name, major_studios)
                print(f"  主要片商: {result['primary_studio']}")
                print(f"  信心度: {result['confidence']}%")
                print(f"  推薦分類: {result['recommendation']}")
                print(f"  總影片數: {result['total_videos']}")
                
                print(f"\n📈 片商分佈統計:")
                for studio, count in result['studio_distribution'].items():
                    print(f"  • {studio}: {count}部")
                
    except Exception as e:
        print(f"❌ 檢查失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    actress_name = "逢沢みゆ"
    check_actress_records(actress_name)
    print()
    input("按 Enter 鍵退出...")
