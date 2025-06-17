#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接測試 EBWH-226
"""

import requests
from bs4 import BeautifulSoup


def test_ebwh_226():
    """直接測試 EBWH-226"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    url = "https://chiba-f.net/search/?keyword=EBWH-226"
    print(f"🔍 測試 URL: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"📡 狀態碼: {response.status_code}")
        print(f"📄 內容長度: {len(response.text)} 字元")
        
        if response.status_code == 200:
            # 檢查是否包含 EBWH-226
            if 'EBWH-226' in response.text or 'ebwh-226' in response.text or 'ebwh00226' in response.text:
                print("✅ 找到 EBWH-226 相關內容!")
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 查找所有可能的產品容器
                product_containers = [
                    soup.find_all('div', class_='product-div'),
                    soup.find_all('div', {'class': lambda x: x and 'product' in str(x)}),
                    soup.find_all('div', {'class': lambda x: x and 'col-sm' in str(x)})
                ]
                
                total_found = 0
                for containers in product_containers:
                    total_found += len(containers)
                    if containers:
                        print(f"📦 找到 {len(containers)} 個產品容器")
                        break
                
                if total_found == 0:
                    print("⚠️ 沒有找到產品容器，檢查頁面結構...")
                    # 查找包含 EBWH 的任何元素
                    ebwh_elements = soup.find_all(text=lambda text: text and 'EBWH' in text)
                    print(f"🔍 找到 {len(ebwh_elements)} 個包含 EBWH 的文字元素")
                    for elem in ebwh_elements[:3]:
                        print(f"  📝 {elem.strip()}")
                
                # 嘗試查找女優名稱
                actress_elements = soup.find_all(['span', 'a', 'div'], {'class': lambda x: x and 'bold' in str(x)})
                if actress_elements:
                    print(f"👩 可能的女優名稱:")
                    for elem in actress_elements[:5]:
                        text = elem.text.strip()
                        if text and len(text) < 20:  # 過濾掉太長的文字
                            print(f"  👤 {text}")
                
            else:
                print("❌ 未找到 EBWH-226 相關內容")
                print("🔍 檢查頁面是否為搜尋結果頁...")
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('title')
                if title:
                    print(f"📋 頁面標題: {title.text}")
        else:
            print(f"❌ HTTP 錯誤: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 請求錯誤: {str(e)}")


if __name__ == "__main__":
    test_ebwh_226()
