# -*- coding: utf-8 -*-
"""
大片商優先分類邏輯測試腳本

**建立日期**: 2025-06-22

測試修正後的分類邏輯，確保只有大片商才能歸類到片商資料夾。
"""

def test_studio_classification_logic():
    """測試片商分類邏輯"""
    print("=" * 70)
    print("🧪 測試大片商優先分類邏輯")
    print("=" * 70)
    
    # 定義大片商列表
    major_studios = {
        'E-BODY', 'FALENO', 'S1', 'SOD', 'PRESTIGE', 
        'MOODYZ', 'MADONNA', 'IdeaPocket', 'KAWAII'
    }
    
    # 測試案例
    test_cases = [
        {
            "actress": "大片商女優 - SOD",
            "best_studio": "SOD",
            "confidence": 100.0,
            "total_videos": 5,
            "studio_count": 1,
            "expected": "studio_classification"
        },
        {
            "actress": "小片商女優 - SMALL_STUDIO",
            "best_studio": "SMALL_STUDIO",
            "confidence": 100.0,
            "total_videos": 5,
            "studio_count": 1,
            "expected": "solo_artist"
        },
        {
            "actress": "小片商女優 - ATTACKERS",
            "best_studio": "ATTACKERS",
            "confidence": 100.0,
            "total_videos": 5,
            "studio_count": 1,
            "expected": "solo_artist"
        },
        {
            "actress": "大片商低信心度 - MOODYZ",
            "best_studio": "MOODYZ",
            "confidence": 40.0,
            "total_videos": 10,
            "studio_count": 3,
            "expected": "solo_artist"
        },
        {
            "actress": "大片商少影片 - KAWAII",
            "best_studio": "KAWAII",
            "confidence": 60.0,
            "total_videos": 2,
            "studio_count": 1,
            "expected": "studio_classification"
        }
    ]
    
    print("測試案例分析:")
    print()
    
    for i, case in enumerate(test_cases, 1):
        actress = case["actress"]
        best_studio = case["best_studio"]
        confidence = case["confidence"]
        total_videos = case["total_videos"]
        studio_count = case["studio_count"]
        expected = case["expected"]
        
        print(f"測試 {i}: {actress}")
        print(f"主要片商: {best_studio}")
        print(f"信心度: {confidence}%")
        print(f"總影片數: {total_videos}")
        print(f"片商數量: {studio_count}")
        
        # 模擬新的分類邏輯
        is_major_studio = best_studio in major_studios
        print(f"是否為大片商: {'✅ 是' if is_major_studio else '❌ 否'}")
        
        # 應用新的分類邏輯
        if total_videos <= 3 and is_major_studio:
            # 大片商例外：影片數少但屬於大片商時，強制推薦片商分類
            recommendation = 'studio_classification'
            final_confidence = max(confidence, 70.0)
        elif studio_count > 3:
            # 多片商女優：優先以大片商為分類依據
            if is_major_studio:
                recommendation = 'studio_classification'
                final_confidence = max(confidence, 50.0)
            else:
                recommendation = 'solo_artist'
                final_confidence = confidence
        elif is_major_studio:
            # 只有大片商且信心度足夠才分類到片商資料夾
            if confidence >= 50:
                recommendation = 'studio_classification'
            else:
                recommendation = 'solo_artist'
            final_confidence = confidence
        else:
            # 非大片商一律歸類為單體企劃，不管信心度多高
            recommendation = 'solo_artist'
            final_confidence = confidence
        
        print(f"最終信心度: {final_confidence}%")
        print(f"分類結果: {recommendation}")
        print(f"預期結果: {expected}")
        
        # 檢查是否符合預期
        if recommendation == expected:
            print("✅ 測試通過")
        else:
            print("❌ 測試失敗")
        
        print("-" * 50)
        print()
    
    print("=" * 70)
    print("📋 新邏輯規則總結")
    print("=" * 70)
    print("1. 只有9家大片商的女優才能歸類到片商資料夾")
    print("2. 所有小片商女優一律歸類為「單體企劃女優」")
    print("3. 大片商女優：≤3部影片強制分類，否則需信心度≥50%")
    print("4. 多片商女優：主要片商是大片商才能分類到片商資料夾")
    print()
    print("🎯 9家大片商:")
    for studio in sorted(major_studios):
        print(f"  • {studio}")
    print()
    print("❌ 以下片商的女優將歸類為「單體企劃女優」:")
    excluded_studios = [
        "SMALL_STUDIO", "S_KYUU_SHIROTO", "LULU", "HOI_SERIES", 
        "MAAN", "OPPAI", "AGAV", "ROCKET", "HALE", "MANZOKU", 
        "MOMOTARO", "NAMH", "ATTACKERS", "等其他非指定大片商"
    ]
    for studio in excluded_studios:
        print(f"  • {studio}")

if __name__ == "__main__":
    print("🚀 開始大片商優先分類邏輯測試")
    print()
    
    test_studio_classification_logic()
    
    print()
    print("✅ 測試完成")
    input("按 Enter 鍵退出...")
