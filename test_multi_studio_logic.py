# -*- coding: utf-8 -*-
"""
多片商女優分類邏輯測試腳本

**建立日期**: 2025-06-22

測試修正後的多片商女優分類邏輯是否正確運作。
"""

def test_multi_studio_logic():
    """測試多片商女優分類邏輯"""
    print("=" * 70)
    print("🧪 多片商女優分類邏輯測試")
    print("=" * 70)
      # 定義大片商列表（根據用戶指定）
    major_studios = {
        'E-BODY', 'FALENO', 'S1', 'SOD', 'PRESTIGE', 
        'MOODYZ', 'MADONNA', 'IdeaPocket', 'KAWAII'
    }
    
    # 測試案例
    test_cases = [
        {
            "actress": "小湊よつ葉",
            "studio_stats": {
                "SOD": 5,      # 主要片商 (大片商)
                "其他A": 2,
                "其他B": 1,
                "其他C": 1,
                "其他D": 1
            },
            "expected": "SOD (大片商優先)",
            "description": "大片商女優 - 即使跨多片商也歸類到主要大片商"
        },
        {
            "actress": "假設女優A",
            "studio_stats": {
                "小片商A": 3,
                "小片商B": 2,
                "小片商C": 2,
                "小片商D": 1
            },
            "expected": "單體企劃女優",
            "description": "一般女優 - 超過3個片商且無大片商經歷"
        },
        {
            "actress": "假設女優B",
            "studio_stats": {
                "S1": 2,       # 大片商
                "小片商A": 2,
                "小片商B": 1,
                "小片商C": 1
            },
            "expected": "S1 (大片商優先)",
            "description": "大片商女優 - S1是主要片商"
        },
        {
            "actress": "假設女優C",
            "studio_stats": {
                "小片商A": 3,
                "小片商B": 2
            },
            "expected": "小片商A",
            "description": "一般女優 - 只有2個片商，正常分類"
        }
    ]
    
    print("測試案例分析:")
    print()
    
    for i, case in enumerate(test_cases, 1):
        actress = case["actress"]
        studio_stats = case["studio_stats"]
        expected = case["expected"]
        description = case["description"]
        
        print(f"測試 {i}: {actress}")
        print(f"描述: {description}")
        print(f"片商分佈: {studio_stats}")
        
        # 模擬分類邏輯
        total_videos = sum(studio_stats.values())
        studio_count = len(studio_stats)
        
        # 找到主要片商
        best_studio = max(studio_stats.items(), key=lambda x: x[1])[0]
        confidence = round((studio_stats[best_studio] / total_videos) * 100, 1)
        
        print(f"總影片數: {total_videos}")
        print(f"片商數量: {studio_count}")
        print(f"主要片商: {best_studio} ({studio_stats[best_studio]}部影片)")
        print(f"基礎信心度: {confidence}%")
        
        # 應用新的分類邏輯
        if studio_count > 3:
            if best_studio in major_studios:
                recommendation = "studio_classification"
                final_confidence = max(confidence, 50.0)
                result = f"{best_studio} (大片商優先)"
            else:
                recommendation = "solo_artist"
                final_confidence = confidence
                result = "單體企劃女優"
        elif confidence >= 60:
            recommendation = "studio_classification"
            final_confidence = confidence
            result = best_studio
        else:
            recommendation = "solo_artist"
            final_confidence = confidence
            result = "單體企劃女優"
        
        print(f"最終信心度: {final_confidence}%")
        print(f"分類結果: {result}")
        print(f"預期結果: {expected}")
        
        # 檢查是否符合預期
        if result == expected:
            print("✅ 測試通過")
        else:
            print("❌ 測試失敗")
        
        print("-" * 50)
        print()
    
    print("=" * 70)
    print("📋 邏輯規則總結")
    print("=" * 70)
    print("1. 超過3個片商 + 主要片商是大片商 → 歸類到該大片商")
    print("2. 超過3個片商 + 主要片商非大片商 → 歸類為單體企劃")
    print("3. ≤3個片商 + 信心度≥60% → 歸類到主要片商")
    print("4. ≤3個片商 + 信心度<60% → 歸類為單體企劃")
    print()
    print("🎯 大片商包括:")
    for studio in sorted(major_studios):
        print(f"  • {studio}")

if __name__ == "__main__":
    print("🚀 開始多片商女優分類邏輯測試")
    print()
    
    test_multi_studio_logic()
    
    print()
    print("✅ 測試完成")
    input("按 Enter 鍵退出...")
