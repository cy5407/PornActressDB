#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 httpx 自動解壓和手動處理
"""

import httpx
import brotli
from bs4 import BeautifulSoup

def test_httpx_decompression():
    """測試 httpx 的自動解壓功能"""
    print("🚀 測試 httpx 自動解壓 vs 手動處理")
    print("=" * 80)
    
    url = "https://av-wiki.net/?s=SONE-553&post_type=product"
    
    # 測試 1: 讓 httpx 自動處理壓縮
    print("\n📋 測試 1: httpx 自動處理")
    print("-" * 40)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    
    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(url, headers=headers)
            
            print(f"📊 狀態碼: {response.status_code}")
            print(f"📏 response.content 長度: {len(response.content)}")
            print(f"📄 response.text 長度: {len(response.text)}")
            print(f"🗜️ content-encoding: {response.headers.get('content-encoding', 'none')}")
            print(f"🔤 charset: {response.charset}")
            
            # 檢查 response.text 是否可讀
            text = response.text
            if '<html' in text.lower() and '</html>' in text.lower():
                print("✅ response.text 包含有效 HTML")
                
                soup = BeautifulSoup(text, 'html.parser')
                print(f"📄 解析到 {len(soup.find_all())} 個 HTML 標籤")
                
                # 檢查頁面標題
                title = soup.find('title')
                if title:
                    print(f"📋 頁面標題: {title.get_text().strip()}")
                
                # 檢查是否有搜尋結果
                actress_elements = soup.find_all(class_="actress-name")
                print(f"🎭 actress-name 元素: {len(actress_elements)}")
                
                # 檢查其他可能的女優相關元素
                potential_selectors = [
                    'a[href*="actress"]',
                    '.performer', '.cast', '.star',
                    '[class*="actress"]', '[class*="performer"]',
                    'a[href*="star"]'
                ]
                
                for selector in potential_selectors:
                    elements = soup.select(selector)
                    if elements:
                        print(f"🔍 {selector}: {len(elements)} 個元素")
                        for i, elem in enumerate(elements[:2]):  # 顯示前2個
                            text_content = elem.get_text().strip()
                            href = elem.get('href', '')
                            print(f"    {i+1}. {text_content[:30]}... (href: {href[:50]}...)")
                
                # 檢查是否有 "No results" 或類似的文字
                page_text = soup.get_text().lower()
                no_result_indicators = ['no results', 'no matches', 'not found', '検索結果がありません', '見つかりません']
                for indicator in no_result_indicators:
                    if indicator in page_text:
                        print(f"⚠️ 發現 '無結果' 指示器: {indicator}")
                        
                # 顯示頁面主要結構
                main_containers = soup.find_all(['main', 'div'], class_=lambda x: x and any(
                    keyword in x.lower() for keyword in ['content', 'main', 'search', 'result']
                ))
                print(f"📦 主要容器: {len(main_containers)} 個")
                
                if main_containers:
                    main_text = main_containers[0].get_text().strip()[:300]
                    print(f"📖 主要內容預覽: {main_text}...")
                    
            else:
                print("❌ response.text 不包含有效 HTML")
                # 檢查前 200 字符
                preview = text[:200]
                print(f"📄 文字內容預覽: {preview}...")
                
                # 檢查是否仍然是二進制數據
                if any(ord(c) > 127 for c in preview):
                    print("⚠️ 內容包含非 ASCII 字符，可能仍是編碼問題")
                    
                    # 嘗試不同編碼
                    encodings = ['cp932', 'shift_jis', 'euc-jp', 'iso-2022-jp']
                    for encoding in encodings:
                        try:
                            decoded = response.content.decode(encoding, errors='replace')
                            replacement_ratio = decoded.count('\ufffd') / len(decoded) if decoded else 1.0
                            print(f"  {encoding}: 替換比例 {replacement_ratio:.3f}")
                            if replacement_ratio < 0.1:
                                print(f"    ✅ {encoding} 可能有效")
                                break
                        except:
                            pass
                            
    except Exception as e:
        print(f"❌ 請求失敗: {e}")

    # 測試 2: 禁用自動解壓縮
    print(f"\n📋 測試 2: 禁用自動解壓縮")
    print("-" * 40)
    
    headers_no_encoding = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
        # 不包含 Accept-Encoding 以避免壓縮
    }
    
    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(url, headers=headers_no_encoding)
            
            print(f"📊 狀態碼: {response.status_code}")
            print(f"📏 content 長度: {len(response.content)}")
            print(f"🗜️ content-encoding: {response.headers.get('content-encoding', 'none')}")
            
            text = response.text
            if '<html' in text.lower() and '</html>' in text.lower():
                print("✅ 未壓縮版本包含有效 HTML")
                
                soup = BeautifulSoup(text, 'html.parser')
                print(f"📄 解析到 {len(soup.find_all())} 個 HTML 標籤")
                
                actress_elements = soup.find_all(class_="actress-name")
                print(f"🎭 actress-name 元素: {len(actress_elements)}")
                
            else:
                print("❌ 未壓縮版本也不包含有效 HTML")
                
    except Exception as e:
        print(f"❌ 禁用壓縮的請求失敗: {e}")

if __name__ == "__main__":
    test_httpx_decompression()
