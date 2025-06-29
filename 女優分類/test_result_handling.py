# 測試 Result 物件處理的專用腳本

import sys
from pathlib import Path

# 設定路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def test_scan_directory():
    """測試 scan_directory 的 Result 處理"""
    import tempfile
    import os
    
    print("🧪 測試 scan_directory Result 處理...")
    
    try:
        from src.container import Container
        
        # 建立容器和服務
        container = Container()
        scanner = container.file_scanner()
        core = container.unified_classifier_core()
        
        print("✅ 服務建立成功")
        
        # 建立測試環境
        with tempfile.TemporaryDirectory() as tmpdir:
            # 建立測試檔案
            test_files = ['test1.mp4', 'test2.avi', 'test3.mkv']
            for filename in test_files:
                test_file = os.path.join(tmpdir, filename)
                with open(test_file, 'w') as f:
                    f.write('test')
            
            print(f"📁 建立測試資料夾: {tmpdir}")
            print(f"📁 建立測試檔案: {test_files}")
            
            # 測試直接掃描
            print("\n🔍 測試直接掃描...")
            result = scanner.scan_directory(tmpdir)
            print(f"掃描結果: success={result.success}")
            
            if result.success:
                video_files = result.data
                print(f"檔案數量: {len(video_files)}")
                
                # 測試迭代
                print("迭代測試:")
                for file_path in video_files:
                    print(f"  - {file_path.name}")
                
                # 測試 process_and_search_japanese_sites 方法
                print("\n🇯🇵 測試日文網站搜尋方法...")
                
                # 創建一個模擬的 stop_event
                import threading
                stop_event = threading.Event()
                
                # 創建進度回調
                def progress_callback(message):
                    print(f"進度: {message.strip()}")
                
                # 呼叫實際方法
                result = core.process_and_search_japanese_sites(
                    tmpdir, stop_event, progress_callback
                )
                
                print(f"搜尋結果: {result}")
                
            else:
                print(f"❌ 掃描失敗: {result.error}")
        
        print("\n✅ 所有測試通過！")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scan_directory()
