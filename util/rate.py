from django.conf import settings


# def rate(group, request):
#     return settings.RATELIMIT_LOGIN if request.session.get('islogin', False) else settings.RATELIMIT_NOLOGIN


# django-ratelimit 限制页面访问频率，超过则返回 403
rate = lambda group, request: settings.RATELIMIT_LOGIN if request.session.get('islogin') else settings.RATELIMIT_NOLOGIN


# def key(group, request):
#     return request.META['HTTP_X_REAL_IP'] if request.META.get('HTTP_X_REAL_IP') else request.META['REMOTE_ADDR']


key = lambda group, request: request.META['HTTP_X_REAL_IP'] if request.META.get('HTTP_X_REAL_IP') else request.META['REMOTE_ADDR']
