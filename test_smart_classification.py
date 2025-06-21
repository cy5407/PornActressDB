# -*- coding: utf-8 -*-
"""
測試智慧分類功能
驗證單人自動分類 + 多人共演互動選擇功能
"""
import sys
import os
from pathlib import Path

# 加入專案根目錄到 Python 路徑
current_dir = Path(__file__).parent
project_root = current_dir / "女優分類"
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from models.config import ConfigManager
from services.classifier_core import UnifiedClassifierCore
from services.interactive_classifier import InteractiveClassifier
from models.preference import PreferenceManager

def test_smart_classification():
    """測試智慧分類功能"""
    print("🧪 開始測試智慧分類功能...\n")
    
    # 初始化配置
    config = ConfigManager()
    
    # 初始化核心分類器
    core = UnifiedClassifierCore(config)
    
    # 初始化偏好管理器
    preference_manager = PreferenceManager(config.get('database', 'database_path'))
    core.set_preference_manager(preference_manager)
    
    # 初始化互動分類器（GUI 模式，但會自動使用 Console 模式）
    interactive_classifier = InteractiveClassifier()
    core.set_interactive_classifier(interactive_classifier)
    
    # 測試資料夾路徑（請修改為您的測試資料夾）
    test_folder = input("請輸入要測試的資料夾路徑（包含影片檔案）: ").strip()
    
    if not test_folder or not Path(test_folder).exists():
        print("❌ 無效的資料夾路徑！")
        return
    
    print(f"📁 測試資料夾: {test_folder}")
    print("🎯 開始智慧分類測試...\n")
    
    def progress_callback(message):
        print(message, end='')
    
    # 執行智慧分類
    result = core.move_files(test_folder, progress_callback)
    
    print("\n" + "="*60)
    print("🧪 測試結果:")
    print(f"狀態: {result.get('status')}")
    
    if result.get('status') == 'success':
        stats = result.get('stats', {})
        print(f"✅ 成功移動: {stats.get('success', 0)}")
        print(f"⚠️ 檔案已存在: {stats.get('exists', 0)}")
        print(f"❓ 無資料檔案: {stats.get('no_data', 0)}")
        print(f"❌ 移動失敗: {stats.get('failed', 0)}")
        print(f"🤝 互動處理數量: {stats.get('interactive', 0)}")
        print(f"📊 總檔案數: {result.get('total_files', 0)}")
    else:
        print(f"❌ 錯誤: {result.get('message')}")
    
    print("\n🎉 測試完成！")

if __name__ == "__main__":
    try:
        test_smart_classification()
    except KeyboardInterrupt:
        print("\n\n⏹️ 使用者中斷測試")
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
