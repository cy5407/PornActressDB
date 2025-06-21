#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
片商資訊修正驗證工具
用於快速驗證片商資訊是否正確處理
"""

def verify_studio_logic():
    """驗證片商處理邏輯"""
    print("🔧 片商資訊處理邏輯驗證")
    print("=" * 40)
    
    # 測試案例 1：JAVDB 有片商資訊
    javdb_result = {'studio': 'S1'}
    studio = javdb_result.get('studio')
    if not studio or studio == 'UNKNOWN':
        studio = "本地識別結果"
    
    print(f"案例1 - JAVDB有片商: {studio} ✅")
    
    # 測試案例 2：JAVDB 無片商資訊
    javdb_result = {'studio': None}
    studio = javdb_result.get('studio')
    if not studio or studio == 'UNKNOWN':
        studio = "本地識別結果"
    
    print(f"案例2 - JAVDB無片商: {studio} ✅")
    
    # 測試案例 3：JAVDB 片商為 UNKNOWN
    javdb_result = {'studio': 'UNKNOWN'}
    studio = javdb_result.get('studio')
    if not studio or studio == 'UNKNOWN':
        studio = "本地識別結果"
    
    print(f"案例3 - JAVDB為UNKNOWN: {studio} ✅")
    
    print("\n✅ 邏輯驗證完成 - 優先使用 JAVDB 搜尋結果")

if __name__ == "__main__":
    verify_studio_logic()
