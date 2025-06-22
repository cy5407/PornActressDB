# -*- coding: utf-8 -*-
"""
HTML 結構解析測試腳本
用於分析 av-wiki.net 和 chiba-f.net 的頁面結構和編碼問題
"""

import requests
import httpx
from bs4 import BeautifulSoup
import chardet
import logging
from typing import Dict, Any
import asyncio

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HTMLStructureAnalyzer:
    """HTML 結構分析器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8,ja;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def analyze_encoding(self, content: bytes, url: str) -> Dict[str, Any]:
        """分析內容編碼"""
        try:
            # 使用 chardet 檢測編碼
            detected = chardet.detect(content)
            logger.info(f"🔍 [{url}] 檢測到的編碼: {detected}")
            
            # 嘗試不同的編碼方式解碼
            encodings_to_try = [
                detected.get('encoding', 'utf-8'),
                'utf-8',
                'shift_jis',
                'euc-jp',
                'iso-2022-jp',
                'cp932',
                'gb2312',
                'big5'
            ]
            
            results = {}
            for encoding in encodings_to_try:
                if encoding:
                    try:
                        decoded = content.decode(encoding, errors='replace')
                        results[encoding] = {
                            'success': True,
                            'length': len(decoded),
                            'has_replacement_chars': '�' in decoded,
                            'replacement_count': decoded.count('�')
                        }
                        logger.info(f"✅ [{url}] {encoding} 解碼成功，替換字符數: {decoded.count('�')}")
                    except Exception as e:
                        results[encoding] = {'success': False, 'error': str(e)}
                        logger.warning(f"❌ [{url}] {encoding} 解碼失敗: {e}")
            
            return {
                'detected_encoding': detected,
                'encoding_results': results,
                'content_length': len(content)
            }
        except Exception as e:
            logger.error(f"❌ [{url}] 編碼分析失敗: {e}")
            return {'error': str(e)}
    
    def analyze_html_structure(self, html_content: str, url: str) -> Dict[str, Any]:
        """分析HTML結構"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 基本結構分析
            structure = {
                'title': soup.title.string if soup.title else 'No title',
                'meta_charset': None,
                'search_results': [],
                'actress_info': [],
                'studio_info': [],
                'video_info': []
            }
            
            # 檢查頁面編碼聲明
            charset_meta = soup.find('meta', {'charset': True})
            if charset_meta:
                structure['meta_charset'] = charset_meta.get('charset')
            else:
                content_type_meta = soup.find('meta', {'http-equiv': 'Content-Type'})
                if content_type_meta:
                    content = content_type_meta.get('content', '')
                    if 'charset=' in content:
                        structure['meta_charset'] = content.split('charset=')[1].strip()
            
            # 針對不同網站分析特定結構
            if 'av-wiki.net' in url:
                structure.update(self._analyze_avwiki_structure(soup))
            elif 'chiba-f.net' in url:
                structure.update(self._analyze_chibaf_structure(soup))
            
            return structure
        except Exception as e:
            logger.error(f"❌ [{url}] HTML結構分析失敗: {e}")
            return {'error': str(e)}
    
    def _analyze_avwiki_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """分析 av-wiki.net 的HTML結構"""
        result = {}
        
        # 搜尋結果
        search_results = soup.find_all('div', class_='product-item') or soup.find_all('article')
        result['search_results_count'] = len(search_results)
        
        if search_results:
            for item in search_results[:3]:  # 只分析前3個結果
                item_info = {
                    'title': '',
                    'actress': '',
                    'studio': '',
                    'code': ''
                }
                
                # 嘗試提取標題
                title_elem = item.find('h2') or item.find('h3') or item.find('a')
                if title_elem:
                    item_info['title'] = title_elem.get_text(strip=True)
                
                # 嘗試提取其他資訊
                links = item.find_all('a')
                for link in links:
                    text = link.get_text(strip=True)
                    href = link.get('href', '')
                    if any(actress_keyword in href.lower() for actress_keyword in ['actress', 'performer', 'star']):
                        item_info['actress'] = text
                    elif any(studio_keyword in href.lower() for studio_keyword in ['studio', 'maker', 'label']):
                        item_info['studio'] = text
                
                result.setdefault('search_items', []).append(item_info)
        
        return result
    
    def _analyze_chibaf_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """分析 chiba-f.net 的HTML結構"""
        result = {}
        
        # 搜尋結果
        search_results = soup.find_all('div', class_='search-result') or soup.find_all('div', class_='item')
        result['search_results_count'] = len(search_results)
        
        if search_results:
            for item in search_results[:3]:  # 只分析前3個結果
                item_info = {
                    'title': '',
                    'actress': '',
                    'studio': '',
                    'code': ''
                }
                
                # 嘗試提取標題
                title_elem = item.find('h2') or item.find('h3') or item.find('a')
                if title_elem:
                    item_info['title'] = title_elem.get_text(strip=True)
                
                result.setdefault('search_items', []).append(item_info)
        
        return result
    
    def test_url_sync(self, url: str) -> Dict[str, Any]:
        """同步測試URL"""
        logger.info(f"🌐 開始同步測試: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # 編碼分析
            encoding_analysis = self.analyze_encoding(response.content, url)
            
            # 使用最佳編碼解碼內容
            best_encoding = 'utf-8'
            if encoding_analysis.get('encoding_results'):
                for enc, result in encoding_analysis['encoding_results'].items():
                    if result.get('success') and result.get('replacement_count', float('inf')) == 0:
                        best_encoding = enc
                        break
            
            try:
                html_content = response.content.decode(best_encoding, errors='replace')
            except:
                html_content = response.text
            
            # HTML結構分析
            structure_analysis = self.analyze_html_structure(html_content, url)
            
            return {
                'url': url,
                'status_code': response.status_code,
                'encoding_analysis': encoding_analysis,
                'structure_analysis': structure_analysis,
                'response_headers': dict(response.headers),
                'content_preview': html_content[:1000] + '...' if len(html_content) > 1000 else html_content
            }
            
        except Exception as e:
            logger.error(f"❌ 同步測試失敗 [{url}]: {e}")
            return {'url': url, 'error': str(e)}
    
    async def test_url_async(self, url: str) -> Dict[str, Any]:
        """非同步測試URL"""
        logger.info(f"🌐 開始非同步測試: {url}")
        
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                # 編碼分析
                encoding_analysis = self.analyze_encoding(response.content, url)
                
                # 使用最佳編碼解碼內容
                best_encoding = 'utf-8'
                if encoding_analysis.get('encoding_results'):
                    for enc, result in encoding_analysis['encoding_results'].items():
                        if result.get('success') and result.get('replacement_count', float('inf')) == 0:
                            best_encoding = enc
                            break
                
                try:
                    html_content = response.content.decode(best_encoding, errors='replace')
                except:
                    html_content = response.text
                
                # HTML結構分析
                structure_analysis = self.analyze_html_structure(html_content, url)
                
                return {
                    'url': url,
                    'status_code': response.status_code,
                    'encoding_analysis': encoding_analysis,
                    'structure_analysis': structure_analysis,
                    'response_headers': dict(response.headers),
                    'content_preview': html_content[:1000] + '...' if len(html_content) > 1000 else html_content
                }
                
        except Exception as e:
            logger.error(f"❌ 非同步測試失敗 [{url}]: {e}")
            return {'url': url, 'error': str(e)}

def run_tests():
    """執行測試"""
    analyzer = HTMLStructureAnalyzer()
    
    test_urls = [
        'https://av-wiki.net/?s=MIDV-661&post_type=product',
        'https://chiba-f.net/search/?keyword=MIDV-661'
    ]
    
    logger.info("🎯 開始HTML結構和編碼分析測試")
    logger.info("=" * 60)
    
    # 同步測試
    logger.info("📊 同步測試結果:")
    for url in test_urls:
        result = analyzer.test_url_sync(url)
        print_analysis_result(result)
    
    # 非同步測試
    logger.info("📊 非同步測試結果:")
    
    async def run_async_tests():
        tasks = [analyzer.test_url_async(url) for url in test_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ 非同步測試異常: {result}")
            else:
                print_analysis_result(result)
    
    asyncio.run(run_async_tests())

def print_analysis_result(result: Dict[str, Any]):
    """印出分析結果"""
    if 'error' in result:
        logger.error(f"❌ {result['url']}: {result['error']}")
        return
    
    logger.info(f"\n🔍 分析結果: {result['url']}")
    logger.info(f"   狀態碼: {result['status_code']}")
    
    # 編碼分析結果
    encoding_analysis = result.get('encoding_analysis', {})
    if 'detected_encoding' in encoding_analysis:
        detected = encoding_analysis['detected_encoding']
        logger.info(f"   檢測編碼: {detected.get('encoding')} (信心度: {detected.get('confidence', 0):.2f})")
    
    if 'encoding_results' in encoding_analysis:
        successful_encodings = [
            enc for enc, res in encoding_analysis['encoding_results'].items() 
            if res.get('success') and res.get('replacement_count', 0) == 0
        ]
        if successful_encodings:
            logger.info(f"   成功編碼: {', '.join(successful_encodings)}")
        else:
            logger.warning("   ⚠️ 沒有完美的編碼方式")
    
    # HTML結構分析結果
    structure = result.get('structure_analysis', {})
    if 'title' in structure:
        logger.info(f"   頁面標題: {structure['title']}")
    if 'meta_charset' in structure:
        logger.info(f"   聲明編碼: {structure['meta_charset']}")
    if 'search_results_count' in structure:
        logger.info(f"   搜尋結果數: {structure['search_results_count']}")
    
    if 'search_items' in structure:
        logger.info("   搜尋項目:")
        for i, item in enumerate(structure['search_items'][:2]):
            logger.info(f"     [{i+1}] 標題: {item.get('title', 'N/A')}")
            if item.get('actress'):
                logger.info(f"         女優: {item['actress']}")
            if item.get('studio'):
                logger.info(f"         片商: {item['studio']}")

if __name__ == "__main__":
    run_tests()
