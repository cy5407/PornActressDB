from dependency_injector import containers, providers
import logging

from .models.config import ConfigManager, PreferenceManager
from .models.database import SQLiteDBManager
from .models.extractor import UnifiedCodeExtractor
from .models.studio import StudioIdentifier
from .services.safe_searcher import SafeSearcher, RequestConfig
from .services.safe_javdb_searcher import SafeJAVDBSearcher
from .services.web_searcher import WebSearcher
from .services.interactive_classifier import InteractiveClassifier
from .services.studio_classifier import StudioClassificationCore
from .services.classifier_core import UnifiedClassifierCore
from .utils.scanner import UnifiedFileScanner


class Container(containers.DeclarativeContainer):
    # 配置日誌
    logger = providers.Singleton(logging.getLogger, __name__)

    # 配置管理器
    config_manager = providers.Singleton(ConfigManager)

    # 偏好設定管理器
    preference_manager = providers.Singleton(PreferenceManager)

    # 資料庫管理器
    db_manager = providers.Singleton(
        SQLiteDBManager,
        db_path="actress_database.db"
    )

    # 檔案掃描器
    file_scanner = providers.Singleton(UnifiedFileScanner)

    # 番號提取器
    code_extractor = providers.Singleton(UnifiedCodeExtractor)

    # 片商識別器
    studio_identifier = providers.Singleton(
        StudioIdentifier, rules_file="studios.json"  # 假設 studios.json 在專案根目錄
    )

    # 互動式分類器
    interactive_classifier = providers.Singleton(
        InteractiveClassifier,
        preference_manager=preference_manager,
        # gui_parent 將在 run.py 中動態傳入
    )

    # 片商分類核心
    studio_classifier = providers.Singleton(
        StudioClassificationCore,
        db_manager=db_manager,
        code_extractor=code_extractor,
        studio_identifier=studio_identifier,
        preference_manager=preference_manager,
    )

    # 網路搜尋器
    web_searcher = providers.Singleton(
        WebSearcher,
        config=config_manager,
    )

    # 核心業務邏輯
    unified_classifier_core = providers.Singleton(
        UnifiedClassifierCore,
        config=config_manager,
        db_manager=db_manager,
        code_extractor=code_extractor,
        file_scanner=file_scanner,
        studio_identifier=studio_identifier,
        web_searcher=web_searcher,
        studio_classifier=studio_classifier,
        preference_manager=preference_manager,
        interactive_classifier=interactive_classifier,
    )

    # 這裡將會定義應用程式的各種服務和依賴
    # 例如:
    # unified_scraper = providers.Factory(UnifiedScraper, javdb_scraper=javdb_scraper)
    pass
