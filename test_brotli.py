#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Brotli 解壓功能
"""

import httpx
import brotli
from bs4 import BeautifulSoup
from urllib.parse import quote

def test_brotli_decompression():
    """測試 Brotli 解壓功能"""
    print("🚀 測試 Brotli 解壓功能")
    print("=" * 60)
    
    test_urls = [
        ("AV-WIKI SONE-553", "https://av-wiki.net/?s=SONE-553&post_type=product"),
        ("chiba-f.net SONE-553", "https://chiba-f.net/search/?keyword=SONE-553"),
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        for test_name, url in test_urls:
            print(f"\n🔍 測試: {test_name}")
            print(f"📋 URL: {url}")
            print("-" * 60)
            
            try:
                response = client.get(url, headers=headers)
                print(f"📊 回應狀態: {response.status_code}")
                print(f"📏 壓縮內容長度: {len(response.content)} bytes")
                
                content_encoding = response.headers.get('content-encoding', 'none')
                print(f"🗜️ 內容編碼: {content_encoding}")
                
                # 嘗試 Brotli 解壓
                if content_encoding == 'br':
                    print("✨ 嘗試 Brotli 解壓...")
                    try:
                        decompressed = brotli.decompress(response.content)
                        print(f"📏 解壓後長度: {len(decompressed)} bytes")
                        
                        # 嘗試 UTF-8 解碼
                        text_content = decompressed.decode('utf-8', errors='replace')
                        replacement_ratio = text_content.count('\ufffd') / len(text_content) if text_content else 1.0
                        print(f"📝 UTF-8 解碼替換比例: {replacement_ratio:.3f}")
                        
                        # 檢查 HTML 結構
                        if '<html' in text_content.lower() and '</html>' in text_content.lower():
                            print("✅ 包含完整 HTML 結構")
                            
                            # 解析 HTML
                            soup = BeautifulSoup(text_content, 'html.parser')
                            print(f"📄 解析到 {len(soup.find_all())} 個 HTML 標籤")
                            
                            # 檢查期望的元素
                            if 'av-wiki' in url:
                                actress_elements = soup.find_all(class_="actress-name")
                                print(f"🎭 找到 {len(actress_elements)} 個 actress-name 元素")
                                
                                # 如果沒找到，嘗試其他可能的選擇器
                                if not actress_elements:
                                    # 嘗試找包含女優相關的元素
                                    potential_elements = []
                                    for selector in ['a[href*="actress"]', '.performer', '.cast', '[class*="actress"]']:
                                        elements = soup.select(selector)
                                        if elements:
                                            potential_elements.extend(elements)
                                    print(f"🔍 找到 {len(potential_elements)} 個潛在女優元素")
                                    
                                    # 顯示前幾個元素的內容
                                    for i, elem in enumerate(potential_elements[:3]):
                                        text = elem.get_text().strip()
                                        print(f"    {i+1}. {text[:50]}...")
                                        
                            elif 'chiba-f' in url:
                                product_divs = soup.find_all('div', class_='product-div')
                                print(f"📦 找到 {len(product_divs)} 個 product-div 元素")
                                
                                # 嘗試找其他產品相關元素
                                if not product_divs:
                                    for selector in ['.product', '.item', '.card', '[class*="product"]']:
                                        elements = soup.select(selector)
                                        if elements:
                                            print(f"🔍 找到 {len(elements)} 個 {selector} 元素")
                            
                            # 顯示頁面標題和主要內容結構
                            title = soup.find('title')
                            if title:
                                print(f"📋 頁面標題: {title.get_text().strip()}")
                            
                            # 顯示主要內容區域
                            main_content = soup.find('main') or soup.find('div', id='main') or soup.find('div', class_='content')
                            if main_content:
                                content_text = main_content.get_text().strip()[:200]
                                print(f"📖 主要內容預覽: {content_text}...")
                                
                        else:
                            print("❌ 不包含完整 HTML 結構")
                            preview = text_content[:300].replace('\n', ' ')
                            print(f"📄 內容預覽: {preview}...")
                            
                    except Exception as e:
                        print(f"❌ Brotli 解壓失敗: {e}")
                        
                else:
                    print(f"ℹ️ 不是 Brotli 編碼，是: {content_encoding}")
                    
            except Exception as e:
                print(f"❌ 請求失敗: {e}")
            
            print("\n⏰ 等待 2 秒...")
            import time
            time.sleep(2)

if __name__ == "__main__":
    test_brotli_decompression()
