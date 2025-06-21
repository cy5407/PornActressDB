#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終分類測試腳本
檢查當前分類系統是否正確實施「只有9家大片商女優才分類到片商資料夾」的邏輯
"""

import sys
import os
from pathlib import Path

# 添加專案路徑
project_root = Path(__file__).parent / "女優分類"
sys.path.insert(0, str(project_root / "src"))

from models.config import ConfigManager
from models.database import ActressDatabase
from services.studio_classifier import StudioClassifier
import sqlite3

def main():
    print("=== 最終分類邏輯測試 ===")
    
    # 1. 檢查資料庫連線
    config = ConfigManager()
    db_path = Path(config.get('database', 'database_path'))
    print(f"資料庫路徑: {db_path}")    
    if not db_path.exists():
        print("❌ 資料庫檔案不存在！")
        return
    
    # 2. 檢查大片商名單
    db = ActressDatabase()
    classifier = StudioClassifier(db)
    major_studios = classifier.major_studios
    print(f"\n大片商名單 ({len(major_studios)} 家):")
    for studio in sorted(major_studios):
        print(f"  - {studio}")
    
    # 3. 測試分類邏輯
    print("\n=== 測試案例 ===")
    
    test_cases = [
        "三上悠亜",  # S1女優
        "高橋しょう子",  # S1女優
        "逢沢みゆ",  # 多片商女優，但S1信心度可能不足
        "桃乃木かな",  # SOD/S1女優
    ]
    
    for actress_name in test_cases:
        print(f"\n--- 測試女優: {actress_name} ---")
          # 檢查資料庫記錄
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT studio, work_count, confidence 
            FROM actress_studio_stats 
            WHERE actress_name = ? 
            ORDER BY confidence DESC
        """, (actress_name,))
        
        records = cursor.fetchall()
        if records:
            print("資料庫記錄:")
            for studio, count, confidence in records:
                print(f"  {studio}: {count} 作品, 信心度 {confidence:.1f}%")
        else:
            print("資料庫中無記錄")
        
        # 測試分類邏輯
        recommendation = db.get_classification_recommendation(actress_name)
        print(f"分類建議: {recommendation}")
        
        conn.close()
    
    # 4. 檢查是否有小片商女優被錯誤分類
    print("\n=== 檢查小片商女優分類 ===")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 找出所有非大片商但信心度很高的女優
    major_studios_str = "','".join(major_studios)
    cursor.execute(f"""
        SELECT actress_name, studio, work_count, confidence 
        FROM actress_studio_stats 
        WHERE studio NOT IN ('{major_studios_str}') 
        AND confidence >= 70
        ORDER BY confidence DESC
        LIMIT 10
    """)
    
    small_studio_actresses = cursor.fetchall()
    if small_studio_actresses:
        print("小片商但高信心度女優（應該都分類為單體企劃女優）:")
        for actress, studio, count, confidence in small_studio_actresses:
            recommendation = db.get_classification_recommendation(actress)
            status = "✅" if recommendation == "單體企劃女優" else "❌"
            print(f"  {status} {actress} - {studio} ({confidence:.1f}%) -> {recommendation}")
    else:
        print("無小片商高信心度女優記錄")
    
    conn.close()
    
    print("\n=== 測試完成 ===")
    print("如果看到 ❌ 標記，表示分類邏輯可能仍有問題")
    print("如果全部都是 ✅，表示分類邏輯正常運作")

if __name__ == "__main__":
    main()
