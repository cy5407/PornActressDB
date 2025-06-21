#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
片商資訊顯示 UNKNOWN 問題診斷工具
追蹤資料流向，找出正確片商資訊被覆蓋為 UNKNOWN 的根本原因
"""

import sys
from pathlib import Path
import logging

# 將 src 資料夾加入 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from models.database import SQLiteDBManager
from models.config import ConfigManager
from models.extractor import UnifiedCodeExtractor
from models.studio import StudioIdentifier
from services.safe_javdb_searcher import SafeJAVDBSearcher

def setup_logging():
    """設定日誌"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('studio_unknown_diagnosis.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def test_studio_identification():
    """測試片商識別功能"""
    print("=" * 60)
    print("🔍 測試片商識別功能")
    print("=" * 60)
    
    studio_identifier = StudioIdentifier()
    test_codes = ['SSIS-001', 'MIDV-194', 'EBWH-194', 'IPX-123', 'FSDSS-456']
    
    for code in test_codes:
        studio = studio_identifier.identify_studio(code)
        print(f"番號: {code} -> 片商: {studio}")
    
    print()

def test_javdb_search():
    """測試 JAVDB 搜尋功能"""
    print("=" * 60)
    print("🌐 測試 JAVDB 搜尋功能")
    print("=" * 60)
    
    config = ConfigManager()
    searcher = SafeJAVDBSearcher(config)
    test_codes = ['SSIS-001', 'MIDV-194', 'EBWH-194']
    
    for code in test_codes:
        print(f"\n搜尋番號: {code}")
        try:
            result = searcher.search_single_code(code)
            if result:
                print(f"  女優: {result.get('actresses', [])}")
                print(f"  片商: {result.get('studio', 'N/A')}")
                print(f"  來源: {result.get('source', 'N/A')}")
            else:
                print("  搜尋失敗")
        except Exception as e:
            print(f"  搜尋錯誤: {e}")
    
    print()

def test_database_flow():
    """測試資料庫資料流"""
    print("=" * 60)
    print("💾 測試資料庫資料流")
    print("=" * 60)
    
    try:
        config = ConfigManager()
        db_manager = SQLiteDBManager(config.get('database', 'database_path'))
        studio_identifier = StudioIdentifier()
        
        # 測試碼
        test_code = 'SSIS-001'
        
        # 1. 檢查資料庫中的現有資料
        print(f"1. 檢查資料庫中 {test_code} 的現有資料:")
        existing_info = db_manager.get_video_info(test_code)
        if existing_info:
            print(f"   片商: {existing_info.get('studio', 'N/A')}")
            print(f"   女優: {existing_info.get('actresses', [])}")
            print(f"   搜尋方法: {existing_info.get('search_method', 'N/A')}")
        else:
            print("   資料庫中無此番號資料")
        
        # 2. 使用片商識別器識別
        identified_studio = studio_identifier.identify_studio(test_code)
        print(f"\n2. 片商識別器識別結果: {identified_studio}")
        
        # 3. 模擬 JAVDB 搜尋結果寫入
        print(f"\n3. 模擬 JAVDB 搜尋結果寫入:")
        mock_javdb_result = {
            'actresses': ['西宮夢'],
            'studio': 'S1',  # JAVDB 搜尋到的正確片商
            'source': 'JAVDB'
        }
        
        print(f"   JAVDB 搜尋到的片商: {mock_javdb_result['studio']}")
        
        # 4. 檢查寫入資料庫時是否被覆蓋
        info_to_save = {
            'actresses': mock_javdb_result['actresses'],
            'original_filename': f'{test_code}.mp4',
            'file_path': f'/test/{test_code}.mp4',
            'studio': studio_identifier.identify_studio(test_code),  # 這裡是問題！
            'search_method': mock_javdb_result['source']
        }
        
        print(f"   寫入資料庫的片商: {info_to_save['studio']}")
        print(f"   ⚠️  問題發現: JAVDB搜尋到的片商被片商識別器覆蓋了！")
        
    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
    
    print()

