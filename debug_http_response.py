#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP 回應分析腳本 - 檢查壓縮和內容問題
"""

import httpx
import gzip
import zlib
from bs4 import BeautifulSoup
from urllib.parse import quote

def analyze_response_details(url, test_name):
    """詳細分析 HTTP 回應"""
    print(f"\n{'='*60}")
    print(f"🔍 分析: {test_name}")
    print(f"📋 URL: {url}")
    print(f"{'='*60}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',  # 支援壓縮
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            
            print(f"📊 回應狀態: {response.status_code}")
            print(f"📏 原始內容長度: {len(response.content)} bytes")
            print(f"🔗 最終 URL: {response.url}")
            
            # 檢查回應標頭
            print(f"\n📄 重要標頭:")
            important_headers = ['content-type', 'content-encoding', 'transfer-encoding', 'content-length']
            for header in important_headers:
                value = response.headers.get(header, 'N/A')
                print(f"  {header}: {value}")
            
            # 嘗試解壓縮內容
            content = response.content
            print(f"\n🗜️ 壓縮檢測:")
            
            # 檢查是否為 gzip
            if content.startswith(b'\x1f\x8b'):
                print("  ✅ 檢測到 gzip 壓縮")
                try:
                    decompressed = gzip.decompress(content)
                    print(f"  📏 解壓後長度: {len(decompressed)} bytes")
                    content = decompressed
                except Exception as e:
                    print(f"  ❌ gzip 解壓失敗: {e}")
            
            # 檢查是否為 deflate
            elif response.headers.get('content-encoding') == 'deflate':
                print("  ✅ 檢測到 deflate 壓縮")
                try:
                    decompressed = zlib.decompress(content)
                    print(f"  📏 解壓後長度: {len(decompressed)} bytes")
                    content = decompressed
                except Exception as e:
                    print(f"  ❌ deflate 解壓失敗: {e}")
            else:
                print("  ℹ️ 未檢測到已知壓縮格式")
            
            # 嘗試 UTF-8 解碼
            print(f"\n📝 內容分析:")
            try:
                text_content = content.decode('utf-8', errors='replace')
                replacement_ratio = text_content.count('\ufffd') / len(text_content) if text_content else 1.0
                print(f"  UTF-8 解碼替換比例: {replacement_ratio:.3f}")
                
                # 檢查是否為有效的 HTML
                if '<html' in text_content.lower() and '</html>' in text_content.lower():
                    print("  ✅ 包含完整 HTML 結構")
                    
                    # 解析 HTML
                    soup = BeautifulSoup(text_content, 'html.parser')
                    print(f"  📄 解析到 {len(soup.find_all())} 個 HTML 標籤")
                    
                    # 檢查是否有 JavaScript 重定向或動態載入
                    scripts = soup.find_all('script')
                    if scripts:
                        print(f"  🎯 找到 {len(scripts)} 個 script 標籤")
                        for i, script in enumerate(scripts[:3]):  # 只檢查前3個
                            script_text = script.get_text()
                            if 'window.location' in script_text or 'redirect' in script_text.lower():
                                print(f"    Script {i+1}: 可能包含重定向邏輯")
                            elif 'ajax' in script_text.lower() or 'fetch' in script_text.lower():
                                print(f"    Script {i+1}: 可能包含動態載入邏輯")
                    
                    # 尋找搜尋結果相關的元素
                    search_indicators = [
                        ('div', 'class', ['search-result', 'search-results', 'results']),
                        ('div', 'class', ['product', 'product-item', 'product-div']),
                        ('div', 'class', ['actress', 'actress-name', 'performer']),
                        ('div', 'id', ['search-results', 'content', 'main']),
                    ]
                    
                    print(f"  🔍 搜尋結果元素:")
                    for tag, attr, values in search_indicators:
                        for value in values:
                            elements = soup.find_all(tag, {attr: value})
                            if elements:
                                print(f"    ✅ {tag}[{attr}='{value}']: {len(elements)} 個")
                            
                    # 顯示前 500 字符的內容預覽
                    clean_text = ' '.join(text_content.split())[:500]
                    print(f"  📖 內容預覽: {clean_text}...")
                    
                else:
                    print("  ❌ 不是有效的 HTML 結構")
                    # 顯示原始內容的前 200 字符
                    preview = text_content[:200].replace('\n', ' ').replace('\r', ' ')
                    print(f"  📄 原始內容預覽: {preview}...")
                    
            except Exception as e:
                print(f"  ❌ UTF-8 解碼失敗: {e}")
                # 顯示二進制內容的十六進制表示
                hex_preview = content[:50].hex()
                print(f"  🔍 十六進制預覽: {hex_preview}")
                
    except Exception as e:
        print(f"❌ 請求失敗: {e}")

def main():
    """主要測試函式"""
    print("🚀 HTTP 回應詳細分析")
    print("=" * 80)
    
    test_cases = [
        ("AV-WIKI SONE-553", "https://av-wiki.net/?s=SONE-553&post_type=product"),
        ("chiba-f.net SONE-553", "https://chiba-f.net/search/?keyword=SONE-553"),
        ("AV-WIKI 首頁", "https://av-wiki.net/"),
        ("chiba-f.net 首頁", "https://chiba-f.net/"),
    ]
    
    for test_name, url in test_cases:
        analyze_response_details(url, test_name)
        print(f"\n⏰ 等待 3 秒...")
        import time
        time.sleep(3)
    
    print(f"\n{'='*80}")
    print("🎉 分析完成！")

if __name__ == "__main__":
    main()
