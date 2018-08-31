from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import Account

class AccountBasicAuthentication(BasicAuthentication):
    """Since the DRF BasicAuthentication class only validates entries in user model, we have to override the authenticate_credentials method which will use our apps model to authenticate API requests."""

    def _get_account(self, userid, password):
        try:
            account = Account.objects.get(username=userid)
        except Account.DoesNotExist:
            return None
        else:
            if account.check_auth_id(password):
                return account

    def authenticate_credentials(self, userid, password, request=None):
        account = self._get_account(userid, password)
        if account is None:
            raise AuthenticationFailed('User not found or wrong password')

        return (account, None)
