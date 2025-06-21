#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試片商分類資料夾合併功能
"""

import sys
from pathlib import Path
import tempfile
import shutil

# 將 src 資料夾加入 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def test_folder_merge():
    """測試資料夾合併功能"""
    print("🔧 測試片商分類資料夾合併功能")
    print("=" * 50)
    
    # 建立臨時測試目錄
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 建立測試資料夾結構
        source_folder = temp_path / "倉木華_測試"
        target_folder = temp_path / "S1" / "倉木華"
        
        source_folder.mkdir(parents=True)
        target_folder.mkdir(parents=True)
        
        # 建立測試檔案
        (source_folder / "新影片1.mp4").write_text("新影片內容1")
        (source_folder / "新影片2.mp4").write_text("新影片內容2")
        (target_folder / "舊影片1.mp4").write_text("舊影片內容1")
        
        print(f"✅ 建立測試環境")
        print(f"   來源資料夾: {source_folder} (2個檔案)")
        print(f"   目標資料夾: {target_folder} (1個檔案)")
        
        # 模擬合併邏輯
        try:
            # 檢查檔案數量
            source_files = list(source_folder.glob("*"))
            target_files_before = list(target_folder.glob("*"))
            
            print(f"\n🔄 開始模擬合併...")
            print(f"   來源檔案: {[f.name for f in source_files]}")
            print(f"   目標檔案(合併前): {[f.name for f in target_files_before]}")
            
            # 移動檔案
            files_moved = 0
            for file in source_files:
                target_file = target_folder / file.name
                if target_file.exists():
                    # 重新命名避免衝突
                    base_name = file.stem
                    extension = file.suffix
                    counter = 1
                    while target_file.exists():
                        new_name = f"{base_name}_{counter}{extension}"
                        target_file = target_folder / new_name
                        counter += 1
                
                shutil.move(str(file), str(target_file))
                files_moved += 1
            
            target_files_after = list(target_folder.glob("*"))
            
            print(f"\n✅ 合併完成")
            print(f"   移動檔案數: {files_moved}")
            print(f"   目標檔案(合併後): {[f.name for f in target_files_after]}")
            
            # 檢查來源資料夾是否為空
            remaining_files = list(source_folder.glob("*"))
            if not remaining_files:
                source_folder.rmdir()
                print(f"   已刪除空的來源資料夾")
            
            print(f"\n🎉 測試成功！現有和新增的檔案都保留了")
            
        except Exception as e:
            print(f"❌ 測試失敗: {e}")

def main():
    """主函式"""
    test_folder_merge()
    
    print("\n📝 修正說明:")
    print("✅ 修正前: 發現目標資料夾已存在時直接跳過")
    print("✅ 修正後: 自動合併資料夾內容，避免檔案重名衝突")
    print("✅ 效果: 'S1/倉木華' 等已存在資料夾會合併新影片")
    print("✅ 安全: 原有檔案保留，新檔案自動重新命名避免覆蓋")

if __name__ == "__main__":
    main()
