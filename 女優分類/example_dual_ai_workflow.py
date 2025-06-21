#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO: [COPILOT] 需要添加完整的 docstring 和類型提示
# TODO: [COPILOT] 需要生成對應的單元測試
# DONE: [CLAUDE] 核心搜尋邏輯已完成

from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import time

class EnhancedActressSearchEngine:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.search_sources = []
        self.cache = {}
        
    def add_search_source(self, source):
        self.search_sources.append(source)
        
    def search_actress_info(self, name: str) -> List[Dict[str, Any]]:
        if name in self.cache:
            return self.cache[name]
            
        results = []
        for source in self.search_sources:
            try:
                result = source.search(name)
                if result:
                    results.append(result)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"Search error in {source.__class__.__name__}: {e}")
                continue
                
        merged_result = self._merge_search_results(results)
        self.cache[name] = merged_result
        return merged_result
        
    def _merge_search_results(self, results: List[Dict]) -> List[Dict[str, Any]]:
        if not results:
            return []
            
        base_result = results[0].copy()
        
        for result in results[1:]:
            for key, value in result.items():
                if key not in base_result or not base_result[key]:
                    base_result[key] = value
                elif isinstance(value, list) and isinstance(base_result[key], list):
                    base_result[key].extend(value)
                    base_result[key] = list(set(base_result[key]))
                    
        return [base_result]

class AVWikiSearchSource:
    
    def __init__(self):
        self.base_url = "https://av-wiki.net"
        
    def search(self, actress_name: str) -> Optional[Dict[str, Any]]:
        search_url = f"{self.base_url}/search"
        params = {"q": actress_name, "type": "actress"}
        
        try:
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return self._parse_actress_page(soup)
            
        except requests.RequestException:
            return None
            
    def _parse_actress_page(self, soup: BeautifulSoup) -> Dict[str, Any]:
        result = {
            "name": "",
            "alias": [],
            "birth_date": "",
            "measurements": "",
            "studio_history": []
        }
        
        name_elem = soup.find("h1", class_="actress-name")
        if name_elem:
            result["name"] = name_elem.text.strip()
            
        alias_elems = soup.find_all("span", class_="alias")
        result["alias"] = [elem.text.strip() for elem in alias_elems]
        
        return result

# TODO: [COPILOT] 需要實作 ChibaFNetSearchSource 類別
# TODO: [COPILOT] 需要添加錯誤處理和日誌記錄
# TODO: [COPILOT] 需要實作快取過期機制
