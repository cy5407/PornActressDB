#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正版分類邏輯檢查腳本
使用實際的資料庫結構計算女優片商統計
建立日期: 2025-06-22
"""

import sqlite3
from pathlib import Path

def main():
    print("=== 女優分類邏輯檢查 (修正版) ===")
    
    # 資料庫路徑
    db_path = Path.home() / "Documents" / "ActressClassifier" / "actress_database.db"
    print(f"資料庫路徑: {db_path}")
    
    if not db_path.exists():
        print("❌ 資料庫檔案不存在！")
        return
    
    # 大片商名單（應該與程式碼一致）
    major_studios = {
        'E-BODY', 'FALENO', 'S1', 'SOD', 'PRESTIGE', 
        'MOODYZ', 'MADONNA', 'IdeaPocket', 'KAWAII'
    }
    
    print(f"\n大片商名單 ({len(major_studios)} 家):")
    for studio in sorted(major_studios):
        print(f"  - {studio}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 檢查測試案例
    test_cases = ["三上悠亜", "高橋しょう子", "逢沢みゆ", "桃乃木かな"]
    
    print("\n=== 測試女優分類 ===")
    for actress_name in test_cases:
        print(f"\n--- {actress_name} ---")
        
        # 查詢女優的片商統計（從現有資料表計算）
        cursor.execute("""
            SELECT 
                v.studio,
                COUNT(*) as work_count,
                ROUND(COUNT(*) * 100.0 / (
                    SELECT COUNT(*) 
                    FROM video_actress_link val2 
                    JOIN actresses a2 ON val2.actress_id = a2.id 
                    WHERE a2.name = ?
                ), 1) as confidence
            FROM videos v
            JOIN video_actress_link val ON v.id = val.video_id
            JOIN actresses a ON val.actress_id = a.id
            WHERE a.name = ?
            GROUP BY v.studio
            ORDER BY confidence DESC
        """, (actress_name, actress_name))
        
        records = cursor.fetchall()
        
        if not records:
            print("資料庫中無記錄")
            continue
        
        print("片商記錄:")
        for studio, count, confidence in records:
            is_major = "大片商" if studio in major_studios else "小片商"
            print(f"  {studio} ({is_major}): {count} 作品, 信心度 {confidence:.1f}%")
        
        # 模擬分類邏輯（基於我們修正的邏輯）
        best_record = records[0]  # 信心度最高的記錄
        studio, count, confidence = best_record
        
        # 根據修正後的邏輯判斷
        if studio in major_studios and confidence >= 70 and count >= 3:
            predicted_classification = f"{studio}所屬女優"
        else:
            predicted_classification = "單體企劃女優"
        
        print(f"預期分類: {predicted_classification}")
    
    # 檢查小片商女優是否被錯誤分類
    print("\n=== 檢查小片商女優 ===")
    
    major_studios_list = list(major_studios)
    placeholders = ','.join(['?' for _ in major_studios_list])
    
    cursor.execute(f"""
        SELECT 
            a.name,
            v.studio,
            COUNT(*) as work_count,
            ROUND(COUNT(*) * 100.0 / (
                SELECT COUNT(*) 
                FROM video_actress_link val2 
                WHERE val2.actress_id = a.id
            ), 1) as confidence
        FROM videos v
        JOIN video_actress_link val ON v.id = val.video_id
        JOIN actresses a ON val.actress_id = a.id
        WHERE v.studio NOT IN ({placeholders})
        GROUP BY a.name, v.studio
        HAVING confidence >= 70 AND work_count >= 3
        ORDER BY confidence DESC
        LIMIT 5
    """, major_studios_list)
    
    small_studio_records = cursor.fetchall()
    if small_studio_records:
        print("小片商高信心度女優（應該都分類為單體企劃女優）:")
        for actress, studio, count, confidence in small_studio_records:
            print(f"  {actress} - {studio}: {count} 作品, 信心度 {confidence:.1f}%")
            print(f"    預期分類: 單體企劃女優 (因為 {studio} 不是大片商)")
    else:
        print("無小片商高信心度女優記錄")
    
    # 檢查統計資訊
    print("\n=== 分類統計 ===")
    
    # 大片商女優統計
    cursor.execute(f"""
        SELECT COUNT(DISTINCT a.name)
        FROM videos v
        JOIN video_actress_link val ON v.id = val.video_id
        JOIN actresses a ON val.actress_id = a.id
        WHERE v.studio IN ({placeholders})
        GROUP BY a.name, v.studio
        HAVING COUNT(*) >= 3 AND COUNT(*) * 100.0 / (
            SELECT COUNT(*) 
            FROM video_actress_link val2 
            WHERE val2.actress_id = a.id
        ) >= 70
    """, major_studios_list)
    
    major_results = cursor.fetchall()
    major_count = len(major_results)
    
    # 小片商女優統計
    cursor.execute(f"""
        SELECT COUNT(DISTINCT a.name)
        FROM videos v
        JOIN video_actress_link val ON v.id = val.video_id
        JOIN actresses a ON val.actress_id = a.id
        WHERE v.studio NOT IN ({placeholders})
        GROUP BY a.name, v.studio
        HAVING COUNT(*) >= 3 AND COUNT(*) * 100.0 / (
            SELECT COUNT(*) 
            FROM video_actress_link val2 
            WHERE val2.actress_id = a.id
        ) >= 70
    """, major_studios_list)
    
    minor_results = cursor.fetchall()
    minor_count = len(minor_results)
    
    print(f"符合大片商分類條件的女優: {major_count} 人")
    print(f"小片商高信心度女優: {minor_count} 人 (應該都分類為單體企劃女優)")
    
    # 總女優統計
    cursor.execute("SELECT COUNT(*) FROM actresses")
    total_actresses = cursor.fetchone()[0]
    print(f"資料庫中總女優數: {total_actresses} 人")
    
    conn.close()
    
    print("\n=== 檢查完成 ===")
    print("根據修正後的邏輯:")
    print("- 只有9家大片商且信心度>=70%、作品數>=3的女優才會分類到片商資料夾")
    print("- 其餘所有女優（包括小片商女優）都會分類到「單體企劃女優」")

if __name__ == "__main__":
    main()
