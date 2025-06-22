#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細的日文網站調試腳本
分析編碼問題和 HTML 結構變化
"""

import httpx
import chardet
from bs4 import BeautifulSoup
from urllib.parse import quote
import sys
import time

def test_encoding_methods(content_bytes, url):
    """測試不同編碼方法"""
    print(f"\n🔍 測試不同編碼方法 - {url}")
    print("=" * 60)
    
    encodings_to_test = ['utf-8', 'cp932', 'shift_jis', 'euc-jp', 'iso-2022-jp']
    
    # 1. chardet 自動檢測
    detected = chardet.detect(content_bytes)
    print(f"📊 chardet 檢測結果: {detected}")
    
    # 2. 測試各種編碼
    for encoding in encodings_to_test:
        try:
            decoded_text = content_bytes.decode(encoding, errors='replace')
            replacement_ratio = decoded_text.count('�') / len(decoded_text) if decoded_text else 1.0
            print(f"  {encoding:12}: 替換比例 {replacement_ratio:.3f}")
            
            # 如果替換比例很低，顯示前200字符
            if replacement_ratio < 0.1:
                preview = decoded_text[:200].replace('\n', ' ').replace('\r', ' ')
                print(f"    預覽: {preview}...")
                
        except (UnicodeDecodeError, LookupError) as e:
            print(f"  {encoding:12}: 解碼失敗 - {e}")
    
    return detected.get('encoding', 'utf-8') if detected else 'utf-8'

def analyze_html_structure(soup, site_name):
    """分析 HTML 結構"""
    print(f"\n🏗️ 分析 {site_name} HTML 結構")
    print("=" * 60)
    
    # 基本統計
    print(f"📄 總文字長度: {len(soup.get_text())}")
    print(f"🏷️  總標籤數量: {len(soup.find_all())}")
    
    # 搜尋相關的類別和ID
    classes_to_check = [
        'actress-name', 'product-div', 'search-result', 'result',
        'product', 'item', 'card', 'entry', 'post', 'content'
    ]
    
    print(f"\n🔍 檢查常見類別:")
    for class_name in classes_to_check:
        elements = soup.find_all(class_=class_name)
        if elements:
            print(f"  ✅ .{class_name}: 找到 {len(elements)} 個元素")
            # 顯示第一個元素的部分內容
            first_text = elements[0].get_text()[:100].strip().replace('\n', ' ')
            if first_text:
                print(f"      內容範例: {first_text}...")
        else:
            print(f"  ❌ .{class_name}: 未找到")
    
    # 檢查可能的女優名稱模式
    print(f"\n👩 尋找可能的女優名稱:")
    potential_actress_patterns = [
        soup.find_all('a', href=lambda x: x and 'actress' in x.lower()),
        soup.find_all('span', class_=lambda x: x and 'name' in x.lower()),
        soup.find_all('div', class_=lambda x: x and 'performer' in x.lower()),
        soup.find_all(text=lambda x: x and any(char in x for char in '女優演員出演者'))
    ]
    
    for i, pattern_results in enumerate(potential_actress_patterns):
        if pattern_results:
            print(f"  模式 {i+1}: 找到 {len(pattern_results)} 個可能結果")
            for result in pattern_results[:3]:  # 只顯示前3個
                if hasattr(result, 'get_text'):
                    text = result.get_text().strip()
                else:
                    text = str(result).strip()
                if text:
                    print(f"    - {text[:50]}...")

def test_japanese_sites():
    """測試日文網站的實際回應"""
    test_codes = ['SONE-553', 'FWAY-031']
    
    sites = [
        {
            'name': 'AV-WIKI',
            'url_template': 'https://av-wiki.net/?s={}&post_type=product',
            'expected_classes': ['actress-name']
        },
        {
            'name': 'chiba-f.net',  
            'url_template': 'https://chiba-f.net/search/?keyword={}',
            'expected_classes': ['product-div', 'fw-bold']
        }
    ]
    
    with httpx.Client(timeout=30) as client:
        for site in sites:
            print(f"\n{'='*80}")
            print(f"🌐 測試網站: {site['name']}")
            print(f"{'='*80}")
            
            for code in test_codes:
                print(f"\n🔎 測試番號: {code}")
                url = site['url_template'].format(quote(code))
                print(f"📋 請求 URL: {url}")
                
                try:
                    # 發送請求
                    response = client.get(url, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    })
                    
                    print(f"📊 回應狀態: {response.status_code}")
                    print(f"📏 內容長度: {len(response.content)} bytes")
                    
                    if response.status_code == 200:
                        # 分析編碼
                        best_encoding = test_encoding_methods(response.content, url)
                        
                        # 嘗試用最佳編碼解析
                        try:
                            soup = BeautifulSoup(response.content, 'html.parser', from_encoding=best_encoding)
                            analyze_html_structure(soup, site['name'])
                            
                            # 檢查期望的類別
                            print(f"\n🎯 檢查期望的類別:")
                            for expected_class in site['expected_classes']:
                                elements = soup.find_all(class_=expected_class)
                                print(f"  .{expected_class}: {len(elements)} 個元素")
                                
                        except Exception as e:
                            print(f"❌ HTML 解析失敗: {e}")
                    else:
                        print(f"❌ 請求失敗: {response.status_code}")
                        print(f"💬 回應內容: {response.text[:200]}...")
                        
                except Exception as e:
                    print(f"❌ 請求發生錯誤: {e}")
                
                print(f"\n⏰ 等待 2 秒...")
                time.sleep(2)

if __name__ == "__main__":
    print("🚀 啟動日文網站詳細調試")
    print("此腳本將分析日文網站的編碼和 HTML 結構問題")
    print("=" * 80)
    
    test_japanese_sites()
    
    print("\n" + "=" * 80)
    print("🎉 調試完成！請檢查以上輸出來診斷問題。")
