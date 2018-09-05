import base64

from django.core.urlresolvers import reverse
from django.test import TestCase

from rest_framework.test import APITestCase
from rest_framework import HTTP_HEADER_ENCODING, status

from utils.api_client import RequestType
from utils.caches import RedisConnection, TEST_REDIS_URL

from .constants import MAX_OUTBOUND_SMS_PER_NUMBER
from .models import Account, PhoneNumber
from .tests_config import Legend, unit_test_config
from .tests_config import test_accounts, test_phone_numbers


class UnitTestCase(TestCase):

    def setUp(self):
        self._unit_test_config = unit_test_config

    def test_unit(self):
        for config in self._unit_test_config:
            cls = config[Legend.CLS]
            ins = cls()
            for method in config[Legend.MDM]:
                func = getattr(cls, method[Legend.MN])
                data_func = method.get(Legend.DT_FN, None)
                exp_func = method.get(Legend.EX_FN, None)
                callback = method.get(Legend.CB, Legend.SOE)
                for data, exp in zip(method[Legend.DT], method[Legend.EX]):
                    dargs = data.get(Legend.AG, [])
                    dkwargs = data.get(Legend.KW, {})
        
                    res = None 
                    if data_func:
                        data = data_func(ins, *dargs, **dkwargs)
                        res = func(ins, data)
                    else:
                        res = func(ins, *dargs, **dkwargs)

                    if exp_func:
                        eargs = exp.get(Legend.AG, [])
                        ekwargs = exp.get(Legend.KW, {})
                        exp = exp_func(*eargs, **ekwargs)

                    callback(res, exp)
                print(method[Legend.MN], ' is OK')

class IntegrationTestCase(APITestCase):

    def setUp(self):
        Account.objects.bulk_create([Account(**data) for data in test_accounts])
        PhoneNumber.objects.bulk_create([PhoneNumber(**data) for data in test_phone_numbers])
        self.username1 = test_accounts[0]['username']
        self.username2 = test_accounts[1]['username']
        self.password1 = test_accounts[0]['auth_id']
        self.password2 = test_accounts[1]['auth_id']

    def _send_request_with_auth_header(self, method, *args, **kwargs):
        auth = self._basic_auth_header()
        kwargs['HTTP_AUTHORIZATION'] = auth
        if args and isinstance(args[-1], dict):
            args[-1]['integration_test'] = True
        return method(*args, **kwargs)

    def _send_request_without_auth_header(self, method, *args, **kwargs):
        if args and isinstance(args[-1], dict):
            args[-1]['integration_test'] = True
        return method(*args, **kwargs)

    def _basic_auth_header(self):
        credentials = ('%s:%s' % (self.username1, self.password1))
        base64_credentials = base64.b64encode(
            credentials.encode(HTTP_HEADER_ENCODING)
        ).decode(HTTP_HEADER_ENCODING)
        return 'Basic %s' % base64_credentials 

    def test_basic_auth(self):
        
        # Checking without basic authenticating
        method = self.client.get
        args = [reverse("inbound_sms"), ]
	
        response = self._send_request_without_auth_header(method, *args)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = self._send_request_with_auth_header(method, *args)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
       
        args = [reverse("outbound_sms"), ]
        response = self._send_request_without_auth_header(method, *args)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = self._send_request_with_auth_header(method, *args)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        print('test_basic_auth is OK')

    def test_only_post_allowed(self):
        method1 = self.client.put
        method2 = self.client.delete
        args1 = [reverse("inbound_sms")]
        args2 = [reverse("outbound_sms")]

        response = self._send_request_with_auth_header(method1, *args1)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        response = self._send_request_with_auth_header(method1, *args2)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        response = self._send_request_with_auth_header(method2, *args1)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        
        response = self._send_request_with_auth_header(method2, *args2)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

        print('test_only_post_allowed is OK')

    def test_params_validation(self):

        method = self.client.post
        args1 = [reverse("inbound_sms"), {}]
        args2 = [reverse("outbound_sms"), {"from": "4343434"}]

        response = self._send_request_with_auth_header(method, *args1)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert b'from is missing' in response.content
        
        response = self._send_request_with_auth_header(method, *args2)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert b'to is missing' in response.content

        args1[-1] = {
            'to': '32',
            'from': '43334343',
            'text': 'fdasfas'
        }
        args2[-1] = {
            'to': '43434343',
            'from': '4',
            'text': 'fdasfas'
        }
        response = self._send_request_with_auth_header(method, *args1)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert b'to is invalid' in response.content
        
        response = self._send_request_with_auth_header(method, *args2)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert b'from is invalid' in response.content


        args1[-1]['to'] = '434343434343'
        args2[-1]['from'] = '43434343434'
        
        response = self._send_request_with_auth_header(method, *args1)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert b'to parameter not found' in response.content
        
        response = self._send_request_with_auth_header(method, *args2)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert b'from parameter not found' in response.content

        print('test_params_validation is OK')


    def test_inbound_sms(self):
        
        method = self.client.post
        args = [reverse("inbound_sms"), {"to": test_phone_numbers[0]["number"], "from": "343434343", "text": "hola"}]
        
        response = self._send_request_with_auth_header(method, *args)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert b'inbound sms ok' in response.content
        
        print('test_inbound is OK')

    def test_stop_request(self):
        method = self.client.post
        args = [reverse("inbound_sms"), {"to": test_phone_numbers[0]["number"], "from": test_phone_numbers[3]["number"], "text": "STOP\r\n"}]
        
        response = self._send_request_with_auth_header(method, *args)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert b'inbound sms ok' in response.content

        args[0] = reverse("outbound_sms")
        d = args[-1]
        d['to'], d['from'] = d['from'], d['to']
        d['text'] = "Test"
        
        response = self._send_request_with_auth_header(method, *args)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert b'blocked by STOP request' in response.content

        print('test_stop_request is OK')

    def test_outbound_sms(self):

        method = self.client.post
        args = [reverse("outbound_sms"), {"from": test_phone_numbers[0]["number"], "to": "343434343", "text": "hola"}]
        
        response = self._send_request_with_auth_header(method, *args)
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert b'outbound sms ok' in response.content

        print('test_outbound_sms is OK')

    def test_outbound_sms_limit(self):

        method = self.client.post
        args = [reverse("outbound_sms"), {"from": test_phone_numbers[0]["number"], "to": "343434343", "text": "hola"}]
        for i in range(MAX_OUTBOUND_SMS_PER_NUMBER): 
            response = self._send_request_with_auth_header(method, *args)
            assert response.status_code == status.HTTP_202_ACCEPTED
            assert b'outbound sms ok' in response.content
        response = self._send_request_with_auth_header(method, *args)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert b'limit reached for from' in response.content
        
        print('test_outbound_sms_limit is OK')

    def tearDown(self):
    
        r = RedisConnection.get_connection(TEST_REDIS_URL)
        r.flushall()
