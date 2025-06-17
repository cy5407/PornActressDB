# -*- coding: utf-8 -*-
"""
測試片商分類功能的路徑錯誤修復
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path

# 加入專案路徑
sys.path.append(str(Path(__file__).parent.parent))

from src.models.extractor import UnifiedCodeExtractor
from src.models.database import SQLiteDBManager
from src.models.studio import StudioIdentifier
from src.models.config import PreferenceManager
from src.services.studio_classifier import StudioClassificationCore


def create_test_structure():
    """建立測試用的資料夾結構"""
    # 建立臨時目錄
    temp_dir = Path(tempfile.mkdtemp(prefix="studio_test_"))
    print(f"建立測試目錄: {temp_dir}")
    
    # 建立測試女優資料夾和影片檔案
    test_actresses = [
        ("桃乃木香奈", ["SSNI-001.mp4", "SSNI-020.mp4", "SSNI-035.mp4"]),  # S1 主要
        ("三上悠亞", ["SSNI-100.mp4", "MOODYZ-200.mp4"]),  # 混合片商
        ("橋本有菜", ["EBOD-500.mp4", "EBOD-520.mp4"]),  # E-BODY 主要
        ("不存在女優", []),  # 空資料夾，會被跳過
    ]
    
    for actress_name, video_files in test_actresses:
        actress_folder = temp_dir / actress_name
        actress_folder.mkdir()
        
        for video_file in video_files:
            (actress_folder / video_file).write_text("fake video content")
    
    # 建立一個會被刪除的資料夾，模擬路徑不存在的情況
    test_folder = temp_dir / "測試女優"
    test_folder.mkdir()
    (test_folder / "TEST-001.mp4").write_text("test content")
    
    return temp_dir, test_folder


def test_studio_classification():
    """測試片商分類功能"""
    try:
        print("🔧 初始化測試組件...")        # 初始化組件
        db_manager = SQLiteDBManager(':memory:')  # 使用內存資料庫
        code_extractor = UnifiedCodeExtractor()
        studio_identifier = StudioIdentifier()
        preference_manager = PreferenceManager()
        
        classifier = StudioClassificationCore(
            db_manager, code_extractor, studio_identifier, preference_manager
        )
        
        # 建立測試資料夾結構
        temp_dir, test_folder = create_test_structure()
        
        print(f"\n📁 測試目錄內容:")
        for item in temp_dir.iterdir():
            if item.is_dir():
                files = list(item.glob("*.mp4"))
                print(f"  {item.name}: {len(files)} 個影片檔案")
        
        # 模擬刪除一個資料夾，測試路徑不存在的處理
        print(f"\n🗑️ 刪除測試資料夾: {test_folder.name}")
        shutil.rmtree(test_folder)
        
        # 執行片商分類
        print(f"\n🚀 開始執行片商分類...")
        result = classifier.classify_actresses_by_studio(
            str(temp_dir), 
            progress_callback=lambda msg: print(f"    {msg.strip()}")
        )
        
        # 顯示結果
        print(f"\n📊 分類結果:")
        print(f"  狀態: {result['status']}")
        if result['status'] == 'success':
            print(f"  掃描女優總數: {result['total_actresses']}")
            print(f"  更新統計數量: {result['updated_count']}")
            
            move_stats = result['move_stats']
            print(f"  移動統計:")
            print(f"    ✅ 成功移動到片商: {move_stats['moved']}")
            print(f"    🎭 移動到單體企劃: {move_stats['solo_artist']}")
            print(f"    ⚠️ 目標已存在: {move_stats['exists']}")
            print(f"    ⏩ 跳過處理: {move_stats['skipped']}")
            print(f"    ❌ 移動失敗: {move_stats['failed']}")
            
            # 顯示摘要
            summary = classifier.get_classification_summary(
                result['total_actresses'], 
                move_stats
            )
            print(f"\n{summary}")
        else:
            print(f"  錯誤訊息: {result.get('message', 'Unknown error')}")
        
        # 檢查分類後的目錄結構
        print(f"\n📂 分類後目錄結構:")
        for item in temp_dir.iterdir():
            if item.is_dir():
                if any(subitem.is_dir() for subitem in item.iterdir()):
                    print(f"  📁 {item.name}/")
                    for subitem in item.iterdir():
                        if subitem.is_dir():
                            files = list(subitem.glob("*.mp4"))
                            print(f"    📁 {subitem.name}/ ({len(files)} 影片)")
                else:
                    files = list(item.glob("*.mp4"))
                    if files:
                        print(f"  📁 {item.name}/ ({len(files)} 影片)")
        
        # 清理測試目錄
        print(f"\n🧹 清理測試目錄...")
        shutil.rmtree(temp_dir)
        
        print("✅ 測試完成！")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 片商分類路徑錯誤修復測試")
    print("=" * 50)
    
    success = test_studio_classification()
    
    if success:
        print("\n🎉 測試通過！路徑錯誤修復成功。")
    else:
        print("\n💥 測試失敗！請檢查程式碼。")
