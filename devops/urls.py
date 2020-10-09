"""devops URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path, include, re_path
from server.views import index
from django.conf import settings
from django.conf.urls.static import static
# import debug_toolbar

urlpatterns = [

    # path('admin/', admin.site.urls),

    # path('__debug__/', include(debug_toolbar.urls)),
    
    path('', index),
    
    path('server/', include('server.urls', namespace='server')),
    path('api/server/', include('server.urls_api', namespace='server_api')),
    
    path('user/', include('user.urls', namespace='user')),
    path('api/user/', include('user.urls_api', namespace='user_api')),
    
    path('webssh/', include('webssh.urls', namespace='webssh')),
    path('api/webssh/', include('webssh.urls_api', namespace='webssh_api')),

    path('webtelnet/', include('webtelnet.urls', namespace='webtelnet')),

    path('webguacamole/', include('webguacamole.urls', namespace='webguacamole')),
    path('api/webguacamole/', include('webguacamole.urls_api', namespace='webguacamole_api')),

    path('batch/', include('batch.urls', namespace='batch')),
    path('api/batch/', include('batch.urls_api', namespace='batch_api')),

    path('scheduler/', include('scheduler.urls', namespace='scheduler')),
    path('api/scheduler/', include('scheduler.urls_api', namespace='scheduler_api')),

]

"""
正式部署时一般静态文件直接用 nginx 转发，django 本身处理动态请求
"""
if settings.DEBUG:  # debug 模式下加载 /media 静态资源
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:  # 非 debug 模式下加载 /static 静态资源，debug 模式下 django 开发服务器会默认加载静态资源
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
