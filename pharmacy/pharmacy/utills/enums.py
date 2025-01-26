from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def list_all_values(cls):
        return list(map(lambda x: x.value, cls))


class ExpiryEnum(ExtendedEnum):
    EXPIRED = "expired"
    SHORT_EXPIRED = "shortExpired"
    EXPIRED_AND_SHORT_EXPIRED = "expiredAndShortExpired"

    def __repr__(self) -> str:
        return self.value


class LowQuantityEnums(ExtendedEnum):
    LOW = "low"
    VERY_LOW = "veryLow"


class LowQuantityThresholEnum(ExtendedEnum):
    LOW_LIMIT = 0.8
    VERY_LOW_LIMIT = 0.4

    def __repr__(self):
        return self.value
