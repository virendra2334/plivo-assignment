from rest_framework.fields import Field

FIELD_REQUIRED_MESSAGE = Field.default_error_messages['required']
SERIALIZER_FIELD_PREFIX = "sms_"
STOP_MESSAGE = 'STOP'

MAX_OUTBOUND_SMS_PER_NUMBER = 5


class SMSType(object):

    INBOUND = "inbound"
    OUTBOUND = "outbound"

class ErrorMessage(object):

    DATA_INVALID = "data must be a dictionary"
    PARAM_NOT_FOUND = "%s parameter not found"
    PARAM_MISSING = "%s is missing"
    PARAM_INVALID = "%s is invalid"
    UNKNOWN_FAILURE = "unknown failure"
    LIMIT_REACHED = "limit reached for from %s"
    SMS_BLOCKED = "sms from %s to %s blocked by STOP request"

class SuccessMessage(object):

    SMS_REQUEST_OK = "%s sms ok"


class SMSParams(object):

    TO = "to"
    FROM = "from"
    TEXT = "text"

