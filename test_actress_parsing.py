# -*- coding: utf-8 -*-
"""
測試修正後的多人共演檢測邏輯
"""
import sys
from pathlib import Path

# 加入專案根目錄到 Python 路徑
current_dir = Path(__file__).parent
project_root = current_dir / "女優分類"
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from models.config import ConfigManager
from services.classifier_core import UnifiedClassifierCore

def test_actress_parsing():
    """測試女優名單解析功能"""
    
    config = ConfigManager()
    core = UnifiedClassifierCore(config)
    
    # 測試案例
    test_cases = [
        # 單一女優
        (["真正的單人作品"], "單人", False),
        
        # 用 # 分隔的多人共演（這是我們要修正的問題）
        (["如月りいさ #小那海あや #美澄玲衣 #逢月ひまり"], "多人共演", True),
        (["わか菜ほの #天沢りん #如月りいさ"], "多人共演", True),
        (["小島みこ #市川りく"], "多人共演", True),
        
        # 已經正確分隔的多人共演
        (["女優A", "女優B"], "多人共演", True),
        (["女優A", "女優B", "女優C"], "多人共演", True),
        
        # 空白案例
        ([], "無資料", False),
    ]
    
    print("🧪 測試女優名單解析功能:\n")
    
    for i, (actresses_input, expected_type, expected_collaboration) in enumerate(test_cases, 1):
        parsed_actresses, is_collaboration = core._parse_actresses_list(actresses_input)
        
        status = "✅" if is_collaboration == expected_collaboration else "❌"
        
        print(f"{status} 測試 {i}: {expected_type}")
        print(f"   輸入: {actresses_input}")
        print(f"   解析結果: {parsed_actresses}")
        print(f"   是否多人共演: {is_collaboration} (預期: {expected_collaboration})")
        print(f"   解析出的女優數量: {len(parsed_actresses)}")
        print()
    
    print("="*60)
    print("🔍 實際資料庫檢測:")
    
    # 檢測實際的問題番號
    problem_codes = ['HOIZ-146', 'STCVS-020', 'BANK-201']
    
    for code in problem_codes:
        info = core.db_manager.get_video_info(code)
        if info and info.get('actresses'):
            actresses = info['actresses']
            parsed_actresses, is_collaboration = core._parse_actresses_list(actresses)
            
            print(f"📼 {code}:")
            print(f"   原始: {actresses}")
            print(f"   解析: {parsed_actresses}")
            print(f"   類型: {'多人共演' if is_collaboration else '單人'}")
            print()

if __name__ == "__main__":
    try:
        test_actress_parsing()
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
