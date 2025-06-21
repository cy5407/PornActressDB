# -*- coding: utf-8 -*-
"""
小湊よつ葉片商分類診斷工具

**建立日期**: 2025-06-22

檢查小湊よつ葉為什麼被分類到「單體企劃女優」而不是 SOD 片商。
"""

import sys
from pathlib import Path

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent / "女優分類" / "src"))

def diagnose_actress_classification():
    """診斷小湊よつ葉的片商分類問題"""
    print("=" * 70)
    print("🔍 小湊よつ葉片商分類診斷")
    print("=" * 70)
    
    actress_name = "小湊よつ葉"
    
    try:
        # 匯入必要模組
        from services.code_extractor import CodeExtractor
        from services.studio_identifier import StudioIdentifier
        from models.database import VideoDatabase
        import json
        
        # 初始化工具
        code_extractor = CodeExtractor()
        studio_identifier = StudioIdentifier()
        db_manager = VideoDatabase()
        
        print(f"🎬 目標女優: {actress_name}")
        print()
        
        # 1. 檢查 studios.json 中的 SOD 對應
        print("=" * 50)
        print("📚 檢查 studios.json 中的 SOD 映射")
        print("=" * 50)
        
        studios_file = Path(__file__).parent / "女優分類" / "studios.json"
        if studios_file.exists():
            with open(studios_file, 'r', encoding='utf-8') as f:
                studios_data = json.load(f)
            
            sod_codes = studios_data.get('SOD', [])
            print(f"SOD 對應的番號前綴: {sod_codes}")
            
            if 'START' in sod_codes:
                print("✅ START 系列已正確映射到 SOD")
            else:
                print("❌ START 系列未映射到 SOD")
        else:
            print("❌ 找不到 studios.json 檔案")
        
        print()
        
        # 2. 檢查資料庫中的女優影片資料
        print("=" * 50)
        print("🎭 檢查資料庫中的女優影片資料")
        print("=" * 50)
        
        actress_videos = db_manager.get_actress_videos(actress_name)
        print(f"資料庫中找到 {len(actress_videos)} 部 {actress_name} 的影片:")
        
        studio_stats = {}
        
        for video in actress_videos:
            code = video.get('code', 'UNKNOWN')
            print(f"  📀 {code}")
            
            # 識別片商
            studio = studio_identifier.identify_studio(code)
            print(f"     片商識別結果: {studio}")
            
            if studio != 'UNKNOWN':
                studio_stats[studio] = studio_stats.get(studio, 0) + 1
        
        print()
        print(f"📊 片商統計: {studio_stats}")
        
        # 3. 計算信心度
        print()
        print("=" * 50)
        print("🧮 計算信心度")
        print("=" * 50)
        
        if studio_stats:
            total_videos = sum(studio_stats.values())
            main_studio = max(studio_stats.items(), key=lambda x: x[1])
            studio_name, video_count = main_studio
            
            base_confidence = round((video_count / total_videos) * 100, 1)
            print(f"主要片商: {studio_name}")
            print(f"該片商影片數: {video_count}/{total_videos}")
            print(f"基礎信心度: {base_confidence}%")
              # 檢查大片商加成（使用用戶指定的9家大片商）
            major_studios = {
                'E-BODY', 'FALENO', 'S1', 'SOD', 'PRESTIGE', 
                'MOODYZ', 'MADONNA', 'IdeaPocket', 'KAWAII'
            }
            
            is_major_studio = studio_name in major_studios
            print(f"是否為大片商: {'✅ 是' if is_major_studio else '❌ 否'}")
            
            # 大片商加成邏輯
            final_confidence = base_confidence
            if total_videos <= 3 and is_major_studio:
                final_confidence = max(base_confidence, 70.0)
                print(f"⚡ 大片商加成 (影片數≤3): {final_confidence}%")
            
            print(f"最終信心度: {final_confidence}%")
            
            # 判斷分類結果
            confidence_threshold = 60.0  # 預設門檻
            print()
            print("🎯 分類結果判斷:")
            if final_confidence >= confidence_threshold:
                print(f"✅ 信心度 {final_confidence}% ≥ {confidence_threshold}% → 應歸類到 {studio_name}")
            else:
                print(f"❌ 信心度 {final_confidence}% < {confidence_threshold}% → 歸類到單體企劃女優")
                
                print("\n🔧 可能的解決方案:")
                print("1. 降低信心度門檻 (目前60%)")
                print("2. 檢查 START 系列是否正確對應到 SOD")
                print("3. 檢查資料庫中是否有遺漏的影片資料")
                
        else:
            print("❌ 沒有找到任何片商統計資料")
        
        # 4. 檢查設定
        print()
        print("=" * 50)
        print("⚙️ 檢查相關設定")
        print("=" * 50)
        
        try:
            from models.config import ConfigManager
            config = ConfigManager()
            threshold = config.get_confidence_threshold()
            solo_folder = config.get_solo_folder_name()
            
            print(f"當前信心度門檻: {threshold}%")
            print(f"單體企劃資料夾名稱: {solo_folder}")
        except Exception as e:
            print(f"❌ 無法載入設定: {e}")
            
    except ImportError as e:
        print(f"❌ 無法匯入模組: {e}")
        print("請確認程式路徑設定正確")
    except Exception as e:
        print(f"❌ 診斷過程發生錯誤: {e}")

def suggest_solutions():
    """提供解決方案建議"""
    print()
    print("=" * 70)
    print("💡 解決方案建議")
    print("=" * 70)
    
    solutions = [
        {
            "問題": "START 系列沒有被識別為 SOD",
            "檢查": "確認 studios.json 中 SOD 陣列包含 'START'",
            "解決": "在 SOD 陣列中添加 'START' 前綴"
        },
        {
            "問題": "信心度不足 60%",
            "檢查": "檢查小湊よつ葉的影片數量和片商分佈",
            "解決": "1. 降低信心度門檻\n       2. 確保大片商加成邏輯正確運作"
        },
        {
            "問題": "資料庫資料不完整",
            "檢查": "確認資料庫中是否有小湊よつ葉的所有影片",
            "解決": "更新資料庫，添加遺漏的影片資料"
        },
        {
            "問題": "片商識別邏輯錯誤",
            "檢查": "檢查 StudioIdentifier 是否正確識別 START 系列",
            "解決": "修正片商識別邏輯或映射表"
        }
    ]
    
    for i, solution in enumerate(solutions, 1):
        print(f"{i}. {solution['問題']}")
        print(f"   檢查: {solution['檢查']}")
        print(f"   解決: {solution['解決']}")
        print()

if __name__ == "__main__":
    print("🚀 開始小湊よつ葉片商分類診斷")
    
    diagnose_actress_classification()
    suggest_solutions()
    
    print("=" * 70)
    print("✅ 診斷完成")
    print("=" * 70)
    print()
    input("按 Enter 鍵退出...")
