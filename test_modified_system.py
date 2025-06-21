#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
實際測試修正後的分類系統
建立日期: 2025-06-22
"""

import sys
from pathlib import Path

# 加入系統路徑
sys.path.insert(0, str(Path(__file__).parent / '女優分類' / 'src'))

def main():
    print("=== 實際測試修正後的分類系統 ===")
    
    try:        # 導入修正後的模組
        from models.database import SQLiteDBManager
        from models.config import Config
        
        # 初始化設定和資料庫
        config = Config()
        db = SQLiteDBManager()
        
        print("✅ 系統模組載入成功")
        
        # 測試幾個關鍵案例
        test_cases = ["三上悠亜", "輝星きら", "逢沢みゆ", "花アリス"]
        
        print("\n=== 使用修正後系統進行分類測試 ===")
        
        for actress_name in test_cases:
            print(f"\n--- {actress_name} ---")
            
            try:
                # 使用修正後的分析函數
                result = db.analyze_actress_primary_studio(
                    actress_name, 
                    major_studios={'E-BODY', 'FALENO', 'S1', 'SOD', 'PRESTIGE', 'MOODYZ', 'MADONNA', 'IdeaPocket', 'KAWAII'}
                )
                
                print(f"  主要片商: {result['primary_studio']}")
                print(f"  信心度: {result['confidence']}%")
                print(f"  總作品數: {result['total_videos']}")
                print(f"  推薦分類: {result['recommendation']}")
                
                # 解釋分類結果
                if result['recommendation'] == 'studio_classification':
                    final_classification = f"{result['primary_studio']}所屬女優"
                    print(f"  ✅ 最終分類: {final_classification}")
                else:
                    print(f"  ➡️  最終分類: 單體企劃女優")
                
                # 顯示片商分佈
                if result['studio_distribution']:
                    print(f"  片商分佈:")
                    for studio, stats in result['studio_distribution'].items():
                        print(f"    {studio}: {stats['total_count']} 作品")
                
            except Exception as e:
                print(f"  ❌ 分析失敗: {e}")
        
        print("\n=== 測試結果驗證 ===")
        print("根據新的分類邏輯，以上女優應該：")
        print("1. 三上悠亜 → S1所屬女優 (有S1作品且小片商作品少)")
        print("2. 輝星きら → MOODYZ所屬女優 (有MOODYZ作品且小片商作品少)")
        print("3. 逢沢みゆ → S1所屬女優 (S1作品最多且小片商作品<10)")
        print("4. 花アリス → S1所屬女優 (有S1作品且小片商作品少)")
        
    except ImportError as e:
        print(f"❌ 模組導入失敗: {e}")
        print("請確認女優分類系統的路徑和模組結構")
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
