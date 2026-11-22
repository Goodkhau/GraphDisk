from enum import Enum
from typing import override

class ColumnType(str, Enum):
    Integer   = "INTEGER"
    Float     = "REAL"
    String    = "TEXT"
    Bytes     = "BLOB"

    # This function overrides enum indexing failure. Makes indexing this enum soft casing.
    @classmethod
    @override
    def _missing_(cls, value):  # pyright: ignore[reportMissingParameterType]
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return super()._missing_(value)  # pyright: ignore[reportAny]