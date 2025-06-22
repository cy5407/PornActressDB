# -*- coding: utf-8 -*-
"""
測試分離式編碼處理效果
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

# 設定詳細日誌
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_separated_encoding():
    """測試分離式編碼處理"""
    
    logger.info("🧪 測試分離式編碼處理...")
    
    try:
        # 建立配置管理器
        config = ConfigManager()
        
        # 建立網路搜尋器
        searcher = WebSearcher(config)
        
        # 測試編碼問題較嚴重的影片編號
        test_codes = ['MIDV-661', 'FSDSS-870']
        
        stop_event = threading.Event()
        
        for code in test_codes:
            logger.info(f"\n🔍 測試搜尋: {code}")
            logger.info("-" * 50)
            
            # 進行搜尋
            result = searcher.search_info(code, stop_event)
            
            if result:
                logger.info(f"✅ 成功找到 {code}:")
                logger.info(f"   來源: {result.get('source', 'Unknown')}")
                logger.info(f"   女優: {', '.join(result.get('actresses', []))}")
                logger.info(f"   片商: {result.get('studio', 'Unknown')}")
            else:
                logger.warning(f"⚠️ 未找到 {code} 的資訊")
        
        logger.info("\n📊 檢查編碼警告...")
        logger.info("如果沒有 'bs4.dammit - WARNING' 出現，說明編碼問題已解決")
        
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}", exc_info=True)

if __name__ == "__main__":
    test_separated_encoding()