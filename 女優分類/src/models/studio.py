# -*- coding: utf-8 -*-
"""
片商識別器模組
"""
import json
import logging
import re
from pathlib import Path
from typing import Dict
from .results import Result, ServiceError, ErrorCode

logger = logging.getLogger(__name__)


class StudioIdentifier:
    """片商識別器"""

    def __init__(self, rules_file: str = "studios.json"):
        self.rules_file = Path(rules_file)
        self.studio_patterns = self._load_rules()

    def _load_rules(self) -> Result[Dict]:
        try:
            if not self.rules_file.exists():
                logger.warning(
                    f"片商規則檔案 {self.rules_file} 不存在，將建立預設檔案。"
                )
                default_rules = {
                    "S1": ["SSIS", "SSNI", "STARS"],
                    "MOODYZ": ["MIRD", "MIDD", "MIDV"],
                    "PREMIUM": ["IPX", "IPZ", "IPZZ"],
                    "WANZ": ["WANZ"],
                    "FALENO": ["FSDSS"],
                }
                try:
                    with self.rules_file.open("w", encoding="utf-8") as f:
                        json.dump(default_rules, f, ensure_ascii=False, indent=4)
                    return Result.ok(default_rules)
                except IOError as e:
                    logger.error(f"無法建立預設片商規則檔案: {e}")
                    return Result.fail(
                        ServiceError(
                            ErrorCode.FILE_ERROR,
                            f"無法建立預設片商規則檔案: {e}",
                            caused_by=e,
                        )
                    )
            try:
                with self.rules_file.open("r", encoding="utf-8") as f:
                    return Result.ok(json.load(f))
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"讀取片商規則檔案失敗: {e}, 將使用空規則。")
                return Result.fail(
                    ServiceError(
                        ErrorCode.FILE_ERROR, f"讀取片商規則檔案失敗: {e}", caused_by=e
                    )
                )
        except Exception as e:
            logger.error(f"未知錯誤 (載入片商規則): {e}", exc_info=True)
            return Result.fail(
                ServiceError(
                    ErrorCode.UNKNOWN_ERROR,
                    f"未知錯誤 (載入片商規則): {e}",
                    caused_by=e,
                )
            )

    def identify_studio(self, code: str) -> Result[str]:
        try:
            if not code:
                return Result.ok("UNKNOWN")
            prefix_match = re.match(r"([A-Z]+)", code.upper())
            if prefix_match:
                prefix = prefix_match.group(1)
                # 確保 self.studio_patterns 是一個 Result 對象
                if (
                    not isinstance(self.studio_patterns, Result)
                    or not self.studio_patterns.success
                ):
                    logger.warning("片商規則未成功載入，無法識別片商。")
                    return Result.ok("UNKNOWN")

                for studio, prefixes in self.studio_patterns.data.items():
                    if prefix in prefixes:
                        return Result.ok(studio)
            return Result.ok("UNKNOWN")
        except Exception as e:
            logger.error(f"識別片商失敗: {e}", exc_info=True)
            return Result.fail(
                ServiceError(
                    ErrorCode.PARSING_ERROR, f"識別片商失敗: {e}", {"code": code}, e
                )
            )
