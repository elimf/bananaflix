from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Generic


class ResponseStatus(str, Enum):
    success = "success"
    failed = "failed"


T = TypeVar("T")


@dataclass
class ResponseModel(Generic[T]):
    status: ResponseStatus
    statusCode: int
    message: str | None = None
    response: T | None = None
