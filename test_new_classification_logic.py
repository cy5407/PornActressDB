#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新的大片商優先分類邏輯
建立日期: 2025-06-22
"""

import sqlite3
from pathlib import Path

def main():
    print("=== 測試新的大片商優先分類邏輯 ===")
    
    # 資料庫路徑
    db_path = Path.home() / "Documents" / "ActressClassifier" / "actress_database.db"
    print(f"資料庫路徑: {db_path}")
    
    if not db_path.exists():
        print("❌ 資料庫檔案不存在！")
        return
    
    # 大片商名單
    major_studios = {
        'E-BODY', 'FALENO', 'S1', 'SOD', 'PRESTIGE', 
        'MOODYZ', 'MADONNA', 'IdeaPocket', 'KAWAII'
    }
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n🔄 新的分類邏輯:")
    print("1. 有大片商作品且作品數≥3、信心度≥70% → 大片商分類")
    print("2. 有大片商作品且小片商作品<10部 → 大片商分類（新增）")
    print("3. 其他情況 → 單體企劃女優")
    
    # 測試原本會被歸類為單體企劃的女優
    test_cases = [
        "輝星きら",   # MOODYZ: 2作品, 100%信心度
        "花アリス",   # S1: 2作品, 100%信心度  
        "三上悠亜",   # S1: 1作品, 100%信心度
        "逢沢みゆ",   # S1: 4作品, 26.7%信心度，但有多片商
        "糸井瑠花",   # S1: 2作品, 100%信心度
        "篠真有",     # S1: 2作品, 100%信心度
    ]
    
    print("\n=== 測試案例分析 ===")
    
    for actress_name in test_cases:
        print(f"\n--- {actress_name} ---")
        
        # 查詢女優的片商統計
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
            ORDER BY confidence DESC, work_count DESC
        """, (actress_name, actress_name))
        
        records = cursor.fetchall()
        
        if not records:
            print("  資料庫中無記錄")
            continue
        
        # 分析片商分佈
        major_studio_works = []
        minor_studio_works = []
        total_works = 0
        
        print("  片商記錄:")
        for studio, count, confidence in records:
            is_major = studio in major_studios
            category = "大片商" if is_major else "小片商"
            print(f"    {studio} ({category}): {count} 作品, {confidence:.1f}%信心度")
            
            total_works += count
            if is_major:
                major_studio_works.append((studio, count, confidence))
            else:
                minor_studio_works.append((studio, count, confidence))
        
        # 應用新的分類邏輯
        if major_studio_works:
            # 有大片商作品
            best_major = max(major_studio_works, key=lambda x: x[1])  # 按作品數排序
            major_studio, major_count, major_confidence = best_major
            
            # 計算小片商總作品數
            minor_total_count = sum(count for _, count, _ in minor_studio_works)
            
            print(f"\n  分析結果:")
            print(f"    最佳大片商: {major_studio} ({major_count}作品)")
            print(f"    小片商總作品數: {minor_total_count}")
            
            # 決定分類
            if major_count >= 3 and major_confidence >= 70:
                classification = f"{major_studio}所屬女優"
                reason = "符合標準條件 (≥3作品且信心度≥70%)"
            elif major_count >= 1 and minor_total_count < 10:
                classification = f"{major_studio}所屬女優"
                reason = "符合新條件 (有大片商作品且小片商作品<10部)"
            else:
                classification = "單體企劃女優"
                if minor_total_count >= 10:
                    reason = f"小片商作品過多 ({minor_total_count}≥10部)"
                else:
                    reason = "不符合任何大片商分類條件"
            
            print(f"    舊邏輯: 單體企劃女優 (因作品數或信心度不足)")
            print(f"    新邏輯: {classification}")
            print(f"    變更原因: {reason}")
            
            # 判斷是否有變更
            old_classification = "單體企劃女優"
            if classification != old_classification:
                print(f"    ✅ 分類變更: {old_classification} → {classification}")
            else:
                print(f"    ➡️  分類維持: {classification}")
        else:
            print(f"    無大片商作品 → 單體企劃女優")
    
    # 統計可能受影響的女優數量
    print("\n=== 影響統計 ===")
    
    major_studios_list = list(major_studios)
    placeholders = ','.join(['?' for _ in major_studios_list])
    
    # 找出有大片商作品但作品數少於3或信心度不足的女優
    cursor.execute(f"""
        SELECT 
            a.name,
            v.studio,
            COUNT(*) as major_count,
            ROUND(COUNT(*) * 100.0 / (
                SELECT COUNT(*) 
                FROM video_actress_link val2 
                WHERE val2.actress_id = a.id
            ), 1) as confidence,
            (SELECT COUNT(*) 
             FROM video_actress_link val3 
             WHERE val3.actress_id = a.id) as total_count
        FROM videos v
        JOIN video_actress_link val ON v.id = val.video_id
        JOIN actresses a ON val.actress_id = a.id
        WHERE v.studio IN ({placeholders})
        GROUP BY a.name, v.studio
        HAVING (major_count < 3 OR confidence < 70)
        ORDER BY major_count DESC, confidence DESC
    """, major_studios_list)
    
    affected_actresses = cursor.fetchall()
    
    print(f"可能受新邏輯影響的女優: {len(affected_actresses)} 人")
    
    if affected_actresses:
        print("前10名可能變更分類的女優:")
        count = 0
        for actress, studio, major_count, confidence, total_count in affected_actresses:
            # 計算該女優的小片商作品數
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM videos v
                JOIN video_actress_link val ON v.id = val.video_id
                JOIN actresses a ON val.actress_id = a.id
                WHERE a.name = ? AND v.studio NOT IN ({placeholders})
            """, [actress] + major_studios_list)
            
            minor_count = cursor.fetchone()[0]
            
            # 檢查是否符合新條件
            if major_count >= 1 and minor_count < 10:
                count += 1
                if count <= 10:
                    print(f"  {count:2d}. {actress} - {studio}: {major_count}作品 ({confidence}%信心度)")
                    print(f"       小片商作品: {minor_count}, 總作品: {total_count}")
                    print(f"       變更: 單體企劃女優 → {studio}所屬女優")
    
    conn.close()
    
    print("\n=== 測試完成 ===")
    print("新的分類邏輯更好地保護了有大片商資歷的女優，")
    print("避免因作品數不足而被錯誤歸類為單體企劃女優。")

if __name__ == "__main__":
    main()
