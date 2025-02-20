from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def list_all_values(cls):
        return list(map(lambda x: x.value, cls))

    @classmethod
    def choices(cls):
        return [(key.value, key.name.replace("_", " ").title()) for key in cls]


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


class TransactionType(ExtendedEnum):
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_MADE = "payment_made"
    PRODUCTS_RECIEVED = "products_recieved"


class DiscrepancyTypeEnum(ExtendedEnum):
    HOME_EXPENSE = "home_expense"
    FREE = "free"
    LOST = "lost"
    DAMAGED = "damaged"
    EXPIRED = "expired"
    DONATED = "donated"
    RETURNED_SHORT_EXPIRY = "returned_shortExpiry"
    RECOVERED_CASH_APPROVAL = "recovered_cash_approval"


class OrderStatusEnum(ExtendedEnum):
    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
