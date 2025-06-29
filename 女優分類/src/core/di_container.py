from typing import Type, Callable, Dict, Any


class DIContainer:
    """簡單的依賴注入容器"""

    def __init__(self):
        self._singletons: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}

    def register_singleton(self, interface: Type, implementation: Type):
        """註冊單例服務"""
        self._factories[interface] = lambda: implementation()

    def register_factory(self, interface: Type, factory: Callable[[], Any]):
        """註冊工廠函數，每次請求時創建新實例"""
        self._factories[interface] = factory

    def resolve(self, interface: Type) -> Any:
        """解析服務實例"""
        if interface not in self._factories:
            raise ValueError(f"未註冊的服務: {interface.__name__}")

        if interface not in self._singletons:
            instance = self._factories[interface]()
            self._singletons[interface] = instance

        return self._singletons[interface]

    def reset(self):
        """重置容器，清除所有單例實例"""
        self._singletons = {}
