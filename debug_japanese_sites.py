# -*- coding: utf-8 -*-
"""
日文網站內容調試腳本
"""

import sys
from pathlib import Path

# 添加專案路徑
project_root = Path(__file__).parent / '女優分類'
sys.path.insert(0, str(project_root / 'src'))

import httpx
from services.japanese_site_enhancer import create_japanese_soup
from urllib.parse import quote

def debug_av_wiki(code: str):
    """調試 av-wiki.net 搜尋結果"""
    search_url = f"https://av-wiki.net/?s={quote(code)}&post_type=product"
    
    print(f"🔍 調試 AV-WIKI 搜尋: {code}")
    print(f"URL: {search_url}")
    print("-" * 80)
    
    try:
        with httpx.Client(timeout=20) as client:
            response = client.get(search_url)
            response.raise_for_status()
            
            # 使用日文編碼增強器
            soup = create_japanese_soup(response, search_url)
            
            print("📋 頁面基本資訊:")
            print(f"  狀態碼: {response.status_code}")
            print(f"  頁面標題: {soup.title.text if soup.title else 'None'}")
            print(f"  頁面大小: {len(response.content)} bytes")
            
            print("\n🎭 尋找女優名稱:")
            
            # 方法1: 查找 class="actress-name"
            actress_elements = soup.find_all(class_="actress-name")
            print(f"  actress-name 元素數量: {len(actress_elements)}")
            for i, elem in enumerate(actress_elements[:5]):
                print(f"    [{i}] {elem.text.strip()}")
            
            # 方法2: 查找可能的女優相關類別
            potential_classes = [
                'actress', 'performer', 'model', 'star', 'talent',
                '女優', '出演者', 'キャスト', 'アクトレス'
            ]
            
            for class_name in potential_classes:
                elements = soup.find_all(class_=lambda x: x and class_name in x.lower() if x else False)
                if elements:
                    print(f"  找到 '{class_name}' 相關元素: {len(elements)}")
                    for elem in elements[:3]:
                        print(f"    - {elem.text.strip()[:50]}")
            
            # 方法3: 查找包含番號的內容
            print(f"\n📄 包含番號 '{code}' 的內容:")
            page_text = soup.get_text()
            lines = page_text.split('\n')
            matching_lines = [line.strip() for line in lines if code in line.upper() and line.strip()]
            
            for i, line in enumerate(matching_lines[:10]):
                print(f"  [{i}] {line[:100]}")
            
            # 方法4: 分析網頁結構
            print(f"\n🏗️ 網頁結構分析:")
            
            # 查找主要內容區域
            main_content = soup.find(['main', 'div'], class_=lambda x: x and ('content' in x.lower() or 'main' in x.lower()) if x else False)
            if main_content:
                print(f"  找到主要內容區域: {main_content.name} class={main_content.get('class')}")
            
            # 查找產品/影片相關區域
            product_areas = soup.find_all(['div', 'article'], class_=lambda x: x and ('product' in x.lower() or 'post' in x.lower() or 'item' in x.lower()) if x else False)
            print(f"  找到產品相關區域: {len(product_areas)}")
            
            for i, area in enumerate(product_areas[:3]):
                print(f"    產品區域 [{i}]: {area.name} class={area.get('class')}")
                area_text = area.get_text()[:200].replace('\n', ' ')
                print(f"      內容: {area_text}")
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")

def debug_chiba_f_net(code: str):
    """調試 chiba-f.net 搜尋結果"""
    search_url = f"https://chiba-f.net/search/?keyword={quote(code)}"
    
    print(f"🔍 調試 chiba-f.net 搜尋: {code}")
    print(f"URL: {search_url}")
    print("-" * 80)
    
    try:
        with httpx.Client(timeout=20) as client:
            response = client.get(search_url)
            response.raise_for_status()
            
            # 使用日文編碼增強器
            soup = create_japanese_soup(response, search_url)
            
            print("📋 頁面基本資訊:")
            print(f"  狀態碼: {response.status_code}")
            print(f"  頁面標題: {soup.title.text if soup.title else 'None'}")
            print(f"  頁面大小: {len(response.content)} bytes")
            
            print("\n🎭 尋找女優名稱:")
            
            # 查找 product-div
            product_divs = soup.find_all('div', class_='product-div')
            print(f"  product-div 數量: {len(product_divs)}")
            
            for i, div in enumerate(product_divs[:3]):
                print(f"\n  產品 [{i}]:")
                
                # 查找番號
                pno_element = div.find('div', class_='pno')
                if pno_element:
                    print(f"    番號: {pno_element.text.strip()}")
                
                # 查找女優名稱
                actress_span = div.find('span', class_='fw-bold')
                if actress_span:
                    print(f"    女優: {actress_span.text.strip()}")
                
                # 查找系列
                series_link = div.find('a', href=lambda x: x and '../series/' in x if x else False)
                if series_link:
                    print(f"    系列: {series_link.text.strip()}")
                
                # 顯示完整內容
                div_text = div.get_text()[:300].replace('\n', ' ')
                print(f"    內容: {div_text}")
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    # 測試幾個番號
    test_codes = ['SONE-323', 'SIVR-345']
    
    for code in test_codes:
        print("=" * 100)
        debug_av_wiki(code)
        print("\n")
        debug_chiba_f_net(code)
        print("=" * 100)
        print()
