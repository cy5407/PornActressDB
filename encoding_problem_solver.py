# -*- coding: utf-8 -*-
"""
編碼問題解決方案與爬蟲優化建議
分析發現的問題並提供解決方案
"""

import requests
import httpx
from bs4 import BeautifulSoup
import logging
from typing import Dict, Any, List
import asyncio
import time
import random

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EncodingProblemSolver:
    """編碼問題解決方案"""
    
    def __init__(self):
        # 更真實的瀏覽器標頭
        self.browser_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8,ja;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive'
        }
    
    def analyze_encoding_issues(self) -> Dict[str, Any]:
        """分析編碼問題"""
        logger.info("🔍 分析編碼問題...")
        
        analysis = {
            'identified_issues': [
                '網站回傳的內容包含大量替換字符 (�)',
                '即使使用 cp932 編碼，仍有 287-1025 個替換字符',
                '網站可能使用了特殊的編碼或反爬蟲機制',
                '頁面標題無法正確解析',
                '搜尋結果結構無法識別'
            ],
            'possible_causes': [
                '網站使用了 JavaScript 動態載入內容',
                '網站有反爬蟲機制，返回加密或混淆的內容',
                '網站使用了非標準的字符編碼',
                '內容可能經過壓縮或編碼處理',
                '需要特定的請求標頭或 Cookie'
            ],
            'solutions': [
                '使用 Selenium 或 Playwright 等瀏覽器自動化工具',
                '模擬真實瀏覽器行為，包括 JavaScript 執行',
                '添加延遲和隨機化請求',
                '使用代理伺服器輪換',
                '分析網站的 API 端點',
                '實作更強健的編碼檢測和處理'
            ]
        }
        
        return analysis
    
    def test_alternative_approaches(self, url: str) -> Dict[str, Any]:
        """測試替代方法"""
        logger.info(f"🧪 測試替代方法: {url}")
        
        results = {}
        
        # 方法1: 不同的請求方式
        methods = [
            ('requests_basic', self.test_requests_basic),
            ('requests_session', self.test_requests_session),
            ('httpx_sync', self.test_httpx_sync),
            ('requests_with_delay', self.test_requests_with_delay)
        ]
        
        for method_name, method_func in methods:
            try:
                logger.info(f"   測試方法: {method_name}")
                result = method_func(url)
                results[method_name] = result
                time.sleep(2)  # 避免請求過於頻繁
            except Exception as e:
                logger.error(f"   {method_name} 失敗: {e}")
                results[method_name] = {'error': str(e)}
        
        return results
    
    def test_requests_basic(self, url: str) -> Dict[str, Any]:
        """基本 requests 測試"""
        response = requests.get(url, headers=self.browser_headers, timeout=15)
        return self.analyze_response(response, 'requests_basic')
    
    def test_requests_session(self, url: str) -> Dict[str, Any]:
        """使用 session 的 requests 測試"""
        session = requests.Session()
        session.headers.update(self.browser_headers)
        response = session.get(url, timeout=15)
        return self.analyze_response(response, 'requests_session')
    
    def test_httpx_sync(self, url: str) -> Dict[str, Any]:
        """HTTPX 同步測試"""
        with httpx.Client(headers=self.browser_headers, timeout=15) as client:
            response = client.get(url)
            return self.analyze_response(response, 'httpx_sync')
    
    def test_requests_with_delay(self, url: str) -> Dict[str, Any]:
        """帶延遲的 requests 測試"""
        time.sleep(random.uniform(1, 3))  # 隨機延遲
        response = requests.get(url, headers=self.browser_headers, timeout=15)
        return self.analyze_response(response, 'requests_with_delay')
    
    def analyze_response(self, response, method_name: str) -> Dict[str, Any]:
        """分析回應"""
        try:
            content_length = len(response.content)
            
            # 嘗試不同的解碼方式
            encoding_results = {}
            for encoding in ['utf-8', 'cp932', 'shift_jis', 'euc-jp']:
                try:
                    decoded = response.content.decode(encoding, errors='replace')
                    replacement_count = decoded.count('�')
                    encoding_results[encoding] = {
                        'replacement_count': replacement_count,
                        'length': len(decoded)
                    }
                except Exception as e:
                    encoding_results[encoding] = {'error': str(e)}
            
            # 找出最佳編碼
            best_encoding = min(
                encoding_results.keys(),
                key=lambda x: encoding_results[x].get('replacement_count', float('inf'))
            )
            
            # 使用最佳編碼解析
            content = response.content.decode(best_encoding, errors='replace')
            soup = BeautifulSoup(content, 'html.parser')
            
            # 檢查是否找到有意義的內容
            title = soup.title.string if soup.title else None
            has_meaningful_content = bool(
                title and title.strip() and '無標題' not in title
            )
            
            # 尋找影片編號
            content_upper = content.upper()
            has_video_codes = any(code in content_upper for code in ['MIDV', 'FSDSS', 'MIZD'])
            
            return {
                'method': method_name,
                'status_code': response.status_code,
                'content_length': content_length,
                'best_encoding': best_encoding,
                'encoding_results': encoding_results,
                'title': title,
                'has_meaningful_content': has_meaningful_content,
                'has_video_codes': has_video_codes,
                'content_preview': content[:200] if content else None
            }
            
        except Exception as e:
            return {'method': method_name, 'error': str(e)}
    
    def generate_recommendations(self, analysis: Dict[str, Any], test_results: Dict[str, Any]) -> List[str]:
        """產生建議"""
        recommendations = []
        
        # 基於測試結果的建議
        successful_methods = [
            method for method, result in test_results.items()
            if not result.get('error') and result.get('has_meaningful_content')
        ]
        
        if not successful_methods:
            recommendations.extend([
                "🚨 所有測試方法都無法獲得有意義的內容",
                "🔧 建議使用 Selenium 或 Playwright 進行瀏覽器自動化",
                "🕘 實作請求間隔和隨機化",
                "🔄 考慮使用代理伺服器輪換",
                "🔍 分析網站是否有公開的 API"
            ])
        else:
            recommendations.append(f"✅ 成功的方法: {', '.join(successful_methods)}")
        
        # 編碼相關建議
        recommendations.extend([
            "📝 實作多編碼嘗試機制 (cp932, shift_jis, utf-8)",
            "🔧 添加更強健的編碼檢測",
            "⚠️ 處理編碼錯誤時使用 'replace' 策略",
            "🧪 對每個網站進行個別的編碼測試"
        ])
        
        # 爬蟲優化建議
        recommendations.extend([
            "🚀 實作非同步爬蟲以提高效率",
            "💾 添加回應快取機制",
            "🛡️ 實作頻率限制和重試機制",
            "📊 記錄和監控爬蟲成功率",
            "🔄 定期更新 User-Agent 和請求標頭"
        ])
        
        return recommendations

