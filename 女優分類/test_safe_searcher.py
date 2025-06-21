#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全搜尋器測試腳本 - AI Playground 驗證用
"""
import sys
import threading
from pathlib import Path
import logging

# 將 src 資料夾加入 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_safe_searcher():
    """測試安全搜尋器基本功能"""
    from models.config import ConfigManager
    from services.web_searcher import WebSearcher
    
    logger.info("🧪 開始測試安全搜尋器...")
    
    # 創建配置管理器
    config = ConfigManager()
    
    # 創建 WebSearcher 實例（包含安全搜尋功能）
    searcher = WebSearcher(config)
    
    # 創建停止事件
    stop_event = threading.Event()
    
    # 測試搜尋功能
    test_codes = ['SSIS-123', 'MIDV-456', 'IPX-789']
    
    logger.info("📊 安全搜尋器統計資訊:")
    stats = searcher.get_safe_searcher_stats()
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    logger.info("🔍 開始測試搜尋...")
    
    for code in test_codes:
        try:
            logger.info(f"搜尋番號: {code}")
            result = searcher.search_info(code, stop_event)
            
            if result:
                logger.info(f"✅ 找到結果:")
                logger.info(f"  來源: {result['source']}")
                logger.info(f"  女優: {', '.join(result['actresses'])}")
                logger.info(f"  片商: {result.get('studio', '未知')}")
            else:
                logger.info(f"❌ 未找到結果")
                
        except Exception as e:
            logger.error(f"搜尋 {code} 時發生錯誤: {e}")
        
        # 檢查是否被中止
        if stop_event.is_set():
            break
    
    logger.info("📈 測試完成後的統計:")
    final_stats = searcher.get_safe_searcher_stats()
    cache_stats = final_stats.get('cache_stats', {})
    logger.info(f"  快取項目: {cache_stats.get('valid_entries', 0)}")
    logger.info(f"  過期項目: {cache_stats.get('expired_entries', 0)}")

def demo_safe_features():
    """展示安全搜尋器特色功能"""
    from services.safe_searcher import SafeSearcher, RequestConfig
    
    logger.info("🛡️ 展示安全搜尋器特色功能:")
    
    # 創建自定義配置
    config = RequestConfig(
        min_interval=0.5,
        max_interval=1.5,
        enable_cache=True,
        cache_duration=3600,  # 1小時
        max_retries=2,
        rotate_headers=True
    )
    
    searcher = SafeSearcher(config)
    
    # 展示標頭輪替
    logger.info("🔄 瀏覽器標頭輪替示例:")
    for i in range(3):
        headers = searcher.get_headers()
        user_agent = headers.get('User-Agent', '')
        browser = 'Chrome' if 'Chrome' in user_agent else 'Firefox' if 'Firefox' in user_agent else 'Edge' if 'Edge' in user_agent else '其他'
        logger.info(f"  請求 {i+1}: {browser}")
    
    # 展示統計資訊
    logger.info("📊 安全搜尋器詳細統計:")
    stats = searcher.get_stats()
    logger.info(f"  配置: {stats['config']}")
    logger.info(f"  快取狀態: {stats['cache_stats']}")
    logger.info(f"  瀏覽器標頭數量: {stats['browser_headers_count']}")

def main():
    """主函數"""
    try:
        logger.info("🚀 安全搜尋器測試開始")
        
        # 基本功能測試
        test_safe_searcher()
        
        print("\n" + "="*50 + "\n")
        
        # 特色功能展示
        demo_safe_features()
        
        logger.info("✅ 所有測試完成!")
        
    except KeyboardInterrupt:
        logger.info("⏹️ 測試被使用者中止")
    except Exception as e:
        logger.error(f"❌ 測試過程中發生錯誤: {e}", exc_info=True)

if __name__ == "__main__":
    main()