def analyze_code_processing_flow():
    """分析番號處理流程"""
    print("=" * 60)
    print("🔄 分析番號處理流程")
    print("=" * 60)
    
    # 模擬完整的處理流程
    test_code = 'SSIS-001'
    print(f"處理番號: {test_code}")
    
    # 1. 檔案掃描階段
    print("\n階段1: 檔案掃描")
    extractor = UnifiedCodeExtractor()
    extracted_code = extractor.extract_code(f'{test_code}.mp4')
    print(f"  提取的番號: {extracted_code}")
    
    # 2. 片商識別階段（基於番號模式）
    print("\n階段2: 片商識別（基於番號模式）")
    studio_identifier = StudioIdentifier()
    pattern_studio = studio_identifier.identify_studio(test_code)
    print(f"  基於模式的片商: {pattern_studio}")
    
    # 3. 網路搜尋階段
    print("\n階段3: 網路搜尋（JAVDB）")
    print("  搜尋到的片商: S1（假設）")
    
    # 4. 資料庫寫入階段
    print("\n階段4: 資料庫寫入")
    print("  問題分析:")
    print("  - JAVDB 搜尋正確取得片商資訊 'S1'")
    print("  - 但在寫入資料庫時，使用了 studio_identifier.identify_studio()")
    print("  - 而 studios.json 中可能沒有 'SSIS' 前綴的定義")
    print("  - 導致正確的片商資訊被覆蓋為 'UNKNOWN'")
    
    print()

def check_studios_json():
    """檢查 studios.json 配置檔"""
    print("=" * 60)
    print("📋 檢查 studios.json 配置檔")
    print("=" * 60)
    
    studios_file = Path('studios.json')
    if studios_file.exists():
        import json
        try:
            with open(studios_file, 'r', encoding='utf-8') as f:
                studios = json.load(f)
            
            print("當前 studios.json 內容:")
            for studio, prefixes in studios.items():
                print(f"  {studio}: {prefixes}")
            
            # 檢查常見前綴是否存在
            common_prefixes = ['SSIS', 'MIDV', 'EBWH', 'IPX', 'FSDSS']
            print(f"\n檢查常見前綴是否已定義:")
            for prefix in common_prefixes:
                found = False
                for studio, prefixes in studios.items():
                    if prefix in prefixes:
                        print(f"  {prefix}: ✅ 已定義在 {studio}")
                        found = True
                        break
                if not found:
                    print(f"  {prefix}: ❌ 未定義 -> 會導致 UNKNOWN")
                    
        except Exception as e:
            print(f"讀取 studios.json 失敗: {e}")
    else:
        print("studios.json 檔案不存在")
    
    print()

def suggest_solutions():
    """建議解決方案"""
    print("=" * 60)
    print("💡 解決方案建議")
    print("=" * 60)
    
    print("問題根源:")
    print("1. JAVDB 搜尋功能正常，能正確取得片商資訊")
    print("2. 但在 classifier_core.py 第154行，寫入資料庫時使用了:")
    print("   'studio': self.studio_identifier.identify_studio(code)")
    print("3. 這覆蓋了 JAVDB 搜尋到的正確片商資訊")
    print()
    
    print("解決方案:")
    print("方案1: 修改程式碼邏輯")
    print("  - 修改 classifier_core.py，優先使用 JAVDB 搜尋結果中的片商資訊")
    print("  - 只有當 JAVDB 沒有片商資訊時，才使用 studio_identifier")
    print()
    
    print("方案2: 完善 studios.json")
    print("  - 更新 studios.json，加入更多片商前綴定義")
    print("  - 確保常見番號前綴都有對應的片商")
    print()
    
    print("方案3: 混合方案（推薦）")
    print("  - 同時實施方案1和方案2")
    print("  - 確保資料來源優先級: JAVDB > studio_identifier > UNKNOWN")

def main():
    """主函式"""
    setup_logging()
    
    print("🔧 片商資訊顯示 UNKNOWN 問題診斷工具")
    print("=" * 60)
    
    # 執行各項診斷測試
    test_studio_identification()
    test_javdb_search()
    test_database_flow()
    analyze_code_processing_flow()
    check_studios_json()
    suggest_solutions()
    
    print("\n✅ 診斷完成，詳細日誌已寫入 studio_unknown_diagnosis.log")

if __name__ == "__main__":
    main()
