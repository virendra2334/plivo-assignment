# Create your views here.

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_202_ACCEPTED
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR

from utils.caches import RedisConnection

from .authentication import AccountBasicAuthentication
from .constants import ErrorMessage, FIELD_REQUIRED_MESSAGE 
from .constants import MAX_OUTBOUND_SMS_PER_NUMBER, SERIALIZER_FIELD_PREFIX
from .constants import SMSParams, SMSType, STOP_MESSAGE, SuccessMessage
from .models import PhoneNumber
from .serializers import SMSDataSerializer
from .utils import OutboundSMSCounter, StopRequestStore


class BaseView(APIView):

    authentication_classes = [AccountBasicAuthentication]
    permission_classes = [IsAuthenticated]

    def _from_request_key(self, key):
        return '%s%s' % (SERIALIZER_FIELD_PREFIX, key)

    def _to_request_key(self, key):
        return key.replace(SERIALIZER_FIELD_PREFIX, '')

    def format_data(self, data): 
        fdata = {}
        for k, v in data.items():
            fdata[self._from_request_key(k)] = v

        return fdata

    def _response(self, message="", error="", status=HTTP_202_ACCEPTED):
        return Response({"error": error, "message": message}, status)

    def _error_response(self, error, status=HTTP_400_BAD_REQUEST):
        return self._response(error=error, status=status)
    
    def _accepted_response(self, message):
        return self._response(message=message)

    def _unknown_failure_response(self):
        return self._error_response(
            ErrorMessage.UNKNOWN_FAILURE, status=HTTP_500_INTERNAL_SERVER_ERROR
        )

    def _process_validation_errors(self, errors):
        missing_fields = []
        invalid_fields = []
        for k, v in errors.items():
            if FIELD_REQUIRED_MESSAGE in v:
                missing_fields.append(k)
            else:
                invalid_fields.append(k)

        if missing_fields or invalid_fields:
            field = None
            error = None

            if missing_fields:
                error = ErrorMessage.PARAM_MISSING
                field = missing_fields[0]
            else:
                error = ErrorMessage.PARAM_INVALID
                field = invalid_fields[0]
            field = self._to_request_key(field)
            
            return self._error_response(error % field)

    def post(self, request, format=None):
        
        self._cache = RedisConnection()

        if not isinstance(request.data, dict):
            return self._error_response(ErrorMessage.DATA_INVALID)

        data = self.format_data(request.data) if request.data else {}
        serializer = SMSDataSerializer(data=data)
        if serializer.is_valid():
            sms = serializer.save()
            resp = self._process_request(request, sms)
        else:
            resp = self._process_validation_errors(serializer.errors)
        
        delattr(self, '_cache')
        return resp

    def _process_request(self, request, sms, execution_chain):
        try:
            for func in execution_chain:
                is_valid, response = func(request, sms)
                if is_valid:
                    continue
                return response
        except Exception as e:
            print(e)
            return self._unknown_failure_response()


class InboundSMSView(BaseView):

    def _validate_to_number(self, request, sms):
        is_valid = PhoneNumber.number_exists(request.user.id, sms.sms_to)
        if is_valid:
            return True, None
        else:
            resp = self._error_response(
                ErrorMessage.PARAM_NOT_FOUND % SMSParams.TO,
                HTTP_404_NOT_FOUND
            )
            return False, resp

    def _handle_stop_request(self, request, sms):
        if sms.sms_text.strip() == STOP_MESSAGE:
            store = StopRequestStore(self._cache)
            key = StopRequestStore.generate_key([sms.sms_from, sms.sms_to])
            store.set(key, True)
        return True, None

    def _process_request(self, request, sms):

        execution_chain = [
            self._validate_to_number,
            self._handle_stop_request,
        ]
        resp =  super()._process_request(request, sms, execution_chain)
        if resp:
            return resp
        else:
            return self._accepted_response(
                SuccessMessage.SMS_REQUEST_OK % SMSType.INBOUND
            )


class OutboundSMSView(BaseView):

    def _validate_from_number(self, request, sms):
        is_valid = PhoneNumber.number_exists(request.user.id, sms.sms_from)
        if is_valid:
            return True, None
        else:
            resp = self._error_response(
                ErrorMessage.PARAM_NOT_FOUND % SMSParams.FROM,
                HTTP_404_NOT_FOUND
            )
            return False, resp

    def _check_request_limit(self, request, sms):
        key = OutboundSMSCounter.generate_key([sms.sms_from])
        store = OutboundSMSCounter(self._cache)
        counter = store.get(key)
        
        if counter is None:
            store.setincr(key, 1)
            return True, None

        counter = int(counter)
        if counter >= MAX_OUTBOUND_SMS_PER_NUMBER:
            error = ErrorMessage.LIMIT_REACHED % sms.sms_from
            resp = self._error_response(error, HTTP_403_FORBIDDEN)
            return False, resp
        else:
            store.incr(key, 1)
            return True, None

    def _check_stop_request(self, request, sms):
        key = StopRequestStore.generate_key([sms.sms_to, sms.sms_from])
        store = StopRequestStore(self._cache)
        if store.exists(key):
            error = ErrorMessage.SMS_BLOCKED % (sms.sms_from, sms.sms_to)
            resp = self._error_response(error, HTTP_403_FORBIDDEN)
            return False, resp
        return True, None

    def _process_request(self, request, sms):

        execution_chain = [
            self._validate_from_number,
            self._check_request_limit,
            self._check_stop_request
        ]

        resp = super()._process_request(request, sms, execution_chain)
        if resp:
            return resp
        else:
            return self._accepted_response(
                SuccessMessage.SMS_REQUEST_OK % SMSType.OUTBOUND
            )
