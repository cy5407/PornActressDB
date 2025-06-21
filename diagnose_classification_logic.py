# -*- coding: utf-8 -*-
"""
片商分類邏輯診斷腳本

**建立日期**: 2025-06-22

診斷當前分類邏輯是否正確應用大片商限制。
"""

def diagnose_classification_logic():
    """診斷分類邏輯"""
    print("=" * 70)
    print("🔍 診斷片商分類邏輯")
    print("=" * 70)
    
    # 模擬測試資料
    test_cases = [
        {
            "actress": "測試女優A",
            "best_studio": "ATTACKERS",  # 小片商
            "confidence": 100.0,
            "total_videos": 5,
            "studio_count": 1
        },
        {
            "actress": "測試女優B", 
            "best_studio": "SOD",  # 大片商
            "confidence": 100.0,
            "total_videos": 5,
            "studio_count": 1
        },
        {
            "actress": "測試女優C",
            "best_studio": "PREMIUM",  # 小片商
            "confidence": 100.0,
            "total_videos": 5,
            "studio_count": 1
        }
    ]
    
    # 大片商清單
    major_studios = {
        'E-BODY', 'FALENO', 'S1', 'SOD', 'PRESTIGE', 
        'MOODYZ', 'MADONNA', 'IdeaPocket', 'KAWAII'
    }
    
    print("🎯 指定的9家大片商:")
    for studio in sorted(major_studios):
        print(f"  • {studio}")
    print()
    
    for case in test_cases:
        actress = case["actress"]
        best_studio = case["best_studio"]
        confidence = case["confidence"]
        total_videos = case["total_videos"]
        studio_count = case["studio_count"]
        
        print(f"📊 測試案例: {actress}")
        print(f"主要片商: {best_studio}")
        print(f"信心度: {confidence}%")
        print(f"總影片數: {total_videos}")
        print(f"片商數量: {studio_count}")
        
        # 檢查是否為大片商
        is_major_studio = best_studio in major_studios
        print(f"是否為大片商: {'✅ 是' if is_major_studio else '❌ 否'}")
        
        # 應用修正後的邏輯
        if total_videos <= 3 and is_major_studio:
            recommendation = 'studio_classification'
            reason = "大片商少影片例外"
        elif studio_count > 3:
            if is_major_studio:
                recommendation = 'studio_classification'
                reason = "多片商但主要是大片商"
            else:
                recommendation = 'solo_artist'
                reason = "多片商且主要非大片商"
        elif is_major_studio:
            if confidence >= 50:
                recommendation = 'studio_classification'
                reason = "大片商且信心度足夠"
            else:
                recommendation = 'solo_artist'
                reason = "大片商但信心度不足"
        else:
            recommendation = 'solo_artist'
            reason = "非大片商一律歸類單體企劃"
        
        print(f"推薦分類: {recommendation}")
        print(f"判斷原因: {reason}")
        
        if recommendation == 'studio_classification':
            print(f"🏢 結果: 歸類到 {best_studio}/ 資料夾")
        else:
            print(f"🎭 結果: 歸類到 單體企劃女優/ 資料夾")
        
        print("-" * 50)
        print()
    
    print("🚨 如果小片商女優仍被歸類到片商資料夾，可能原因:")
    print("1. 程式需要重新啟動以載入修正後的邏輯")
    print("2. 系統可能使用了其他的分類路徑")
    print("3. 修正沒有正確套用到所有相關函式")
    print()
    print("💡 建議:")
    print("1. 完全關閉程式後重新啟動")
    print("2. 檢查是否有其他快取或持久化的設定")

if __name__ == "__main__":
    diagnose_classification_logic()
    input("按 Enter 鍵退出...")
