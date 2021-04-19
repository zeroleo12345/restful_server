from rest_framework.views import APIView
# 项目库
from framework.restful import BihuResponse
from trade.models import Account, User
from . import validators


class SearchUserView(APIView):
    authentication_classes = ()      # 默认配置
    permission_classes = ()

    # /search/user?name=abc
    def get(self, request):
        serializer = validators.SearchValidator(data=request.GET)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data.get('name')
        #
        data = []
        for user in User.search(nickname__contains=name):
            accounts = Account.search(user_id=user.user_id)
            for account in accounts:
                data.append(account.to_dict())
        return BihuResponse(data=data)
