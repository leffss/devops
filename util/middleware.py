from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.conf import settings
import random
from django.urls import Resolver404, resolve, reverse
import sys
import re
from django.views.debug import technical_500_response, technical_404_response


class NextMiddleware(MiddlewareMixin):      # 老版本写法，后面会废弃
    @staticmethod
    def process_request(request):
        # 若请求的是登陆页面 则往下执行
        next = request.GET.get('next', None)
        if next:
            request.next = next

    # def process_response(self, request, response):
    #     response.status_code = 500
    #     return response


class NewNextMiddleware:                 # 新版 2.2 写法
    def __init__(self, get_response):
        self.get_response = get_response
        # 配置和初始化

    def __call__(self, request):
        # 在这里编写视图和后面的中间件被调用之前需要执行的代码
        # 这里其实就是旧的process_request()方法的代码
        next = request.GET.get('next', None)
        if next:
            request.next = next
        response = self.get_response(request)

        # 在这里编写视图调用后需要执行的代码
        # 这里其实就是旧的process_response()方法的代码
        return response


class GetRealClientMiddleware:
    """
    前端有 nginx 代理时，配置：
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.META.get('HTTP_X_REAL_IP'):
            try:
                request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
            except Exception:
                pass
        else:
            try:
                if request.META.get('HTTP_X_FORWARDED_FOR'):
                    request.META['REMOTE_ADDR'] = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
            except Exception:
                pass
        response = self.get_response(request)
        return response


class BlackListMiddleware:
    """
    黑名单中间件，可以在 settings.py 中添加一个 BLACKLIST（全大写）列表
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.META['REMOTE_ADDR'] in getattr(settings, "BLACKLIST", []):
            return HttpResponseForbidden('<h1>该IP地址被限制访问！</h1>')
        response = self.get_response(request)
        return response


class LockScreenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path not in [reverse('user:lockscreen'), reverse('user:login'), reverse('user:logout'), reverse('scheduler_api:client_upload')]:
            if request.session.get('locked', False):
                return redirect(reverse('user:lockscreen'))
        response = self.get_response(request)
        return response


class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 当 debug 设置为 False 时，返回 404 时
        # 如果是管理员，则返回一个特殊的响应对象，也就是Debug页面
        # 如果是普通用户，则返回None，交给默认的流程处理
        response = self.get_response(request)
        if not settings.DEBUG:
            if response.status_code == 404:
                if request.session['issuperuser']:
                    try:
                        resolve(request.path)
                    except Resolver404 as e:
                        return technical_404_response(request, e)
        return response
        # response = self.get_response(request)
        # return response

    def process_exception(self, request, exception):
        # 当 debug 设置为 False 时，返回服务器错误时
        # 如果是管理员，则返回一个特殊的响应对象，也就是Debug页面
        # 如果是普通用户，则返回None，交给默认的流程处理
        if not settings.DEBUG:
            if request.session['issuperuser']:
                return technical_500_response(request, *sys.exc_info())


class PermissionMiddleware:
    """
    根据 session 里面记录的 url, 判断当前请求是否有权限
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_url = request.path_info
        for valid in settings.VALID_URL:    # 白名单直接返回
            if re.match('^%s$' % valid, current_url):
                response = self.get_response(request)
                return response
        try:
            if not request.session.get('islogin', None):    # 未登录直接调整到登陆页面
                return redirect(reverse('user:login'))
        except Exception:
            return redirect(reverse('user:login'))
        for url in request.session[settings.INIT_PERMISSION]['urls']:
            reg = '^%s$' % url
            if re.match(reg, current_url):
                # print('当前url： {} -- 有权限'.format(current_url))
                break
        else:
            if request.session[settings.INIT_PERMISSION]['urls']:   # 首页仪表盘无权限时尝试跳转
                return redirect('/user/profile/')
            else:
                return HttpResponseForbidden('<h1>无权限访问！</h1>')
        response = self.get_response(request)
        return response
