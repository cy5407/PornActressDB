# -*- coding: utf-8 -*-
"""
詳細HTML內容分析腳本
深入分析編碼問題並找出最佳解決方案
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

class DetailedHTMLAnalyzer:
    """詳細HTML分析器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8,ja;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def find_best_encoding(self, content: bytes) -> str:
        """找出最佳編碼方式"""
        encodings_to_try = [
            'utf-8',
            'shift_jis', 
            'cp932',
            'euc-jp',
            'iso-2022-jp',
            'gb2312',
            'big5'
        ]
        
        best_encoding = 'utf-8'
        min_replacement_chars = float('inf')
        
        for encoding in encodings_to_try:
            try:
                decoded = content.decode(encoding, errors='replace')
                replacement_count = decoded.count('�')
                
                logger.info(f"   {encoding}: {replacement_count} 個替換字符")
                
                if replacement_count < min_replacement_chars:
                    min_replacement_chars = replacement_count
                    best_encoding = encoding
                    
            except Exception as e:
                logger.warning(f"   {encoding}: 解碼失敗 - {e}")
        
        logger.info(f"🎯 最佳編碼: {best_encoding} (替換字符: {min_replacement_chars})")
        return best_encoding
    
    def analyze_content_in_detail(self, url: str) -> Dict[str, Any]:
        """詳細分析內容"""
        logger.info(f"\n🔍 詳細分析: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            logger.info(f"   狀態碼: {response.status_code}")
            logger.info(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
            logger.info(f"   內容長度: {len(response.content)} bytes")
            
            # 找出最佳編碼
            best_encoding = self.find_best_encoding(response.content)
            
            # 使用最佳編碼解碼
            content = response.content.decode(best_encoding, errors='replace')
            
            # BeautifulSoup 解析
            soup = BeautifulSoup(content, 'html.parser')
            
            # 基本資訊
            title = soup.title.string if soup.title else "無標題"
            logger.info(f"   頁面標題: {title}")
            
            # 檢查meta標籤中的編碼聲明
            charset_meta = soup.find('meta', {'charset': True})
            if charset_meta:
                declared_charset = charset_meta.get('charset')
                logger.info(f"   聲明編碼 (meta charset): {declared_charset}")
            
            content_type_meta = soup.find('meta', {'http-equiv': 'Content-Type'})
            if content_type_meta:
                content_type = content_type_meta.get('content', '')
                logger.info(f"   聲明編碼 (http-equiv): {content_type}")
            
            # 分析搜尋結果結構
            self.analyze_search_structure(soup, url)
            
            # 儲存部分內容供檢視
            preview_content = content[:2000]
            
            return {
                'url': url,
                'success': True,
                'best_encoding': best_encoding,
                'title': title,
                'content_length': len(content),
                'preview': preview_content
            }
            
        except Exception as e:
            logger.error(f"❌ 分析失敗: {e}")
            return {'url': url, 'success': False, 'error': str(e)}
    
    def analyze_search_structure(self, soup: BeautifulSoup, url: str):
        """分析搜尋結果結構"""
        logger.info("   🔎 搜尋結果結構分析:")
        
        # 通用搜尋結果容器
        possible_containers = [
            'div[class*="search"]',
            'div[class*="result"]', 
            'div[class*="product"]',
            'div[class*="item"]',
            'article',
            '.post',
            '.entry'
        ]
        
        found_containers = []
        for selector in possible_containers:
            elements = soup.select(selector)
            if elements:
                found_containers.append((selector, len(elements)))
                logger.info(f"     {selector}: {len(elements)} 個元素")
        
        if not found_containers:
            logger.warning("     ⚠️ 未找到明顯的搜尋結果容器")
            
            # 嘗試找任何包含影片編號的元素
            midv_elements = soup.find_all(text=lambda text: text and 'MIDV' in text.upper())
            if midv_elements:
                logger.info(f"     找到 {len(midv_elements)} 個包含 'MIDV' 的文字元素")
                for i, elem in enumerate(midv_elements[:3]):
                    parent = elem.parent if elem.parent else None
                    parent_tag = f"{parent.name}#{parent.get('id', '')}.{parent.get('class', '')}" if parent else "無父元素"
                    logger.info(f"       [{i+1}] {elem.strip()[:50]}... (父元素: {parent_tag})")
        
        # 分析連結
        links = soup.find_all('a', href=True)
        relevant_links = [link for link in links if 'midv' in link.get('href', '').lower() or 'midv' in link.get_text().lower()]
        
        if relevant_links:
            logger.info(f"     找到 {len(relevant_links)} 個相關連結:")
            for i, link in enumerate(relevant_links[:3]):
                href = link.get('href', '')
                text = link.get_text(strip=True)[:50]
                logger.info(f"       [{i+1}] {text}... -> {href}")
        else:
            logger.warning("     ⚠️ 未找到相關連結")

def run_detailed_analysis():
    """執行詳細分析"""
    analyzer = DetailedHTMLAnalyzer()
    
    test_urls = [
        'https://av-wiki.net/?s=MIDV-661&post_type=product',
        'https://chiba-f.net/search/?keyword=MIDV-661'
    ]
    
    logger.info("🎯 開始詳細HTML內容分析")
    logger.info("=" * 80)
    
    results = []
    for url in test_urls:
        result = analyzer.analyze_content_in_detail(url)
        results.append(result)
    
    # 產生分析報告
    logger.info("\n📊 分析總結:")
    for result in results:
        if result.get('success'):
            logger.info(f"✅ {result['url']}")
            logger.info(f"   最佳編碼: {result['best_encoding']}")
            logger.info(f"   內容長度: {result['content_length']}")
        else:
            logger.error(f"❌ {result['url']}: {result.get('error')}")
    
    return results

def save_content_samples(results):
    """儲存內容樣本供檢視"""
    for i, result in enumerate(results):
        if result.get('success') and result.get('preview'):
            filename = f"content_sample_{i+1}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"<!-- URL: {result['url']} -->\n")
                f.write(f"<!-- Best Encoding: {result['best_encoding']} -->\n")
                f.write(f"<!-- Title: {result['title']} -->\n\n")
                f.write(result['preview'])
            logger.info(f"💾 已儲存內容樣本: {filename}")

if __name__ == "__main__":
    results = run_detailed_analysis()
    save_content_samples(results)
