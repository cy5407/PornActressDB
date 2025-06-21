#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化版分類邏輯驗證腳本
直接測試修正後的程式碼邏輯
建立日期: 2025-06-22
"""

import sqlite3
from pathlib import Path

def simulate_new_classification_logic(actress_name, db_path):
    """模擬新的分類邏輯"""
    
    # 大片商名單
    major_studios = {
        'E-BODY', 'FALENO', 'S1', 'SOD', 'PRESTIGE', 
        'MOODYZ', 'MADONNA', 'IdeaPocket', 'KAWAII'
    }
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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
        ORDER BY work_count DESC
    """, (actress_name, actress_name))
    
    records = cursor.fetchall()
    conn.close()
    
    if not records:
        return None
    
    # 分析片商分佈
    studio_stats = {}
    total_videos = 0
    
    for studio, count, confidence in records:
        studio_stats[studio] = {
            'total_count': count,
            'confidence': confidence
        }
        total_videos += count
    
    # 找出作品數最多的片商
    best_studio = max(studio_stats.items(), key=lambda x: x[1]['total_count'])
    best_studio_name = best_studio[0]
    best_stats = best_studio[1]
    
    # 應用新的分類邏輯
    recommendation = 'solo_artist'  # 預設值
    
    # 檢查是否有大片商作品
    has_major_studio_work = False
    major_studio_work_count = 0
    minor_studio_work_count = 0
    best_major_studio = None
    best_major_count = 0
    
    for studio, stats in studio_stats.items():
        if studio in major_studios:
            has_major_studio_work = True
            major_studio_work_count += stats['total_count']
            if stats['total_count'] > best_major_count:
                best_major_count = stats['total_count']
                best_major_studio = studio
        else:
            minor_studio_work_count += stats['total_count']
    
    # 新的分類邏輯
    if has_major_studio_work:
        if best_major_studio and best_major_studio == best_studio_name:
            # 最佳片商就是大片商
            if best_stats['total_count'] >= 3 and best_stats['confidence'] >= 70:
                recommendation = 'studio_classification'
            elif best_stats['total_count'] >= 1 and minor_studio_work_count < 10:
                recommendation = 'studio_classification'
        elif best_major_studio:
            # 最佳片商不是大片商，但有大片商作品
            if major_studio_work_count >= 1 and minor_studio_work_count < 10:
                recommendation = 'studio_classification'
                best_studio_name = best_major_studio  # 改用大片商
                best_stats = studio_stats[best_major_studio]
    
    return {
        'actress_name': actress_name,
        'primary_studio': best_studio_name,
        'confidence': best_stats['confidence'],
        'total_videos': total_videos,
        'recommendation': recommendation,
        'studio_distribution': studio_stats,
        'major_studio_count': major_studio_work_count,
        'minor_studio_count': minor_studio_work_count
    }

def main():
    print("=== 驗證修正後的分類邏輯 ===")
    
    # 資料庫路徑
    db_path = Path.home() / "Documents" / "ActressClassifier" / "actress_database.db"
    
    if not db_path.exists():
        print("❌ 資料庫檔案不存在！")
        return
    
    # 測試案例
    test_cases = ["三上悠亜", "輝星きら", "逢沢みゆ", "花アリス", "糸井瑠花", "篠真有"]
    
    print("測試修正後的分類邏輯是否按預期運作...\n")
    
    for actress_name in test_cases:
        result = simulate_new_classification_logic(actress_name, db_path)
        
        if result:
            print(f"--- {actress_name} ---")
            print(f"  主要片商: {result['primary_studio']}")
            print(f"  信心度: {result['confidence']}%")
            print(f"  總作品數: {result['total_videos']}")
            print(f"  大片商作品: {result['major_studio_count']}")
            print(f"  小片商作品: {result['minor_studio_count']}")
            
            if result['recommendation'] == 'studio_classification':
                classification = f"{result['primary_studio']}所屬女優"
                print(f"  ✅ 分類: {classification}")
            else:
                print(f"  ➡️  分類: 單體企劃女優")
            
            # 分析變更原因
            if result['major_studio_count'] > 0:
                if result['major_studio_count'] >= 3 and result['confidence'] >= 70:
                    reason = "符合標準條件"
                elif result['major_studio_count'] >= 1 and result['minor_studio_count'] < 10:
                    reason = "符合新條件（大片商優先）"
                else:
                    reason = f"小片商作品過多 ({result['minor_studio_count']}≥10)"
                print(f"  理由: {reason}")
            
            print()
        else:
            print(f"--- {actress_name} ---")
            print("  資料庫中無記錄\n")
    
    print("=== 驗證結果 ===")
    print("根據新的邏輯，有大片商作品的女優優先歸類到大片商，")
    print("只有小片商作品≥10部時才會被歸類為單體企劃女優。")
    print("這樣可以避免知名女優因作品數少被錯誤歸類。")

if __name__ == "__main__":
    main()
