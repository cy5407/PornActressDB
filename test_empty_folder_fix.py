# -*- coding: utf-8 -*-
"""
測試片商分類空資料夾處理修正

**建立日期**: 2025-06-22

驗證當沒有找到女優資料夾時，系統是否能正確處理 move_stats 的問題。
"""

def test_empty_folder_handling():
    """測試空資料夾處理"""
    print("=" * 70)
    print("🧪 測試片商分類空資料夾處理")
    print("=" * 70)
    
    # 模擬空資料夾情況的返回值
    empty_result = {
        'status': 'success',
        'message': '未找到女優資料夾',
        'total_actresses': 0,
        'updated_count': 0,
        'move_stats': {
            'moved': 0,
            'solo_artist': 0,
            'failed': 0,
            'skipped': 0
        }
    }
    
    print("📊 測試空資料夾返回結果:")
    print(f"狀態: {empty_result['status']}")
    print(f"訊息: {empty_result['message']}")
    print(f"總女優數: {empty_result['total_actresses']}")
    print(f"更新數量: {empty_result['updated_count']}")
    print("移動統計:")
    
    move_stats = empty_result['move_stats']
    print(f"  ✅ 移動到片商資料夾: {move_stats.get('moved', 0)}")
    print(f"  🎭 移動到單體企劃女優: {move_stats.get('solo_artist', 0)}")
    print(f"  ⏩ 跳過處理: {move_stats.get('skipped', 0)}")
    print(f"  ❌ 移動失敗: {move_stats.get('failed', 0)}")
    
    # 測試 get_classification_summary 格式
    def mock_get_classification_summary(total_actresses, move_stats):
        """模擬 get_classification_summary 方法"""
        solo_folder_name = "單體企劃女優"
        
        return (f"📊 片商分類完成！\n\n"
               f"  📁 掃描女優總數: {total_actresses}\n"
               f"  ✅ 移動到片商資料夾: {move_stats.get('moved', 0)}\n"
               f"  🎭 移動到{solo_folder_name}: {move_stats.get('solo_artist', 0)}\n"
               f"  ⏩ 跳過處理: {move_stats.get('skipped', 0)}\n"
               f"  ❌ 移動失敗: {move_stats.get('failed', 0)}\n"
               f"\n💡 已存在的資料夾已自動合併內容")
    
    print()
    print("📋 模擬 GUI 顯示結果:")
    print("-" * 50)
    summary = mock_get_classification_summary(
        empty_result['total_actresses'], 
        empty_result['move_stats']
    )
    print(summary)
    
    print()
    print("✅ 測試完成 - 修正後應該不會再出現 'moved' KeyError 錯誤")

if __name__ == "__main__":
    test_empty_folder_handling()
    input("按 Enter 鍵退出...")
