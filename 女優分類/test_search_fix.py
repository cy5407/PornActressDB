#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修復後的網路搜尋功能
"""

import sys
from pathlib import Path

# 將 src 資料夾加入 Python 路徑
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

import logging
from services.web_searcher import UnifiedWebSearcher

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_search_functionality():
    """測試搜尋功能"""
    logger = logging.getLogger(__name__)
    
    # 初始化搜尋器
    searcher = UnifiedWebSearcher()
    
    # 測試番號
    test_codes = ["SONE-280", "SONE-418"]
    
    for code in test_codes:
        logger.info(f"🔍 測試搜尋番號: {code}")
        
        try:
            # 測試 AV-WIKI 搜尋
            result = searcher.search_av_wiki(code)
            if result:
                logger.info(f"✅ AV-WIKI 搜尋成功: {result}")
            else:
                logger.warning(f"⚠️ AV-WIKI 搜尋失敗: {code}")
            
            # 測試 chiba-f.net 搜尋
            result = searcher.search_chiba_f_net(code)
            if result:
                logger.info(f"✅ chiba-f.net 搜尋成功: {result}")
            else:
                logger.warning(f"⚠️ chiba-f.net 搜尋失敗: {code}")
                
        except Exception as e:
            logger.error(f"❌ 搜尋 {code} 時發生錯誤: {e}", exc_info=True)
        
        logger.info("-" * 50)

if __name__ == "__main__":
    test_search_functionality()