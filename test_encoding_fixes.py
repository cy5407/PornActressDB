# -*- coding: utf-8 -*-
"""
測試編碼修復效果的腳本
"""

import sys
from pathlib import Path

# 添加專案路徑
project_root = Path(__file__).parent / '女優分類'
sys.path.insert(0, str(project_root / 'src'))

import logging
from models.config import ConfigManager
from services.web_searcher import WebSearcher
import threading

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_encoding_fixes():
    """測試編碼修復效果"""
    
    logger.info("🧪 開始測試編碼修復效果...")
    
    try:
        # 建立配置管理器
        config = ConfigManager()
        
        # 建立網路搜尋器（已整合編碼修復）
        searcher = WebSearcher(config)
        
        # 測試編碼警告較多的影片編號
        test_codes = ['MIDV-661', 'FSDSS-870', 'MIDV-631']
        
        stop_event = threading.Event()
        
        for code in test_codes:
            logger.info(f"\n🔍 測試搜尋: {code}")
            logger.info("-" * 40)
            
            # 進行搜尋
            result = searcher.search_info(code, stop_event)
            
            if result:
                logger.info(f"✅ 成功找到 {code} 的資訊:")
                logger.info(f"   來源: {result.get('source', 'Unknown')}")
                logger.info(f"   女優: {', '.join(result.get('actresses', []))}")
                logger.info(f"   片商: {result.get('studio', 'Unknown')}")
            else:
                logger.warning(f"⚠️ 未找到 {code} 的資訊")
        
        # 顯示統計資訊
        logger.info("\n📊 搜尋器統計資訊:")
        logger.info("-" * 40)
        
        stats = searcher.get_all_search_stats()
        for searcher_name, searcher_stats in stats.items():
            logger.info(f"{searcher_name}: {searcher_stats}")
        
        logger.info("\n🎉 編碼修復測試完成！")
        logger.info("💡 如果沒有出現大量的編碼警告，說明修復成功。")
        
    except Exception as e:
        logger.error(f"❌ 測試過程中發生錯誤: {e}", exc_info=True)

if __name__ == "__main__":
    test_encoding_fixes()
