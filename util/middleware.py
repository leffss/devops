# -*- coding: utf-8 -*-
from django.utils.deprecation import MiddlewareMixin


class NextMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        # 若请求的是登陆页面 则往下执行
        next = request.GET.get('next', None)
        if next:
            request.next = next

    # def process_response(self, request, response):
    #     response.status_code = 500
    #     return response
