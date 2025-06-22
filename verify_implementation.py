# -*- coding: utf-8 -*-
"""
驗證分離式編碼處理實施
"""

from pathlib import Path
import re

def verify_implementation():
    """驗證分離式編碼處理實施"""
    
    print("🔍 驗證分離式編碼處理實施...")
    project_root = Path(__file__).parent / '女優分類'
    
    checks = []
    
    # 1. 檢查日文網站增強器檔案
    japanese_enhancer_file = project_root / 'src' / 'services' / 'japanese_site_enhancer.py'
    if japanese_enhancer_file.exists():
        with open(japanese_enhancer_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'cp932' in content and 'av-wiki.net' in content and 'chiba-f.net' in content:
                checks.append("✅ 日文網站增強器檔案存在且包含正確配置")
            else:
                checks.append("❌ 日文網站增強器檔案存在但配置不完整")
    else:
        checks.append("❌ 日文網站增強器檔案不存在")
    
    # 2. 檢查 web_searcher.py 是否匯入日文增強器
    web_searcher_file = project_root / 'src' / 'services' / 'web_searcher.py'
    if web_searcher_file.exists():
        with open(web_searcher_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'from .japanese_site_enhancer import' in content:
                checks.append("✅ web_searcher.py 正確匯入日文網站增強器")
            else:
                checks.append("❌ web_searcher.py 未匯入日文網站增強器")
            
            if 'japanese_searcher' in content:
                checks.append("✅ web_searcher.py 包含日文網站專用搜尋器")
            else:
                checks.append("❌ web_searcher.py 未包含日文網站專用搜尋器")
            
            if 'create_japanese_soup' in content:
                checks.append("✅ web_searcher.py 使用日文編碼增強函式")
            else:
                checks.append("❌ web_searcher.py 未使用日文編碼增強函式")
    else:
        checks.append("❌ web_searcher.py 檔案不存在")
    
    # 3. 檢查 JAVDB 搜尋器保持原狀
    javdb_searcher_file = project_root / 'src' / 'services' / 'safe_javdb_searcher.py'
    if javdb_searcher_file.exists():
        with open(javdb_searcher_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'encoding_enhancer' not in content and 'japanese_site_enhancer' not in content:
                checks.append("✅ JAVDB 搜尋器保持原有標準編碼處理")
            else:
                checks.append("❌ JAVDB 搜尋器被污染了編碼增強器")
    else:
        checks.append("❌ JAVDB 搜尋器檔案不存在")
    
    # 4. 檢查舊的編碼增強器是否已移除
    old_enhancer_file = project_root / 'src' / 'services' / 'encoding_enhancer.py'
    if not old_enhancer_file.exists():
        checks.append("✅ 舊的編碼增強器已移除，避免衝突")
    else:
        checks.append("⚠️ 舊的編碼增強器仍存在，可能造成衝突")
    
    # 5. 輸出結果
    print("\n📋 檢查結果:")
    for check in checks:
        print(f"   {check}")
    
    success_count = len([c for c in checks if c.startswith("✅")])
    total_count = len([c for c in checks if not c.startswith("⚠️")])
    
    print(f"\n📊 總結: {success_count}/{total_count} 項檢查通過")
    
    if success_count == total_count:
        print("🎉 分離式編碼處理實施完成！")
        print("\n🎯 預期效果:")
        print("   - 日文網站 (av-wiki.net, chiba-f.net) 使用 CP932 編碼")
        print("   - JAVDB 保持 UTF-8 標準編碼")
        print("   - 日文網站使用較短延遲 (0.5-1.5秒)")
        print("   - 編碼警告問題應已解決")
        return True
    else:
        print("❌ 實施不完整，請檢查失敗項目")
        return False

if __name__ == "__main__":
    verify_implementation()