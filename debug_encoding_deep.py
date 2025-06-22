# -*- coding: utf-8 -*-
"""
深度編碼分析腳本 - 專門分析 chiba-f.net 的編碼問題
"""

import httpx
import re
from bs4 import BeautifulSoup
from urllib.parse import quote

def analyze_encoding_issues():
    """深度分析 chiba-f.net 的編碼問題"""
    
    # 測試番號
    test_code = "SSIS-678"
    search_url = f"https://chiba-f.net/search/?keyword={quote(test_code)}"
    
    print(f"🔍 分析 chiba-f.net 編碼問題")
    print(f"📡 測試 URL: {search_url}")
    print("=" * 60)
    
    try:
        # 獲取原始回應
        with httpx.Client(timeout=30.0) as client:
            response = client.get(search_url)
            response.raise_for_status()
        
        print(f"📋 HTTP 狀態碼: {response.status_code}")
        print(f"📋 回應編碼: {response.encoding}")
        print(f"📋 Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"📋 內容長度: {len(response.content)} 位元組")
        print()
        
        # 測試不同編碼
        encodings_to_test = ['cp932', 'shift_jis', 'euc-jp', 'utf-8', 'iso-2022-jp']
        
        best_results = []
        
        for encoding in encodings_to_test:
            print(f"🧪 測試編碼: {encoding}")
            try:
                # 解碼內容
                decoded_content = response.content.decode(encoding, errors='replace')
                replacement_count = decoded_content.count('\ufffd')
                replacement_ratio = replacement_count / len(decoded_content) if decoded_content else 1.0
                
                print(f"   替換字元數量: {replacement_count}")
                print(f"   替換比例: {replacement_ratio:.4f}")
                
                # 創建 BeautifulSoup
                soup = BeautifulSoup(decoded_content, "html.parser")
                
                # 查找產品區塊
                product_divs = soup.find_all('div', class_='product-div')
                print(f"   找到產品區塊數量: {len(product_divs)}")
                
                # 分析女優名稱
                actresses_found = []
                for product_div in product_divs:
                    # 檢查番號匹配
                    pno_element = product_div.find('div', class_='pno')
                    if pno_element and test_code.upper() in pno_element.text.upper():
                        print(f"   ✓ 找到匹配的產品區塊")
                        
                        # 提取女優名稱
                        actress_span = product_div.find('span', class_='fw-bold')
                        if actress_span:
                            actress_name = actress_span.text.strip()
                            actresses_found.append(actress_name)
                            print(f"   女優名稱: '{actress_name}'")
                            
                            # 檢查是否包含日文字元
                            has_japanese = bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', actress_name))
                            has_replacement = '\ufffd' in actress_name
                            print(f"   包含日文字元: {has_japanese}")
                            print(f"   包含替換字元: {has_replacement}")
                            
                best_results.append({
                    'encoding': encoding,
                    'replacement_ratio': replacement_ratio,
                    'actresses': actresses_found,
                    'success': len(actresses_found) > 0 and not any('\ufffd' in name for name in actresses_found)
                })
                            
            except Exception as e:
                print(f"   ❌ 編碼失敗: {e}")
                
            print()
        
        # 總結最佳結果
        print("📊 編碼分析總結:")
        print("=" * 40)
        
        successful_results = [r for r in best_results if r['success']]
        if successful_results:
            best = min(successful_results, key=lambda x: x['replacement_ratio'])
            print(f"🏆 最佳編碼: {best['encoding']}")
            print(f"🏆 替換比例: {best['replacement_ratio']:.4f}")
            print(f"🏆 女優名稱: {best['actresses']}")
        else:
            print("❌ 沒有找到成功的編碼組合")
            
        # 顯示所有結果
        print("\n📋 所有編碼結果:")
        for result in best_results:
            status = "✓" if result['success'] else "✗"
            print(f"{status} {result['encoding']:<12} 替換比例: {result['replacement_ratio']:.4f}  女優: {result['actresses']}")
            
    except Exception as e:
        print(f"❌ 分析過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_encoding_issues()