def run_encoding_analysis():
    """執行編碼分析"""
    solver = EncodingProblemSolver()
    
    logger.info("🎯 開始編碼問題分析與解決方案研究")
    logger.info("=" * 80)
    
    # 分析問題
    analysis = solver.analyze_encoding_issues()
    
    logger.info("🔍 識別的問題:")
    for issue in analysis['identified_issues']:
        logger.info(f"   • {issue}")
    
    logger.info("\n🤔 可能的原因:")
    for cause in analysis['possible_causes']:
        logger.info(f"   • {cause}")
    
    # 測試替代方法
    test_urls = [
        'https://av-wiki.net/?s=MIDV-661&post_type=product',
        'https://chiba-f.net/search/?keyword=MIDV-661'
    ]
    
    all_test_results = {}
    for url in test_urls:
        logger.info(f"\n🧪 測試 URL: {url}")
        test_results = solver.test_alternative_approaches(url)
        all_test_results[url] = test_results
        
        # 顯示測試結果摘要
        for method, result in test_results.items():
            if result.get('error'):
                logger.error(f"   ❌ {method}: {result['error']}")
            else:
                status = "✅" if result.get('has_meaningful_content') else "⚠️"
                logger.info(f"   {status} {method}: 編碼={result.get('best_encoding')}, 內容長度={result.get('content_length')}")
    
    # 產生建議
    logger.info("\n💡 解決方案建議:")
    recommendations = solver.generate_recommendations(analysis, all_test_results)
    for rec in recommendations:
        logger.info(f"   {rec}")
    
    return {
        'analysis': analysis,
        'test_results': all_test_results,
        'recommendations': recommendations
    }

if __name__ == "__main__":
    results = run_encoding_analysis()
