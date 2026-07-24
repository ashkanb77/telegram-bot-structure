from enum import Enum


class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CANCELED = "CANCELED"


class UserRegisteredFromType(str, Enum):
    TELEGRAM = "TELEGRAM"
    BALE = "BALE"
    WEBSITE = "WEBSITE"
