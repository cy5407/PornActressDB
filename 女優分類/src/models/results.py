from enum import Enum
from dataclasses import dataclass
from typing import Optional, Union, TypeVar, Generic

T = TypeVar("T")


class ErrorCode(Enum):
    NETWORK_ERROR = "NETWORK_ERROR"
    PARSING_ERROR = "PARSING_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    FILE_ERROR = "FILE_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"  # Added for general unhandled exceptions


@dataclass
class ServiceError:
    code: ErrorCode
    message: str
    details: Optional[dict] = None
    caused_by: Optional[Exception] = None


@dataclass
class Result(Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[ServiceError] = None

    @classmethod
    def ok(cls, data: T) -> "Result[T]":
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: ServiceError) -> "Result[T]":
        return cls(success=False, error=error)
