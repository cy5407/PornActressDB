"""
檢查資料庫結構和女優共演資料
"""
import sys
from pathlib import Path
import sqlite3

# 將 src 資料夾加入 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from models.config import ConfigManager

def main():
    print('📊 女優分類系統 - 資料庫結構分析')
    print('=' * 60)
    
    try:
        # 初始化配置
        config = ConfigManager()
        db_path = config.get('database', 'database_path')
        
        print(f'資料庫路徑: {db_path}')
        
        # 檢查資料庫是否存在
        if not Path(db_path).exists():
            print('❌ 資料庫檔案不存在')
            return
        
        # 連接資料庫
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 檢查資料表結構
        print('\n1️⃣ 資料表結構:')
        tables = ['videos', 'actresses', 'video_actress_link']
        for table in tables:
            print(f'\n📋 {table} 資料表:')
            cursor.execute(f'PRAGMA table_info({table})')
            columns = cursor.fetchall()
            for col in columns:
                print(f'  - {col[1]:<20} {col[2]:<10} {"(主鍵)" if col[5] else ""}')
        
        # 2. 統計資料
        print('\n2️⃣ 資料統計:')
        cursor.execute('SELECT COUNT(*) FROM videos')
        video_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM actresses')
        actress_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM video_actress_link')
        link_count = cursor.fetchone()[0]
        
        print(f'  📹 影片數量: {video_count}')
        print(f'  👩 女優數量: {actress_count}')
        print(f'  🔗 關聯記錄: {link_count}')
        
        # 3. 檔案關聯類型分析
        print('\n3️⃣ 檔案關聯類型分佈:')
        cursor.execute('''
            SELECT 
                file_association_type,
                COUNT(*) as count
            FROM video_actress_link
            GROUP BY file_association_type
        ''')
        
        assoc_data = cursor.fetchall()
        for row in assoc_data:
            assoc_type, count = row
            percentage = (count / link_count * 100) if link_count > 0 else 0
            print(f'  {assoc_type:<15}: {count:>6} 筆 ({percentage:5.1f}%)')
        
        # 4. 共演分析
        print('\n4️⃣ 共演影片分析:')
        cursor.execute('''
            SELECT 
                COUNT(va.actress_id) as actress_count_per_video,
                COUNT(DISTINCT v.id) as video_count
            FROM videos v
            JOIN video_actress_link va ON v.id = va.video_id
            GROUP BY v.id
        ''')
        
        # 統計每種人數的影片數量
        actress_count_stats = {}
        for row in cursor.fetchall():
            actress_count_per_video, _ = row
            if actress_count_per_video not in actress_count_stats:
                actress_count_stats[actress_count_per_video] = 0
            actress_count_stats[actress_count_per_video] += 1
        
        for actress_count in sorted(actress_count_stats.keys()):
            video_count = actress_count_stats[actress_count]
            percentage = (video_count / sum(actress_count_stats.values()) * 100) if actress_count_stats else 0
            print(f'  {actress_count}人影片: {video_count:>6} 部 ({percentage:5.1f}%)')
        
        # 5. 多人共演範例
        print('\n5️⃣ 多人共演範例 (前10部):')
        cursor.execute('''
            SELECT 
                v.code,
                v.studio,
                GROUP_CONCAT(a.name, ', ') as actresses,
                COUNT(va.actress_id) as actress_count
            FROM videos v
            JOIN video_actress_link va ON v.id = va.video_id
            JOIN actresses a ON va.actress_id = a.id
            GROUP BY v.code, v.studio
            HAVING COUNT(va.actress_id) > 1
            ORDER BY COUNT(va.actress_id) DESC, v.code
            LIMIT 10
        ''')
        
        collab_videos = cursor.fetchall()
        if collab_videos:
            for i, (code, studio, actresses, count) in enumerate(collab_videos, 1):
                print(f'  {i:2d}. {code:<12} [{studio or "未知"}] ({count}人)')
                print(f'      女優: {actresses}')
        else:
            print('  🤷 目前資料庫中沒有多人共演影片')
        
        # 6. 女優片商分佈範例
        print('\n6️⃣ 女優片商分佈範例 (前5位):')
        cursor.execute('''
            SELECT 
                a.name,
                COUNT(DISTINCT v.studio) as studio_count,
                GROUP_CONCAT(DISTINCT v.studio) as studios,
                COUNT(v.id) as video_count
            FROM actresses a
            JOIN video_actress_link va ON a.id = va.actress_id
            JOIN videos v ON va.video_id = v.id
            WHERE v.studio IS NOT NULL AND v.studio != 'UNKNOWN'
            GROUP BY a.name
            HAVING COUNT(v.id) >= 2
            ORDER BY COUNT(v.id) DESC, a.name
            LIMIT 5
        ''')
        
        actress_stats = cursor.fetchall()
        if actress_stats:
            for i, (name, studio_count, studios, video_count) in enumerate(actress_stats, 1):
                print(f'  {i}. {name:<15} ({video_count}部影片, {studio_count}個片商)')
                print(f'     片商: {studios}')
        else:
            print('  🤷 目前資料庫中沒有足夠的女優片商資料')
            
        conn.close()
        print('\n✅ 資料庫分析完成')
        
    except Exception as e:
        print(f'❌ 分析失敗: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
