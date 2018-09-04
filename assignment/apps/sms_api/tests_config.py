from rest_framework.response import Response

from utils.api_client import RequestType

from .client import SMSAPIClient
from .constants import ErrorMessage, SERIALIZER_FIELD_PREFIX, SMSParams
from .serializers import SMSDataSerializer
from .views import BaseView


class AssertionCallback(object):

    @classmethod
    def simple_object_equality(cls, obj1, obj2):
        assert obj1 == obj2

    @classmethod
    def drf_response_equality(cls, obj1, obj2):
        cls.simple_object_equality(obj1.status_code, obj2.status_code)
        cls.simple_object_equality(obj1.data, obj2.data)


class DataGeneratorFunction(object):

    @staticmethod
    def generate_serializer_errors(instance, *args, **kwargs):
        data = instance._format_data(kwargs)
        serializer = SMSDataSerializer(data=data)
        if not serializer.is_valid():
            return serializer.errors
        return {}


class Legend(object):
    CLS = 'cls'
    MDM = 'method_data_map'
    MN = 'method_name'
    DT = 'data'
    EX = 'expected'
    AG = 'args'
    KW = 'kwargs'
    CB = 'callback'
    DT_FN = 'data_function'
    EX_FN = 'expected_function'
    RM = 'request_method'
    SOE = AssertionCallback.simple_object_equality
    DRE = AssertionCallback.drf_response_equality
    GSE = DataGeneratorFunction.generate_serializer_errors
        
unit_test_config = [
    {
        Legend.CLS: BaseView,
        Legend.MDM: [
            {
                Legend.MN: '_from_request_key',
                Legend.DT: [
                    {Legend.AG: ['test'],},
                ],
                Legend.EX: [
                    SERIALIZER_FIELD_PREFIX + 'test'
                ],
            },
            {
                Legend.MN: '_to_request_key',
                Legend.DT: [
                    {Legend.AG: ['test1'],},
                    {Legend.AG: [SERIALIZER_FIELD_PREFIX + 'test2'],}
                ],
                Legend.EX: ['test1', 'test2']
            },
            {
                Legend.MN: '_format_data',
                Legend.DT: [
                    {Legend.AG: [{'a': 'b', 'c': 'd'}],},
                    {Legend.AG: [78787878],}
                ],
                Legend.EX: [
                    {
                        SERIALIZER_FIELD_PREFIX + 'a': 'b',
                        SERIALIZER_FIELD_PREFIX + 'c': 'd'
                    },
                    None
                ],
            },
            {
                Legend.MN: '_response',
                Legend.CB: Legend.DRE,
                Legend.DT: [
                    {Legend.AG: []},
                    {Legend.AG: ['success', 'failure', 200]},
                    {Legend.AG:['success']},
                    {Legend.KW:{'error': 'failure', 'status': 400}},
                ],
                Legend.EX_FN: Response,
                Legend.EX: [
                    {Legend.AG: [{"error": "", "message": ""}, 202]},
                    {Legend.AG: [{"message": "success", "error": "failure"}, 200]},
                    {Legend.AG: [{"message": "success", "error": ""}, 202]},
                    {Legend.AG: [{"message": "", "error": "failure"}, 400]}
                ]
            },
            {
                Legend.MN: '_error_response',
                Legend.CB: Legend.DRE,
                Legend.DT: [
                    {Legend.AG: ['error']},
                    {Legend.AG: ['not found', 404]}
                ],
                Legend.EX_FN: Response,
                Legend.EX: [
                    {Legend.AG: [{'error': 'error', 'message': ''}, 400]},
                    {Legend.AG: [{'error': 'not found', 'message':''}, 404]}
                ],
            },
            {
                Legend.MN: '_accepted_response',
                Legend.CB: Legend.DRE,
                Legend.DT: [
                    {Legend.AG: ['accepted']},
                ],
                Legend.EX_FN: Response,
                Legend.EX: [
                    {Legend.AG: [{'error': '', 'message':'accepted'}, 202]}
                ]
            },
            {
                Legend.MN: '_unknown_failure_response',
                Legend.CB: Legend.DRE,
                Legend.DT: [
                    {}
                ],
                Legend.EX_FN: Response,
                Legend.EX: [
                    {Legend.AG: [{'message': '', 'error': ErrorMessage.UNKNOWN_FAILURE}, 500]}
                ]
            },
            {
                Legend.MN: '_process_validation_errors',
                Legend.CB: Legend.DRE,
                Legend.DT_FN: Legend.GSE,
                Legend.DT: [
                    {Legend.KW: {}},
                    {Legend.KW: {SMSParams.FROM: '1'}},
                    {Legend.KW: {SMSParams.TO: '1', SMSParams.FROM: '4343434343', SMSParams.TEXT: 'test'}},
                ],
                Legend.EX_FN: Response,
                Legend.EX: [
                    {Legend.AG: [{'message': '', 'error': ErrorMessage.PARAM_MISSING % SMSParams.FROM}, 400]},
                    {Legend.AG: [{'message': '', 'error': ErrorMessage.PARAM_MISSING % SMSParams.TO}, 400]},
                    {Legend.AG: [{'message': '', 'error': ErrorMessage.PARAM_INVALID % SMSParams.TO}, 400]}
                ],
            },
        ]
    }
]

test_accounts = [
    {'username': 'user1', 'auth_id': 1, 'id': 1},
    {'username': 'user2', 'auth_id': 2, 'id': 2}
]
test_phone_numbers = [
    {'account_id': 1, 'number': '1111111'},
    {'account_id': 1, 'number': '2222222'},
    {'account_id': 1, 'number': '3333333'},
    {'account_id': 2, 'number': '4444444'},
    {'account_id': 2, 'number': '5555555'}
]
