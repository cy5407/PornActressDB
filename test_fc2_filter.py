#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 FC2/PPV 過濾功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.extractor import UnifiedCodeExtractor

def test_fc2_ppv_filter():
    """測試 FC2/PPV 檔案過濾功能"""
    extractor = UnifiedCodeExtractor()
    
    # 測試案例：應該被過濾的檔案
    should_skip = [
        "FC2PPV-4075437.mp4",
        "FC2PPV-4595652-01.mp4", 
        "FC2-123456.mp4",
        "FC2_123456.mp4",
        "PPV-46563.mp4",
        "PPV-45925.mp4",
        "PPV_123456.mp4",
        "FC2-PPV-123456.mp4",
        "FC2_PPV_123456.mp4"
    ]
    
    # 測試案例：不應該被過濾的檔案
    should_not_skip = [
        "PPPE-353.mp4",
        "SDJS-303.mp4", 
        "STARS-707.mp4",
        "MEYD-978.mp4",
        "KAGP-340.mp4"
    ]
    
    print("=== 測試 FC2/PPV 過濾功能 ===\n")
    
    print("應該被過濾的檔案:")
    for filename in should_skip:
        result = extractor.extract_code(filename)
        status = "✓ 正確過濾" if result is None else f"✗ 錯誤解析為: {result}"
        print(f"  {filename:<25} → {status}")
    
    print("\n不應該被過濾的檔案:")
    for filename in should_not_skip:
        result = extractor.extract_code(filename)
        status = f"✓ 正確解析為: {result}" if result else "✗ 錯誤過濾"
        print(f"  {filename:<25} → {status}")

if __name__ == "__main__":
    test_fc2_ppv_filter()
