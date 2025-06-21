# -*- coding: utf-8 -*-
"""
測試女優名單解析功能

**建立日期**: 2025-06-22

此腳本用於測試修正後的多人共演識別邏輯。
"""

import sys
from pathlib import Path

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent / "女優分類" / "src"))

def test_actresses_parsing():
    """測試女優名單解析功能"""
    print("=" * 60)
    print("🧪 測試女優名單解析功能")
    print("=" * 60)
    
    try:
        from services.classifier_core import UnifiedActressClassifier
        
        # 建立分類器實例（僅用於測試解析功能）
        classifier = UnifiedActressClassifier()
        
        # 測試案例
        test_cases = [
            # 單人女優
            (["橘メアリー"], "單人女優"),
            (["森沢かな"], "單人女優"),
            
            # 資料庫中的多人記錄
            (["橘メアリー", "森沢かな"], "資料庫多人記錄"),
            (["伊織ひなの", "宮ノ木しゅんか", "神崎ゆま"], "資料庫多人記錄"),
            
            # # 分隔的多人共演（這是問題所在）
            (["ゆめ莉りか #白石なぎさ #真白さら"], "# 分隔多人共演"),
            (["如月りいさ #小那海あや #美澄玲衣 #逢月ひまり"], "# 分隔多人共演"),
            (["わか菜ほの #天沢りん #如月りいさ"], "# 分隔多人共演"),
            (["柏木こなつ #胡桃さくら #高瀬りな"], "# 分隔多人共演"),
        ]
        
        print("測試案例:")
        print()
        
        for i, (actresses_input, description) in enumerate(test_cases, 1):
            print(f"測試 {i}: {description}")
            print(f"輸入: {actresses_input}")
            
            try:
                parsed_actresses, is_collaboration = classifier._parse_actresses_list(actresses_input)
                print(f"解析結果: {parsed_actresses}")
                print(f"是否為多人共演: {'✅ 是' if is_collaboration else '❌ 否'}")
                print(f"女優數量: {len(parsed_actresses)}")
                
                if is_collaboration:
                    print(f"🎯 這將觸發互動式分類")
                else:
                    print(f"🤖 這將使用自動分類")
                    
            except Exception as e:
                print(f"❌ 解析失敗: {e}")
            
            print("-" * 40)
            print()
        
        print("=" * 60)
        print("🔍 結論分析")
        print("=" * 60)
        print("根據您的問題，檔案名稱包含 # 分隔的女優應該要被識別為多人共演。")
        print("修正後的程式碼應該能正確解析這些名稱並觸發互動式分類。")
        print()
        
    except ImportError as e:
        print(f"❌ 無法匯入模組: {e}")
        print("請確認程式路徑設定正確")
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")

def simulate_file_classification():
    """模擬檔案分類過程"""
    print("=" * 60)
    print("🎬 模擬檔案分類過程")
    print("=" * 60)
    
    # 模擬您提到的檔案
    sample_files = [
        "SVSHA-030.mp4 → ゆめ莉りか #白石なぎさ #真白さら",
        "HOIZ-146[H265].mp4 → 如月りいさ #小那海あや #美澄玲衣 #逢月ひまり",
        "STCVS-020.mp4 → わか菜ほの #天沢りん #如月りいさ",
        "REAL-887.mp4 → 柏木こなつ #胡桃さくら #高瀬りな",
    ]
    
    print("以下檔案應該要被識別為多人共演並觸發互動式分類：")
    print()
    
    for i, file_info in enumerate(sample_files, 1):
        filename, actresses_str = file_info.split(" → ")
        print(f"{i}. {filename}")
        print(f"   女優資訊: {actresses_str}")
        
        # 模擬解析過程
        if "#" in actresses_str:
            actresses = actresses_str.split("#")
            actresses = [name.strip() for name in actresses]
            print(f"   解析後: {actresses}")
            print(f"   女優數量: {len(actresses)}")
            print(f"   🎯 應觸發互動式分類")
        else:
            print(f"   🤖 單人作品，自動分類")
        print()

if __name__ == "__main__":
    print("🚀 開始測試女優分類修正")
    print()
    
    test_actresses_parsing()
    print()
    simulate_file_classification()
    print()
    input("按 Enter 鍵退出...")
