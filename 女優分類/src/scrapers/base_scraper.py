# -*- coding: utf-8 -*-
"""
基礎爬蟲類別和容錯機制
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import random

from .encoding_utils import EncodingDetector, create_safe_soup
from .rate_limiter import RateLimiter, get_global_rate_limiter
from .cache_manager import CacheManager
from ..models.results import Result, ServiceError, ErrorCode

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """重試配置"""

    max_retries: int = 3  # 最大重試次數
    base_delay: float = 1.0  # 基礎延遲(秒)
    max_delay: float = 60.0  # 最大延遲(秒)
    backoff_factor: float = 2.0  # 指數退避因子
    jitter: bool = True  # 添加隨機抖動
    retry_on_errors: List[ErrorCode] = None  # 需要重試的錯誤類型

    def __post_init__(self):
        if self.retry_on_errors is None:
            self.retry_on_errors = [
                ErrorCode.NETWORK_ERROR,
                ErrorCode.TIMEOUT_ERROR,
                ErrorCode.SERVER_ERROR,
            ]


@dataclass
class HealthCheckConfig:
    """健康檢查配置"""

    check_interval: float = 300.0  # 檢查間隔(秒)
    timeout: float = 10.0  # 超時時間(秒)
    failure_threshold: int = 3  # 失敗閾值
    recovery_threshold: int = 2  # 恢復閾值
    enable_auto_recovery: bool = True  # 啟用自動恢復


class RetryManager:
    """重試管理器"""

    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
        self.stats = {
            "total_attempts": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "retry_reasons": {},
        }

    def should_retry(self, error: ServiceError, attempt: int) -> bool:
        """判斷是否應該重試"""
        if attempt >= self.config.max_retries:
            return False

        return error.code in self.config.retry_on_errors

    def calculate_delay(self, attempt: int) -> float:
        """計算重試延遲"""
        delay = self.config.base_delay * (self.config.backoff_factor**attempt)
        delay = min(delay, self.config.max_delay)

        if self.config.jitter:
            # 添加±25%的隨機抖動
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)

        return max(delay, 0.1)  # 最小延遲0.1秒

    async def retry_async(self, func: Callable, *args, **kwargs) -> Result[Any]:
        """非同步重試執行"""
        last_error: Optional[ServiceError] = None

        for attempt in range(self.config.max_retries + 1):
            self.stats["total_attempts"] += 1

            try:
                result = await func(*args, **kwargs)

                if result.success:
                    if attempt > 0:
                        self.stats["successful_retries"] += 1
                        logger.info(f"✅ 重試成功 (第 {attempt + 1} 次嘗試)")
                    return result
                else:
                    last_error = result.error

                    # 記錄錯誤類型統計
                    error_code = last_error.code
                    if error_code not in self.stats["retry_reasons"]:
                        self.stats["retry_reasons"][error_code] = 0
                    self.stats["retry_reasons"][error_code] += 1

                    # 判斷是否重試
                    if not self.should_retry(last_error, attempt):
                        self.stats["failed_retries"] += 1
                        logger.error(f"❌ 重試失敗，不再重試: {last_error.message}")
                        break

                    if attempt < self.config.max_retries:
                        delay = self.calculate_delay(attempt)
                        logger.warning(
                            f"⚠️ 第 {attempt + 1} 次嘗試失敗: {last_error.message}"
                        )
                        logger.info(f"⏳ 等待 {delay:.2f} 秒後重試...")
                        await asyncio.sleep(delay)
            except Exception as e:
                last_error = ServiceError(
                    ErrorCode.UNKNOWN_ERROR, f"重試過程中發生未知錯誤: {e}", caused_by=e
                )
                self.stats["failed_retries"] += 1
                logger.error(f"❌ 重試過程中發生未知錯誤: {e}")
                break

        # 所有重試都失敗了
        if last_error:
            return Result.fail(last_error)
        else:
            return Result.fail(ServiceError(ErrorCode.UNKNOWN_ERROR, "所有重試都失敗"))

    def retry_sync(self, func: Callable, *args, **kwargs) -> Result[Any]:
        """同步重試執行"""
        last_error: Optional[ServiceError] = None

        for attempt in range(self.config.max_retries + 1):
            self.stats["total_attempts"] += 1

            try:
                result = func(*args, **kwargs)

                if result.success:
                    if attempt > 0:
                        self.stats["successful_retries"] += 1
                        logger.info(f"✅ 重試成功 (第 {attempt + 1} 次嘗試)")
                    return result
                else:
                    last_error = result.error

                    # 記錄錯誤類型統計
                    error_code = last_error.code
                    if error_code not in self.stats["retry_reasons"]:
                        self.stats["retry_reasons"][error_code] = 0
                    self.stats["retry_reasons"][error_code] += 1

                    # 判斷是否重試
                    if not self.should_retry(last_error, attempt):
                        self.stats["failed_retries"] += 1
                        logger.error(f"❌ 重試失敗，不再重試: {last_error.message}")
                        break

                    if attempt < self.config.max_retries:
                        delay = self.calculate_delay(attempt)
                        logger.warning(
                            f"⚠️ 第 {attempt + 1} 次嘗試失敗: {last_error.message}"
                        )
                        logger.info(f"⏳ 等待 {delay:.2f} 秒後重試...")
                        time.sleep(delay)
            except Exception as e:
                last_error = ServiceError(
                    ErrorCode.UNKNOWN_ERROR, f"重試過程中發生未知錯誤: {e}", caused_by=e
                )
                self.stats["failed_retries"] += 1
                logger.error(f"❌ 重試過程中發生未知錯誤: {e}")
                break

        # 所有重試都失敗了
        if last_error:
            return Result.fail(last_error)
        else:
            return Result.fail(ServiceError(ErrorCode.UNKNOWN_ERROR, "所有重試都失敗"))

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """獲取重試統計"""
        total = self.stats["total_attempts"]
        success_rate = (
            (self.stats["successful_retries"] / total * 100) if total > 0 else 0
        )

        return {
            **self.stats,
            "success_rate": f"{success_rate:.1f}%",
            "config": {
                "max_retries": self.config.max_retries,
                "base_delay": self.config.base_delay,
                "backoff_factor": self.config.backoff_factor,
            },
        }


class HealthChecker:
    """健康檢查器"""

    def __init__(self, config: HealthCheckConfig = None):
        self.config = config or HealthCheckConfig()
        self.domain_health = {}  # 域名健康狀態
        self.lock = asyncio.Lock()

        # 啟動健康檢查任務
        if self.config.enable_auto_recovery:
            self._start_health_check_task()

    async def check_domain_health(self, domain: str) -> Result[bool]:
        """檢查單個域名的健康狀態"""
        try:
            import aiohttp

            # 構造健康檢查URL
            check_url = f"https://{domain}/"

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(check_url) as response:
                    if response.status < 500:
                        return Result.ok(True)
                    else:
                        return Result.fail(
                            ServiceError(
                                ErrorCode.SERVER_ERROR,
                                f"域名 {domain} 返回伺服器錯誤: {response.status}",
                                {"url": check_url, "status": response.status},
                            )
                        )

        except aiohttp.ClientError as e:
            logger.debug(f"域名健康檢查網路錯誤 {domain}: {e}")
            return Result.fail(
                ServiceError(
                    ErrorCode.NETWORK_ERROR,
                    f"域名 {domain} 網路連線錯誤",
                    {"url": check_url},
                    e,
                )
            )
        except Exception as e:
            logger.debug(f"域名健康檢查未知錯誤 {domain}: {e}")
            return Result.fail(
                ServiceError(
                    ErrorCode.UNKNOWN_ERROR,
                    f"域名 {domain} 健康檢查失敗",
                    {"url": check_url},
                    e,
                )
            )

    async def update_domain_health(self, domain: str, is_healthy: bool):
        """更新域名健康狀態"""
        async with self.lock:
            if domain not in self.domain_health:
                self.domain_health[domain] = {
                    "healthy": True,
                    "consecutive_failures": 0,
                    "consecutive_successes": 0,
                    "last_check": time.time(),
                    "total_checks": 0,
                    "total_failures": 0,
                }

            health_info = self.domain_health[domain]
            health_info["last_check"] = time.time()
            health_info["total_checks"] += 1

            if is_healthy:
                health_info["consecutive_successes"] += 1
                health_info["consecutive_failures"] = 0

                # 恢復健康狀態
                if (
                    not health_info["healthy"]
                    and health_info["consecutive_successes"]
                    >= self.config.recovery_threshold
                ):
                    health_info["healthy"] = True
                    logger.info(f"✅ 域名 {domain} 已恢復健康")
            else:
                health_info["consecutive_failures"] += 1
                health_info["consecutive_successes"] = 0
                health_info["total_failures"] += 1

                # 標記為不健康
                if (
                    health_info["healthy"]
                    and health_info["consecutive_failures"]
                    >= self.config.failure_threshold
                ):
                    health_info["healthy"] = False
                    logger.warning(f"⚠️ 域名 {domain} 被標記為不健康")

    def is_domain_healthy(self, domain: str) -> bool:
        """檢查域名是否健康"""
        if domain not in self.domain_health:
            return True  # 未知域名預設為健康
        return self.domain_health[domain]["healthy"]

    def _start_health_check_task(self):
        """啟動背景健康檢查任務"""

        async def health_check_worker():
            while True:
                try:
                    await asyncio.sleep(self.config.check_interval)

                    # 檢查所有已知域名
                    for domain in list(self.domain_health.keys()):
                        health_check_result = await self.check_domain_health(domain)
                        await self.update_domain_health(
                            domain, health_check_result.success
                        )

                except Exception as e:
                    logger.error(f"健康檢查任務失敗: {e}")

        # 在背景執行
        asyncio.create_task(health_check_worker())
        logger.info(f"🏥 健康檢查任務已啟動 (間隔: {self.config.check_interval}秒)")

    def get_health_report(self) -> Dict[str, Any]:
        """獲取健康報告"""
        healthy_domains = []
        unhealthy_domains = []

        for domain, info in self.domain_health.items():
            if info["healthy"]:
                healthy_domains.append(domain)
            else:
                unhealthy_domains.append(domain)

        total_domains = len(self.domain_health)
        health_rate = (
            (len(healthy_domains) / total_domains * 100) if total_domains > 0 else 100
        )

        return {
            "total_domains": total_domains,
            "healthy_domains": healthy_domains,
            "unhealthy_domains": unhealthy_domains,
            "health_rate": f"{health_rate:.1f}%",
            "domain_details": self.domain_health,
        }


class BaseScraper(ABC):
    """基礎爬蟲抽象類"""

    def __init__(
        self,
        encoding_detector: EncodingDetector = None,
        rate_limiter: RateLimiter = None,
        cache_manager: CacheManager = None,
        retry_manager: RetryManager = None,
        health_checker: HealthChecker = None,
    ):

        self.encoding_detector = encoding_detector or EncodingDetector()
        self.rate_limiter = rate_limiter or get_global_rate_limiter()
        self.cache_manager = cache_manager or CacheManager()
        self.retry_manager = retry_manager or RetryManager()
        self.health_checker = health_checker or HealthChecker()

        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "retry_attempts": 0,
        }

    @abstractmethod
    async def scrape_url(self, url: str) -> Result[Dict[str, Any]]:
        """抽象方法：爬取單個URL"""
        pass

    @abstractmethod
    def parse_content(self, content: str, url: str) -> Result[Dict[str, Any]]:
        """抽象方法：解析內容"""
        pass

    async def safe_scrape(self, url: str) -> Result[Dict[str, Any]]:
        """安全爬取（包含所有保護機制）"""
        domain = url.split("//")[-1].split("/")[0]

        # 檢查域名健康狀態
        health_check_result = self.health_checker.is_domain_healthy(domain)
        if not health_check_result:
            return Result.fail(
                ServiceError(
                    ErrorCode.SERVER_ERROR, f"域名 {domain} 當前不健康", {"url": url}
                )
            )

        # 使用重試管理器
        retry_result = await self.retry_manager.retry_async(
            self._scrape_with_protection, url
        )

        # 更新健康狀態
        await self.health_checker.update_domain_health(domain, retry_result.success)

        return retry_result

    async def _scrape_with_protection(self, url: str) -> Result[Dict[str, Any]]:
        """帶保護機制的爬取"""
        # 頻率控制
        await self.rate_limiter.wait_if_needed_async(url)

        # 檢查快取
        cached_result = await self.cache_manager.get_async(url)
        if cached_result:
            self.stats["cache_hits"] += 1
            return Result.ok(cached_result)

        # 執行實際爬取
        self.stats["total_requests"] += 1

        result = await self.scrape_url(url)

        if result.success:
            # 記錄成功
            self.rate_limiter.record_request(url, True, 0.0)
            self.stats["successful_requests"] += 1

            # 儲存到快取
            await self.cache_manager.set_async(url, result.data)

            return result
        else:
            # 記錄失敗
            self.rate_limiter.record_request(url, False, 0.0)
            self.stats["failed_requests"] += 1
            return result

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """獲取綜合統計資訊"""
        return {
            "scraper_stats": self.stats,
            "encoding_stats": self.encoding_detector.get_stats(),
            "rate_limiter_stats": self.rate_limiter.get_stats(),
            "cache_stats": self.cache_manager.get_stats(),
            "retry_stats": self.retry_manager.get_stats(),
            "health_stats": self.health_checker.get_health_report(),
        }
