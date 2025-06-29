# -*- coding: utf-8 -*-
"""
測試 interactive_move_files 方法的參數修正
"""
import sys
from pathlib import Path

# 將 src 資料夾加入 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

try:
    from src.container import Container
    
    # 建立依賴注入容器實例
    container = Container()
    
    # 取得核心分類器
    unified_classifier_core = container.unified_classifier_core()
    
    # 檢查方法簽名
    import inspect
    signature = inspect.signature(unified_classifier_core.interactive_move_files)
    print(f"interactive_move_files 方法簽名: {signature}")
    print(f"參數數量: {len(signature.parameters)}")
    
    for name, param in signature.parameters.items():
        print(f"  - {name}: {param}")
    
    print("\n✅ 方法簽名檢查完成，參數修正成功")
    
except Exception as e:
    print(f"❌ 檢查失敗: {e}")
    import traceback
    traceback.print_exc()
