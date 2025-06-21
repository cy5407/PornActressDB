#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化分類邏輯檢查腳本
直接檢查資料庫和分類結果
"""

import sqlite3
from pathlib import Path

def main():
    print("=== 女優分類邏輯檢查 ===")
    
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
        
        # 查詢女優的片商統計
        cursor.execute("""
            SELECT studio, work_count, confidence 
            FROM actress_studio_stats 
            WHERE actress_name = ? 
            ORDER BY confidence DESC
        """, (actress_name,))
        
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
    
    major_studios_str = "','".join(major_studios)
    cursor.execute(f"""
        SELECT actress_name, studio, work_count, confidence 
        FROM actress_studio_stats 
        WHERE studio NOT IN ('{major_studios_str}') 
        AND confidence >= 70 
        AND work_count >= 3
        ORDER BY confidence DESC
        LIMIT 5
    """)
    
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
        SELECT COUNT(DISTINCT actress_name) 
        FROM actress_studio_stats 
        WHERE studio IN ('{major_studios_str}') 
        AND confidence >= 70 
        AND work_count >= 3
    """)
    major_count = cursor.fetchone()[0]
    
    # 小片商女優統計
    cursor.execute(f"""
        SELECT COUNT(DISTINCT actress_name) 
        FROM actress_studio_stats 
        WHERE studio NOT IN ('{major_studios_str}') 
        AND confidence >= 70 
        AND work_count >= 3
    """)
    minor_count = cursor.fetchone()[0]
    
    print(f"符合大片商分類條件的女優: {major_count} 人")
    print(f"小片商高信心度女優: {minor_count} 人 (應該都分類為單體企劃女優)")
    
    conn.close()
    
    print("\n=== 檢查完成 ===")
    print("根據修正後的邏輯:")
    print("- 只有9家大片商且信心度>=70%、作品數>=3的女優才會分類到片商資料夾")
    print("- 其餘所有女優（包括小片商女優）都會分類到「單體企劃女優」")

if __name__ == "__main__":
    main()
